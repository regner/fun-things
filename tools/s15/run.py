#!/usr/bin/env python3
"""Run capped Forward+ S15 VFX stress cases and retain bounded graphical telemetry."""
import argparse
import ctypes
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from measurement_identity import measurement_identity  # noqa: E402
from script_checks import DIAGNOSTIC, PIN, environment  # noqa: E402
from window_safety import capped_window_arguments, require_capped_window  # noqa: E402

FIXTURES = ["s02", "s03", "s04", "s06", "s15"]
MODELS = ["s02_*", "s04_*", "s06_*"]
EFFECT_MODELS = "s15_*"
SCENE = "res://tests/fixtures/s15/stress.tscn"
CHECK_SCRIPT = "res://tests/fixtures/s15/check.gd"
FIELDS = [
    "elapsed_s", "frame_interval_ms", "render_cpu_ms", "render_gpu_ms", "process_ms",
    "physics_ms", "draw_calls", "primitives", "objects", "video_mem_bytes",
]
CASES = [(12, "full"), (24, "full"), (24, "adaptive")]
STAGED_INPUTS = [
    "tests/fixtures/s02", "tests/fixtures/s03", "tests/fixtures/s04",
    "tests/fixtures/s06", "tests/fixtures/s15", "art/models/spikes",
    "art/models/effects", "project.godot", "tools/s15/run.py",
]
CASE_SLACK_SECONDS = 60
CLEANUP_SECONDS = 5
QUIET_SETTLE_SECONDS = 1.0


class FileTime(ctypes.Structure):
    """Windows FILETIME layout used for a short whole-system CPU sample."""

    _fields_ = [("low", ctypes.c_ulong), ("high", ctypes.c_ulong)]


# Write JSON receipts with deterministic formatting and LF endings.
def save(path, value):
    """Write strict JSON with stable formatting and LF endings."""
    path.write_text(json.dumps(value, indent=2) + "\n", newline="\n")


# Bind copied inputs and the runner to the recorded source revision.
def dirty_inputs():
    """Return scoped changes that prevent evidence from binding to HEAD."""
    return subprocess.check_output(
        ["git", "status", "--porcelain", "--", *STAGED_INPUTS],
        cwd=ROOT,
        text=True,
    ).strip()


# Keep the runtime mirror addon-free while preserving renderer and physics settings.
def stage(output):
    """Copy the saved fixture closure and source-linked models to a fresh project."""
    project = output / "project"
    for fixture in FIXTURES:
        shutil.copytree(
            ROOT / "tests/fixtures" / fixture,
            project / "tests/fixtures" / fixture,
            ignore=shutil.ignore_patterns("editor_harness.tscn"),
        )
    models = project / "art/models/spikes"
    models.mkdir(parents=True)
    for pattern in MODELS:
        for path in (ROOT / "art/models/spikes").glob(pattern):
            shutil.copy2(path, models / path.name)
    effects = project / "art/models/effects"
    effects.mkdir(parents=True)
    for path in (ROOT / "art/models/effects").glob(EFFECT_MODELS):
        shutil.copy2(path, effects / path.name)
    settings = (ROOT / "project.godot").read_text()
    settings = re.sub(r"(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)", "", settings)
    settings = settings.replace('config/icon="res://icon.svg"\n', "")
    settings = re.sub(r'^run/main_scene=".*"\n', "", settings, flags=re.MULTILINE)
    (project / "project.godot").write_text(settings, newline="\n")
    return project


# Nearest-rank matches the existing graphical foundation runner.
def percentile(values, quantile):
    """Return a nearest-rank percentile, or None for an empty sequence."""
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(quantile * len(ordered)) - 1))
    return ordered[index]


# Summaries retain the budget-relevant frame and renderer distributions.
def summarize_samples(result):
    """Summarize fixture frame rows using their declared field order."""
    rows = result.get("samples", [])
    summary = {"frames": len(rows)}
    if rows:
        summary["span_s"] = rows[-1][0] - rows[0][0]
    for index, field in enumerate(FIELDS[1:], start=1):
        values = [row[index] for row in rows]
        summary[field] = {
            "p50": percentile(values, 0.5),
            "p95": percentile(values, 0.95),
            "p99": percentile(values, 0.99),
            "max": max(values) if values else None,
        }
    intervals = [row[1] for row in rows]
    summary["mean_fps"] = (
        len(intervals) / (sum(intervals) / 1000.0) if intervals else None
    )
    summary["hitches_over_33ms"] = sum(value > 33.4 for value in intervals)
    return summary


