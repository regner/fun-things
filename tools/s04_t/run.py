#!/usr/bin/env python3
"""Run the bounded two-process foot/car prediction-transition fixture."""

from __future__ import annotations

import argparse
import heapq
import json
import math
from pathlib import Path
import platform
import random
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from measurement_identity import measurement_identity
from run_s03 import stop_children
from script_checks import ROOT, DIAGNOSTIC, checked_command, engine_version, environment
from window_safety import capped_window_arguments, require_capped_window

PROFILES = {
    "normal": (75, 30, 0.02),
    "adverse": (125, 50, 0.05),
}
POLL_SECONDS = 0.002
MAX_POLL = 128
MAX_QUEUE = 1024
BLACKOUT_START_SECONDS = 2.0
BLACKOUT_SECONDS = 0.5
MEASUREMENT_SOURCES = [
    "tools/s04_t",
    "tools/measurement_identity.py",
    "tools/window_safety.py",
    "tools/script_checks.py",
    "tools/run_s03.py",
    "tests/fixtures/s02",
    "tests/fixtures/s03_r",
    "tests/fixtures/s04",
    "tests/fixtures/s04_t",
]


class TransitionProxy:
    """Impair one loopback ENet route with seeded delay, loss, and an adverse blackout."""

    def __init__(self, host_port: int, proxy_port: int, profile: str, log) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.socket.bind(("127.0.0.1", proxy_port))
        except OSError:
            self.socket.close()
            raise
        self.socket.setblocking(False)
        self.host = ("127.0.0.1", host_port)
        self.client = None
        self.profile = profile
        self.delay_ms, self.jitter_ms, self.loss = PROFILES[profile]
        self.random = {"up": random.Random(4041), "down": random.Random(4049)}
        self.queue = []
        self.serial = 0
        self.started = None
        self.blackout_done = profile != "adverse"
        self.peak_queue = 0
        self.events = []
        self.log = log

    def record(self, event: str, **values) -> None:
        """Retain one complete proxy event for diagnosis and independent timing checks."""
        row = {"event": event, "wall_ms": time.time() * 1000,
               "monotonic": time.monotonic(), **values}
        self.events.append(row)
        self.log.write(json.dumps(row) + "\n")
        self.log.flush()

    def poll(self) -> None:
        """Receive and deliver bounded datagram work without blocking the process runner."""
        now = time.monotonic()
        interrupted = False
        if self.profile == "adverse" and self.started is not None:
            age = now - self.started
            interrupted = BLACKOUT_START_SECONDS <= age < (
                BLACKOUT_START_SECONDS + BLACKOUT_SECONDS)
            if age >= BLACKOUT_START_SECONDS + BLACKOUT_SECONDS:
                self.blackout_done = True

        for _ in range(MAX_POLL):
            try:
                data, source = self.socket.recvfrom(65_535)
            except BlockingIOError:
                break
            except ConnectionResetError:
                continue
            direction = "down" if source == self.host else "up"
            if direction == "up":
                if self.client is not None and source != self.client:
                    raise RuntimeError("unexpected second proxy client")
                self.client = source
            destination = self.client if direction == "down" else self.host
            if destination is None:
                raise RuntimeError("host datagram arrived before a client route")
            self.serial += 1
            rng = self.random[direction]
            if interrupted or rng.random() < self.loss:
                self.record("drop", direction=direction, bytes=len(data),
                            reason="blackout" if interrupted else "random")
                continue
            if len(self.queue) >= MAX_QUEUE:
                raise RuntimeError("proxy queue bound exceeded")
            delay = max(0.0, self.delay_ms + rng.uniform(-self.jitter_ms, self.jitter_ms))
            heapq.heappush(self.queue, (now + delay / 1000, self.serial, now,
                                      data, destination, direction))
            self.peak_queue = max(self.peak_queue, len(self.queue))

        for _ in range(MAX_POLL):
            if not self.queue or self.queue[0][0] > now:
                break
            due, serial, received, data, destination, direction = heapq.heappop(self.queue)
            if interrupted:
                self.record("drop", direction=direction, bytes=len(data),
                            reason="blackout_pending", id=serial)
                continue
            self.socket.sendto(data, destination)
            self.record("delivery", direction=direction, bytes=len(data), id=serial,
                        actual_delay_ms=(now - received) * 1000,
                        scheduled_delay_ms=(due - received) * 1000)


def percentile(values: list[float], quantile: float = 0.95) -> float | None:
    """Return the nearest-rank percentile used by the prediction records."""
    if not values:
        return None
    return sorted(values)[math.ceil(len(values) * quantile) - 1]


def records(path: Path) -> list[dict]:
    """Read complete fixture telemetry rows while ignoring ordinary engine output."""
    return [json.loads(line[5:]) for line in path.read_text(errors="replace").splitlines()
            if line.startswith("S04T ")]


