#!/usr/bin/env python3
"""Measure capped graphical cost for saved S07 environment-size variants.

The runner stages only the linked fixture inputs in a fresh external project, imports once,
then launches a fresh owned Godot process for each repeat. Every case uses 1280x800,
VSync disabled, a 60 FPS cap, 10 seconds of warmup and 30 measured seconds by default.
"""
import argparse
import array
import ctypes
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from script_checks import DIAGNOSTIC, PIN, environment  # noqa: E402

VARIANTS = [6, 24, 96, 384]
FIELDS = [
    "elapsed_s",
    "frame_interval_ms",
    "render_cpu_ms",
    "render_gpu_ms",
    "physics_ms",
    "draw_calls",
    "objects",
    "primitives",
    "video_mem_bytes",
    "node_count",
]
FIXTURE_FILES = [
    "tests/fixtures/s02/low_prefab.tscn",
    "tests/fixtures/s02/near_prefab.tscn",
    "tests/fixtures/s02/tall_prefab.tscn",
    "tests/fixtures/s06/anchor.gd",
    "tests/fixtures/s06/anchor.gd.uid",
    "tests/fixtures/s06/link.gd",
    "tests/fixtures/s06/link.gd.uid",
    "tests/fixtures/s06/sector.gd",
    "tests/fixtures/s06/sector.gd.uid",
    "tests/fixtures/s06/east.tscn",
    "tests/fixtures/s06/west.tscn",
    "tests/fixtures/s07_env/measure.gd",
    "tests/fixtures/s07_env/measure.gd.uid",
]
MODEL_NAMES = ["s02_low.glb", "s02_near.glb", "s02_tall.glb", "s06_east.glb",
               "s06_west.glb"]
CLEAN_INPUTS = ["project.godot", "tools/s07_env", "tests/fixtures/s07_env",
                "tests/fixtures/s02", "tests/fixtures/s06", "art/models/spikes"]
SCRIPT = "res://tests/fixtures/s07_env/measure.gd"
CASE_SLACK_SECONDS = 90
CLEANUP_SECONDS = 5
RAM_STOP_BYTES = 2 * 1024 * 1024 * 1024
LOAD_STOP_MS = 30_000
FRAME_STOP_MS = 20


class Memory(ctypes.Structure):
    """PROCESS_MEMORY_COUNTERS from psapi."""

    _fields_ = [
        ("cb", ctypes.c_ulong),
        ("PageFaultCount", ctypes.c_ulong),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


def save(path, value):
    """Write strict JSON with LF endings."""
    path.write_text(json.dumps(value, indent=2) + "\n", newline="\n")


def dirty_inputs():
    """Return changes in every copied input and in this runner/authoring tool."""
    return subprocess.check_output(
        ["git", "status", "--porcelain", "--", *CLEAN_INPUTS], cwd=ROOT, text=True
    ).strip()


def copy_file(source, project):
    """Copy one project-relative source while preserving its relative path."""
    destination = project / source
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / source, destination)


def stage(output, variants):
    """Stage only the saved linked scenes, scripts, models, and sanitized settings."""
    project = output / "project"
    project.mkdir()
    for source in FIXTURE_FILES:
        copy_file(source, project)
    for variant in variants:
        copy_file(f"tests/fixtures/s07_env/city_{variant}.tscn", project)
    for model_name in MODEL_NAMES:
        copy_file(f"art/models/spikes/{model_name}", project)
        copy_file(f"art/models/spikes/{model_name}.import", project)
    settings = (ROOT / "project.godot").read_text()
    settings = re.sub(r"(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)", "", settings)
    settings = settings.replace('config/icon="res://icon.svg"\n', "")
    (project / "project.godot").write_text(settings, newline="\n")
    return project


def resident(child):
    """Return working-set and peak-working-set bytes for the owned child."""
    if platform.system() != "Windows":
        try:
            for line in Path(f"/proc/{child.pid}/status").read_text().splitlines():
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) * 1024, None
        except OSError:
            return None
        return None
    counters = Memory()
    counters.cb = ctypes.sizeof(Memory)
    if ctypes.windll.psapi.GetProcessMemoryInfo(
        int(child._handle), ctypes.byref(counters), counters.cb
    ):
        return counters.WorkingSetSize, counters.PeakWorkingSetSize
    return None


