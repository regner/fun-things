#!/usr/bin/env python3
"""Bounded arcade-car-controller ENet experiment with retained native fault telemetry."""

import argparse
import heapq
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import re
import shutil
import signal
import socket
import subprocess
import tempfile
import time

from run_s03 import stop_children
from script_checks import ROOT, DIAGNOSTIC, checked_command, engine_version, environment

PROFILES = {"baseline": (0, 0, 0), "normal": (75, 30, 0.02),
            "adverse": (125, 50, 0.05)}
MAX_QUEUE = 1024
MAX_POLL = 128
POLL_SECONDS = 0.002
BLACKOUT_START_SECONDS = 12.15
BLACKOUT_SECONDS = 1.0


class CarProxy:
    """Impair actual bidirectional UDP datagrams with seeded, bounded independent streams."""

    def __init__(self, host_port, proxy_port, profile, log):
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
        self.delay, self.jitter, self.loss = PROFILES[profile]
        self.random = {"up": random.Random(731), "down": random.Random(947)}
        self.queue = []
        self.serial = 0
        self.start = None
        self.log = log
        self.events = []
        self.peak_queue = 0
        self.blackout_open = False
        self.blackout_done = False

    def record(self, event, **values):
        record = {"event": event, "wall_ms": time.time() * 1000,
                  "monotonic": time.monotonic(), **values}
        self.events.append(record)
        self.log.write(json.dumps(record) + "\n")

    def poll(self):
        now = time.monotonic()
        interrupted = False
        if self.profile == "adverse" and self.start is not None:
            age = now - self.start
            interrupted = BLACKOUT_START_SECONDS <= age < (
                BLACKOUT_START_SECONDS + BLACKOUT_SECONDS)
            if interrupted and not self.blackout_open:
                self.blackout_open = True
                self.record("blackout_begin")
            if age >= BLACKOUT_START_SECONDS + BLACKOUT_SECONDS and not self.blackout_done:
                self.blackout_done = True
                self.record("blackout_end")
        for _ in range(MAX_POLL):
            try:
                data, source = self.socket.recvfrom(65535)
            except BlockingIOError:
                break
            except ConnectionResetError:
                # Windows reports an earlier ICMP port-unreachable on the next receive.
                continue
            direction = "down" if source == self.host else "up"
            if direction == "up":
                if self.client is not None and source != self.client:
                    raise RuntimeError("unexpected second proxy client")
                self.client = source
            destination = self.client if direction == "down" else self.host
            if destination is None:
                raise RuntimeError("host datagram before client route")
            self.serial += 1
            rng = self.random[direction]
            lost = rng.random() < self.loss
            delay_ms = max(0, self.delay + rng.uniform(-self.jitter, self.jitter))
            if interrupted or lost:
                self.record("drop", id=self.serial, direction=direction, bytes=len(data),
                            reason="blackout" if interrupted else "random")
                continue
            if len(self.queue) >= MAX_QUEUE:
                raise RuntimeError("proxy queue limit exceeded")
            heapq.heappush(self.queue, (now + delay_ms / 1000, self.serial, now,
                                      data, destination, direction))
            self.peak_queue = max(self.peak_queue, len(self.queue))
        for _ in range(MAX_POLL):
            if not self.queue or self.queue[0][0] > now:
                break
            due, serial, received, data, destination, direction = heapq.heappop(self.queue)
            if interrupted:
                self.record("drop", id=serial, direction=direction, bytes=len(data),
                            reason="blackout_pending")
                continue
            self.socket.sendto(data, destination)
            self.record("delivery", id=serial, direction=direction, bytes=len(data),
                        actual_delay_ms=(now - received) * 1000,
                        scheduled_delay_ms=(due - received) * 1000)


def records(path):
    return [json.loads(line.removeprefix("S04 ")) for line in path.read_text().splitlines()
            if line.startswith("S04 ")]


def percentile(values, quantile=0.95):
    if not values:
        return None
    return sorted(values)[math.ceil(len(values) * quantile) - 1]


def distance(a, b):
    return math.dist(a, b)