# Count all desktop Godot processes so timings can be labeled for contention.
def godot_process_count():
    """Count currently listed Godot processes without terminating or opening handles."""
    if platform.system() == "Windows":
        completed = subprocess.run(
            ["tasklist"], capture_output=True, text=True, timeout=10, check=False
        )
        return sum("godot" in line.lower() for line in completed.stdout.splitlines())
    completed = subprocess.run(
        ["ps", "-eo", "comm="], capture_output=True, text=True, timeout=10, check=False
    )
    return sum("godot" in line.lower() for line in completed.stdout.splitlines())


# FILETIME conversion stays local to the Windows contention sample.
def _filetime_value(value):
    """Convert a FILETIME pair to its unsigned 64-bit tick value."""
    return (value.high << 32) | value.low


# A short sample records ambient workstation contention for each repetition.
def cpu_load_percent():
    """Return a short whole-system CPU-load sample, or an explicit unavailable value."""
    if platform.system() != "Windows":
        try:
            return {"percent": None, "load_average_1m": os.getloadavg()[0]}
        except OSError:
            return {"percent": None, "load_average_1m": None}
    idle_a, kernel_a, user_a = FileTime(), FileTime(), FileTime()
    idle_b, kernel_b, user_b = FileTime(), FileTime(), FileTime()
    if not ctypes.windll.kernel32.GetSystemTimes(
        ctypes.byref(idle_a), ctypes.byref(kernel_a), ctypes.byref(user_a)
    ):
        return {"percent": None}
    time.sleep(0.25)
    if not ctypes.windll.kernel32.GetSystemTimes(
        ctypes.byref(idle_b), ctypes.byref(kernel_b), ctypes.byref(user_b)
    ):
        return {"percent": None}
    idle = _filetime_value(idle_b) - _filetime_value(idle_a)
    total = (
        _filetime_value(kernel_b) - _filetime_value(kernel_a)
        + _filetime_value(user_b) - _filetime_value(user_a)
    )
    percent = 100.0 * (total - idle) / total if total else 0.0
    return {"percent": round(percent, 2)}


# Retain complete process streams and only stop the owned child on timeout.
def run_case(args, project, output, explosions, quality, repeat):
    """Run one capped windowed load case and return its complete receipt."""
    name = f"e{explosions}-{quality}-r{repeat}"
    folder = output / name
    folder.mkdir()
    result_path = folder / "raw-result.json"
    capture_path = folder / "frame.png"
    env = environment(folder / "user")
    env.update(
        S15_EXPLOSIONS=str(explosions),
        S15_QUALITY=quality,
        S15_WARMUP_SECONDS=str(args.warmup),
        S15_DURATION_SECONDS=str(args.duration),
        S15_RESULT_PATH=str(result_path),
    )
    if repeat == 1 and (explosions, quality) in [(12, "full"), (24, "full")]:
        env["S15_CAPTURE_PATH"] = str(capture_path)
    argv = [
        args.godot, "--path", str(project), "--windowed", *capped_window_arguments(),
        "--resolution", "1280x800", "--log-file", str(folder / "engine.log"), SCENE,
    ]
    require_capped_window(argv)
    with (folder / "stdout.log").open("wb") as stdout, (
        folder / "stderr.log"
    ).open("wb") as stderr:
        child = subprocess.Popen(argv, cwd=project, stdout=stdout, stderr=stderr, env=env)
        try:
            child.wait(timeout=args.warmup + args.duration + CASE_SLACK_SECONDS)
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
            child.terminate()
            try:
                child.wait(timeout=CLEANUP_SECONDS)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=CLEANUP_SECONDS)
    contention = {
        "godot_processes_after": godot_process_count(),
        "cpu_after": cpu_load_percent(),
        "mode": "post-case only; no sampler ran in timed window",
    }
    time.sleep(QUIET_SETTLE_SECONDS)
    text = "".join(
        (folder / filename).read_text(errors="replace")
        for filename in ["stdout.log", "stderr.log", "engine.log"]
        if (folder / filename).exists()
    )
    diagnostics = [line for line in text.splitlines() if DIAGNOSTIC.search(line)]
    raw = json.loads(result_path.read_text()) if result_path.exists() else None
    frames = summarize_samples(raw) if raw is not None else None
    record = {
        "name": name,
        "explosions": explosions,
        "quality": quality,
        "repeat": repeat,
        "argv": argv,
        "exit": child.returncode,
        "timed_out": timed_out,
        "diagnostics": diagnostics,
        "contention": contention,
        "particle_capacity": raw.get("particle_capacity") if raw else None,
        "renderer": raw.get("renderer") if raw else None,
        "adapter": raw.get("adapter") if raw else None,
        "api_version": raw.get("api_version") if raw else None,
        "frames": frames,
        "capture": str(capture_path) if capture_path.exists() else None,
    }
    record["ok"] = (
        child.returncode == 0 and not timed_out and not diagnostics and raw is not None
        and frames is not None and frames["frames"] > 0
    )
    save(folder / "case.json", record)
    return record