def stage_fixture(directory: Path) -> Path:
    """Copy only the accepted fixture dependencies into an addon-free project."""
    project = directory / "project"
    for fixture in ["s02", "s03_r", "s04", "s04_t"]:
        shutil.copytree(ROOT / "tests/fixtures" / fixture,
                        project / "tests/fixtures" / fixture)
    models = project / "art/models/spikes"
    models.mkdir(parents=True)
    for pattern in ["s02_*.*", "s04_*.*"]:
        for path in (ROOT / "art/models/spikes").glob(pattern):
            shutil.copy2(path, models / path.name)
    (project / "project.godot").write_text(
        'config_version=5\n[application]\nconfig/name="S04-T transition proof"\n'
        'run/main_scene="res://tests/fixtures/s04_t/boot.tscn"\n'
        '[display]\nwindow/size/viewport_width=1280\nwindow/size/viewport_height=800\n'
        '[rendering]\nrenderer/rendering_method="gl_compatibility"\n'
        'renderer/rendering_method.mobile="gl_compatibility"\n')
    return project


def analyze(directory: Path, profile: str, proxy: TransitionProxy) -> dict:
    """Independently derive the transition and authority outcomes from raw telemetry."""
    host = records(directory / "host/stdout.log")
    client = records(directory / "client/stdout.log")
    transitions = [row for row in client if row.get("event") == "transition"]
    by_stage = {row["stage"]: row for row in transitions}
    host_result = next((row for row in host if row.get("event") == "result"), {})
    client_result = next((row for row in client if row.get("event") == "result"), {})
    expected = {
        "race_entry": (False, "SEAT_OCCUPIED"),
        "parked_entry": (True, ""),
        "moving_exit": (False, "EXIT_MOVING"),
        "blocked_exit": (False, "EXIT_BLOCKED"),
        "successful_exit": (True, ""),
        "traffic_entry": (True, ""),
    }
    verdicts = all(stage in by_stage and by_stage[stage]["accepted"] == accepted
                   and by_stage[stage]["failure"] == failure
                   for stage, (accepted, failure) in expected.items())
    entries = [by_stage[name] for name in ["race_entry", "parked_entry", "traffic_entry"]
               if name in by_stage]
    delays = [row["actual_delay_ms"] for row in proxy.events
              if row.get("event") == "delivery"]
    captures = sorted(path.name for path in (directory / "client/captures").glob("*.png"))
    transfer_stages = {"race_entry", "parked_entry", "successful_exit", "traffic_entry"}
    transfer_rows = [row for row in transitions if row["stage"] in transfer_stages]
    measurements = {
        "entry_correction_m": {row["stage"]: row["correction_m"] for row in entries},
        "entry_visual_jump_m": {row["stage"]: row["visual_jump_m"] for row in entries},
        "transition_visual_jump_p95_m": percentile(
            [row["visual_jump_m"] for row in transitions]),
        "accepted_time_to_control_p95_ms": percentile(
            [row["time_to_control_ms"] for row in entries if row["accepted"]]),
        "action_round_trip_p95_ms": percentile(
            [row["round_trip_ms"] for row in transitions]),
        "history_clean": len(transfer_rows) == len(transfer_stages)
        and all(row["foot_history"] == 0 and row["car_history"] == 0
                for row in transfer_rows),
        "ownership_flips": all(row["camera_owner"] == row["hud_owner"]
                               for row in transitions),
        "proxy_delay_p95_ms": percentile(delays),
        "proxy_delay_max_ms": max(delays, default=0.0),
        "captures": captures,
    }
    race = next((row for row in host if row.get("event") == "seat_race"), {})
    criteria = {
        "two_process_results": host_result.get("ok") is True
        and client_result.get("ok") is True,
        "host_granted_race": race.get("winner") == 1 and race.get("loser", 0) > 1,
        "all_verdicts": verdicts,
        "history_clean": measurements["history_clean"],
        "ownership_flips": measurements["ownership_flips"],
        "traffic_released": host_result.get("traffic_stolen") is True
        and host_result.get("traffic_ai_active") is False,
        "disconnect_coasted": host_result.get("disconnect_coast_m", 0) > 0.05
        and host_result.get("final_speed_mps", 1) < 0.01,
        "adverse_blackout": proxy.blackout_done,
        "draw_receipts": bool(captures),
    }
    return {"profile": profile, "ok": all(criteria.values()),
            "criteria": criteria, "measurements": measurements,
            "host_result": host_result, "client_result": client_result}


