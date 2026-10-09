#!/usr/bin/env python3
"""Measure full-cap packed population replication through bounded ENet fault proxies."""

import argparse
import hashlib
import heapq
import json
import math
import os
from pathlib import Path
import platform
import random
import shutil
import signal
import socket
import subprocess
import tempfile
import time

from run_s03 import stop_children
from script_checks import ROOT, DIAGNOSTIC, checked_command, engine_version, environment

PROFILES = {"normal": (75, 30, 0.02), "adverse": (125, 50, 0.05)}
BUDGETS_KIB_S = {"host_out": 256, "host_in": 128, "client_in": 96, "client_out": 48}
MAX_QUEUE = 1024
MAX_POLL = 128
POLL_SECONDS = 0.002
WIRE_OVERHEAD_BYTES = 28
BLACKOUT_START_SECONDS = 4.0
BLACKOUT_SECONDS = 1.0
MIN_HOST_STALL_MS = 245
MEASUREMENT_SOURCES = ["tools/run_s11.py", "tools/run_s03.py", "tools/script_checks.py"]


class PopulationProxy:
    """Route one client with independent bounded delay, jitter, loss and wire accounting."""

    def __init__(self, host_port, proxy_port, profile, seed, log):
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
        self.random = {"up": random.Random(seed), "down": random.Random(seed + 10_000)}
        self.queue = []
        self.serial = 0
        self.peak_queue = 0
        self.measurement_start = None
        self.events = []
        self.log = log
        self.blackout_begin = False
        self.blackout_end = False

    def record(self, event, **values):
        """Retain one proxy event and flush it for failure diagnosis."""
        record = {"event": event, "monotonic": time.monotonic(), **values}
        self.events.append(record)
        self.log.write(json.dumps(record) + "\n")
        self.log.flush()

    def poll(self):
        """Receive and deliver bounded datagram batches without blocking the runner."""
        now = time.monotonic()
        interrupted = False
        if self.profile == "adverse" and self.measurement_start is not None:
            age = now - self.measurement_start
            interrupted = BLACKOUT_START_SECONDS <= age < BLACKOUT_START_SECONDS + BLACKOUT_SECONDS
            if interrupted and not self.blackout_begin:
                self.blackout_begin = True
                self.record("blackout_begin")
            if age >= BLACKOUT_START_SECONDS + BLACKOUT_SECONDS and not self.blackout_end:
                self.blackout_end = True
                self.record("blackout_end")

        for _ in range(MAX_POLL):
            try:
                data, source = self.socket.recvfrom(65535)
            except BlockingIOError:
                break
            except ConnectionResetError:
                continue
            direction = "down" if source == self.host else "up"
            if direction == "up":
                if self.client is not None and source != self.client:
                    raise RuntimeError("unexpected second client on one proxy route")
                self.client = source
            destination = self.client if direction == "down" else self.host
            if destination is None:
                raise RuntimeError("host datagram arrived before proxy learned client route")

            self.serial += 1
            wire_bytes = len(data) + WIRE_OVERHEAD_BYTES
            self.record("ingress", id=self.serial, direction=direction,
                        payload_bytes=len(data), wire_bytes=wire_bytes)
            rng = self.random[direction]
            random_drop = rng.random() < self.loss
            if interrupted or random_drop:
                self.record("drop", id=self.serial, direction=direction,
                            reason="blackout" if interrupted else "random")
                continue

            delay_ms = max(0.0, self.delay_ms + rng.uniform(-self.jitter_ms, self.jitter_ms))
            if len(self.queue) >= MAX_QUEUE:
                raise RuntimeError("proxy queue limit exceeded")
            heapq.heappush(self.queue, (now + delay_ms / 1000.0, self.serial, now,
                                      data, destination, direction))
            self.peak_queue = max(self.peak_queue, len(self.queue))

        for _ in range(MAX_POLL):
            if not self.queue or self.queue[0][0] > now:
                break
            due, serial, received, data, destination, direction = heapq.heappop(self.queue)
            if interrupted:
                self.record("drop", id=serial, direction=direction, reason="blackout_pending")
                continue
            self.socket.sendto(data, destination)
            self.record("delivery", id=serial, direction=direction,
                        actual_delay_ms=(now - received) * 1000.0,
                        scheduled_delay_ms=(due - received) * 1000.0)


def percentile(values, quantile=0.95):
    """Return a nearest-rank percentile, or zero when no sample exists."""
    if not values:
        return 0
    return sorted(values)[math.ceil(len(values) * quantile) - 1]


