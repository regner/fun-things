#!/usr/bin/env python3
"""Bounded actual-foot-controller ENet experiment with retained native fault telemetry."""

import argparse
import ctypes
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
MAX_PENDING_INPUT_FRAMES = 3
POLL_SECONDS = 0.002
BLACKOUT_START_SECONDS = 12.15
BLACKOUT_SECONDS = 1.0
TIMER_PERIOD_MS = 1


def begin_timer_period(enabled):
    """Request Windows' 1 ms scheduler period for this proxy process when selected."""
    if not enabled or platform.system() != "Windows":
        return False
    result = ctypes.WinDLL("winmm").timeBeginPeriod(TIMER_PERIOD_MS)
    if result != 0:
        raise OSError(f"timeBeginPeriod({TIMER_PERIOD_MS}) failed: {result}")
    return True


def end_timer_period(active):
    """Balance a successful Windows timer-period request."""
    if active:
        ctypes.WinDLL("winmm").timeEndPeriod(TIMER_PERIOD_MS)


class FootProxy:
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
        self.last_poll_end = time.monotonic()
        self.blackout_open = False
        self.blackout_done = False

    def record(self, event, **values):
        record = {"event": event, "wall_ms": time.time() * 1000,
                  "monotonic": time.monotonic(), **values}
        self.events.append(record)
        self.log.write(json.dumps(record) + "\n")

    def poll(self):
        """Receive, schedule and forward bounded packets with actual boundary timestamps."""
        poll_started = time.monotonic()
        interrupted = False
        if self.profile == "adverse" and self.start is not None:
            age = poll_started - self.start
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
                received = time.monotonic()
                received_wall_ms = time.time() * 1000
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
            self.record("receive", id=self.serial, direction=direction, bytes=len(data),
                        receive_monotonic=received, receive_wall_ms=received_wall_ms,
                        poll_gap_ms=(received - self.last_poll_end) * 1000,
                        poll_active_ms=(received - poll_started) * 1000)
            rng = self.random[direction]
            lost = rng.random() < self.loss
            delay_ms = max(0, self.delay + rng.uniform(-self.jitter, self.jitter))
            if interrupted or lost:
                self.record("drop", id=self.serial, direction=direction, bytes=len(data),
                            reason="blackout" if interrupted else "random")
                continue
            if len(self.queue) >= MAX_QUEUE:
                raise RuntimeError("proxy queue limit exceeded")
            heapq.heappush(self.queue, (received + delay_ms / 1000, self.serial, received,
                                      received_wall_ms, data, destination, direction))
            self.peak_queue = max(self.peak_queue, len(self.queue))
        for _ in range(MAX_POLL):
            forward_started = time.monotonic()
            if not self.queue or self.queue[0][0] > forward_started:
                break
            due, serial, received, received_wall_ms, data, destination, direction = (
                heapq.heappop(self.queue))
            if interrupted:
                self.record("drop", id=serial, direction=direction, bytes=len(data),
                            reason="blackout_pending")
                continue
            self.socket.sendto(data, destination)
            forwarded = time.monotonic()
            forwarded_wall_ms = time.time() * 1000
            self.record("delivery", id=serial, direction=direction, bytes=len(data),
                        receive_monotonic=received, receive_wall_ms=received_wall_ms,
                        forward_started_monotonic=forward_started,
                        forward_monotonic=forwarded, forward_wall_ms=forwarded_wall_ms,
                        actual_delay_ms=(forwarded - received) * 1000,
                        scheduled_delay_ms=(due - received) * 1000,
                        schedule_overrun_ms=max(0, forward_started - due) * 1000,
                        send_call_ms=(forwarded - forward_started) * 1000)
        self.last_poll_end = time.monotonic()


def records(path):
    return [json.loads(line.removeprefix("S03R ")) for line in path.read_text().splitlines()
            if line.startswith("S03R ")]


def percentile(values, quantile=0.95):
    if not values:
        return None
    return sorted(values)[math.ceil(len(values) * quantile) - 1]


def distance(a, b):
    return math.dist(a, b)


def angle(a, b):
    return abs((a - b + math.pi) % (2 * math.pi) - math.pi)