def angle(a, b):
    return abs((a - b + math.pi) % (2 * math.pi) - math.pi)


def analyze(directory, proxy_events):
    """Compare outcome telemetry independently; targets may fail while an experiment succeeds."""
    host = records(directory / "host/stdout.log")
    client = records(directory / "client/stdout.log")
    simulation = [r for r in host if r["event"] == "simulation"]
    applied = [r for r in client if r["event"] == "apply"]
    poses = {(r["pose"]["entity"], r["pose"]["tick"]): r for r in simulation}
    errors = []
    ages = []
    jumps = []
    previous = {}
    for receipt in applied:
        pose = receipt["pose"]
        source = poses.get((pose["entity"], pose["tick"]))
        if source is None:  # Initial grant before experiment telemetry starts.
            continue
        errors.append(distance(receipt["position"], source["pose"]["position"]))
        ages.append(receipt.get("wall_ms", 0) - source["wall_ms"])
        if pose["entity"] in previous and source["local_tick"] < 600:
            jumps.append(distance(receipt["position"], previous[pose["entity"]]))
        previous[pose["entity"]] = receipt["position"]
    response = []
    for entry in (r for r in client if r["event"] == "input" and r["index"] <= 20):
        row = {"index": entry["index"], "move": entry["move"], "turn": entry["turn"]}
        kinds = [("apply", "physics_ms", False),
                 ("render", "rendered_frame_ms", False),
                 ("prediction", "predicted_physics_ms", True),
                 ("render", "predicted_frame_ms", True)]
        for kind, label, predicted in kinds:
            candidate = None
            for frame in client:
                if frame["event"] != kind or frame["time_ms"] < entry["time_ms"]:
                    continue
                if kind == "apply" and frame["entity"] != 2:
                    continue  # The fixed fixture's client owns entity2, never the host's pose.
                if frame["time_ms"] >= entry["time_ms"] + 500:
                    break
                if predicted:
                    if frame.get("input_tick", -1) < entry["input_tick_floor"]:
                        continue
                else:
                    sequence = (frame["pose"]["sequence"] if kind == "apply"
                                else frame["sequence"])
                    if sequence < entry["sequence_floor"]:
                        continue
                if entry["turn"]:
                    changed = angle(frame["yaw"], entry["yaw"]) > math.radians(0.2)
                elif kind in ["apply", "prediction"]:
                    velocity = frame["pose"]["velocity"] if kind == "apply" else frame["velocity"]
                    changed = abs(math.dist(velocity, [0, 0, 0]) -
                                  math.dist(entry["velocity"], [0, 0, 0])) > 0.05
                else:
                    changed = distance(frame["position"], entry["position"]) > 0.005
                if changed:
                    candidate = frame["time_ms"] - entry["time_ms"]
                    break
            row[label] = candidate
        response.append(row)
    wall = [r for r in simulation if r["pose"]["entity"] == 2 and
            705 <= r["local_tick"] <= 715]
    collision = bool(wall) and all(-17.85 <= r["pose"]["position"][2] <= -17.65 and
                                  abs(r["pose"]["position"][0]) < 0.01 for r in wall)
    stale = [r for r in simulation if r["decision_age_ms"] > 250]
    expiry_transitions = []
    last_active = {}
    previous_tick = {}
    for row in simulation:
        entity = row["pose"]["entity"]
        if row["held"] != {"throttle": 0.0, "steer": 0.0, "brake": 0.0, "handbrake": False}:
            last_active[entity] = row["receipt_ms"]
        elif entity in last_active and row["receipt_ms"] == last_active[entity]:
            expiry_transitions.append({"entity": entity,
                                       "age_ms": row["time_ms"] - row["receipt_ms"],
                                       "previous_age_ms": (previous_tick[entity]["time_ms"] -
                                                           row["receipt_ms"]),
                                       "decision_age_ms": row["decision_age_ms"],
                                       "previous_decision_age_ms":
                                           previous_tick[entity]["decision_age_ms"],
                                       "tick_gap_ms": row["time_ms"] - previous_tick[entity]["time_ms"],
                                       "velocity": row["pose"]["velocity"]})
            del last_active[entity]
        previous_tick[entity] = row
    expired = (bool(expiry_transitions) and all(r["held"] == {"throttle": 0.0, "steer": 0.0, "brake": 0.0, "handbrake": False} for r in stale) and
               all(r["previous_decision_age_ms"] <= 250 < r["decision_age_ms"]
                   for r in expiry_transitions))
    # Matching state of a settled authority, after the two isolated recovery segments.
    recovery = []
    for label, low, high in [("interruption", 790, 885), ("host_stall", 950, 999)]:
        settled = [r for r in simulation if r["pose"]["entity"] == 2 and
                   low <= r["local_tick"] <= high and
                   math.dist(r["pose"]["velocity"], [0, 0, 0]) < 0.001]
        if not settled:
            recovery.append({"case": label, "converged": False})
            continue
        source = settled[0]
        origin = next((r["wall_ms"] for r in proxy_events if r["event"] == "blackout_end"),
                      source["wall_ms"]) if label == "interruption" else next(
                          (r["wall_ms"] for r in host if r["event"] == "stall_end"), source["wall_ms"])
        matching = [r for r in applied if r["entity"] == 2 and
                    r.get("wall_ms", 0) >= origin and
                    distance(r["position"], source["pose"]["position"]) <= 0.01 and
                    angle(r["yaw"], source["pose"]["yaw"]) <= math.radians(0.1)]
        delay = matching[0]["wall_ms"] - origin if matching else None
        recovery.append({"case": label, "settled_tick": source["pose"]["tick"],
                         "observed_delay_ms": delay, "converged": delay is not None and delay <= 1000})
    final = {role: next((r for r in reversed(rows) if r["event"] == "result"), None)
             for role, rows in [("host", host), ("client", client)]}
    resync = next((r for r in client if r["event"] == "resync_applied"), None)
    corrections = [r for r in client if r["event"] == "correction"]
    correction_magnitudes = [r["magnitude_m"] for r in corrections]
    replay_per_tick = [r["cpu_per_tick_usec"] for r in corrections if r["replayed"] > 0]
    prediction_recovery = []
    for label, origin in [
            ("interruption", next((r["wall_ms"] for r in proxy_events
                                   if r["event"] == "blackout_end"), None)),
            ("host_stall", next((r["wall_ms"] for r in host
                                 if r["event"] == "stall_end"), None))]:
        if origin is None:
            prediction_recovery.append({"case": label, "observed_delay_ms": None,
                                        "converged": True})
            continue
        matching = next((r for r in corrections if r["wall_ms"] >= origin and
                         r["magnitude_m"] <= 0.01), None)
        delay = matching["wall_ms"] - origin if matching else None
        prediction_recovery.append({"case": label, "observed_delay_ms": delay,
                                    "converged": delay is not None and delay <= 1000})
    delays = [r["actual_delay_ms"] for r in proxy_events if r["event"] == "delivery"]
    response_keys = ["physics_ms", "rendered_frame_ms", "predicted_physics_ms",
                     "predicted_frame_ms"]
    return {"responses": response,
            "response_p95_ms": {key: percentile([r[key] for r in response if r[key] is not None])
                                for key in response_keys},
            "response_samples": len(response),
            "response_missing": sum(r["rendered_frame_ms"] is None for r in response),
            "physics_response_missing": sum(r["physics_ms"] is None for r in response),
            "predicted_response_missing": sum(r["predicted_physics_ms"] is None
                                              for r in response),
            "predicted_frame_missing": sum(r["predicted_frame_ms"] is None
                                           for r in response),
            "correction_samples": len(corrections),
            "correction_p95_m": percentile(correction_magnitudes),
            "correction_max_m": max(correction_magnitudes, default=0),
            "correction_target_m": 0.5,
            "replay_cpu_per_tick_usec": {"p95": percentile(replay_per_tick),
                                          "max": max(replay_per_tick, default=0)},
            "prediction_recovery": prediction_recovery,
            "snapshot_age_p95_ms": percentile(ages), "snapshot_age_max_ms": max(ages, default=0),
            "matching_tick_install_error_max_m": max(errors, default=0),
            "matching_tick_samples": len(errors), "update_jump_p95_m": percentile(jumps),
            "prediction_correction": "rewind and replay correction magnitude",
            "wall_stop": collision, "input_expiry": expired,
            "expiry_transitions": expiry_transitions, "recovery": recovery,
            "window_states": [r for r in host + client if r["event"] == "start"],
            "resync_retained_entity_health": bool(resync and resync["entity"] == 2 and
                                                   resync["health"] == 70 and resync["control"] == 2
                                                   and resync.get("seat") == {"player": 2, "vehicle": 1002, "seat": "driver", "equipment": {"selected": "pistol", "magazine": 7}}),
            "proxy_delays_ms": {"min": min(delays, default=0), "p95": percentile(delays),
                                "max": max(delays, default=0)},
            "native_drops": sum(r["event"] == "drop" for r in proxy_events), "results": final}