# Aggregate three repeats into median/worst rows without hiding individual receipts.
def aggregate_cases(cases):
    """Report median and worst repeat values for each load and frame statistic."""
    aggregated = {}
    for explosions, quality in CASES:
        name = f"e{explosions}-{quality}"
        selected = [
            case for case in cases
            if case["explosions"] == explosions and case["quality"] == quality
        ]
        row = {
            "repetitions": len(selected),
            "particle_capacity": sorted({case["particle_capacity"] for case in selected}),
            "contention": [case["contention"] for case in selected],
            "metrics": {},
        }
        for field in ["frame_interval_ms", "render_cpu_ms", "render_gpu_ms", "draw_calls"]:
            for quantile in ["p50", "p95", "p99"]:
                values = [case["frames"][field][quantile] for case in selected]
                row["metrics"][f"{field}_{quantile}"] = {
                    "median": statistics.median(values) if values else None,
                    "worst": max(values) if values else None,
                }
        aggregated[name] = row
    return aggregated


# Checked subprocess logs use the same diagnostic policy as foundation tools.
def run_checked(argv, log_path, env, timeout_seconds):
    """Run one bounded setup/check command and reject engine diagnostics."""
    with log_path.open("wb") as log:
        completed = subprocess.run(
            argv, stdout=log, stderr=subprocess.STDOUT, env=env, timeout=timeout_seconds
        )
    lines = log_path.read_text(errors="replace").splitlines()
    diagnostics = [line for line in lines if DIAGNOSTIC.search(line)]
    return {"argv": argv, "exit": completed.returncode, "diagnostics": diagnostics}


# Main deliberately stops after the first failure rather than manufacturing repeats.
def main():
    """Import, validate, and run three repetitions of each bounded load case."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--duration", type=float, default=20.0)
    parser.add_argument("--warmup", type=float, default=5.0)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if args.godot is None:
        parser.error("godot not found on PATH; pass --godot")
    if not (1 <= args.duration <= 60 and 0 <= args.warmup <= 20 and 3 <= args.repeats <= 3):
        parser.error("duration must be 1..60 s, warmup 0..20 s, repeats exactly 3")
    output = (args.output or Path(tempfile.mkdtemp(prefix="s15-vfx-"))).resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("output must be a fresh empty directory")
    print(f"S15 VFX evidence: {output}", flush=True)

    version = subprocess.run(
        [args.godot, "--version"], capture_output=True, text=True, timeout=10, check=True
    ).stdout.strip()
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    dirty = dirty_inputs()
    summary = {
        "ok": False,
        "engine": version,
        "revision": revision,
        "dirty_inputs": dirty,
        "platform": platform.platform(),
        "duration_s": args.duration,
        "warmup_s": args.warmup,
        "repeats": args.repeats,
        "measurement_identity": measurement_identity(
            ROOT,
            [*STAGED_INPUTS, "tools/measurement_identity.py", "tools/window_safety.py",
             "tools/script_checks.py"],
            {**vars(args), "output": output},
        ),
        "cases": [],
    }
    if version != PIN:
        summary["failure"] = f"expected {PIN}, got {version}"
    elif dirty:
        summary["failure"] = "scoped staged inputs or runner are dirty"
    else:
        project = stage(output)
        import_result = run_checked(
            [args.godot, "--headless", "--editor", "--path", str(project), "--import", "--quit"],
            output / "import.log",
            environment(output / "import-user"),
            120,
        )
        summary["import"] = import_result
        if import_result["exit"] != 0 or import_result["diagnostics"]:
            summary["failure"] = "import failed or reported diagnostics"
        else:
            check_result = run_checked(
                [args.godot, "--headless", "--path", str(project), "--script", CHECK_SCRIPT],
                output / "check.log",
                environment(output / "check-user"),
                60,
            )
            summary["check"] = check_result
            if check_result["exit"] != 0 or check_result["diagnostics"]:
                summary["failure"] = "saved public-API check failed or reported diagnostics"
            else:
                for explosions, quality in CASES:
                    for repeat in range(1, args.repeats + 1):
                        record = run_case(
                            args, project, output, explosions, quality, repeat
                        )
                        summary["cases"].append(record)
                        save(output / "summary.json", summary)
                        if not record["ok"]:
                            summary["failure"] = f"case {record['name']} failed; stopping"
                            break
                    if summary.get("failure"):
                        break
                if not summary.get("failure"):
                    summary["aggregates"] = aggregate_cases(summary["cases"])
                    summary["ok"] = True
    save(output / "summary.json", summary)
    print(json.dumps({"ok": summary["ok"], "failure": summary.get("failure")}))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
