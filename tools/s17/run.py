#!/usr/bin/env python3
"""Stage and measure the full-cap S17 integrated host-tick composition."""

import argparse
import csv
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
sys.path.insert(0, str(ROOT / "tools"))
from script_checks import DIAGNOSTIC, PIN, environment  # noqa: E402

DEFAULT_SEEDS = (171, 272, 373)


def external_timeout():
    """Resolve GNU timeout rather than Windows' unrelated interactive utility."""
    if os.name == "nt":
        git = shutil.which("git")
        if git:
            candidate = Path(git).resolve().parents[1] / "usr/bin/timeout.exe"
            if candidate.is_file():
                return str(candidate)
    command = shutil.which("timeout")
    if not command:
        raise RuntimeError("GNU timeout is required to run Godot")
    return command


TIMEOUT = external_timeout()
SUBSYSTEMS = (
    "pedestrians",
    "traffic",
    "combat",
    "explosions",
    "snapshot_encode",
    "snapshot_encode_production_schedule",
    "total",
    "total_production_schedule",
)


def godot_command(godot, timeout_seconds, arguments):
    """Wrap every engine invocation in the external deadline required by the lane."""
    return [TIMEOUT, str(timeout_seconds), godot, *arguments]


def pinned_engine_version(godot):
    """Read and verify the engine version through a bounded Godot invocation."""
    result = subprocess.run(
        godot_command(godot, 30, ["--version"]),
        capture_output=True,
        text=True,
        timeout=35,
        check=True,
    )
    version = result.stdout.strip()
    if version != PIN:
        raise RuntimeError(f"expected pinned engine {PIN}; got {version}")
    return version


def process_count():
    """Count Godot processes without touching processes owned by other lanes."""
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
    """Read one bounded CPU-load snapshot with its platform-specific source."""
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


def command_text(command):
    """Return bounded command output without turning identity gaps into run failures."""
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() or None


def machine_identity():
    """Capture stable host CPU and OS identity before any measured child starts."""
    cpu_model = platform.processor() or None
    os_details = None
    if os.name == "nt":
        cpu_model = command_text(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-CimInstance Win32_Processor | Select-Object -First 1).Name",
            ]
        ) or cpu_model
        os_details = command_text(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "$o=Get-CimInstance Win32_OperatingSystem; "
                '"$($o.Caption) version $($o.Version) build $($o.BuildNumber)"',
            ]
        )
    return {
        "cpu_model": cpu_model,
        "logical_cpu_count": os.cpu_count(),
        "os": os_details or platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
    }


def telemetry_snapshot():
    """Capture concurrent engine count and CPU load outside the measured window."""
    return {"godot_processes": process_count(), "cpu_load": cpu_load()}


def stage_project(project):
    """Copy S17 and its read-only fixture dependencies into an addon-free project."""
    fixture_root = project / "tests/fixtures"
    for fixture in ("s02", "s03", "s04", "s05", "s06", "s09", "s10", "s11", "s12", "s17"):
        shutil.copytree(ROOT / "tests/fixtures" / fixture, fixture_root / fixture)
    models = project / "art/models/spikes"
    models.mkdir(parents=True)
    for prefix in ("s02_", "s04_", "s06_"):
        for source in (ROOT / "art/models/spikes").glob(f"{prefix}*"):
            if source.is_file():
                shutil.copy2(source, models / source.name)
    settings = (ROOT / "project.godot").read_text()
    for section in ("autoload", "editor_plugins"):
        settings = re.sub(rf"(?ms)^\[{section}\]\n.*?(?=^\[|\Z)", "", settings)
    settings = re.sub(r"^(config/icon|run/main_scene)=.*\n", "", settings, flags=re.MULTILINE)
    (project / "project.godot").write_text(settings)


def checked_process(command, log, engine_log, env, timeout_seconds, observe=False):
    """Run one owned child with bounded cleanup and only out-of-window telemetry."""
    before = telemetry_snapshot() if observe else None
    with log.open("w") as output:
        child = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT, env=env)
        startup_warmup = None
        if observe:
            time.sleep(0.1)
            startup_warmup = telemetry_snapshot()
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
        "telemetry": {
            "before": before,
            "startup_or_warmup": startup_warmup,
            "after": after,
        }
        if observe
        else None,
    }


def percentile(samples, fraction):
    """Return one nearest-rank percentile from finite integer microsecond samples."""
    ordered = sorted(samples)
    index = max(0, min(len(ordered) - 1, int(len(ordered) * fraction + 0.999999) - 1))
    return ordered[index]


def distribution(samples):
    """Summarize complete pooled microsecond samples in milliseconds."""
    return {
        "count": len(samples),
        "median": percentile(samples, 0.50) / 1000.0,
        "p95": percentile(samples, 0.95) / 1000.0,
        "p99": percentile(samples, 0.99) / 1000.0,
        "worst": percentile(samples, 1.0) / 1000.0,
    }