def run_case(args, directory: Path, profile: str) -> dict:
    """Run one fresh host/client profile and retain all bounded process evidence."""
    directory.mkdir()
    project = stage_fixture(directory)
    import_command = [args.godot, "--headless", "--editor", "--path", str(project),
                      "--import", "--quit", "--log-file", str(directory / "import.engine.log")]
    if not checked_command(import_command, directory / "import.log",
                           environment(directory / "import-user")):
        raise RuntimeError("isolated fixture import failed")

    children = []
    logs = {}
    offsets = {"host": 0, "client": 0}
    process_results = {}
    ready = False
    commands = {}
    proxy_log = (directory / "proxy.jsonl").open("w")
    proxy = TransitionProxy(args.port, args.proxy_port, profile, proxy_log)
    deadline = time.monotonic() + args.deadline
    try:
        def start(role: str, port: int) -> None:
            role_dir = directory / role
            role_dir.mkdir()
            captures = role_dir / "captures"
            captures.mkdir()
            command = [args.godot]
            if args.windowed:
                command.extend(capped_window_arguments())
            else:
                command.append("--headless")
            command.extend(["--path", str(project), "--resolution", "1280x800",
                            "--position", "0,0" if role == "host" else "1280,0",
                            "--log-file", str(role_dir / "engine.log"),
                            "res://tests/fixtures/s04_t/boot.tscn", "--",
                            "--role=" + role, "--port=" + str(port)])
            if args.windowed:
                require_capped_window(command)
            commands[role] = command
            logs[role] = (role_dir / "stdout.log").open("w")
            env = environment(role_dir / "user")
            if args.windowed and role == "client":
                env["S04_T_CAPTURE_DIR"] = str(captures)
            children.append(subprocess.Popen(command, stdout=logs[role],
                                             stderr=subprocess.STDOUT, env=env))

        start("host", args.port)
        while time.monotonic() < deadline:
            proxy.poll()
            for role in list(logs):
                with (directory / role / "stdout.log").open() as output:
                    output.seek(offsets[role])
                    while True:
                        position = output.tell()
                        line = output.readline()
                        if not line.endswith("\n"):
                            offsets[role] = position
                            break
                        offsets[role] = output.tell()
                        if not line.startswith("S04T "):
                            continue
                        row = json.loads(line[5:])
                        if role == "host" and row.get("event") == "ready":
                            ready = True
                        if role == "client" and row.get("event") == "start":
                            proxy.started = time.monotonic()
                        if row.get("event") == "result":
                            process_results[role] = row
                            if row.get("ok") is not True:
                                raise RuntimeError(f"{role} fixture result failed: {row}")
            if ready and "client" not in logs:
                start("client", args.proxy_port)
            if len(process_results) == 2 and all(child.poll() is not None for child in children):
                break
            for index, child in enumerate(children):
                role = "host" if index == 0 else "client"
                if child.poll() is not None and role not in process_results:
                    raise RuntimeError(f"{role} exited before result ({child.returncode})")
            time.sleep(POLL_SECONDS)
        else:
            raise RuntimeError("two-process wall-clock deadline")
        if any(child.returncode != 0 for child in children):
            raise RuntimeError("nonzero process exit")
        for role in logs:
            for name in ["stdout.log", "engine.log"]:
                if DIAGNOSTIC.search((directory / role / name).read_text(errors="replace")):
                    raise RuntimeError(f"engine/script diagnostics in {role}/{name}")
        result = analyze(directory, profile, proxy)
        result.update({"commands": commands, "process_ids": [child.pid for child in children],
                       "exits": [child.returncode for child in children],
                       "peak_proxy_queue": proxy.peak_queue})
        (directory / "result.json").write_text(json.dumps(result, indent=2) + "\n")
        if not result["ok"]:
            raise RuntimeError(f"independent criteria failed: {result['criteria']}")
        return result
    finally:
        stop_children(children)
        for output in logs.values():
            output.close()
        proxy.socket.close()
        proxy_log.close()


def main() -> int:
    """Parse bounded parameters, execute fresh profiles, and retain source-bound results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot") or "godot")
    parser.add_argument("--port", type=int, default=25440)
    parser.add_argument("--proxy-port", type=int, default=25441)
    parser.add_argument("--deadline", type=float, default=45)
    parser.add_argument("--profiles", nargs="+", choices=PROFILES, default=list(PROFILES))
    parser.add_argument("--windowed", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not (1 <= args.port <= 65_535 and 1 <= args.proxy_port <= 65_535
            and args.port != args.proxy_port and 1 <= args.deadline <= 90):
        parser.error("distinct ports 1..65535 and deadline 1..90 seconds required")
    if not args.windowed:
        parser.error("S04-T visual discontinuity measurement requires --windowed")
    directory = (args.output or Path(tempfile.mkdtemp(prefix="s04-t-"))).resolve()
    if directory.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        parser.error("output must be a fresh empty directory")

    identity = measurement_identity(ROOT, MEASUREMENT_SOURCES,
                                    {**vars(args), "output": directory})
    previous_handler = signal.signal(signal.SIGTERM,
                                     lambda _signal, _frame: (_ for _ in ()).throw(
                                         KeyboardInterrupt()))
    results = []
    try:
        version = engine_version(args.godot)
        for index, profile in enumerate(args.profiles):
            args.port += index * 2
            args.proxy_port += index * 2
            results.append(run_case(args, directory / profile, profile))
        result = {"ok": all(row["ok"] for row in results), "engine": version,
                  "platform": platform.platform(), "measurement_identity": identity,
                  "profiles": results}
    except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as error:
        result = {"ok": False, "failure": str(error), "measurement_identity": identity,
                  "profiles": results}
    except KeyboardInterrupt:
        result = {"ok": False, "failure": "runner interrupted; owned children stopped",
                  "measurement_identity": identity, "profiles": results}
    finally:
        signal.signal(signal.SIGTERM, previous_handler)
    (directory / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"ok": result["ok"], "failure": result.get("failure"),
                      "output": str(directory)}))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