def worst_window_bytes(events, direction, seconds=10.0):
    """Compute the largest ingress-byte total in any fixed-duration sliding window."""
    rows = [(event["monotonic"], event["wire_bytes"]) for event in events
            if event["event"] == "ingress" and event["direction"] == direction]
    left = 0
    total = 0
    worst = 0
    for right, (timestamp, size) in enumerate(rows):
        total += size
        while left <= right and timestamp - rows[left][0] > seconds:
            total -= rows[left][1]
            left += 1
        worst = max(worst, total)
    return worst


def delivered_profile(events):
    """Summarize actual impairment outcomes per direction from retained proxy events."""
    directions = {}
    for direction in ["up", "down"]:
        ingress = [event for event in events
                   if event["event"] == "ingress" and event["direction"] == direction]
        deliveries = [event for event in events
                      if event["event"] == "delivery" and event["direction"] == direction]
        random_drops = [event for event in events
                        if event["event"] == "drop" and event["direction"] == direction
                        and event["reason"] == "random"]
        blackout_drops = [event for event in events
                          if event["event"] == "drop" and event["direction"] == direction
                          and event["reason"].startswith("blackout")]
        delays = [event["actual_delay_ms"] for event in deliveries]
        median_delay = percentile(delays, 0.5)
        delay_variation = [abs(delay - median_delay) for delay in delays]
        directions[direction] = {
            "ingress_datagrams": len(ingress),
            "random_drop_datagrams": len(random_drops),
            "random_drop_percent": len(random_drops) / len(ingress) * 100.0 if ingress else 0.0,
            "blackout_drop_datagrams": len(blackout_drops),
            "delivered_datagrams": len(deliveries),
            "actual_delay_ms": {
                "min": min(delays, default=0),
                "median": median_delay,
                "p95": percentile(delays),
                "max": max(delays, default=0),
            },
            "actual_delay_variation_ms": {
                "median_absolute_deviation": percentile(delay_variation, 0.5),
                "p95_absolute_deviation": percentile(delay_variation),
                "max_absolute_deviation": max(delay_variation, default=0),
            },
        }
    blackout_begin = next((event["monotonic"] for event in events
                            if event["event"] == "blackout_begin"), None)
    blackout_end = next((event["monotonic"] for event in events
                          if event["event"] == "blackout_end"), None)
    return {
        "directions": directions,
        "interruption": {
            "observed": blackout_begin is not None and blackout_end is not None,
            "duration_ms": ((blackout_end - blackout_begin) * 1000.0
                            if blackout_begin is not None and blackout_end is not None else 0),
        },
    }


def summarize_delivered_profiles(routes):
    """Retain both aggregate and per-client-route delivered profile characteristics."""
    aggregate_events = [event for route in routes for event in route.events]
    aggregate_events.sort(key=lambda event: event["monotonic"])
    return {
        "route": "IPv4 UDP loopback through one independent proxy socket per client",
        "aggregate": delivered_profile(aggregate_events),
        "clients": [{"client": index + 1, **delivered_profile(route.events)}
                    for index, route in enumerate(routes)],
    }


def process_environment():
    """Record concurrent Godot count and an OS CPU-load observation for timing context."""
    godot_count = None
    cpu_percent = None
    if platform.system() == "Windows":
        tasklist = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=10,
                                  check=False)
        if tasklist.returncode == 0:
            godot_count = sum("godot" in line.lower() for line in tasklist.stdout.splitlines())
        command = ["powershell", "-NoProfile", "-Command",
                   "(Get-CimInstance Win32_Processor | "
                   "Measure-Object -Property LoadPercentage -Average).Average"]
        load = subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)
        if load.returncode == 0:
            try:
                cpu_percent = float(load.stdout.strip())
            except ValueError:
                pass
    else:
        probe = subprocess.run(["pgrep", "-ci", "godot"], capture_output=True, text=True,
                               timeout=5, check=False)
        try:
            godot_count = int(probe.stdout.strip() or "0")
        except ValueError:
            pass
        try:
            cpu_percent = min(100.0, os.getloadavg()[0] / (os.cpu_count() or 1) * 100.0)
        except (AttributeError, OSError):
            pass
    return {"godot_processes": godot_count, "cpu_load_percent": cpu_percent}


def records(path):
    """Read complete S11 JSON records from one process log."""
    return [json.loads(line.removeprefix("S11 ")) for line in path.read_text().splitlines()
            if line.startswith("S11 ")]


