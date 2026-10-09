#!/usr/bin/env python
"""Run the S14 audio cap/settings fixture headless and windowed three times each."""

from __future__ import annotations

import argparse
import hashlib
import json
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
from script_checks import DIAGNOSTIC, PIN, environment  # noqa: E402

SCENE = "res://tests/fixtures/s14/audio_test.tscn"
CASE_TIMEOUT_SECONDS = 20


def _save(path: Path, value: object) -> None:
    """Write stable JSON with LF endings."""
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def _fixture_inventory() -> list[Path]:
    """Return the one Git-owned file inventory used for staging and source binding."""
    output = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "tests/fixtures/s14"], cwd=ROOT
    )
    paths = [Path(value.decode("utf-8")) for value in output.split(b"\0") if value]
    if not paths:
        raise RuntimeError("Git returned no committed S14 fixture files")
    return sorted(paths)


def _stage(output: Path, inventory: list[Path]) -> Path:
    """Copy the committed S14 inventory into an addon-free external Godot project."""
    project = output / "project"
    for relative_path in inventory:
        target = project / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative_path, target)
    settings = (ROOT / "project.godot").read_text(encoding="utf-8")
    settings = re.sub(r"(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)", "", settings)
    settings = settings.replace('config/icon="res://icon.svg"\n', "")
    (project / "project.godot").write_text(settings, encoding="utf-8", newline="\n")
    return project


def _source_manifest(inventory: list[Path]) -> dict[str, str]:
    """Hash exactly the committed fixture inventory copied into the staged project."""
    return {
        path.as_posix(): hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in inventory
    }


def _godot_process_count() -> int | None:
    """Count other Godot processes immediately before a timed case."""
    try:
        if platform.system() == "Windows":
            text = subprocess.check_output(
                ["tasklist"], text=True, errors="replace", timeout=8
            )
            return sum("godot" in line.lower() for line in text.splitlines())
        text = subprocess.check_output(["ps", "-eo", "comm="], text=True, timeout=8)
        return sum("godot" in line.lower() for line in text.splitlines())
    except (OSError, subprocess.SubprocessError):
        return None


def _cpu_load_percent() -> float | None:
    """Sample total workstation CPU load without adding a Python dependency."""
    try:
        if platform.system() == "Windows":
            command = [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                "(Get-Counter '\\Processor(_Total)\\% Processor Time')."
                "CounterSamples.CookedValue",
            ]
            text = subprocess.check_output(command, text=True, timeout=10).strip()
            return round(float(text.replace(",", ".")), 3)
        first = Path("/proc/stat").read_text(encoding="utf-8").splitlines()[0].split()[1:]
        start = [int(value) for value in first]
        time.sleep(0.2)
        second = Path("/proc/stat").read_text(encoding="utf-8").splitlines()[0].split()[1:]
        end = [int(value) for value in second]
        total = sum(end) - sum(start)
        idle = (end[3] + end[4]) - (start[3] + start[4])
        return round(100.0 * (1.0 - idle / total), 3) if total else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def validate_receipt(receipt: dict) -> list[str]:
    """Return semantic failures from one fixture receipt."""
    failures = list(receipt.get("failures", []))
    if not receipt.get("success"):
        failures.append("fixture did not report success")
    peak = receipt.get("peak", {})
    caps = peak.get("caps", {})
    active = peak.get("active", {})
    expected_peak = {"engines": 8, "explosions": 8, "weapons": 6}
    if caps != expected_peak:
        failures.append("category caps differ from independent expectations")
    if active != expected_peak:
        failures.append("instantaneous peak voices differ from independent expectations")
    requests = peak.get("requests", {})
    expected = {
        "explosions_accepted": 8,
        "explosions_dropped": 16,
        "weapon_accepted": 6,
        "weapon_dropped": 6,
    }
    if any(requests.get(key) != value for key, value in expected.items()):
        failures.append("storm request accounting differs from independent expectations")
    settings = receipt.get("settings_roundtrip", {})
    if not settings.get("passed"):
        failures.append("settings roundtrip did not pass")
    if not settings.get("malformed_defaults", {}).get("passed"):
        failures.append("malformed settings did not retain safe defaults")
    return failures


def classify_diagnostics(diagnostics: list[str], receipt: dict | None) -> tuple[list[str], list[str]]:
    """Separate only the exact retained pinned-Dummy teardown observation."""
    exact_known = {
        "WARNING: 23 ObjectDB instances were leaked at exit (run with `--verbose` for details).",
        "ERROR: 7 resources still in use at exit (run with --verbose for details).",
    }
    if (
        not receipt
        or receipt.get("audio_driver") != "Dummy"
        or not exact_known.issubset(diagnostics)
    ):
        return [], diagnostics
    known = [line for line in diagnostics if line in exact_known]
    unexpected = [line for line in diagnostics if line not in exact_known]
    return known, unexpected