def _row_sequence(row, entity=2):
    """Return an entity sequence from either one pose or a staged row list."""
    if "pose" in row and row["pose"].get("entity") == entity:
        return row["pose"]["sequence"]
    if row.get("entity") == entity:
        return row.get("sequence")
    if "sequence" in row and "rows" not in row:
        return row["sequence"]
    for item in row.get("rows", []):
        if item.get("entity") == entity:
            return item.get("sequence")
    return None


def _first_stage(rows, event, sequence, after_ms):
    """Find the first correlated stage at or after the preceding same-machine wall time."""
    return next((row for row in rows if row["event"] == event and
                 row.get("wall_ms", 0) >= after_ms and
                 (_row_sequence(row) or -1) >= sequence), None)


def latency_budget(host, client):
    """Correlate the first accepted sequence for each pulse across every instrumented stage."""
    host_receipts = {row["sequence"]: row for row in host if
                     row["event"] == "host_receive" and row["participant"] == 2}
    sends = [row for row in client if row["event"] == "input_send"]
    stage_rows = []
    for entry in (row for row in client if row["event"] == "input" and row["index"] <= 20):
        candidates = [row for row in sends if row["index"] == entry["index"] and
                      row["sequence"] >= entry["sequence_floor"] and
                      row["sequence"] in host_receipts]
        if not candidates:
            continue
        sent = candidates[0]
        received = host_receipts[sent["sequence"]]
        consumed = _first_stage(host, "simulation", sent["sequence"], received["wall_ms"])
        state_sent = (_first_stage(host, "state_send", sent["sequence"], consumed["wall_ms"])
                      if consumed else None)
        state_received = (_first_stage(client, "state_receive", sent["sequence"],
                                       state_sent["send_wall_ms"]) if state_sent else None)
        applied = (_first_stage(client, "apply", sent["sequence"], state_received["wall_ms"])
                   if state_received else None)
        drawn = (_first_stage(client, "render", sent["sequence"], applied["wall_ms"])
                 if applied else None)
        required = [sent, received, consumed, state_sent, state_received, applied]
        if any(row is None for row in required):
            continue
        times = [sent["sample_wall_ms"], sent["send_wall_ms"], received["wall_ms"],
                 consumed["wall_ms"], state_sent["send_wall_ms"], state_received["wall_ms"],
                 applied["wall_ms"]]
        labels = ["sample_to_send_ms", "send_to_host_receive_ms", "receive_to_consume_ms",
                  "consume_to_state_send_ms", "state_send_to_receive_ms",
                  "state_receive_to_apply_ms"]
        row = {"index": entry["index"], "sequence": sent["sequence"],
               **{label: times[index + 1] - times[index]
                  for index, label in enumerate(labels)},
               "sample_to_apply_ms": times[-1] - times[0],
               "apply_to_draw_ms": None,
               "sample_to_draw_ms": None}
        if drawn is not None:
            row["apply_to_draw_ms"] = drawn["wall_ms"] - times[-1]
            row["sample_to_draw_ms"] = drawn["wall_ms"] - times[0]
        stage_rows.append(row)
    labels = ["sample_to_send_ms", "send_to_host_receive_ms", "receive_to_consume_ms",
              "consume_to_state_send_ms", "state_send_to_receive_ms",
              "state_receive_to_apply_ms", "sample_to_apply_ms", "apply_to_draw_ms",
              "sample_to_draw_ms"]
    summary = {}
    for label in labels:
        values = [row[label] for row in stage_rows if row[label] is not None]
        summary[label] = {"samples": len(values), "p50": percentile(values, 0.5),
                          "p95": percentile(values), "max": max(values, default=None)}
    return {"samples": len(stage_rows), "stages_ms": summary, "rows": stage_rows}


def proxy_latency_budget(proxy_events):
    """Summarize measured proxy polling, queue dwell and socket-forward boundaries."""
    receives = [row for row in proxy_events if row["event"] == "receive"]
    deliveries = [row for row in proxy_events if row["event"] == "delivery"]
    fields = {"poll_gap_ms": receives,
              "receive_to_forward_ms": deliveries,
              "schedule_overrun_ms": deliveries,
              "send_call_ms": deliveries}
    sources = {"poll_gap_ms": "poll_gap_ms",
               "receive_to_forward_ms": "actual_delay_ms",
               "schedule_overrun_ms": "schedule_overrun_ms",
               "send_call_ms": "send_call_ms"}
    summary = {}
    for label, rows in fields.items():
        values = [row[sources[label]] for row in rows]
        summary[label] = {"samples": len(values), "p50": percentile(values, 0.5),
                          "p95": percentile(values), "max": max(values, default=None)}
    summary["directions"] = {}
    for direction in ["up", "down"]:
        values = [row["actual_delay_ms"] for row in deliveries if
                  row["direction"] == direction]
        summary["directions"][direction] = {
            "samples": len(values), "p95_receive_to_forward_ms": percentile(values)}
    return summary


