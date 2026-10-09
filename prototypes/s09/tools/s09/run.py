"""Run six isolated ten-minute S09 traffic cases and retain exact timing evidence."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from measurement_identity import measurement_identity
from script_checks import checked_command, engine_version, environment

POPULATIONS = (24, 32)
SEEDS = (11, 29, 47)
TICKS = 36_000
QUIET_SETTLE_SECONDS = 1.0
MEASUREMENT_SOURCES = ["tools/s09/run.py", "tools/measurement_identity.py",
                       "tools/script_checks.py", "tests/fixtures/s09",
                       "tests/fixtures/s04/drive_rules.gd",
                       "tests/fixtures/s04/drive_rules.gd.uid", "project.godot"]


def percentile(values, fraction):
    """Return a nearest-rank percentile for a nonempty numeric sequence."""
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(len(ordered) * fraction + 0.999999) - 1))
    return ordered[index]


def distribution(values):
    """Summarize exact retained samples without averaging seed percentiles."""
    if not values:
        return {"count": 0}
    return {"count": len(values), "median": percentile(values, 0.5),
            "p95": percentile(values, 0.95), "p99": percentile(values, 0.99),
            "worst": max(values)}


def aggregate_cases(cases):
    """Aggregate full tick samples and outcome counts by requested population."""
    result = {}
    for population in POPULATIONS:
        selected = [case for case in cases if case["population"] == population]
        samples_ms = [sample / 1000.0 for case in selected
                      for sample in case["ai_tick_usec_samples"]]
        recoveries = [sample for case in selected
                      for sample in case["stuck_recovery_samples_seconds"]]
        result[str(population)] = {
            "runs": len(selected), "ai_tick_ms": distribution(samples_ms),
            "ai_collisions": sum(case["ai_collisions"] for case in selected),
            "deadlocks": sum(case["deadlocks"] for case in selected),
            "intersection_gridlock": {
                "episodes": sum(case["intersection_gridlock"]["episodes"]
                                for case in selected),
                "resolved": sum(case["intersection_gridlock"]["resolved"]
                                for case in selected),
                "unresolved": sum(case["intersection_gridlock"]["unresolved"]
                                  for case in selected),
                "max_stall_seconds": max(case["intersection_gridlock"]
                                         ["max_stall_seconds"] for case in selected),
            },
            "stuck_events": sum(case["stuck_events"] for case in selected),
            "stuck_recovery_seconds": distribution(recoveries),
            "lane_error_p95_m_by_seed": [case["lane_error_m"]["p95"] for case in selected],
            "lane_error_worst_m_by_seed": [case["lane_error_m"]["worst"]
                                             for case in selected],
        }
    return result


def host_snapshot():
    """Sample Windows CPU load and Godot processes only after a measured case exits."""
    process = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True,
                             text=True, timeout=10, check=True)
    godot_count = sum(1 for line in process.stdout.splitlines()
                      if line.lstrip('"').lower().startswith("godot"))
    cpu = subprocess.run([
        "powershell.exe", "-NoProfile", "-Command",
        "(Get-CimInstance Win32_Processor | "
        "Measure-Object -Property LoadPercentage -Average).Average",
    ], capture_output=True, text=True, timeout=10, check=True)
    cpu_percent = float(cpu.stdout.strip())
    return {"godot_processes_after_case": godot_count,
            "cpu_load_percent_after_case": cpu_percent,
            "timing_label": "post-case context only; measurement exclusivity not proven"}


def fingerprints(root):
    """Bind the copied simulation and shared handling inputs to exact bytes."""
    paths = list((root / "tests/fixtures/s09").glob("*"))
    paths += list((root / "tests/fixtures/s04").glob("drive_rules.gd*"))
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths if path.is_file()}


def stage_project(project):
    """Create an addon-free dependency mirror containing only S09 and its rule owner."""
    shutil.copytree(ROOT / "tests/fixtures/s09", project / "tests/fixtures/s09")
    s04 = project / "tests/fixtures/s04"
    s04.mkdir(parents=True)
    for path in (ROOT / "tests/fixtures/s04").glob("drive_rules.gd*"):
        shutil.copy2(path, s04 / path.name)
    settings = (ROOT / "project.godot").read_text()
    for section in ("autoload", "editor_plugins"):
        settings = re.sub(r"(?ms)^\[" + section + r"\]\n.*?(?=^\[|\Z)", "", settings)
    settings = re.sub(r"^(?:config/icon|run/main_scene)=.*\n", "", settings, flags=re.M)
    (project / "project.godot").write_text(settings)


def main():
    """Validate the pin, import once, run six cases, and write one review summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--ticks", type=int, default=TICKS,
                        help="bounded development override; accepted evidence uses 36000")
    args = parser.parse_args()
    if args.ticks < 1 or args.ticks > TICKS:
        parser.error("--ticks must be between 1 and 36000")
    output = (args.output or Path(tempfile.mkdtemp(prefix="s09-"))).resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("fresh external output required")
    print("S09 evidence:", output, flush=True)
    identity = measurement_identity(
        ROOT, MEASUREMENT_SOURCES, {**vars(args), "output": output})
    version = engine_version(args.godot)
    project = output / "project"
    project.mkdir()
    stage_project(project)
    before = fingerprints(project)
    user = environment(output / "user")
    base_command = [args.godot, "--headless", "--path", str(project)]
    import_command = base_command + ["--editor", "--import", "--quit", "--log-file",
                                     str(output / "import.engine.log")]
    imported = checked_command(import_command, output / "import.log", user, 60)
    cases = []
    commands = [import_command]
    if imported:
        for population in POPULATIONS:
            for seed in SEEDS:
                result_path = output / "cases" / f"population-{population}-seed-{seed}.json"
                result_path.parent.mkdir(exist_ok=True)
                command = base_command + ["--script",
                    "res://tests/fixtures/s09/proof.gd", "--log-file",
                    str(output / "cases" / f"population-{population}-seed-{seed}.engine.log"),
                    "--", str(population), str(seed), str(args.ticks), str(result_path)]
                commands.append(command)
                passed = checked_command(command, output / "cases" /
                                         f"population-{population}-seed-{seed}.log", user, 180)
                snapshot = host_snapshot()
                time.sleep(QUIET_SETTLE_SECONDS)
                if result_path.exists():
                    case = json.loads(result_path.read_text())
                    case["host_snapshot"] = snapshot
                    case["command_passed"] = passed
                    result_path.write_text(json.dumps(case, indent=2) + "\n")
                    cases.append(case)
                if not passed:
                    break
            if len(cases) != POPULATIONS.index(population) * len(SEEDS) + len(SEEDS):
                break
    complete = len(cases) == len(POPULATIONS) * len(SEEDS)
    unchanged = before == fingerprints(project)
    semantic_success = complete and all(not case["failures"] and case["command_passed"]
                                        for case in cases)
    summary = {"engine": version, "ticks_per_case": args.ticks,
               "measurement_identity": identity,
               "accepted_duration_used": args.ticks == TICKS,
               "import_passed": imported, "cases_complete": complete,
               "semantic_success": semantic_success, "saved_files_unchanged": unchanged,
               "commands": commands, "source_fingerprints": before,
               "cases": [{key: case[key] for key in ("population", "seed", "host_snapshot",
                           "ai_tick_ms", "ai_collisions", "deadlocks",
                           "intersection_gridlock", "stuck_events", "stuck_recovery_seconds",
                           "lane_error_m", "failures")}
                         for case in cases],
               "by_population": aggregate_cases(cases) if complete else {}}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({key: value for key, value in summary.items()
                      if key not in ("commands", "source_fingerprints", "cases")}))
    return 0 if imported and semantic_success and unchanged else 1


if __name__ == "__main__":
    raise SystemExit(main())