def _run_case(godot: str, project: Path, output: Path, mode: str, repeat: int) -> dict:
    """Run one bounded fixture process and retain its logs and receipt."""
    case_name = f"{mode}-{repeat}"
    folder = output / case_name
    folder.mkdir()
    receipt_path = folder / "receipt.json"
    argv = [godot]
    if mode == "headless":
        argv.append("--headless")
    else:
        argv.extend(["--windowed", "--resolution", "1280x800"])
    argv.extend(
        [
            "--path",
            str(project),
            "--log-file",
            str(folder / "engine.log"),
            SCENE,
            "--",
            f"--s14-output={receipt_path}",
            f"--s14-mode={mode}",
        ]
    )
    environment_before = {
        "godot_processes": _godot_process_count(),
        "cpu_load_percent": _cpu_load_percent(),
    }
    with (folder / "stdout.log").open("wb") as stdout:
        completed = subprocess.run(
            argv,
            cwd=project,
            stdout=stdout,
            stderr=subprocess.STDOUT,
            env=environment(folder / "user"),
            timeout=CASE_TIMEOUT_SECONDS,
            check=False,
        )
    logs = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in (folder / "stdout.log", folder / "engine.log")
        if path.exists()
    )
    all_diagnostics = [line for line in logs.splitlines() if DIAGNOSTIC.search(line)]
    receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.exists() else None
    semantic_failures = validate_receipt(receipt) if receipt else ["missing receipt"]
    known_diagnostics, diagnostics = classify_diagnostics(all_diagnostics, receipt)
    contended = environment_before["godot_processes"] not in (None, 0)
    record = {
        "name": case_name,
        "mode": mode,
        "repeat": repeat,
        "argv": argv,
        "exit": completed.returncode,
        "diagnostics": diagnostics,
        "known_pinned_dummy_teardown_diagnostics": known_diagnostics,
        "semantic_failures": semantic_failures,
        "environment_before": environment_before,
        "timing_label": "contended upper bound" if contended else "uncontended desktop sample",
        "receipt": receipt,
    }
    record["ok"] = completed.returncode == 0 and not diagnostics and not semantic_failures
    _save(folder / "case.json", record)
    return record


def _aggregate(cases: list[dict]) -> dict:
    """Report median and worst process monitor values for each execution mode."""
    result = {}
    for mode in ("headless", "windowed"):
        selected = [case for case in cases if case["mode"] == mode and case["receipt"]]
        medians = [case["receipt"]["performance"]["process_ms_median"] for case in selected]
        worsts = [case["receipt"]["performance"]["process_ms_worst"] for case in selected]
        latencies = [
            case["receipt"]["performance"]["audio_output_latency_ms_median"]
            for case in selected
        ]
        result[mode] = {
            "runs": len(selected),
            "process_ms_run_median": statistics.median(medians) if medians else None,
            "process_ms_worst": max(worsts) if worsts else None,
            "audio_output_latency_ms_run_median": (
                statistics.median(latencies) if latencies else None
            ),
            "note": "Process time is not an audio-mix CPU measurement.",
        }
    return result


def main() -> int:
    """Stage, import, and run three headless plus three capped-windowed repetitions."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--godot", default=shutil.which("godot"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--modes", nargs="+", choices=["headless", "windowed"],
                        default=["headless", "windowed"])
    args = parser.parse_args()
    if args.godot is None:
        parser.error("godot not found on PATH; pass --godot")
    if not 1 <= args.repeats <= 3:
        parser.error("repeats must be 1..3")
    output = (args.output or Path(tempfile.mkdtemp(prefix="s14-audio-"))).resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("output must be fresh and empty")
    print(f"S14 audio evidence: {output}", flush=True)

    version = subprocess.run(
        [args.godot, "--version"], capture_output=True, text=True, timeout=10, check=True
    ).stdout.strip()
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain", "--", "tests/fixtures/s14", "tools/s14"],
        cwd=ROOT,
        text=True,
    ).strip()
    inventory = _fixture_inventory()
    summary = {
        "ok": False,
        "engine": version,
        "revision": revision,
        "dirty_inputs": dirty,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "source_inventory": [path.as_posix() for path in inventory],
        "source_manifest": _source_manifest(inventory),
        "cases": [],
    }
    if version != PIN:
        summary["failure"] = f"expected {PIN}, got {version}"
    else:
        project = _stage(output, inventory)
        import_argv = [
            args.godot,
            "--headless",
            "--editor",
            "--path",
            str(project),
            "--import",
            "--quit",
        ]
        with (output / "import.log").open("wb") as log:
            import_result = subprocess.run(
                import_argv,
                stdout=log,
                stderr=subprocess.STDOUT,
                env=environment(output / "import-user"),
                timeout=60,
                check=False,
            )
        import_text = (output / "import.log").read_text(encoding="utf-8", errors="replace")
        import_diagnostics = [
            line for line in import_text.splitlines() if DIAGNOSTIC.search(line)
        ]
        summary["import"] = {
            "argv": import_argv,
            "exit": import_result.returncode,
            "diagnostics": import_diagnostics,
        }
        if import_result.returncode != 0 or import_diagnostics:
            summary["failure"] = "isolated import failed or reported diagnostics"
        else:
            for mode in args.modes:
                for repeat in range(1, args.repeats + 1):
                    case = _run_case(args.godot, project, output, mode, repeat)
                    summary["cases"].append(case)
                    _save(output / "summary.json", summary)
                    if not case["ok"]:
                        summary["failure"] = f"{case['name']} failed"
                        break
                if summary.get("failure"):
                    break
            summary["aggregate"] = _aggregate(summary["cases"])
            summary["ok"] = not summary.get("failure") and not dirty
            if dirty and not summary.get("failure"):
                summary["failure"] = "fixture/tool inputs were dirty; commit and rerun for binding"
    _save(output / "summary.json", summary)
    print(json.dumps({"ok": summary["ok"], "failure": summary.get("failure")}))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
