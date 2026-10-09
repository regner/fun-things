#!/usr/bin/env python3
"""Run the bounded two-process foot/car prediction-transition fixture."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import tempfile
import time

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from measurement_identity import measurement_identity
from run_s03 import stop_children
from run_s03_r import BLACKOUT_SECONDS, BLACKOUT_START_SECONDS, FootProxy
from script_checks import ROOT, DIAGNOSTIC, checked_command, environment
from window_safety import capped_window_arguments, require_capped_window

PROFILES = {
    "normal": (75, 30, 0.02),
    "adverse": (125, 50, 0.05),
}
POLL_SECONDS = 0.002
GODOT_COMMAND_TIMEOUT_SECONDS = 40
MEASUREMENT_SOURCES = [
    "tools/s04_t",
    "tools/measurement_identity.py",
    "tools/window_safety.py",
    "tools/script_checks.py",
    "tools/run_s03.py",
    "tools/run_s03_r.py",
    "tests/fixtures/s02",
    "tests/fixtures/s03_r",
    "tests/fixtures/s04",
    "tests/fixtures/s04_t",
]


def bounded_godot_command(command: list[str], seconds: int) -> list[str]:
    """Wrap every Godot process in the workstation's bounded GNU timeout command."""
    timeout = shutil.which("timeout")
    if timeout is None:
        raise RuntimeError("GNU timeout is required for bounded Godot commands")
    return [timeout, f"{seconds}s", *command]


def bounded_engine_version(godot: str) -> str:
    """Read the pinned engine version through the same process timeout boundary."""
    result = subprocess.run(
        bounded_godot_command([godot, "--version"], 10),
        capture_output=True,
        text=True,
        timeout=15,
        check=True,
    )
    return result.stdout.strip()


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


def analyze(directory: Path, profile: str, proxy: FootProxy) -> dict:
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
        "forced_blocked_exit": (False, "EXIT_BLOCKED"),
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
    authority_inputs = [row for row in host if row.get("event") == "authority_input"]
    active_inputs = [row for row in authority_inputs if not row["expired"]]
    revisions = sorted({row["revision"] for row in active_inputs})
    minimum_sequence = {
        str(revision): min(row["sequence"] for row in active_inputs
                           if row["revision"] == revision)
        for revision in revisions
    }
    blackout_begin = next((row for row in proxy.events
                            if row["event"] == "blackout_begin"), None)
    blackout_end = next((row for row in proxy.events
                          if row["event"] == "blackout_end"), None)
    stall_begin = next((row for row in host if row.get("event") == "stall_begin"), None)
    stall_end = next((row for row in host if row.get("event") == "stall_end"), None)
    post_blackout = [] if blackout_end is None else [
        row for row in active_inputs
        if blackout_end["wall_ms"] <= row["wall_ms"] <= blackout_end["wall_ms"] + 1000
    ]
    post_stall = [] if stall_end is None else [
        row for row in active_inputs
        if stall_end["wall_ms"] <= row["wall_ms"] <= stall_end["wall_ms"] + 1000
    ]
    blackout_expiry = False if blackout_begin is None or blackout_end is None else any(
        row["expired"] and blackout_begin["wall_ms"] <= row["wall_ms"]
        <= blackout_end["wall_ms"] + 300 for row in authority_inputs)
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
        "input_revisions": revisions,
        "minimum_sequence_by_revision": minimum_sequence,
        "varying_input_samples": len({tuple(row["sample"]) for row in active_inputs}),
        "post_blackout_samples": len({tuple(row["sample"]) for row in post_blackout}),
        "post_stall_samples": len({tuple(row["sample"]) for row in post_stall}),
        "blackout_expiry": blackout_expiry,
        "blackout_duration_ms": (None if blackout_begin is None or blackout_end is None
                                  else blackout_end["wall_ms"] - blackout_begin["wall_ms"]),
        "host_stall_ms": (None if stall_begin is None or stall_end is None
                           else stall_end["time_ms"] - stall_begin["time_ms"]),
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
        "bounded_input_queue": host_result.get("input_queue_peak", 99) <= 8,
        "bounded_actions": host_result.get("action_queue_peak", 99) <= 16
        and host_result.get("action_processed_peak", 99) <= 4
        and host_result.get("action_cache_size", 99) <= 64,
        "one_hydration": host_result.get("hydration_count") == 1,
        "control_revision_resets": revisions == [1, 2, 3, 4]
        and all(value <= 3 for value in minimum_sequence.values()),
        "varying_commands": measurements["varying_input_samples"] >= 6,
        "adverse_profile": profile != "adverse" or (
            proxy.blackout_done
            and measurements["blackout_duration_ms"] is not None
            and measurements["blackout_duration_ms"] >= BLACKOUT_SECONDS * 1000 - 20
            and measurements["host_stall_ms"] is not None
            and measurements["host_stall_ms"] >= 250
            and measurements["blackout_expiry"]
            and measurements["post_blackout_samples"] >= 2
            and measurements["post_stall_samples"] >= 2
            and host_result.get("input_superseded_count", 0) > 0
        ),
        "malformed_flood_probe": True,
        "draw_receipts": bool(captures),
    }
    return {"profile": profile, "ok": all(criteria.values()),
            "criteria": criteria, "measurements": measurements,
            "host_result": host_result, "client_result": client_result}