def analyze(directory, proxy_events):
    """Compare outcome telemetry independently; targets may fail while an experiment succeeds."""
    host = records(directory / "host/stdout.log")
    client = records(directory / "client/stdout.log")
    simulation = [r for r in host if r["event"] == "simulation"]
    applied = [r for r in client if r["event"] == "apply"]
    poses = {(r["pose"]["entity"], r["pose"]["tick"]): r for r in simulation}
    errors = []
    local_restore_errors = []
    ages = []
    jumps = []
    previous = {}
    for receipt in applied:
        pose = receipt["pose"]
        source = poses.get((pose["entity"], pose["tick"]))
        if source is None:  # Initial grant before experiment telemetry starts.
            continue
        errors.append(distance(pose["position"], source["pose"]["position"]))
        local_restore_errors.append(receipt["authority_install_error_m"])
        ages.append(receipt.get("wall_ms", 0) - source["wall_ms"])
        if pose["entity"] in previous and source["local_tick"] < 600:
            jumps.append(distance(receipt["position"], previous[pose["entity"]]))
        previous[pose["entity"]] = receipt["position"]
    response = []
    for entry in (r for r in client if r["event"] == "input" and r["index"] <= 20):
        row = {"index": entry["index"], "move": entry["move"],
               "aim_yaw": entry["aim_yaw"]}
        kinds = [("apply", "physics_ms"), ("render", "rendered_frame_ms"),
                 ("prediction", "predicted_physics_ms"),
                 ("render", "predicted_drawn_ms")]
        for kind, label in kinds:
            candidate = None
            for frame in client:
                if frame["event"] != kind or frame["time_ms"] < entry["time_ms"]:
                    continue
                if kind == "apply" and frame["entity"] != 2:
                    continue  # The fixed fixture's client owns entity2, never the host's pose.
                if frame["time_ms"] >= entry["time_ms"] + 500:
                    break
                predicted = label.startswith("predicted_")
                if predicted:
                    if frame.get("predicted_tick", -1) < entry["tick"]:
                        continue
                    position = frame["position"]
                    yaw = frame["yaw"]
                else:
                    sequence = (frame["pose"]["sequence"] if kind == "apply"
                                else frame["sequence"])
                    if sequence < entry["sequence_floor"]:
                        continue
                    position = (frame["pose"]["position"] if kind == "apply"
                                else frame["position"])
                    yaw = frame["pose"]["yaw"] if kind == "apply" else frame["yaw"]
                changed = (distance(position, entry["position"]) > 0.005 or
                           angle(yaw, entry["yaw"]) > math.radians(0.2))
                if changed:
                    candidate = frame["time_ms"] - entry["time_ms"]
                    break
            row[label] = candidate
        response.append(row)
    wall = [r for r in simulation if r["pose"]["entity"] == 2 and
            705 <= r["local_tick"] <= 715]
    collision = bool(wall) and all(0.37 <= r["pose"]["position"][2] <= 0.41 and
                                  abs(r["pose"]["position"][0] - 6) < 0.01 for r in wall)
    stale = [r for r in simulation if r["pose"]["entity"] == 2 and
             1002 <= r["local_tick"] < 1040 and r["decision_age_ms"] > 267]
    expiry_transitions = []
    last_active = {}
    previous_tick = {}
    for row in simulation:
        entity = row["pose"]["entity"]
        if row["held"] != [0, 0]:
            last_active[entity] = row["receipt_ms"]
        elif entity in last_active and row["receipt_ms"] == last_active[entity]:
            if entity == 2 and 990 <= row["local_tick"] <= 1070:
                expiry_transitions.append({"entity": entity, "local_tick": row["local_tick"],
                                           "age_ms": row["held_age_ms"],
                                           "previous_age_ms": previous_tick[entity]["held_age_ms"],
                                           "tick_gap_ms": row["time_ms"] - previous_tick[entity]["time_ms"],
                                           "velocity": row["pose"]["velocity"]})
            del last_active[entity]
        previous_tick[entity] = row
    expired = (bool(expiry_transitions) and all(r["held"] == [0, 0] for r in stale) and
               all(0 <= r["age_ms"] <= 267 and r["velocity"] == [0, 0, 0]
                   for r in expiry_transitions))
    # Matching state of a settled authority, after the two isolated recovery segments.
    recovery = []
    for label, low, high in [("interruption", 805, 840), ("host_stall", 960, 995)]:
        settled = [r for r in simulation if r["pose"]["entity"] == 2 and
                   low <= r["local_tick"] <= high]
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
    delays = [r["actual_delay_ms"] for r in proxy_events if r["event"] == "delivery"]
    corrections = [r for r in client if r["event"] == "correction"]
    correction_magnitudes = [r["correction_m"] for r in corrections]
    replay_per_tick = [r["replay_usec"] / max(1, r["replay_frames"]) for r in corrections]
    causes = {}
    for correction in corrections:
        causes[correction["cause"]] = causes.get(correction["cause"], 0) + 1
    response_keys = ["physics_ms", "rendered_frame_ms", "predicted_physics_ms",
                     "predicted_drawn_ms"]
    return {"responses": response,
            "response_p95_ms": {key: percentile([r[key] for r in response if r[key] is not None])
                                for key in response_keys},
            "response_samples": len(response),
            "response_missing": sum(r["rendered_frame_ms"] is None for r in response),
            "predicted_response_missing": sum(r["predicted_drawn_ms"] is None for r in response),
            "snapshot_age_p95_ms": percentile(ages), "snapshot_age_max_ms": max(ages, default=0),
            "matching_tick_install_error_max_m": max(errors, default=0),
            "local_restore_error_max_m": max(local_restore_errors, default=0),
            "matching_tick_samples": len(errors), "update_jump_p95_m": percentile(jumps),
            "prediction_correction_p50_m": percentile(correction_magnitudes, 0.50),
            "prediction_correction_p95_m": percentile(correction_magnitudes),
            "prediction_correction_max_m": max(correction_magnitudes, default=0),
            "correction_samples": len(corrections),
            "replay_cpu_usec_per_tick_p95": percentile(replay_per_tick),
            "replay_frames_max": max((r["replay_frames"] for r in corrections), default=0),
            "history_exhaustions": sum(r["history_exhausted"] for r in corrections),
            "pending_input_frames_max": max(
                (r.get("pending_input_frames", 0) for r in simulation), default=0),
            "superseded_input_frames": max(
                (r.get("superseded_input_frames", 0) for r in simulation), default=0),
            "misprediction_causes": causes,
            "wall_stop": collision, "input_expiry": expired,
            "expiry_transitions": expiry_transitions, "recovery": recovery,
            "window_states": [r for r in host + client if r["event"] == "start"],
            "resync_retained_entity_health": bool(resync and resync["entity"] == 2 and
                                                   resync["health"] == 70 and resync["control"] == 2),
            "proxy_delays_ms": {"min": min(delays, default=0), "p95": percentile(delays),
                                "max": max(delays, default=0)},
            "proxy_stage_ms": proxy_latency_budget(proxy_events),
            "latency_budget": latency_budget(host, client),
            "native_drops": sum(r["event"] == "drop" for r in proxy_events), "results": final}