def stage(directory):
    """Copy only saved fixture dependencies into an addon-free fresh project."""
    project = directory / "project"
    for fixture in ["s02", "s03", "s04"]:
        shutil.copytree(ROOT / "tests/fixtures" / fixture, project / "tests/fixtures" / fixture,
                        ignore=shutil.ignore_patterns("editor_harness.tscn"))
    models = project / "art/models/spikes"
    models.mkdir(parents=True)
    for pattern in ["s02_*.*", "s04_*.*"]:
        for path in (ROOT / "art/models/spikes").glob(pattern):
            shutil.copy2(path, models / path.name)
    settings = (ROOT / "project.godot").read_text()
    for section in ["autoload", "editor_plugins"]:
        settings = re.sub(r"(?ms)^\[" + section + r"\]\n.*?(?=^\[|\Z)", "", settings)
    settings = settings.replace('config/icon="res://icon.svg"', '')
    settings = re.sub(r'(?m)^run/main_scene=.*\n', '', settings)
    settings += '\n'
    (project / "project.godot").write_text(settings)
    return project


def run_case(args, directory, profile):
    directory.mkdir()
    project = stage(directory)
    before = {str(p.relative_to(project)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in project.rglob("*") if p.is_file()}
    if not checked_command([args.godot, "--headless", "--editor", "--path", str(project),
                            "--import", "--quit"], directory / "import.log",
                           environment(directory / "import-user")):
        raise RuntimeError("isolated fixture import failed")
    logs = {}
    children = []
    offsets = {"host": 0, "client": 0}
    results = {}
    ready = False
    commands = {}
    proxy_log = (directory / "proxy.jsonl").open("w")
    proxy = CarProxy(args.port, args.proxy_port, profile, proxy_log)
    deadline = time.monotonic() + args.deadline
    try:
        def start(role, port):
            role_dir = directory / role
            role_dir.mkdir()
            capture_dir = role_dir / "captures"
            capture_dir.mkdir()
            env = environment(role_dir / "user")
            env["S04_CAPTURE_DIR"] = str(capture_dir)
            command = [args.godot, *([] if args.windowed else ["--headless"]),
                       "--path", str(project), "--resolution", "1280x800",
                       "--position", "0,0" if role == "host" else "1280,0",
                       "--log-file", str(role_dir / "engine.log"),
                       "res://tests/fixtures/s04/boot.tscn", "--",
                       "--role=" + role, "--port=" + str(port), "--profile=" + profile]
            commands[role] = command
            logs[role] = (role_dir / "stdout.log").open("w")
            child = subprocess.Popen(command, stdout=logs[role], stderr=subprocess.STDOUT, env=env)
            children.append(child)

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
                        if not line.startswith("S04 "):
                            continue
                        record = json.loads(line.removeprefix("S04 "))
                        if record["event"] == "ready" and role == "host":
                            ready = True
                        if record["event"] == "start" and role == "client":
                            proxy.start = time.monotonic()
                        if record["event"] == "result":
                            results[role] = record
                            if not record["ok"]:
                                raise RuntimeError(f"{role} outcome failures: {record['failures']}")
            if ready and "client" not in logs:
                start("client", args.proxy_port)
            if len(results) == 2 and all(c.poll() is not None for c in children):
                break
            for index, child in enumerate(children):
                role = "host" if index == 0 else "client"
                if child.poll() is not None and role not in results:
                    raise RuntimeError(f"{role} exited before result ({child.returncode})")
            time.sleep(POLL_SECONDS)
        else:
            raise RuntimeError("two-process wall-clock deadline")
        if any(c.returncode != 0 for c in children):
            raise RuntimeError("nonzero process exit")
        for role in logs:
            for name in ["stdout.log", "engine.log"]:
                if DIAGNOSTIC.search((directory / role / name).read_text(errors="replace")):
                    raise RuntimeError(f"engine/script diagnostics in {role}/{name}")
        measurements = analyze(directory, proxy.events)
        required = [measurements["wall_stop"], measurements["input_expiry"],
                    measurements["resync_retained_entity_health"],
                    measurements["matching_tick_samples"] > 100,
                    measurements["matching_tick_install_error_max_m"] < 0.00001,
                    measurements["response_samples"] == 20,
                    measurements["physics_response_missing"] == 0,
                    measurements["predicted_response_missing"] == 0,
                    measurements["correction_samples"] > 100,
                    measurements["correction_p95_m"] <= measurements["correction_target_m"],
                    all(r["converged"] for r in measurements["recovery"]),
                    all(r["converged"] for r in measurements["prediction_recovery"])]
        if profile == "adverse":
            required.append(proxy.blackout_done)
        unchanged = all(hashlib.sha256((project / path).read_bytes()).hexdigest() == digest
                        for path, digest in before.items())
        summary = {"ok": all(required) and unchanged, "profile": profile,
                   "measurements": measurements, "source_sha256": before,
                   "saved_source_unchanged": unchanged, "commands": commands,
                   "process_ids": [c.pid for c in children], "exits": [c.returncode for c in children],
                   "peak_proxy_queue": proxy.peak_queue, "ports": [args.port, args.proxy_port]}
        (directory / "result.json").write_text(json.dumps(summary, indent=2) + "\n")
        return summary
    finally:
        stop_children(children)
        for output in logs.values():
            output.close()
        proxy.socket.close()
        proxy_log.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot") or "godot")
    parser.add_argument("--port", type=int, default=24900)
    parser.add_argument("--proxy-port", type=int, default=24901)
    parser.add_argument("--deadline", type=float, default=45)
    parser.add_argument("--windowed", action="store_true",
                        help="attempt real graphical frame receipts; never substitute forced draws")
    parser.add_argument("--profiles", nargs="+", choices=PROFILES, default=list(PROFILES))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not (1 <= args.port <= 65535 and 1 <= args.proxy_port <= 65535 and
            args.port != args.proxy_port and 1 <= args.deadline <= 90):
        parser.error("distinct ports 1..65535 and deadline 1..90 seconds required")
    directory = (args.output or Path(tempfile.mkdtemp(prefix="s04-"))).resolve()
    if directory.is_relative_to(ROOT):
        parser.error("evidence output must be outside checkout")
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        parser.error("fresh empty evidence directory required")
    print("S04 evidence:", directory, flush=True)
    def interrupted(_signal, _frame):
        raise KeyboardInterrupt
    previous = signal.signal(signal.SIGTERM, interrupted)
    results = []
    try:
        version = engine_version(args.godot)
        for profile in args.profiles:
            result = run_case(args, directory / profile, profile)
            results.append(result)
            print(json.dumps({"profile": profile, "ok": result["ok"],
                              "measurements": result["measurements"]}), flush=True)
            if not result["ok"]:
                raise RuntimeError("independent outcome criteria failed; inspect result/logs")
        summary = {"ok": True, "engine": version, "platform": platform.platform(),
                   "profiles": results}
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        summary = {"ok": False, "failure": str(error), "profiles": results}
    except KeyboardInterrupt:
        summary = {"ok": False, "failure": "runner interrupted; owned children stopped",
                   "profiles": results}
    finally:
        signal.signal(signal.SIGTERM, previous)
    (directory / "result.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"ok": summary["ok"], "failure": summary.get("failure")}))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
