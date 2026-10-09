#!/usr/bin/env python3
"""Run bounded graphical and headless S13 crowd measurements with the pinned engine."""
import argparse
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
from window_safety import capped_window_arguments, require_capped_window  # noqa: E402

FIXTURE = ROOT / "tests/fixtures/s13"
MODEL = ROOT / "art/models/characters"
MATERIAL_NAMES = ["s13_ivory.tres", "s13_coral.tres", "s13_cobalt.tres"]
SCENE = "res://tests/fixtures/s13/crowd.tscn"
CLEANUP_SECONDS = 5
QUIET_SETTLE_SECONDS = 1.0


def save(path, value):
    """Write stable human-readable JSON with LF endings."""
    path.write_text(json.dumps(value, indent=2) + "\n", newline="\n")


def percentile(values, quantile):
    """Return one nearest-rank percentile, ignoring unavailable monitor samples."""
    available = [value for value in values if value is not None]
    if not available:
        return None
    ordered = sorted(available)
    index = min(len(ordered) - 1, max(0, math.ceil(quantile * len(ordered)) - 1))
    return ordered[index]


def distribution(values):
    """Summarize one telemetry series without hiding worst frames."""
    return {
        "samples": len(values),
        "median": percentile(values, 0.5),
        "p95": percentile(values, 0.95),
        "p99": percentile(values, 0.99),
        "worst": max(values) if values else None,
    }


def system_load():
    """Sample Godot processes and Windows CPU load only after a measured case exits."""
    godot_count = None
    tasklist_error = None
    try:
        result = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=5, check=True)
        godot_count = sum("godot" in line.lower() for line in result.stdout.splitlines())
    except (OSError, subprocess.SubprocessError) as error:
        tasklist_error = repr(error)
    cpu_percent = None
    cpu_error = None
    command = [
        "powershell", "-NoProfile", "-Command",
        "(Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average).Average",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=8, check=True)
        cpu_percent = float(result.stdout.strip())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        cpu_error = repr(error)
    return {
        "godot_processes_after_case": godot_count,
        "cpu_load_percent_after_case": cpu_percent,
        "tasklist_error": tasklist_error,
        "cpu_error": cpu_error,
    }


def identity_sources():
    """Return measurement owner, helper, and staged fixture/model input paths."""
    return ["tools/s13/run.py", "tools/measurement_identity.py", "tools/window_safety.py",
            "tools/script_checks.py", "tests/fixtures/s13", "art/models/characters",
            *(f"art/materials/{name}" for name in MATERIAL_NAMES), "project.godot"]


def stage(output):
    """Stage only the saved S13 runtime closure into an addon-free external project."""
    project = output / "project"
    shutil.copytree(FIXTURE, project / "tests/fixtures/s13")
    shutil.copytree(MODEL, project / "art/models/characters")
    materials = project / "art/materials"
    materials.mkdir(parents=True)
    for name in MATERIAL_NAMES:
        shutil.copy2(ROOT / "art/materials" / name, materials / name)
    settings = (ROOT / "project.godot").read_text()
    settings = re.sub(r"(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)", "", settings)
    settings = settings.replace('config/icon="res://icon.svg"\n', "")
    (project / "project.godot").write_text(settings, newline="\n")
    return project


def stop(child):
    """Terminate and reap only one child created by this runner."""
    if child.poll() is not None:
        return
    child.terminate()
    try:
        child.wait(timeout=CLEANUP_SECONDS)
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait(timeout=CLEANUP_SECONDS)


def read_diagnostics(folder):
    """Return engine/script diagnostics from retained process streams."""
    text = "".join((folder / name).read_text(errors="replace")
                   for name in ["stdout.log", "stderr.log", "engine.log"]
                   if (folder / name).exists())
    return [line for line in text.splitlines() if DIAGNOSTIC.search(line)]


def run_case(args, project, output, group, mode, repeat):
    """Run one measured owned process with a deadline and retained telemetry."""
    name = f"{group}-{mode}-{repeat}"
    folder = output / name
    folder.mkdir()
    result_path = folder / "telemetry.json"
    capture_path = folder / "crowd.png" if group == "graphical" and mode == "throttled" \
        and repeat == 1 else None
    child_environment = environment(folder / "user")
    child_environment.update({
        "S13_MODE": mode,
        "S13_OUTPUT": str(result_path),
        "S13_WARMUP_SECONDS": str(args.warmup),
        "S13_DURATION_SECONDS": str(args.duration),
    })
    if capture_path is not None:
        child_environment["S13_CAPTURE"] = str(capture_path)
    command = [args.godot, "--path", str(project), "--log-file", str(folder / "engine.log")]
    if group == "headless":
        command.append("--headless")
    else:
        command.extend(["--windowed", *capped_window_arguments(),
                        "--resolution", "1280x800"])
        require_capped_window(command)
    command.append(SCENE)
    deadline_seconds = args.warmup + args.duration + 45
    with (folder / "stdout.log").open("wb") as stdout, (folder / "stderr.log").open("wb") as stderr:
        child = subprocess.Popen(command, cwd=project, env=child_environment,
                                 stdout=stdout, stderr=stderr)
        try:
            child.wait(timeout=deadline_seconds)
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
            stop(child)
    load = system_load()
    time.sleep(QUIET_SETTLE_SECONDS)
    diagnostics = read_diagnostics(folder)
    telemetry = json.loads(result_path.read_text()) if result_path.exists() else None
    record = {
        "name": name,
        "group": group,
        "mode": mode,
        "repeat": repeat,
        "command": command,
        "deadline_seconds": deadline_seconds,
        "exit": child.returncode,
        "timed_out": timed_out,
        "diagnostics": diagnostics,
        "system_load": load,
        "telemetry": telemetry,
    }
    if telemetry is not None:
        record["distributions"] = {
            key: distribution(values) for key, values in telemetry["samples"].items()
        }
    expected_active = 68 if mode == "full" else 30
    record["ok"] = (
        child.returncode == 0 and not timed_out and not diagnostics and telemetry is not None
        and telemetry["live_count"] == 68 and telemetry["dead_count"] == 16
        and telemetry["active_animation_count"] == expected_active
        and telemetry["triangles_per_character"] < 1500
        and sorted(name for name in telemetry["clips"] if name != "RESET")
        == ["death", "idle", "run", "walk"]
    )
    save(folder / "case.json", record)
    return record