def matching_tick_valid(measurements):
    """Accept only source-bound receipt poses, never the local restore diagnostic alone."""
    return (measurements["matching_tick_samples"] > 100
            and measurements["matching_tick_install_error_max_m"] < 0.00001)


def visible_response_valid(measurements, windowed):
    """Require actual drawable states and complete drawn response evidence when requested."""
    if not windowed:
        return True
    states = measurements["window_states"]
    return (len(states) == 2 and {state["role"] for state in states} == {"host", "client"}
            and all(state.get("can_draw") and state.get("window_visible")
                    and state.get("display") != "headless" for state in states)
            and measurements["response_missing"] == 0
            and measurements["predicted_response_missing"] == 0
            and measurements["response_p95_ms"]["rendered_frame_ms"] is not None
            and measurements["response_p95_ms"]["predicted_drawn_ms"] is not None
            and measurements["response_p95_ms"]["predicted_drawn_ms"] <= 50)


def stage(directory):
    """Copy only saved fixture dependencies into an addon-free fresh project."""
    project = directory / "project"
    for fixture in ["s02", "s03", "s03_r"]:
        shutil.copytree(ROOT / "tests/fixtures" / fixture, project / "tests/fixtures" / fixture)
    models = project / "art/models/spikes"
    models.mkdir(parents=True)
    for path in (ROOT / "art/models/spikes").glob("s02_*.*"):
        shutil.copy2(path, models / path.name)
    settings = (ROOT / "project.godot").read_text()
    for section in ["autoload", "editor_plugins"]:
        settings = re.sub(r"(?ms)^\[" + section + r"\]\n.*?(?=^\[|\Z)", "", settings)
    settings = settings.replace('config/icon="res://icon.svg"', '')
    settings = re.sub(r'(?m)^run/main_scene=.*$',
                      'run/main_scene="res://tests/fixtures/s03_r/boot.tscn"', settings)
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
    proxy = None if args.bypass_proxy else FootProxy(
        args.port, args.proxy_port, profile, proxy_log)
    proxy_log.write(json.dumps({"event": "configuration", "wall_ms": time.time() * 1000,
                                "proxy_mode": "bypassed" if proxy is None else "proxied",
                                "high_resolution_timer": args.high_resolution_timer}) + "\n")
    deadline = time.monotonic() + args.deadline
    try:
        def start(role, port):
            role_dir = directory / role
            role_dir.mkdir()
            capture_dir = role_dir / "captures"
            capture_dir.mkdir()
            env = environment(role_dir / "user")
            env["S03R_CAPTURE_DIR"] = str(capture_dir)
            command = [args.godot, *([] if args.windowed else ["--headless"]),
                       *(["--disable-vsync"] if args.disable_vsync else []),
                       "--path", str(project), "--resolution", "1280x800",
                       "--position", "0,0" if role == "host" else "1280,0",
                       "--log-file", str(role_dir / "engine.log"),
                       "res://tests/fixtures/s03_r/boot.tscn", "--",
                       "--role=" + role, "--port=" + str(port), "--profile=" + profile,
                       "--max-fps=" + str(args.max_fps),
                       *(["--low-processor-mode"] if args.low_processor_mode else [])]
            commands[role] = command
            logs[role] = (role_dir / "stdout.log").open("w")
            child = subprocess.Popen(command, stdout=logs[role], stderr=subprocess.STDOUT, env=env)
            children.append(child)

        start("host", args.port)
        while time.monotonic() < deadline:
            if proxy is not None:
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
                        if not line.startswith("S03R "):
                            continue
                        record = json.loads(line.removeprefix("S03R "))
                        if record["event"] == "ready" and role == "host":
                            ready = True
                        if record["event"] == "start" and role == "client" and proxy is not None:
                            proxy.start = time.monotonic()
                        if record["event"] == "result":
                            results[role] = record
                            if not record["ok"]:
                                raise RuntimeError(f"{role} outcome failures: {record['failures']}")
            if ready and "client" not in logs:
                start("client", args.port if proxy is None else args.proxy_port)
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
        measurements = analyze(directory, [] if proxy is None else proxy.events)
        required = [measurements["wall_stop"], measurements["input_expiry"],
                    measurements["resync_retained_entity_health"],
                    matching_tick_valid(measurements),
                    measurements["response_samples"] == 20,
                    all(r["physics_ms"] is not None for r in measurements["responses"]),
                    all(r["predicted_physics_ms"] is not None
                        for r in measurements["responses"]),
                    measurements["response_p95_ms"]["predicted_physics_ms"] <= 50,
                    measurements["correction_samples"] > 100,
                    measurements["prediction_correction_p95_m"] <= 0.5,
                    measurements["history_exhaustions"] == 0,
                    measurements["pending_input_frames_max"] <= MAX_PENDING_INPUT_FRAMES,
                    all(r["converged"] for r in measurements["recovery"]),
                    visible_response_valid(measurements, args.windowed)]
        if profile == "adverse":
            required.append(proxy is not None and proxy.blackout_done)
        unchanged = all(hashlib.sha256((project / path).read_bytes()).hexdigest() == digest
                        for path, digest in before.items())
        summary = {"ok": all(required) and unchanged, "profile": profile,
                   "measurements": measurements, "source_sha256": before,
                   "saved_source_unchanged": unchanged, "commands": commands,
                   "process_ids": [c.pid for c in children], "exits": [c.returncode for c in children],
                   "peak_proxy_queue": 0 if proxy is None else proxy.peak_queue,
                   "proxy_mode": "bypassed" if proxy is None else "proxied",
                   "pacing": {"max_fps": args.max_fps,
                              "low_processor_mode": args.low_processor_mode,
                              "disable_vsync": args.disable_vsync,
                              "high_resolution_timer": args.high_resolution_timer},
                   "ports": [args.port, args.proxy_port]}
        (directory / "result.json").write_text(json.dumps(summary, indent=2) + "\n")
        return summary
    finally:
        stop_children(children)
        for output in logs.values():
            output.close()
        if proxy is not None:
            proxy.socket.close()
        proxy_log.close()


