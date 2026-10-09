#!/usr/bin/env python3
"""Stage and measure the bounded S10 pedestrian experiment with the pinned engine."""

import argparse
import csv
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from script_checks import DIAGNOSTIC, engine_version, environment  # noqa: E402

DEFAULT_SEEDS = (101, 202, 303)


def process_count():
    """Count Godot processes without stopping or otherwise touching any of them."""
    if os.name == "nt":
        result = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode != 0:
            return None
        rows = csv.reader(result.stdout.splitlines())
        return sum(1 for row in rows if row and row[0].lower().startswith("godot"))
    result = subprocess.run(
        ["ps", "-A", "-o", "comm="],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if result.returncode != 0:
        return None
    return sum(1 for line in result.stdout.splitlines() if "godot" in line.lower())


def cpu_load():
    """Read a bounded system CPU-load snapshot with an explicit source label."""
    if os.name == "nt":
        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            "(Get-CimInstance Win32_Processor | "
            "Measure-Object -Property LoadPercentage -Average).Average",
        ]
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=10, check=False
        )
        try:
            return {"percent": float(result.stdout.strip()), "source": "Win32_Processor"}
        except ValueError:
            return {"percent": None, "source": "Win32_Processor_unavailable"}
    try:
        normalized = os.getloadavg()[0] / max(1, os.cpu_count() or 1) * 100.0
        return {"percent": normalized, "source": "loadavg_1m_normalized"}
    except OSError:
        return {"percent": None, "source": "loadavg_unavailable"}


def telemetry_snapshot():
    """Capture process contention and CPU load around a timing repetition."""
    return {"godot_processes": process_count(), "cpu_load": cpu_load()}


def stage_project(project):
    """Copy only S06/S10 saved dependencies into an addon-free external project."""
    shutil.copytree(ROOT / "tests/fixtures/s06", project / "tests/fixtures/s06")
    shutil.copytree(ROOT / "tests/fixtures/s10", project / "tests/fixtures/s10")
    models = project / "art/models/spikes"
    models.mkdir(parents=True)
    for source in (ROOT / "art/models/spikes").glob("s06_*"):
        if source.is_file():
            shutil.copy2(source, models / source.name)
    settings = (ROOT / "project.godot").read_text()
    for section in ("autoload", "editor_plugins"):
        settings = re.sub(
            rf"(?ms)^\[{section}\]\n.*?(?=^\[|\Z)", "", settings
        )
    settings = re.sub(r"^config/icon=.*\n", "", settings, flags=re.MULTILINE)
    (project / "project.godot").write_text(settings)


def checked_process(command, log, engine_log, env, timeout_seconds, observe=False):
    """Run one owned child with a deadline, retained logs and optional live telemetry."""
    before = telemetry_snapshot() if observe else None
    with log.open("w") as output:
        child = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT, env=env)
        during = None
        if observe:
            time.sleep(0.1)
            during = telemetry_snapshot()
        try:
            returncode = child.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            child.terminate()
            try:
                child.wait(timeout=2)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=2)
            output.write("\nCHECK DEADLINE EXCEEDED\n")
            returncode = -1
    after = telemetry_snapshot() if observe else None
    text = log.read_text(errors="replace")
    if engine_log.exists():
        text += engine_log.read_text(errors="replace")
    return {
        "ok": returncode == 0 and not DIAGNOSTIC.search(text),
        "returncode": returncode,
        "telemetry": {"before": before, "during": during, "after": after}
        if observe
        else None,
    }


