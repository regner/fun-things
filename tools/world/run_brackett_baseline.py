#!/usr/bin/env python3
"""Run the capped Brackett capacity baseline and summarize retained frame rows."""

from array import array
import argparse
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = "res://tests/performance/world/brackett_capacity.gd"
DIAGNOSTIC = re.compile(r"(?:SCRIPT ERROR:|ERROR:|WARNING:)")
DEADLINE_SECONDS = 120.0


def godot_command(godot, output):
    """Build the capped graphical command without a shell or shared process mutation."""
    return [
        godot,
        "--path",
        os.fspath(ROOT),
        "--max-fps",
        "60",
        "--resolution",
        "1280x800",
        "--log-file",
        os.fspath(output / "engine.log"),
        "--script",
        SCRIPT,
    ]


def working_set_bytes(pid):
    """Return one child working-set sample using only platform standard facilities."""
    if os.name == "nt":
        return _windows_working_set_bytes(pid)
    status = Path(f"/proc/{pid}/status")
    if status.is_file():
        for line in status.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) * 1024
    return 0


def _windows_working_set_bytes(pid):
    """Read PROCESS_MEMORY_COUNTERS_EX for the one runner-owned Windows child."""
    class ProcessMemoryCountersEx(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
            ("PrivateUsage", ctypes.c_size_t),
        ]

    process = ctypes.windll.kernel32.OpenProcess(0x0410, False, pid)
    if not process:
        return 0
    counters = ProcessMemoryCountersEx()
    counters.cb = ctypes.sizeof(counters)
    try:
        ok = ctypes.windll.psapi.GetProcessMemoryInfo(
            process, ctypes.byref(counters), counters.cb
        )
        return int(counters.WorkingSetSize) if ok else 0
    finally:
        ctypes.windll.kernel32.CloseHandle(process)


def count_godot_processes():
    """Count unrelated Godot processes for an explicit contention label."""
    try:
        if os.name == "nt":
            result = subprocess.run(
                ["tasklist", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            return sum(
                1
                for line in result.stdout.splitlines()
                if line.lower().startswith('"godot')
            )
        result = subprocess.run(
            ["ps", "-eo", "comm="],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return sum(
            1 for line in result.stdout.splitlines() if line.strip().lower().startswith("godot")
        )
    except (OSError, subprocess.SubprocessError):
        return -1


def percentile(values, percentile_value):
    """Return the nearest-rank percentile used by the existing capacity records."""
    ordered = sorted(values)
    if not ordered:
        return 0.0
    rank = max(1, (len(ordered) * percentile_value + 99) // 100)
    return float(ordered[min(len(ordered), rank) - 1])


def summarize_frames(output):
    """Decode the self-described float rows and write compact review statistics."""
    result = json.loads((output / "result.json").read_text(encoding="utf-8"))
    values = array("d")
    values.frombytes((output / "frames.f64").read_bytes())
    fields = result["fields"]
    width = result["sample_fields"]
    rows = [values[index : index + width] for index in range(0, len(values), width)]
    columns = {name: [row[index] for row in rows] for index, name in enumerate(fields)}
    summary = {
        "sample_count": len(rows),
        "frame_interval_ms": _distribution(columns["frame_interval_ms"]),
        "render_cpu_ms": _distribution(columns["render_cpu_ms"]),
        "render_gpu_ms": _distribution(columns["render_gpu_ms"]),
        "process_ms": _distribution(columns["process_ms"]),
        "physics_ms": _distribution(columns["physics_ms"]),
        "draw_calls": _distribution(columns["draw_calls"]),
        "objects": _distribution(columns["objects"]),
        "video_mem_bytes": _distribution(columns["video_mem_bytes"]),
        "node_count": _distribution(columns["node_count"]),
    }
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def _distribution(values):
    """Build the common median/p95/p99/max report for one sampled field."""
    return {
        "median": percentile(values, 50),
        "p95": percentile(values, 95),
        "p99": percentile(values, 99),
        "max": max(values, default=0.0),
    }


def isolated_environment(output):
    """Give the child private writable Godot and XDG data roots."""
    environment = os.environ.copy()
    user_root = output / "user"
    for name, child in {
        "APPDATA": "appdata",
        "LOCALAPPDATA": "localappdata",
        "XDG_DATA_HOME": "xdg-data",
        "XDG_CONFIG_HOME": "xdg-config",
        "XDG_CACHE_HOME": "xdg-cache",
    }.items():
        path = user_root / child
        path.mkdir(parents=True, exist_ok=True)
        environment[name] = os.fspath(path)
    environment["BRACKETT_BASELINE_OUTPUT"] = os.fspath(output)
    return environment


def run_baseline(godot, output):
    """Run one owned child to a monotonic deadline while sampling its working set."""
    before = count_godot_processes()
    command = godot_command(godot, output)
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    started = time.monotonic()
    peak_working_set = 0
    with (output / "stdout.log").open("w", encoding="utf-8") as stdout:
        child = subprocess.Popen(
            command,
            cwd=ROOT,
            env=isolated_environment(output),
            stdout=stdout,
            stderr=subprocess.STDOUT,
            creationflags=creationflags,
        )
        try:
            while child.poll() is None:
                peak_working_set = max(peak_working_set, working_set_bytes(child.pid))
                if time.monotonic() - started > DEADLINE_SECONDS:
                    raise subprocess.TimeoutExpired(command, DEADLINE_SECONDS)
                time.sleep(0.1)
        except subprocess.TimeoutExpired:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=5)
            raise
    after = count_godot_processes()
    elapsed = time.monotonic() - started
    host = {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "command": command,
        "returncode": child.returncode,
        "wall_seconds": elapsed,
        "peak_working_set_bytes": peak_working_set,
        "godot_processes_before": before,
        "godot_processes_after": after,
        "contention": "contended workstation; concurrent Godot process counts recorded",
    }
    (output / "host.json").write_text(
        json.dumps(host, indent=2) + "\n", encoding="utf-8"
    )
    return child.returncode


def main():
    """Validate arguments, run the baseline, reject diagnostics, and summarize evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot") or "godot")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    if output.exists() and any(output.iterdir()):
        parser.error("output must be a fresh empty directory")
    output.mkdir(parents=True, exist_ok=True)

    try:
        returncode = run_baseline(args.godot, output)
    except subprocess.TimeoutExpired:
        print("Brackett baseline exceeded its 120 second deadline", file=sys.stderr)
        return 1
    combined = ""
    for name in ("stdout.log", "engine.log"):
        path = output / name
        if path.is_file():
            combined += path.read_text(encoding="utf-8", errors="replace")
    if returncode != 0 or DIAGNOSTIC.search(combined):
        print(f"Brackett baseline failed: returncode={returncode}", file=sys.stderr)
        return 1
    required = (output / "result.json", output / "frames.f64")
    if not all(path.is_file() for path in required):
        print("Brackett baseline did not produce required evidence", file=sys.stderr)
        return 1

    summary = summarize_frames(output)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