def stage(output):
    """Copy only S03's unchanged transport/session fixture and the S11 fixture."""
    project = output / "project"
    for fixture in ["s03", "s11"]:
        shutil.copytree(ROOT / "tests/fixtures" / fixture,
                        project / "tests/fixtures" / fixture)
    (project / "project.godot").write_text(
        'config_version=5\n[application]\nconfig/name="S11 population replication"\n'
        'run/main_scene="res://tests/fixtures/s11/boot.tscn"\n'
        '[physics]\ncommon/physics_ticks_per_second=60\n'
        '[rendering]\nrenderer/rendering_method="gl_compatibility"\n'
    )
    return project


def source_fingerprints(project):
    """Bind every staged S03/S11 fixture source to the result."""
    return {path.relative_to(project).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for fixture in ["s03", "s11"]
            for path in sorted((project / "tests/fixtures" / fixture).iterdir()) if path.is_file()}


def repository_identity():
    """Bind the result to the exact committed repository revision and tree under test."""
    def git(*arguments):
        result = subprocess.run(["git", *arguments], cwd=ROOT, capture_output=True, text=True,
                                timeout=10, check=True)
        return result.stdout.strip()

    return {
        "commit": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "status_porcelain": git("status", "--porcelain").splitlines(),
    }


def measurement_source_fingerprints():
    """Hash runner and imported helpers that own impairment, accounting and cleanup."""
    return {path: {
        "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
        "bytes": (ROOT / path).stat().st_size,
    } for path in MEASUREMENT_SOURCES}


def summarize_network(routes, measurement_start, join_bytes):
    """Compare actual endpoint datagrams, including IP/UDP overhead, with all four budgets."""
    aggregate_events = [event for route in routes for event in route.events]
    aggregate_events.sort(key=lambda event: event["monotonic"])
    host_out = worst_window_bytes(aggregate_events, "down")
    host_in = worst_window_bytes(aggregate_events, "up")
    clients = []
    for index, route in enumerate(routes):
        client_in = worst_window_bytes(route.events, "down")
        client_out = worst_window_bytes(route.events, "up")
        clients.append({
            "client": index + 1,
            "in_worst_10s_bytes": client_in,
            "out_worst_10s_bytes": client_out,
            "in_kib_s": client_in / 10.0 / 1024.0,
            "out_kib_s": client_out / 10.0 / 1024.0,
            "join_wire_bytes": join_bytes[index],
        })
    rates = {
        "host_out": host_out / 10.0 / 1024.0,
        "host_in": host_in / 10.0 / 1024.0,
        "client_in": max((row["in_kib_s"] for row in clients), default=0),
        "client_out": max((row["out_kib_s"] for row in clients), default=0),
    }
    return {
        "accounting": "endpoint datagram bytes plus 20-byte IPv4 and 8-byte UDP headers",
        "measurement_start": measurement_start,
        "host_out_worst_10s_bytes": host_out,
        "host_in_worst_10s_bytes": host_in,
        "rates_kib_s": rates,
        "budgets_kib_s": BUDGETS_KIB_S,
        "budget_pass": {key: rates[key] <= BUDGETS_KIB_S[key] for key in rates},
        "join_baseline_pass": all(value <= 1024 * 1024 for value in join_bytes),
        "clients": clients,
    }