def aggregate(receipts):
    """Pool equal-duration seed samples and evaluate both host-tick cases."""
    timing = {}
    for subsystem in SUBSYSTEMS:
        samples = []
        for receipt in receipts:
            samples.extend(receipt["timing_usec_samples"][subsystem])
        timing[subsystem] = distribution(samples)
    timer_samples = []
    for receipt in receipts:
        timer_samples.extend(receipt["empty_timer_usec_samples"])
    return {
        "timing_ms": timing,
        "empty_timer_baseline_ms": distribution(timer_samples),
        "budget": {
            "total_p95_limit_ms": 4.0,
            "total_p99_limit_ms": 8.0,
            "conservative_total_p95_pass": timing["total"]["p95"] <= 4.0,
            "conservative_total_p99_pass": timing["total"]["p99"] <= 8.0,
            "production_schedule_total_p95_pass": (
                timing["total_production_schedule"]["p95"] <= 4.0
            ),
            "production_schedule_total_p99_pass": (
                timing["total_production_schedule"]["p99"] <= 8.0
            ),
            "traffic_audit_share_ms": 1.5,
            "traffic_audit_share_pass": timing["traffic"]["p95"] <= 1.5,
            "traffic_s09_share_ms": 2.0,
            "traffic_s09_share_pass": timing["traffic"]["p95"] <= 2.0,
            "pedestrian_share_ms": 1.0,
            "pedestrian_share_pass": timing["pedestrians"]["p95"] <= 1.0,
        },
    }


def compact_receipt(receipt, telemetry):
    """Retain outcomes and summaries in aggregate JSON while raw samples stay per seed."""
    compact = {
        key: value
        for key, value in receipt.items()
        if key not in ("timing_usec_samples", "empty_timer_usec_samples")
    }
    compact["contention"] = telemetry
    warmup = telemetry["startup_or_warmup"] if telemetry else None
    count = warmup["godot_processes"] if warmup else None
    compact["timing_label"] = (
        "contended upper bound" if count is None or count > 1 else "quiet candidate"
    )
    return compact


def main():
    """Stage, import, execute three ten-minute seeds and write aggregate JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
    args = parser.parse_args()
    if len(args.seeds) < 3:
        parser.error("at least three seeds are required")
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    if output.exists() and any(output.iterdir()):
        parser.error("output must be absent or empty")
    output.mkdir(parents=True, exist_ok=True)
    print(f"S17 evidence: {output}", flush=True)

    machine = machine_identity()
    version = pinned_engine_version(args.godot)
    project = output / "project"
    project.mkdir()
    stage_project(project)
    env = environment(output / "user")
    base_arguments = ["--headless", "--path", str(project)]
    import_engine = output / "import.engine.log"
    import_command = godot_command(
        args.godot,
        120,
        base_arguments
        + ["--editor", "--import", "--quit", "--log-file", str(import_engine)],
    )
    import_result = checked_process(
        import_command,
        output / "import.log",
        import_engine,
        env,
        130,
    )

    receipts = []
    runs = []
    commands = []
    failures = []
    if not import_result["ok"]:
        failures.append("isolated import failed")
    else:
        for seed in args.seeds:
            receipt_path = output / f"seed-{seed}.json"
            engine_log = output / f"seed-{seed}.engine.log"
            command = godot_command(
                args.godot,
                1400,
                base_arguments
                + [
                    "--script",
                    "res://tests/fixtures/s17/run.gd",
                    "--log-file",
                    str(engine_log),
                    "--",
                    "--seed",
                    str(seed),
                    "--output",
                    str(receipt_path),
                ],
            )
            commands.append(command)
            process_result = checked_process(
                command,
                output / f"seed-{seed}.log",
                engine_log,
                env,
                1410,
                observe=True,
            )
            receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
            if receipt:
                receipts.append(receipt)
                runs.append(compact_receipt(receipt, process_result["telemetry"]))
                failures.extend(f"seed {seed}: {item}" for item in receipt["failures"])
            if not process_result["ok"] or receipt is None:
                failures.append(f"seed {seed} process or receipt failed")

    if len(receipts) != len(args.seeds):
        failures.append(f"expected {len(args.seeds)} receipts, got {len(receipts)}")
    aggregate_result = aggregate(receipts) if len(receipts) == len(args.seeds) else {}
    result = {
        "engine": version,
        "machine": machine,
        "seeds": list(args.seeds),
        "warmup_ticks_per_seed": 3_600,
        "measured_ticks_per_seed": 36_000,
        "warmup_minutes_per_seed": 1,
        "measured_minutes_per_seed": 10,
        "import": import_result,
        "commands": commands,
        "runs": runs,
        "aggregate": aggregate_result,
        "timing_interpretation": (
            "Rows marked contended upper bound had another Godot process observed before "
            "launch or during startup/warmup. No contention subprocess runs in the measured "
            "window. CPU-load snapshots are instantaneous and do not prove exclusive use."
        ),
        "failures": failures,
    }
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"runs": len(runs), "failures": failures, "aggregate": aggregate_result}))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