def percentile(values, quantile):
    """Return a nearest-rank percentile, or None when no samples exist."""
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(quantile * len(ordered)) - 1))
    return ordered[index]


def summarize_frames(path, warmup):
    """Summarize measured frame telemetry while retaining raw samples separately."""
    raw = array.array("d")
    raw.frombytes(path.read_bytes())
    rows = [raw[index:index + len(FIELDS)] for index in range(0, len(raw), len(FIELDS))]
    selected = [row for row in rows if row[0] >= warmup]
    summary = {"frames": len(selected)}
    if selected:
        summary["span_s"] = selected[-1][0] - selected[0][0]
    for index, field in enumerate(FIELDS[1:], start=1):
        values = [row[index] for row in selected]
        summary[field] = {
            "p50": percentile(values, 0.5),
            "p95": percentile(values, 0.95),
            "p99": percentile(values, 0.99),
            "max": max(values) if values else None,
        }
    intervals = [row[1] for row in selected]
    summary["mean_fps"] = (
        len(intervals) / (sum(intervals) / 1000.0) if intervals else None
    )
    summary["hitches_over_33ms"] = sum(value > 33.4 for value in intervals)
    return summary


def stop_reasons(record):
    """Return predeclared growth-stop reasons observed in one case."""
    reasons = []
    if not record["ok"]:
        reasons.append("diagnostic, crash, timeout, or missing telemetry")
    result = record.get("result") or {}
    if result.get("cold_first_load_ms", 0) > LOAD_STOP_MS:
        reasons.append("cold first load exceeded 30 s")
    if result.get("warm_reload_ms", 0) > LOAD_STOP_MS:
        reasons.append("warm reload exceeded 30 s")
    if (record["resident_bytes"].get("max") or 0) > RAM_STOP_BYTES:
        reasons.append("working set exceeded 2 GiB")
    frame_p99 = ((record.get("frames") or {}).get("frame_interval_ms") or {}).get("p99")
    if frame_p99 is not None and frame_p99 > FRAME_STOP_MS:
        reasons.append("measured frame interval p99 exceeded 20 ms")
    return reasons


def run_case(args, project, output, variant, repeat):
    """Run one fresh owned windowed process and retain logs, samples, and summary."""
    folder = output / f"city-{variant}-repeat-{repeat}"
    folder.mkdir()
    env = environment(folder / "user")
    env.update(
        S07_ENV_OUTPUT=str(folder),
        S07_ENV_WARMUP=str(args.warmup),
        S07_ENV_DURATION=str(args.duration),
    )
    scene = f"res://tests/fixtures/s07_env/city_{variant}.tscn"
    argv = [
        args.godot,
        "--path",
        str(project),
        "--windowed",
        "--resolution",
        "1280x800",
        "--log-file",
        str(folder / "engine.log"),
        "--script",
        SCRIPT,
        "--",
        scene,
    ]
    deadline = time.monotonic() + args.warmup + args.duration + CASE_SLACK_SECONDS
    memory = []
    with (folder / "stdout.log").open("wb") as stdout, (
        folder / "stderr.log"
    ).open("wb") as stderr:
        child = subprocess.Popen(argv, cwd=project, stdout=stdout, stderr=stderr, env=env)
        started = time.monotonic()
        while child.poll() is None and time.monotonic() < deadline:
            sample = resident(child)
            if sample:
                memory.append([round(time.monotonic() - started, 3), *sample])
            time.sleep(1.0)
        timed_out = child.poll() is None
        if timed_out:
            child.terminate()
            try:
                child.wait(timeout=CLEANUP_SECONDS)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=CLEANUP_SECONDS)
    log_text = "".join(
        (folder / name).read_text(errors="replace")
        for name in ["stdout.log", "stderr.log", "engine.log"]
        if (folder / name).exists()
    )
    diagnostics = [line for line in log_text.splitlines() if DIAGNOSTIC.search(line)]
    result = json.loads((folder / "result.json").read_text()) if (
        folder / "result.json"
    ).exists() else None
    frames = summarize_frames(folder / "frames.f64", args.warmup) if (
        folder / "frames.f64"
    ).exists() else None
    rss = [row[1] for row in memory]
    peak = [row[2] for row in memory if len(row) > 2 and row[2] is not None]
    record = {
        "variant": variant,
        "repeat": repeat,
        "argv": argv,
        "exit": child.returncode,
        "timed_out": timed_out,
        "diagnostics": diagnostics,
        "result": result,
        "frames": frames,
        "resident_bytes": {
            "samples": len(rss),
            "p50": percentile(rss, 0.5),
            "p95": percentile(rss, 0.95),
            "max": max(rss) if rss else None,
            "peak_working_set": max(peak) if peak else None,
        },
    }
    record["ok"] = (
        child.returncode == 0
        and not timed_out
        and not diagnostics
        and result is not None
        and frames is not None
        and frames["frames"] > 0
    )
    record["stop_reasons"] = stop_reasons(record)
    save(folder / "memory.json", memory)
    save(folder / "case.json", record)
    return record


