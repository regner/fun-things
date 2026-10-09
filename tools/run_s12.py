#!/usr/bin/env python3
"""Run the bounded S12 hit-registration experiment through impaired real ENet processes."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import tempfile
import time

from run_s03 import stop_children
from run_s03_r import FootProxy, POLL_SECONDS
from script_checks import ROOT, DIAGNOSTIC, checked_command, engine_version, environment

DEFAULT_PROFILES = ["normal", "adverse"]
EXPECTED_PROBE_REASONS = ["STALE_SEQUENCE", "INVALID", "INVALID"]


def percentile(values, quantile=0.95):
    """Return the nearest-rank percentile for a finite measurement list."""
    if not values:
        return None
    return sorted(values)[math.ceil(len(values) * quantile) - 1]


def records(path):
    """Read structured S12 records while retaining unrelated engine output in the log."""
    return [json.loads(line.removeprefix("S12 ")) for line in path.read_text().splitlines()
            if line.startswith("S12 ")]


def analyze(client_summary):
    """Calculate agreement, false-positive, rewind-cost, memory, and rocket-offset evidence."""
    shots = client_summary["shots"]
    groups = {}
    for target in ["pedestrian", "car"]:
        rows = [row for row in shots if row["target"] == target]
        current_agree = sum(row["client_hit"] == row["current_hit"] for row in rows)
        rewind_agree = sum(row["client_hit"] == row["rewind_hit"] for row in rows)
        groups[target] = {
            "samples": len(rows),
            "speed_mps": rows[0]["speed"] if rows else None,
            "current_agreement_rate": current_agree / len(rows) if rows else None,
            "rewind_agreement_rate": rewind_agree / len(rows) if rows else None,
            "current_false_positives": sum(not row["client_hit"] and row["current_hit"]
                                           for row in rows),
            "rewind_false_positives": sum(not row["client_hit"] and row["rewind_hit"]
                                          for row in rows),
            "current_false_negatives": sum(row["client_hit"] and not row["current_hit"]
                                           for row in rows),
            "rewind_false_negatives": sum(row["client_hit"] and not row["rewind_hit"]
                                          for row in rows),
            "rewind_clamped": sum(row["rewind_clamped"] for row in rows),
        }
    cpu = [row["rewind_cpu_usec"] for row in shots]
    offsets = [abs(row["offset_m"]) for row in client_summary["rockets"]]
    return {
        "by_target": groups,
        "accepted_shots": len(shots),
        "attempts": client_summary["attempts"],
        "responses": client_summary["responses"],
        "rewind_cpu_usec": {"median": percentile(cpu, 0.5), "p95": percentile(cpu),
                             "worst": max(cpu, default=0)},
        "history_peak_bytes": client_summary["host"]["history_peak_bytes"],
        "history_samples": client_summary["host"]["history_samples"],
        "host_rejections": client_summary["host"]["rejections"],
        "security_probes": client_summary["probes"],
        "rocket_presentation_offset_m": {"samples": len(offsets),
                                          "median": percentile(offsets, 0.5),
                                          "p95": percentile(offsets),
                                          "worst": max(offsets, default=0)},
    }


def evaluate_case(measurements, profile, proxy_events, host_records, unchanged):
    """Return independently reviewable criteria, including probes and adverse events."""
    attempts = measurements["attempts"]
    probes = measurements["security_probes"]
    probe_shape = len(probes) == len(EXPECTED_PROBE_REASONS)
    if probe_shape:
        probe_shape = all(
            row.get("accepted") is False
            and row.get("sequence") == attempts + index
            and row.get("reason") == reason
            for index, (row, reason) in enumerate(zip(probes, EXPECTED_PROBE_REASONS))
        )
    events = [row.get("event") for row in proxy_events]
    blackout_drops = [row for row in proxy_events if row.get("event") == "drop"
                      and row.get("reason") in ["blackout", "blackout_pending"]]
    stall_begin = [row for row in host_records if row.get("event") == "stall_begin"]
    stall_end = [row for row in host_records if row.get("event") == "stall_end"]
    stall_complete = len(stall_begin) == 1 and len(stall_end) == 1
    if stall_complete:
        stall_complete = (stall_end[0]["wall_usec"] - stall_begin[0]["wall_usec"]
                          >= 250_000)
    adverse_complete = True
    profile_isolated = True
    if profile == "adverse":
        adverse_complete = (events.count("blackout_begin") == 1
                            and events.count("blackout_end") == 1
                            and bool(blackout_drops) and stall_complete)
    else:
        profile_isolated = ("blackout_begin" not in events and "blackout_end" not in events
                            and not blackout_drops and not stall_begin and not stall_end)
    criteria = {
        "all_attempts_answered": measurements["responses"] == attempts,
        "accepted_sample_floor": measurements["accepted_shots"] >= attempts // 2,
        "per_target_sample_floor": all(
            row["samples"] >= attempts // 4
            for row in measurements["by_target"].values()),
        "history_sample_bound": measurements["history_samples"] <= 24,
        "history_byte_bound": measurements["history_peak_bytes"] < 32768,
        "security_probe_outcomes": probe_shape,
        "rocket_sample_floor": measurements["rocket_presentation_offset_m"]["samples"] >= 6,
        "adverse_interruption_and_stall": adverse_complete,
        "profile_isolated": profile_isolated,
        "saved_source_unchanged": unchanged,
    }
    return criteria


def host_load():
    """Record concurrent Godot process count and best-effort Windows CPU utilization."""
    count = 0
    try:
        listing = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True,
                                 text=True, timeout=5, check=False).stdout.lower()
        count = sum("godot" in line for line in listing.splitlines())
    except (OSError, subprocess.SubprocessError):
        pass
    cpu = None
    try:
        command = ["powershell", "-NoProfile", "-Command",
                   "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage "
                   "-Average).Average"]
        output = subprocess.run(command, capture_output=True, text=True, timeout=10,
                                check=False).stdout.strip()
        cpu = float(output) if output else None
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    return {"concurrent_godot_processes": count, "cpu_load_percent": cpu,
            "timing_label": "quiet measurement" if count == 0 else "contended upper bound"}


def stage(directory):
    """Copy only S03 admission/transport and the owned S12 fixture into an addon-free project."""
    project = directory / "project"
    for fixture in ["s03", "s12"]:
        shutil.copytree(ROOT / "tests/fixtures" / fixture,
                        project / "tests/fixtures" / fixture)
    settings = (ROOT / "project.godot").read_text()
    for section in ["autoload", "editor_plugins"]:
        settings = re.sub(r"(?ms)^\[" + section + r"\]\n.*?(?=^\[|\Z)", "", settings)
    settings = settings.replace('config/icon="res://icon.svg"', '') + "\n"
    (project / "project.godot").write_text(settings)
    return project


def run_case(args, directory, profile):
    """Run one host/client pair through the seeded native UDP proxy and retain all logs."""
    directory.mkdir()
    project = stage(directory)
    before = {str(path.relative_to(project)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in project.rglob("*") if path.is_file()}
    if not checked_command([args.godot, "--headless", "--editor", "--path", str(project),
                            "--import", "--quit"], directory / "import.log",
                           environment(directory / "import-user")):
        raise RuntimeError("isolated fixture import failed")

    load = host_load()
    logs = {}
    offsets = {"host": 0, "client": 0}
    children = []
    results = {}
    commands = {}
    ready = False
    proxy_log = (directory / "proxy.jsonl").open("w")
    proxy = FootProxy(args.port, args.proxy_port, profile, proxy_log)
    deadline = time.monotonic() + args.deadline
    try:
        def start(role, port):
            role_dir = directory / role
            role_dir.mkdir()
            command = [args.godot, "--headless", "--path", str(project), "--log-file",
                       str(role_dir / "engine.log"), "res://tests/fixtures/s12/boot.tscn", "--",
                       "--role=" + role, "--port=" + str(port), "--profile=" + profile]
            commands[role] = command
            logs[role] = (role_dir / "stdout.log").open("w")
            child = subprocess.Popen(command, stdout=logs[role], stderr=subprocess.STDOUT,
                                     env=environment(role_dir / "user"))
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
                        if not line.startswith("S12 "):
                            continue
                        record = json.loads(line.removeprefix("S12 "))
                        if role == "host" and record["event"] == "ready":
                            ready = True
                        if role == "client" and record["event"] == "shot_sent" and proxy.start is None:
                            proxy.start = time.monotonic()
                        if record["event"] == "result":
                            results[role] = record
                            if not record["ok"]:
                                raise RuntimeError(f"{role} outcome failed: {record['details']}")
            if ready and "client" not in logs:
                start("client", args.proxy_port)
            if len(results) == 2 and all(child.poll() is not None for child in children):
                break
            for index, child in enumerate(children):
                role = "host" if index == 0 else "client"
                if child.poll() is not None and role not in results:
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
        client_summary = results["client"]["details"]["summary"]
        measurements = analyze(client_summary)
        unchanged = all(hashlib.sha256((project / path).read_bytes()).hexdigest() == digest
                        for path, digest in before.items())
        host_records = records(directory / "host/stdout.log")
        criteria = evaluate_case(measurements, profile, proxy.events, host_records, unchanged)
        summary = {"ok": all(criteria.values()), "profile": profile,
                   "criteria": criteria, "measurements": measurements,
                   "load": load, "source_sha256": before, "saved_source_unchanged": unchanged,
                   "commands": commands, "process_ids": [child.pid for child in children],
                   "exits": [child.returncode for child in children],
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
    """Validate arguments, run requested profiles, and write one reproducible JSON receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot") or "godot")
    parser.add_argument("--port", type=int, default=25200)
    parser.add_argument("--proxy-port", type=int, default=25201)
    parser.add_argument("--deadline", type=float, default=45)
    parser.add_argument("--profiles", nargs="+", choices=["normal", "adverse"],
                        default=DEFAULT_PROFILES)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not (1 <= args.port <= 65535 and 1 <= args.proxy_port <= 65535 and
            args.port != args.proxy_port and 1 <= args.deadline <= 60):
        parser.error("distinct ports 1..65535 and deadline 1..60 seconds required")
    directory = (args.output or Path(tempfile.mkdtemp(prefix="s12-"))).resolve()
    if directory.is_relative_to(ROOT):
        parser.error("evidence output must be outside checkout")
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        parser.error("fresh empty evidence directory required")
    print("S12 evidence:", directory, flush=True)

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
                raise RuntimeError("independent criteria failed; inspect profile result")
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