def validate_arguments(args):
    """Reject invalid ranges and unsafe uncapped windowed rendering before any engine launch."""
    if not (1 <= args.port <= 65535 and 1 <= args.proxy_port <= 65535 and
            args.port != args.proxy_port and 1 <= args.deadline <= 90 and
            0 <= args.max_fps <= 1000):
        raise ValueError("distinct ports 1..65535, deadline 1..90, and max-fps 0..1000 required")
    if args.bypass_proxy and args.profiles != ["baseline"]:
        raise ValueError("proxy bypass is a baseline-only diagnosis")
    if args.windowed and args.max_fps != 60:
        raise ValueError("safe windowed diagnosis requires --max-fps 60")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot") or "godot")
    parser.add_argument("--port", type=int, default=24900)
    parser.add_argument("--proxy-port", type=int, default=24901)
    parser.add_argument("--deadline", type=float, default=45)
    parser.add_argument("--windowed", action="store_true",
                        help="attempt real graphical receipts; requires --max-fps 60")
    parser.add_argument("--bypass-proxy", action="store_true",
                        help="connect baseline client directly to the host's loopback port")
    parser.add_argument("--high-resolution-timer", action="store_true",
                        help="request a balanced Windows timeBeginPeriod(1) for proxy pacing")
    parser.add_argument("--max-fps", type=int, default=0,
                        help="set Engine.max_fps in both fixture processes (0 is uncapped)")
    parser.add_argument("--low-processor-mode", action="store_true",
                        help="enable OS.low_processor_usage_mode in both fixture processes")
    parser.add_argument("--disable-vsync", action="store_true",
                        help="pass Godot's --disable-vsync to both fixture processes")
    parser.add_argument("--profiles", nargs="+", choices=PROFILES, default=list(PROFILES))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        validate_arguments(args)
    except ValueError as error:
        parser.error(str(error))
    directory = (args.output or Path(tempfile.mkdtemp(prefix="s03-r-"))).resolve()
    if directory.is_relative_to(ROOT):
        parser.error("evidence output must be outside checkout")
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        parser.error("fresh empty evidence directory required")
    print("S03-R evidence:", directory, flush=True)
    def interrupted(_signal, _frame):
        raise KeyboardInterrupt
    previous = signal.signal(signal.SIGTERM, interrupted)
    results = []
    timer_period_active = False
    try:
        version = engine_version(args.godot)
        timer_period_active = begin_timer_period(args.high_resolution_timer)
        for profile in args.profiles:
            result = run_case(args, directory / profile, profile)
            results.append(result)
            print(json.dumps({"profile": profile, "ok": result["ok"],
                              "measurements": result["measurements"]}), flush=True)
            if not result["ok"]:
                raise RuntimeError("independent outcome criteria failed; inspect result/logs")
        summary = {"ok": True, "engine": version, "platform": platform.platform(),
                   "timer_period_active": timer_period_active, "profiles": results}
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        summary = {"ok": False, "failure": str(error), "profiles": results}
    except KeyboardInterrupt:
        summary = {"ok": False, "failure": "runner interrupted; owned children stopped",
                   "profiles": results}
    finally:
        end_timer_period(timer_period_active)
        signal.signal(signal.SIGTERM, previous)
    (directory / "result.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"ok": summary["ok"], "failure": summary.get("failure")}))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