def validate_args(parser, args):
    """Reject unsafe durations, duplicate/out-of-order variants, and repository output."""
    if args.godot is None:
        parser.error("godot not found on PATH; pass --godot")
    if not (0 < args.duration <= 30 and 0 <= args.warmup <= 10 and args.repeats == 2):
        parser.error("duration must be 0..30 s, warmup 0..10 s, and repeats exactly 2")
    if args.variants != sorted(set(args.variants), key=VARIANTS.index):
        parser.error("variants must be unique and ordered from 6 toward 384")
    output = (args.output or Path(tempfile.mkdtemp(prefix="s07-env-"))).resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("output must be a fresh empty directory")
    return output


def main():
    """Import once, measure variants in order, and stop growth at the first failed limit."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--godot", default=shutil.which("godot"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--warmup", type=float, default=10.0)
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--variants", nargs="+", type=int, choices=VARIANTS, default=VARIANTS)
    args = parser.parse_args()
    output = validate_args(parser, args)
    print(f"S07 environment evidence: {output}", flush=True)
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
        "processor": platform.processor(),
        "duration_s": args.duration,
        "warmup_s": args.warmup,
        "repeats": args.repeats,
        "variants_requested": args.variants,
        "cases": [],
    }
    if version != PIN:
        summary["failure"] = f"expected {PIN}, got {version}"
    elif dirty:
        summary["failure"] = "copied inputs or runner/authoring tool are dirty"
    else:
        project = stage(output, args.variants)
        with (output / "import.log").open("wb") as log:
            import_code = subprocess.run(
                [args.godot, "--headless", "--editor", "--path", str(project),
                 "--import", "--quit"],
                stdout=log,
                stderr=subprocess.STDOUT,
                env=environment(output / "import-user"),
                timeout=120,
            ).returncode
        import_diagnostics = [
            line for line in (output / "import.log").read_text(errors="replace").splitlines()
            if DIAGNOSTIC.search(line)
        ]
        summary["import"] = {"exit": import_code, "diagnostics": import_diagnostics}
        if import_code != 0 or import_diagnostics:
            summary["failure"] = "import failed or reported diagnostics"
        else:
            for variant in args.variants:
                variant_stopped = False
                for repeat in range(1, args.repeats + 1):
                    record = run_case(args, project, output, variant, repeat)
                    summary["cases"].append(record)
                    save(output / "summary.json", summary)
                    if record["stop_reasons"]:
                        variant_stopped = True
                        if not record["ok"]:
                            summary["failure"] = f"case city-{variant}-repeat-{repeat} failed"
                        break
                if variant_stopped:
                    summary["stopped_at_variant"] = variant
                    break
            summary["ok"] = bool(summary["cases"]) and not summary.get("failure")
    save(output / "summary.json", summary)
    print(json.dumps({"ok": summary["ok"], "failure": summary.get("failure"),
                      "stopped_at_variant": summary.get("stopped_at_variant")}))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