def run_case(args, project, case_dir, profile, repetition):
    """Run one host and the requested clients through independent profile proxies."""
    case_dir.mkdir(parents=True)
    logs = {}
    offsets = {}
    children = []
    results = {}
    commands = {}
    proxy_logs = []
    routes = []
    host_port = args.port
    proxy_ports = [args.proxy_port + index for index in range(args.clients)]
    for index, proxy_port in enumerate(proxy_ports):
        log = (case_dir / f"proxy-{index + 1}.jsonl").open("w")
        proxy_logs.append(log)
        routes.append(PopulationProxy(host_port, proxy_port, profile,
                                      1103 + repetition * 100 + index, log))

    environment_before = process_environment()
    deadline = time.monotonic() + args.deadline
    ready = False
    started = False
    measurement_start = None
    join_bytes = [0] * args.clients
    environment_measurement = None
    host_stall_records = []

    def start(role_name, role, connect_port):
        role_dir = case_dir / role_name
        role_dir.mkdir()
        command = [args.godot, "--headless", "--max-fps", "60", "--path", str(project),
                   "--log-file", str(role_dir / "engine.log"),
                   "res://tests/fixtures/s11/boot.tscn", "--", f"--role={role}",
                   f"--port={connect_port}", f"--clients={args.clients}",
                   f"--profile={profile}"]
        commands[role_name] = command
        logs[role_name] = (role_dir / "stdout.log").open("w")
        offsets[role_name] = 0
        child = subprocess.Popen(command, stdout=logs[role_name], stderr=subprocess.STDOUT,
                                 env=environment(role_dir / "user"))
        children.append(child)

    try:
        start("host", "host", host_port)
        while time.monotonic() < deadline:
            for route in routes:
                route.poll()
            for role_name in list(logs):
                path = case_dir / role_name / "stdout.log"
                with path.open() as output:
                    output.seek(offsets[role_name])
                    while True:
                        position = output.tell()
                        line = output.readline()
                        if not line.endswith("\n"):
                            offsets[role_name] = position
                            break
                        offsets[role_name] = output.tell()
                        if not line.startswith("S11 "):
                            continue
                        record = json.loads(line.removeprefix("S11 "))
                        if role_name == "host" and record["event"] == "ready":
                            ready = True
                        elif role_name == "host" and record["event"].startswith("host_stall_"):
                            host_stall_records.append(record)
                        elif role_name == "host" and record["event"] == "snapshots_started":
                            started = True
                            measurement_start = time.monotonic()
                            join_bytes = [sum(event["wire_bytes"] for event in route.events
                                              if event["event"] == "ingress" and
                                              event["direction"] == "down")
                                          for route in routes]
                            for route in routes:
                                route.measurement_start = measurement_start
                            environment_measurement = process_environment()
                        elif record["event"] == "result":
                            results[role_name] = record
                            if not record.get("ok"):
                                raise RuntimeError(f"{role_name} outcome failure: "
                                                   f"{record.get('failures')}")
            if ready and len(logs) == 1:
                for index, proxy_port in enumerate(proxy_ports):
                    start(f"client{index + 1}", "client", proxy_port)
            if len(results) == args.clients + 1 and all(child.poll() is not None
                                                        for child in children):
                break
            for role_name, child in zip(commands, children):
                if child.poll() is not None and role_name not in results:
                    raise RuntimeError(f"{role_name} exited before result ({child.returncode})")
            time.sleep(POLL_SECONDS)
        else:
            raise RuntimeError("S11 case wall-clock deadline")

        if not started or measurement_start is None:
            raise RuntimeError("host never started snapshots")
        if any(child.returncode != 0 for child in children):
            raise RuntimeError("nonzero fixture process exit")
        for role_name in logs:
            for filename in ["stdout.log", "engine.log"]:
                text = (case_dir / role_name / filename).read_text(errors="replace")
                if DIAGNOSTIC.search(text):
                    raise RuntimeError(f"diagnostic in {role_name}/{filename}")
        if profile == "adverse" and not all(route.blackout_end for route in routes):
            raise RuntimeError("adverse blackout schedule incomplete")
        stall_duration_ms = 0
        if len(host_stall_records) == 2:
            stall_duration_ms = host_stall_records[1]["time_ms"] - host_stall_records[0]["time_ms"]
        stall_complete = (len(host_stall_records) == 2 and
                          host_stall_records[0]["event"] == "host_stall_begin" and
                          host_stall_records[1]["event"] == "host_stall_end" and
                          stall_duration_ms >= MIN_HOST_STALL_MS)
        if profile == "adverse" and not stall_complete:
            raise RuntimeError(f"adverse host stall incomplete: {host_stall_records}")
        if profile == "normal" and host_stall_records:
            raise RuntimeError("normal profile unexpectedly stalled the host")

        network = summarize_network(routes, measurement_start, join_bytes)
        host = results["host"]
        clients = [results[f"client{index + 1}"] for index in range(args.clients)]
        encode_values = host["encode_usec"]
        decode_values = [value for client in clients for value in client["decode_usec"]]
        measurements = {
            "network": network,
            "delivered_profile": summarize_delivered_profiles(routes),
            "host_stall": {
                "required": profile == "adverse",
                "complete": stall_complete,
                "duration_ms": stall_duration_ms,
                "records": host_stall_records,
            },
            "application_bytes_per_entity_row": host["bytes_per_entity_row"],
            "baseline_payload_bytes_per_client": host["baseline_payload_bytes"] // args.clients,
            "encode_usec_per_snapshot": {
                "median": percentile(encode_values, 0.5), "p95": percentile(encode_values),
                "max": max(encode_values, default=0), "samples": len(encode_values),
            },
            "decode_usec_per_packet": {
                "median": percentile(decode_values, 0.5), "p95": percentile(decode_values),
                "max": max(decode_values, default=0), "samples": len(decode_values),
            },
            "client_jitter_p95_m": [client["jitter_p95_m"] for client in clients],
            "client_extrapolation_frames": [client["extrapolation_frames"] for client in clients],
            "client_interpolation_frames": [client["interpolation_frames"] for client in clients],
            "stale_rows_rejected": [client["stale_rows_rejected"] for client in clients],
            "max_motion_packet_bytes": host["max_packet_bytes"],
        }
        requirements = list(network["budget_pass"].values()) + [
            network["join_baseline_pass"], host["max_packet_bytes"] <= 1200,
            stall_complete if profile == "adverse" else not host_stall_records,
            all(client["entities"] == 148 for client in clients),
            all(client["lifecycle_events"] == ["death", "wreck", "despawn", "spawn"]
                for client in clients),
        ]
        summary = {
            "ok": all(requirements),
            "profile": profile,
            "repetition": repetition,
            "commands": commands,
            "process_ids": [child.pid for child in children],
            "exits": [child.returncode for child in children],
            "environment_before": environment_before,
            "environment_measurement": environment_measurement,
            "timing_label": ("contended upper bound" if
                             (environment_before["godot_processes"] or 0) > 0 else
                             "uncontended before launch"),
            "measurements": measurements,
            "results": results,
            "peak_proxy_queues": [route.peak_queue for route in routes],
            "ports": {"host": host_port, "proxies": proxy_ports},
        }
        (case_dir / "result.json").write_text(json.dumps(summary, indent=2) + "\n")
        if not summary["ok"]:
            raise RuntimeError("measured budget or lifecycle criterion failed")
        return summary
    finally:
        stop_children(children)
        for output in logs.values():
            output.close()
        for route in routes:
            route.socket.close()
        for output in proxy_logs:
            output.close()