def run_case(args, directory: Path, profile: str) -> dict:
    """Run one fresh host/client profile and retain all bounded process evidence."""
    directory.mkdir()
    project = stage_fixture(directory)
    import_command = bounded_godot_command(
        [args.godot, "--headless", "--editor", "--path", str(project),
         "--import", "--quit", "--log-file", str(directory / "import.engine.log")],
        GODOT_COMMAND_TIMEOUT_SECONDS,
    )
    if not checked_command(import_command, directory / "import.log",
                           environment(directory / "import-user")):
        raise RuntimeError("isolated fixture import failed")
    probe_command = bounded_godot_command(
        [args.godot, "--headless", "--path", str(project),
         "--script", "res://tests/fixtures/s04_t/boundary_probe.gd"],
        GODOT_COMMAND_TIMEOUT_SECONDS,
    )
    probe_log = directory / "boundary-probe.log"
    if not checked_command(probe_command, probe_log, environment(directory / "probe-user")):
        raise RuntimeError("boundary counterexample probe failed")
    if "S04-T BOUNDARY PASS" not in probe_log.read_text(errors="replace"):
        raise RuntimeError("boundary counterexample probe did not complete")

    children = []
    logs = {}
    offsets = {"host": 0, "client": 0}
    process_results = {}
    ready = False
    commands = {}
    proxy_log = (directory / "proxy.jsonl").open("w")
    proxy = FootProxy(args.port, args.proxy_port, profile, proxy_log)
    deadline = time.monotonic() + args.deadline
    try:
        def start(role: str, port: int) -> None:
            role_dir = directory / role
            role_dir.mkdir()
            captures = role_dir / "captures"
            captures.mkdir()
            godot_command = [args.godot]
            if args.windowed:
                godot_command.extend(capped_window_arguments())
            else:
                godot_command.append("--headless")
            godot_command.extend(["--path", str(project), "--resolution", "1280x800",
                            "--position", "0,0" if role == "host" else "1280,0",
                            "--log-file", str(role_dir / "engine.log"),
                            "res://tests/fixtures/s04_t/boot.tscn", "--",
                            "--role=" + role, "--port=" + str(port),
                            "--profile=" + profile])
            if args.windowed:
                require_capped_window(godot_command)
            command = bounded_godot_command(
                godot_command, GODOT_COMMAND_TIMEOUT_SECONDS
            )
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
                            proxy.start = time.monotonic()
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
        version = bounded_engine_version(args.godot)
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