def aggregate(cases):
    """Aggregate all repeats by group/mode and retain repeat median/worst evidence."""
    result = {}
    for group in ["graphical", "headless"]:
        result[group] = {}
        for mode in ["full", "throttled"]:
            selected = [case for case in cases
                        if case["group"] == group and case["mode"] == mode]
            measured = [case for case in selected if case.get("telemetry") is not None]
            fields = measured[0]["telemetry"]["samples"] if measured else {}
            stats = {}
            for field in fields:
                values = [value for case in measured
                          for value in case["telemetry"]["samples"][field]]
                stats[field] = distribution(values)
                repeat_medians = [case["distributions"][field]["median"] for case in measured]
                repeat_worst = [case["distributions"][field]["worst"] for case in measured]
                stats[field]["repeat_median"] = percentile(repeat_medians, 0.5)
                available_worst = [value for value in repeat_worst if value is not None]
                stats[field]["repeat_worst"] = max(available_worst) if available_worst else None
            result[group][mode] = {
                "runs": len(selected),
                "all_ok": bool(selected) and all(case["ok"] for case in selected),
                "telemetry": stats,
                "system_load": [case["system_load"] for case in selected],
            }
    full_process = result.get("headless", {}).get("full", {}).get("telemetry", {}).get(
        "process_ms", {}).get("median")
    throttled_process = result.get("headless", {}).get("throttled", {}).get(
        "telemetry", {}).get("process_ms", {}).get("median")
    result["headless_process_median_delta_ms"] = (
        full_process - throttled_process
        if full_process is not None and throttled_process is not None else None
    )
    return result


def main():
    """Import once, execute requested three-repeat comparisons, and write one summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--warmup", type=float, default=2.0)
    parser.add_argument("--duration", type=float, default=6.0)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--groups", nargs="+", choices=["graphical", "headless"],
                        default=["graphical", "headless"])
    args = parser.parse_args()
    if args.godot is None:
        parser.error("godot not found on PATH; pass --godot")
    if not (0.5 <= args.duration <= 120 and 0 <= args.warmup <= 30 and 1 <= args.repeats <= 3):
        parser.error("duration 0.5..120, warmup 0..30, repeats 1..3")
    output = (args.output or Path(tempfile.mkdtemp(prefix="s13-"))).resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("output must be fresh and empty")
    print(f"S13 evidence: {output}", flush=True)
    version = subprocess.run([args.godot, "--version"], capture_output=True, text=True,
                             timeout=10, check=True).stdout.strip()
    summary = {
        "ok": False,
        "engine": version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, timeout=10
        ).strip(),
        "source_status": subprocess.check_output(
            ["git", "status", "--porcelain", "--", "tests/fixtures/s13", "art/models/characters",
             "art/materials/s13_*.tres"], cwd=ROOT, text=True, timeout=10
        ).strip(),
        "warmup_seconds": args.warmup,
        "duration_seconds": args.duration,
        "repeats": args.repeats,
        "groups": args.groups,
        "measurement_identity": measurement_identity(
            ROOT, identity_sources(), {**vars(args), "output": output}),
        "cases": [],
    }
    if version != PIN:
        summary["failure"] = f"expected {PIN}, got {version}"
    else:
        project = stage(output)
        import_command = [args.godot, "--headless", "--editor", "--path", str(project),
                          "--import", "--quit", "--log-file", str(output / "import.engine.log")]
        with (output / "import.log").open("wb") as log:
            imported = subprocess.run(import_command, stdout=log, stderr=subprocess.STDOUT,
                                      env=environment(output / "import-user"), timeout=120)
        import_text = (output / "import.log").read_text(errors="replace")
        engine_text = (output / "import.engine.log").read_text(errors="replace") \
            if (output / "import.engine.log").exists() else ""
        import_diagnostics = [line for line in (import_text + engine_text).splitlines()
                              if DIAGNOSTIC.search(line)]
        summary["import"] = {
            "command": import_command,
            "exit": imported.returncode,
            "diagnostics": import_diagnostics,
        }
        if imported.returncode != 0 or import_diagnostics:
            summary["failure"] = "isolated import failed or reported diagnostics"
        else:
            for group in args.groups:
                for repeat in range(1, args.repeats + 1):
                    for mode in ["full", "throttled"]:
                        case = run_case(args, project, output, group, mode, repeat)
                        summary["cases"].append(case)
                        save(output / "summary.json", summary)
                        if not case["ok"]:
                            summary["failure"] = f"case failed: {case['name']}"
                            break
                    if summary.get("failure"):
                        break
                if summary.get("failure"):
                    break
            summary["aggregate"] = aggregate(summary["cases"])
            summary["ok"] = not summary.get("failure") and all(
                case["ok"] for case in summary["cases"]
            )
    save(output / "summary.json", summary)
    print(json.dumps({"ok": summary["ok"], "failure": summary.get("failure")}))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
