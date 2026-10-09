#!/usr/bin/env python3
"""Run the capped production host-budget tracking scene and label contention."""

import argparse
import csv
import io
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time

from script_checks import PIN, environment

ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC = re.compile(r"(?:SCRIPT ERROR:|ERROR:|WARNING:)")
SCENE = "res://tests/performance/host_budget/host_budget_tracking.tscn"


def godot_process_count():
    """Return a best-effort count of unrelated or owned Godot processes."""
    try:
        if os.name == "nt":
            result = subprocess.run(
                ["tasklist", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            rows = csv.reader(io.StringIO(result.stdout))
            return sum(1 for row in rows if row and "godot" in row[0].lower())
        result = subprocess.run(
            ["pgrep", "-fc", "godot"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return int(result.stdout.strip() or "0")
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def pinned_engine_version(godot, timeout_tool):
    """Read the engine version through the required external timeout wrapper."""
    result = subprocess.run(
        [timeout_tool, "15", godot, "--version"],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    version = result.stdout.strip()
    if result.returncode != 0 or version != PIN:
        raise RuntimeError(f"expected pinned engine {PIN}; got {version!r}")
    return version


def run_tracking(godot, timeout_tool, output, warmup_ticks, measured_ticks):
    """Run one capped headless scene and return its augmented report."""
    output.mkdir(parents=True, exist_ok=True)
    raw_result = output / "scene-result.json"
    engine_log = output / "godot.engine.log"
    process_log = output / "godot.log"
    child_env = environment(output / "user")
    child_env["HOST_BUDGET_OUTPUT"] = os.fspath(raw_result)
    child_env["HOST_BUDGET_WARMUP_TICKS"] = str(warmup_ticks)
    child_env["HOST_BUDGET_MEASURED_TICKS"] = str(measured_ticks)
    command = [
        timeout_tool,
        "180",
        godot,
        "--headless",
        "--max-fps",
        "60",
        "--path",
        os.fspath(ROOT),
        "--log-file",
        os.fspath(engine_log),
        SCENE,
    ]

    before_count = godot_process_count()
    with process_log.open("w", encoding="utf-8") as log:
        child = subprocess.Popen(
            command,
            cwd=ROOT,
            env=child_env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        time.sleep(1.0)
        during_count = godot_process_count()
        try:
            returncode = child.wait(timeout=190)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=10)
            returncode = None
    after_count = godot_process_count()

    combined_log = process_log.read_text(encoding="utf-8", errors="replace")
    if engine_log.exists():
        combined_log += engine_log.read_text(encoding="utf-8", errors="replace")
    if returncode != 0:
        raise RuntimeError(f"tracking scene failed with return code {returncode}")
    if DIAGNOSTIC.search(combined_log):
        raise RuntimeError("tracking scene emitted an engine/script diagnostic")
    if not raw_result.is_file():
        raise RuntimeError("tracking scene did not write its result")

    result = json.loads(raw_result.read_text(encoding="utf-8"))
    expected_samples = measured_ticks
    if not result.get("ok") or result["timing_ms"]["sample_count"] != expected_samples:
        raise RuntimeError("tracking scene returned an incomplete sample set")
    other_during = None if during_count is None else max(0, during_count - 1)
    counts = [value for value in (before_count, other_during, after_count) if value is not None]
    contention_observed = any(value > 0 for value in counts)
    result.update({
        "engine_pin": PIN,
        "scene": SCENE,
        "command": command,
        "machine": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "logical_cpu_count": os.cpu_count(),
        },
        "contention": {
            "godot_processes_before": before_count,
            "other_godot_processes_during": other_during,
            "godot_processes_after": after_count,
            "observed": contention_observed,
            "label": "contended" if contention_observed else "no other Godot process observed",
            "method": "instantaneous process-count samples; not a quiet-machine proof",
        },
        "safety": {
            "headless": True,
            "max_fps": 60,
            "d3d12_used": False,
            "report_only": True,
        },
    })
    (output / "result.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main():
    """Validate arguments, run the scene, and print its concise timing report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot") or "godot")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--warmup-ticks", type=int, default=600)
    parser.add_argument("--measured-ticks", type=int, default=3600)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    if output.exists() and any(output.iterdir()):
        parser.error("output must be a fresh empty directory")
    if args.warmup_ticks <= 0 or args.measured_ticks <= 0:
        parser.error("tick counts must be positive")
    timeout_tool = shutil.which("timeout")
    if timeout_tool is None:
        parser.error("GNU timeout is required for every Godot invocation")

    try:
        pinned_engine_version(args.godot, timeout_tool)
        result = run_tracking(
            args.godot,
            timeout_tool,
            output,
            args.warmup_ticks,
            args.measured_ticks,
        )
    except (OSError, RuntimeError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        output.mkdir(parents=True, exist_ok=True)
        (output / "failure.txt").write_text(f"{error}\n", encoding="utf-8")
        print(error, file=sys.stderr)
        return 1

    print(json.dumps({
        "timing_ms": result["timing_ms"],
        "soft_target": result["soft_target"],
        "contention": result["contention"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
