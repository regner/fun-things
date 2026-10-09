#!/usr/bin/env python3
"""Graphical T runs: the accepted S07 sustained driver plus per-frame telemetry, windowed.

Stages the saved S02/S03/S04/S06/S07 fixtures and models into a fresh external project,
imports once, then runs capped60 repeats sequentially with one bounded deadline per case.
The former uncapped mode is withdrawn after retained DXGI device-removal failures on this laptop.
Samples OS resident memory of the owned child on Windows.
Records frame-interval, render CPU/GPU, process/physics, draw-call, primitive, object and
video-memory percentiles separately for warmup and measured time. See
docs/spikes/s07-graphical-t.md.
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
from measurement_identity import measurement_identity  # noqa: E402
from script_checks import DIAGNOSTIC, PIN, environment  # noqa: E402
from window_safety import (capped_window_arguments, require_capped_modes,
                           require_capped_window)  # noqa: E402

FIXTURES = ["s02", "s03", "s04", "s06", "s07_driver", "s07_graphical"]
MODELS = ["s02_*", "s04_*", "s06_*"]
SCRIPT = "res://tests/fixtures/s07_graphical/run.gd"
FIELDS = ["elapsed_s", "frame_interval_ms", "render_cpu_ms", "render_gpu_ms", "process_ms",
          "physics_ms", "draw_calls", "primitives", "objects", "video_mem_bytes"]
CLEANUP_SECONDS = 5
CASE_SLACK_SECONDS = 90
STAGED_INPUTS = ["tests", "art", "project.godot", "tools/s07_graphical"]


def save(path, value):
    """Write strict JSON with LF endings."""
    path.write_text(json.dumps(value, indent=2) + "\n", newline="\n")


def dirty_inputs():
    """Return staged-input changes that would break revision binding."""
    return subprocess.check_output(
        ["git", "status", "--porcelain", "--", *STAGED_INPUTS], cwd=ROOT, text=True
    ).strip()


def identity_sources():
    """Return runner/helper and exact staged-input sources that own this measurement."""
    sources = ["tools/s07_graphical/run.py", "tools/measurement_identity.py",
               "tools/window_safety.py", "tools/script_checks.py", "project.godot"]
    sources.extend(f"tests/fixtures/{fixture}" for fixture in FIXTURES)
    for pattern in MODELS:
        sources.extend(path.relative_to(ROOT).as_posix()
                       for path in (ROOT / "art/models/spikes").glob(pattern))
    return sources


def stage(output):
    """Copy committed runtime fixtures and models without addons, editor plugins or sources."""
    project = output / "project"
    for fixture in FIXTURES:
        shutil.copytree(ROOT / "tests/fixtures" / fixture, project / "tests/fixtures" / fixture,
                        ignore=shutil.ignore_patterns("editor_harness.tscn"))
    models = project / "art/models/spikes"
    models.mkdir(parents=True)
    for pattern in MODELS:
        for path in (ROOT / "art/models/spikes").glob(pattern):
            shutil.copy2(path, models / path.name)
    settings = (ROOT / "project.godot").read_text()
    settings = re.sub(r"(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)", "", settings)
    settings = settings.replace('config/icon="res://icon.svg"\n', "")
    (project / "project.godot").write_text(settings, newline="\n")
    return project


class Memory(ctypes.Structure):
    """PROCESS_MEMORY_COUNTERS from psapi."""
    _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]


def resident(child):
    """Return (working set, peak working set) bytes for an owned child, or None."""
    if platform.system() != "Windows":
        try:
            for line in Path(f"/proc/{child.pid}/status").read_text().splitlines():
                if line.startswith("VmRSS:"):
                    value = int(line.split()[1]) * 1024
                    return value, None
        except OSError:
            return None
        return None
    counters = Memory()
    counters.cb = ctypes.sizeof(Memory)
    if ctypes.windll.psapi.GetProcessMemoryInfo(int(child._handle), ctypes.byref(counters),
                                                counters.cb):
        return counters.WorkingSetSize, counters.PeakWorkingSetSize
    return None


def percentile(values, q):
    """Nearest-rank percentile; None for no samples."""
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, math.ceil(q * len(ordered)) - 1))]


def summarize(project, warmup):
    """Split frame rows into warmup/measured phases and report distribution statistics."""
    raw = array.array("d")
    raw.frombytes((project / "frames.f64").read_bytes())
    rows = [raw[i:i + len(FIELDS)] for i in range(0, len(raw), len(FIELDS))]
    phases = {"warmup": [r for r in rows if r[0] < warmup],
              "measured": [r for r in rows if r[0] >= warmup]}
    summary = {}
    for phase, selected in phases.items():
        stats = {"frames": len(selected)}
        if selected:
            stats["span_s"] = selected[-1][0] - selected[0][0]
        for index, field in enumerate(FIELDS[1:], start=1):
            values = [r[index] for r in selected]
            stats[field] = {"p50": percentile(values, .5), "p95": percentile(values, .95),
                            "p99": percentile(values, .99),
                            "max": max(values) if values else None}
        intervals = [r[1] for r in selected]
        stats["hitches_over_33ms"] = sum(value > 33.4 for value in intervals)
        stats["mean_fps"] = (len(intervals) / (sum(intervals) / 1000)) if intervals else None
        summary[phase] = stats
    return summary


def run_case(args, project, output, name, mode):
    """Run one bounded windowed case and retain streams, result, telemetry and memory."""
    folder = output / name
    folder.mkdir()
    for leftover in ["frames.f64", "frames.json", "result.json", "traversals.jsonl"]:
        (project / leftover).unlink(missing_ok=True)
    env = environment(folder / "user")
    env.update(S07_GRAPHICAL_MODE=mode, S07_GRAPHICAL_WARMUP=str(args.warmup))
    argv = [args.godot, "--path", str(project), "--windowed",
            *capped_window_arguments(), "--resolution", "1280x800", "--log-file",
            str(folder / "engine.log"), "--script", SCRIPT, "--", str(args.duration)]
    require_capped_window(argv)
    deadline = time.monotonic() + args.warmup + args.duration + CASE_SLACK_SECONDS
    memory = []
    with (folder / "stdout.log").open("wb") as out, (folder / "stderr.log").open("wb") as err:
        child = subprocess.Popen(argv, cwd=project, stdout=out, stderr=err, env=env)
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
    text = "".join((folder / n).read_text(errors="replace")
                   for n in ["stdout.log", "stderr.log", "engine.log"] if (folder / n).exists())
    diagnostics = [line for line in text.splitlines() if DIAGNOSTIC.search(line)]
    for name_out in ["result.json", "frames.json", "traversals.jsonl", "frames.f64"]:
        if (project / name_out).exists():
            shutil.copy2(project / name_out, folder / name_out)
    driver = json.loads((folder / "result.json").read_text()) if (
        folder / "result.json").exists() else None
    meta = json.loads((folder / "frames.json").read_text()) if (
        folder / "frames.json").exists() else None
    stats = summarize(folder, args.warmup) if (folder / "frames.f64").exists() else None
    rss = [row[1] for row in memory]
    record = {"name": name, "mode": mode, "argv": argv, "exit": child.returncode,
              "timed_out": timed_out, "diagnostics": diagnostics, "driver": driver,
              "meta": meta, "frames": stats,
              "resident_bytes": {"samples": len(rss), "p50": percentile(rss, .5),
                                 "max": max(rss) if rss else None,
                                 "peak_working_set": max((r[2] for r in memory if r[2]),
                                                         default=None)}}
    save(folder / "memory.json", memory)
    record["ok"] = (child.returncode == 0 and not timed_out and not diagnostics and
                    driver is not None and not driver["failures"] and stats is not None)
    save(folder / "case.json", record)
    return record


def main():
    """Import once and run the requested cases sequentially; never retry a failed case."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--godot", default=shutil.which("godot"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--duration", type=float, default=600.0)
    parser.add_argument("--warmup", type=float, default=60.0)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--modes", nargs="+", choices=["capped60"], default=["capped60"])
    args = parser.parse_args()
    if args.godot is None:
        parser.error("godot not found on PATH; pass --godot")
    try:
        require_capped_modes(args.modes)
    except ValueError as error:
        parser.error(str(error))
    if not (0 < args.duration <= 600 and 0 <= args.warmup <= 120 and 1 <= args.repeats <= 3):
        parser.error("duration 0..600 s, warmup 0..120 s, repeats 1..3")
    output = (args.output or Path(tempfile.mkdtemp(prefix="s07-graphical-"))).resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("output must be a fresh empty directory")
    print(f"S07 graphical evidence: {output}", flush=True)
    version = subprocess.run([args.godot, "--version"], capture_output=True, text=True,
                             timeout=10, check=True).stdout.strip()
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = dirty_inputs()
    summary = {"ok": False, "engine": version, "revision": revision, "dirty_inputs": dirty,
               "platform": platform.platform(), "processor": platform.processor(),
               "duration_s": args.duration, "warmup_s": args.warmup, "cases": [],
               "measurement_identity": measurement_identity(
                   ROOT, identity_sources(), {**vars(args), "output": output})}
    if version != PIN:
        summary["failure"] = f"expected {PIN}, got {version}"
    else:
        project = stage(output)
        with (output / "import.log").open("wb") as log:
            code = subprocess.run([args.godot, "--headless", "--editor", "--path", str(project),
                                   "--import", "--quit"], stdout=log, stderr=subprocess.STDOUT,
                                  env=environment(output / "import-user"), timeout=120).returncode
        problems = [line for line in (output / "import.log").read_text(errors="replace")
                    .splitlines() if DIAGNOSTIC.search(line)]
        summary["import"] = {"exit": code, "diagnostics": problems}
        if code == 0 and not problems:
            for repeat in range(1, args.repeats + 1):
                for mode in args.modes:
                    record = run_case(args, project, output, f"{mode}-{repeat}", mode)
                    summary["cases"].append({k: record[k] for k in
                                             ["name", "ok", "exit", "frames", "resident_bytes"]})
                    save(output / "summary.json", summary)
                    if not record["ok"]:
                        summary["failure"] = f"case {record['name']} failed; stopping"
                        break
                if summary.get("failure"):
                    break
            # Staging copies the working tree; only clean inputs bind evidence to the revision.
            summary["ok"] = not summary.get("failure") and bool(summary["cases"]) and not dirty
        else:
            summary["failure"] = "import failed or reported diagnostics"
    save(output / "summary.json", summary)
    print(json.dumps({"ok": summary["ok"], "failure": summary.get("failure")}))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