def aggregate(runs):
    """Aggregate three independent repetitions without pretending percentiles pool."""
    grouped = {}
    for run in runs:
        key = f"{run['scenario']}/{run['motion']}"
        grouped.setdefault(key, []).append(run)
    result = {}
    for key, rows in sorted(grouped.items()):
        medians = [row["ai_movement_ms"]["median"] for row in rows]
        p95s = [row["ai_movement_ms"]["p95"] for row in rows]
        p99s = [row["ai_movement_ms"]["p99"] for row in rows]
        result[key] = {
            "repetitions": len(rows),
            "median_of_tick_medians_ms": statistics.median(medians),
            "median_of_tick_p95_ms": statistics.median(p95s),
            "worst_tick_p95_ms": max(p95s),
            "median_of_tick_p99_ms": statistics.median(p99s),
            "worst_tick_p99_ms": max(p99s),
            "worst_tick_max_ms": max(row["ai_movement_ms"]["max"] for row in rows),
            "max_flee_latency_ms": max(
                row["metrics"]["flee_latency_ms"]["max"] for row in rows
            ),
            "max_stuck_entities": max(row["metrics"]["stuck_entities"] for row in rows),
            "max_overlap_pairs": max(row["metrics"]["max_overlap_pairs"] for row in rows),
            "total_off_sidewalk_agent_ticks": sum(
                row["metrics"]["off_sidewalk_agent_ticks"] for row in rows
            ),
            "total_road_outside_crossing_agent_ticks": sum(
                row["metrics"]["road_outside_crossing_agent_ticks"] for row in rows
            ),
        }
    return result


def main():
    """Validate arguments, stage the fixture, execute three seeds and write JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    if output.exists() and any(output.iterdir()):
        parser.error("output must be absent or empty")
    output.mkdir(parents=True, exist_ok=True)
    print(f"S10 evidence: {output}", flush=True)

    version = engine_version(args.godot)
    project = output / "project"
    project.mkdir()
    stage_project(project)
    env = environment(output / "user")
    base = [args.godot, "--headless", "--path", str(project)]
    import_engine = output / "import.engine.log"
    import_result = checked_process(
        base + ["--editor", "--import", "--quit", "--log-file", str(import_engine)],
        output / "import.log",
        import_engine,
        env,
        60,
    )

    all_runs = []
    seed_receipts = []
    commands = []
    if import_result["ok"]:
        for seed in args.seeds:
            receipt_path = output / f"seed-{seed}.json"
            engine_log = output / f"seed-{seed}.engine.log"
            command = base + [
                "--script",
                "res://tests/fixtures/s10/benchmark.gd",
                "--log-file",
                str(engine_log),
                "--",
                "--seed",
                str(seed),
                "--output",
                str(receipt_path),
            ]
            commands.append(command)
            process_result = checked_process(
                command,
                output / f"seed-{seed}.log",
                engine_log,
                env,
                900,
                observe=True,
            )
            receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
            seed_receipts.append(
                {
                    "seed": seed,
                    "process": process_result,
                    "receipt_available": receipt is not None,
                }
            )
            if receipt:
                for run in receipt["runs"]:
                    run["contention"] = process_result["telemetry"]
                    run["timing_label"] = "contended upper bound"
                    all_runs.append(run)

    failures = []
    if not import_result["ok"]:
        failures.append("isolated import failed")
    for receipt in seed_receipts:
        if not receipt["process"]["ok"] or not receipt["receipt_available"]:
            failures.append(f"seed {receipt['seed']} process or receipt failed")
    for run in all_runs:
        failures.extend(
            f"seed {run['seed']} {run['scenario']}/{run['motion']}: {failure}"
            for failure in run["failures"]
        )
    expected_runs = len(args.seeds) * 4
    if len(all_runs) != expected_runs:
        failures.append(f"expected {expected_runs} measured runs, got {len(all_runs)}")

    result = {
        "engine": version,
        "seeds": list(args.seeds),
        "simulation_seconds_per_run": 600,
        "population_per_run": 64,
        "import": import_result,
        "commands": commands,
        "seed_receipts": seed_receipts,
        "runs": all_runs,
        "aggregate": aggregate(all_runs),
        "timing_interpretation": (
            "All timing rows are contended upper bounds because process/CPU snapshots do "
            "not prove exclusive machine use throughout a run."
        ),
        "failures": failures,
    }
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"runs": len(all_runs), "failures": failures}))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