def main():
    """Parse bounded runner options, execute all repetitions and retain an aggregate result."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot") or "godot")
    parser.add_argument("--profiles", nargs="+", choices=PROFILES, default=list(PROFILES))
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--clients", type=int, default=3)
    parser.add_argument("--port", type=int, default=25220)
    parser.add_argument("--proxy-port", type=int, default=25221)
    parser.add_argument("--deadline", type=float, default=25)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.clients <= 3 or not 1 <= args.repetitions <= 5:
        parser.error("clients must be 1..3 and repetitions 1..5")
    ports = [args.port] + [args.proxy_port + index for index in range(args.clients)]
    if len(set(ports)) != len(ports) or any(port < 1 or port > 65535 for port in ports):
        parser.error("host/proxy ports must be distinct and within 1..65535")
    if not 15 <= args.deadline <= 90:
        parser.error("deadline must be 15..90 seconds per case")

    output = (args.output or Path(tempfile.mkdtemp(prefix="s11-"))).resolve()
    if output.is_relative_to(ROOT):
        parser.error("evidence output must be outside checkout")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("fresh empty evidence directory required")
    print("S11 evidence:", output, flush=True)

    previous = signal.signal(signal.SIGTERM, lambda _signal, _frame: (_ for _ in ()).throw(
        KeyboardInterrupt()))
    aggregate = {"ok": False, "cases": []}
    try:
        aggregate["engine"] = engine_version(args.godot)
        aggregate["repository"] = repository_identity()
        aggregate["measurement_source_sha256"] = measurement_source_fingerprints()
        project = stage(output)
        aggregate["source_sha256"] = source_fingerprints(project)
        import_command = [args.godot, "--headless", "--editor", "--path", str(project),
                          "--import", "--quit", "--log-file", str(output / "import.engine.log")]
        if not checked_command(import_command, output / "import.log",
                               environment(output / "import-user"), 45):
            raise RuntimeError("isolated fixture import failed")
        probe_command = [args.godot, "--headless", "--path", str(project), "--script",
                         "res://tests/fixtures/s11/api_probe.gd", "--log-file",
                         str(output / "probe.engine.log")]
        if not checked_command(probe_command, output / "probe.log",
                               environment(output / "probe-user"), 30):
            raise RuntimeError("S11 public API probe failed")
        aggregate["commands"] = {"import": import_command, "probe": probe_command}
        for profile in args.profiles:
            for repetition in range(1, args.repetitions + 1):
                case = run_case(args, project, output / f"{profile}-{repetition}",
                                profile, repetition)
                aggregate["cases"].append(case)
                print(json.dumps({"profile": profile, "repetition": repetition,
                                  "ok": case["ok"],
                                  "measurements": case["measurements"]}), flush=True)
        aggregate["ok"] = all(case["ok"] for case in aggregate["cases"])
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        aggregate["failure"] = str(error)
    except KeyboardInterrupt:
        aggregate["failure"] = "runner interrupted; owned children stopped"
    finally:
        signal.signal(signal.SIGTERM, previous)
        (output / "result.json").write_text(json.dumps(aggregate, indent=2) + "\n")
    print(json.dumps({"ok": aggregate["ok"], "failure": aggregate.get("failure"),
                      "case_count": len(aggregate["cases"])}))
    return 0 if aggregate["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
