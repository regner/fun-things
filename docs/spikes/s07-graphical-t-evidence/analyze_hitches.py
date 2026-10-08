#!/usr/bin/env python3
"""Reproduce capped-run hitch attribution from retained compressed raw samples."""
import array
import gzip
import json
import math
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parent / "s07g-capped"
FRAME_WIDTH = 10
WARMUP_SECONDS = 60.0
HITCH_THRESHOLD_MS = 33.4


def percentile(values, quantile):
    """Return the nearest-rank percentile used by the graphical runner."""
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(quantile * len(ordered)) - 1))
    return ordered[index]


def inside(value, windows):
    """Report whether a timestamp falls in any inclusive window."""
    return any(start <= value <= end for start, end in windows)


def read_frames(path):
    """Decode retained little-endian native-double rows from a gzip member."""
    raw = array.array("d")
    raw.frombytes(gzip.decompress(path.read_bytes()))
    if len(raw) % FRAME_WIDTH:
        raise ValueError(f"partial frame row in {path}")
    return [raw[index:index + FRAME_WIDTH]
            for index in range(0, len(raw), FRAME_WIDTH)]


def read_traversals(path):
    """Decode retained traversal JSON lines from a gzip member."""
    return [json.loads(line) for line in gzip.decompress(path.read_bytes()).splitlines()]


def analyze(case):
    """Analyze one retained case using only its two compressed raw inputs."""
    folder = EVIDENCE / case
    frames = read_frames(folder / "frames.f64.gz")
    traversals = read_traversals(folder / "traversals.jsonl.gz")
    measured = [row for row in frames if row[0] >= WARMUP_SECONDS]
    hitches = [row for row in measured if row[1] > HITCH_THRESHOLD_MS]
    load_windows = [(row["load_start_seconds"], row["traversal_start_seconds"] + 0.1)
                    for row in traversals]
    teardown_windows = [(row["traversal_end_seconds"] - 0.05,
                         row["retired_seconds"] + 0.1) for row in traversals]
    traversal_windows = [(row["traversal_start_seconds"] + 0.1,
                          row["traversal_end_seconds"] - 0.05) for row in traversals]
    traversal_intervals = [row[1] for row in measured if inside(row[0], traversal_windows)]

    return {
        "case": case,
        "measured_frames": len(measured),
        "long_frames_over_33_4_ms": len(hitches),
        "long_frames_in_load_windows": sum(inside(row[0], load_windows) for row in hitches),
        "long_frames_in_teardown_windows": sum(
            inside(row[0], teardown_windows) for row in hitches
        ),
        "long_frames_in_load_or_teardown_windows": sum(
            inside(row[0], load_windows + teardown_windows) for row in hitches
        ),
        "traversal_only_frames": len(traversal_intervals),
        "traversal_only_interval_ms": {
            "p95": percentile(traversal_intervals, 0.95),
            "p99": percentile(traversal_intervals, 0.99),
            "max": max(traversal_intervals),
        },
    }


def main():
    """Print deterministic JSON for all three retained capped cases."""
    result = {
        "warmup_seconds": WARMUP_SECONDS,
        "hitch_threshold_ms": HITCH_THRESHOLD_MS,
        "load_window": "[load_start_seconds, traversal_start_seconds + 0.1]",
        "teardown_window": "[traversal_end_seconds - 0.05, retired_seconds + 0.1]",
        "traversal_only_window": (
            "[traversal_start_seconds + 0.1, traversal_end_seconds - 0.05]"
        ),
        "runs": [analyze(f"capped60-{index}") for index in (1, 2, 3)],
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
