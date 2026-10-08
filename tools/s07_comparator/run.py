#!/usr/bin/env python3
"""Run the standalone S07 S05-comparator scheduler in a fresh external project."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from script_checks import DIAGNOSTIC, PIN, environment  # noqa: E402

FIXTURES = ["s02", "s03", "s04", "s05", "s05_effect", "s05_draw", "s07_comparator"]
MODELS = ["s02_*.*", "s04_*.*", "s05_*.*"]
SCRIPT = "res://tests/fixtures/s07_comparator/run.gd"
IMPORT_SECONDS = 120
CLEANUP_SECONDS = 5
TRIAL_SLACK_SECONDS = 3
BASE_SLACK_SECONDS = 20
REQUIRED_TRUE = ["start_valid", "identities_fresh", "stale_shot_rejected",
                 "stale_event_rejected", "stale_callback_retired", "held_velocity_zero",
                 "outcomes_valid", "producer_stopped", "local_effects_cleared",
                 "no_live_job", "fixture_freed"]


def identity(path):
    """Return a stable byte identity for staged-input preservation checks."""
    return {"bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def save(path, value):
    """Write strict JSON with LF endings."""
    path.write_text(json.dumps(value, indent=2) + "\n", newline="\n")


def stage(output):
    """Copy only the comparator's committed fixtures, models and addon-free settings."""
    project = output / "project"
    ignore = shutil.ignore_patterns("editor_harness.tscn")
    for fixture in FIXTURES:
        shutil.copytree(ROOT / "tests/fixtures" / fixture,
                        project / "tests/fixtures" / fixture, ignore=ignore)
    models = project / "art/models/spikes"
    models.mkdir(parents=True)
    for pattern in MODELS:
        for path in (ROOT / "art/models/spikes").glob(pattern):
            shutil.copy2(path, models / path.name)
    settings = (ROOT / "project.godot").read_text()
    settings = re.sub(r"(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)", "", settings)
    settings = settings.replace('config/icon="res://icon.svg"\n', "")
    (project / "project.godot").write_text(settings, newline="\n")
    ledger = {path.relative_to(project).as_posix(): identity(path)
              for path in sorted(project.rglob("*")) if path.is_file()}
    save(output / "copy-ledger.json", ledger)
    return project, ledger


def read_trials(path):
    """Decode only complete JSONL trial rows."""
    if not path.exists():
        return []
    text = path.read_text(errors="replace")
    complete = text[:text.rfind("\n") + 1]
    return [json.loads(line) for line in complete.splitlines() if line]


def evaluate(result, rows, graphical):
    """Independently check literal per-trial outcomes and lifecycle receipts."""
    failures = []
    if result is None or not result.get("ok"):
        failures.append("driver result missing or failed")
        return failures
    if len(rows) != result.get("trials_requested") or len(rows) != result.get("trials_completed"):
        failures.append("trial count mismatch")
    sessions = [row.get("session") for row in rows]
    if len(set(sessions)) != len(rows) or any(len(value or "") != 32 for value in sessions):
        failures.append("fresh session identities")
    for index, row in enumerate(rows, start=1):
        if row.get("trial") != index or row.get("admission") != "OK":
            failures.append(f"trial {index} admission/order")
        if any(row.get(field) is not True for field in REQUIRED_TRUE):
            failures.append(f"trial {index} lifecycle")
        expected = {"damage": 12, "visits": 144, "target_peak": 4, "completed": 12,
                    "explosions": 12}
        capacity = row.get("slot_capacity")
        explosions = row.get("explosions")
        if not isinstance(capacity, int) or capacity < 0 or not isinstance(explosions, int):
            failures.append(f"trial {index} effect configuration")
            expected_drawn, expected_dropped = None, None
        else:
            expected_drawn = min(explosions, capacity)
            expected_dropped = max(0, explosions - capacity)
        if (any(row.get(field) != value for field, value in expected.items())
                or row.get("expected_drawn") != expected_drawn
                or row.get("expected_dropped") != expected_dropped
                or row.get("effects_accepted") != expected_drawn
                or row.get("effects_dropped") != expected_dropped):
            failures.append(f"trial {index} literal outcomes")
        for span in ["loading_seconds", "chain_seconds", "reset_seconds"]:
            if not isinstance(row.get(span), (int, float)) or row[span] < 0:
                failures.append(f"trial {index} {span}")
        if graphical:
            draw = row.get("draw", {})
            if (row.get("drawn") is not True or not isinstance(row.get("first_draw_seconds"),
                                                               (int, float))
                    or draw.get("explosions") != explosions
                    or draw.get("slot_capacity") != capacity
                    or draw.get("expected_drawn") != expected_drawn
                    or draw.get("expected_dropped") != expected_dropped
                    or draw.get("visible") != expected_drawn
                    or draw.get("visible_in_tree") != expected_drawn
                    or draw.get("mesh_nodes", 0) < expected_drawn
                    or draw.get("dropped") != expected_dropped
                    or draw.get("can_draw") is not True
                    or draw.get("png", {}).get("save_error") != 0):
                failures.append(f"trial {index} draw receipt")
    return failures


def stop_child(child):
    """Terminate and then kill only this runner's child, always observing its exit."""
    actions = []
    if child.poll() is None:
        child.terminate()
        actions.append("terminate")
        try:
            child.wait(timeout=CLEANUP_SECONDS)
        except subprocess.TimeoutExpired:
            child.kill()
            actions.append("kill")
            child.wait(timeout=CLEANUP_SECONDS)
    return actions


def main():
    """Import once and spend one bounded headless or windowed comparator run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--trials", type=int, default=20)
    parser.add_argument("--initial-delay", type=float, default=15.0)
    parser.add_argument("--spacing", type=float, default=30.0)
    parser.add_argument("--windowed", action="store_true")
    args = parser.parse_args()
    if args.godot is None:
        parser.error("godot not found on PATH; pass --godot")
    if not (1 <= args.trials <= 20 and 0 <= args.initial_delay <= 15
            and 0 <= args.spacing <= 30):
        parser.error("trials 1..20, initial delay 0..15 s, spacing 0..30 s")
    output = (args.output or Path(tempfile.mkdtemp(prefix="s07-comparator-"))).resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("output must be a fresh empty directory")

    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                       text=True).strip()
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain", "--", "tests/fixtures/s02",
         "tests/fixtures/s03", "tests/fixtures/s04", "tests/fixtures/s05",
         "tests/fixtures/s05_effect", "tests/fixtures/s05_draw",
         "tests/fixtures/s07_comparator", "art/models/spikes", "project.godot",
         "tools/s07_comparator"], cwd=ROOT, text=True).strip()
    summary = {"ok": False, "revision": revision, "dirty_inputs": dirty,
               "graphical": args.windowed, "schedule": {"trials": args.trials,
               "initial_delay_seconds": args.initial_delay, "spacing_seconds": args.spacing}}
    project = None
    ledger = {}
    child = None
    streams = []
    started = time.monotonic()
    try:
        version = subprocess.run([args.godot, "--version"], capture_output=True, text=True,
                                 timeout=10, check=True).stdout.strip()
        summary["engine"] = {"version": version, **identity(Path(args.godot))}
        if version != PIN:
            raise RuntimeError(f"expected {PIN}, got {version}")
        project, ledger = stage(output)
        with (output / "import.log").open("wb") as log:
            code = subprocess.run([args.godot, "--headless", "--editor", "--path",
                                   str(project), "--import", "--quit"], stdout=log,
                                  stderr=subprocess.STDOUT,
                                  env=environment(output / "import-user"),
                                  timeout=IMPORT_SECONDS).returncode
        import_diagnostics = [line for line in (output / "import.log")
                              .read_text(errors="replace").splitlines()
                              if DIAGNOSTIC.search(line)]
        summary["import"] = {"exit": code, "diagnostics": import_diagnostics}
        if code != 0 or import_diagnostics:
            raise RuntimeError("import failed or reported diagnostics")

        folder = output / "run"
        folder.mkdir()
        argv = [args.godot, "--path", str(project),
                "--windowed" if args.windowed else "--headless"]
        if args.windowed:
            argv.extend(["--resolution", "1280x800"])
        argv.extend(["--log-file", str(folder / "engine.log"), "--script", SCRIPT, "--",
                     f"--trials={args.trials}", f"--initial-delay={args.initial_delay}",
                     f"--spacing={args.spacing}"])
        out = (folder / "stdout.log").open("wb")
        err = (folder / "stderr.log").open("wb")
        streams.extend([out, err])
        child = subprocess.Popen(argv, cwd=project, stdout=out, stderr=err,
                                 env=environment(folder / "user"))
        deadline_seconds = (args.initial_delay + args.spacing * (args.trials - 1)
                            + BASE_SLACK_SECONDS + TRIAL_SLACK_SECONDS * args.trials)
        try:
            child.wait(timeout=deadline_seconds)
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
        actions = stop_child(child)
        for stream in streams:
            stream.close()
        streams.clear()

        text = "".join((folder / name).read_text(errors="replace")
                       for name in ["stdout.log", "stderr.log", "engine.log"]
                       if (folder / name).exists())
        diagnostics = [line for line in text.splitlines() if DIAGNOSTIC.search(line)]
        result_path = project / "result.json"
        rows_path = project / "trials.jsonl"
        result = json.loads(result_path.read_text()) if result_path.exists() else None
        rows = read_trials(rows_path)
        receipt_failures = evaluate(result, rows, args.windowed)
        artifacts = output / "artifacts"
        artifacts.mkdir()
        for path in [result_path, rows_path, *sorted(project.glob("trial-*-burst.png"))]:
            if path.exists():
                shutil.copy2(path, artifacts / path.name)
        unchanged = all(identity(project / name) == value for name, value in ledger.items())
        criteria = {"exit_zero": child.returncode == 0, "absolute_deadline": not timed_out,
                    "no_diagnostics": not diagnostics, "receipts": not receipt_failures,
                    "inputs_preserved": unchanged, "clean_inputs": not dirty,
                    "child_reaped": child.poll() is not None}
        summary.update(argv=argv, exit=child.returncode, timed_out=timed_out,
                       cleanup=actions, diagnostics=diagnostics, result=result,
                       receipt_failures=receipt_failures, criteria=criteria,
                       inputs_preserved=unchanged, duration_seconds=time.monotonic() - started)
        summary["ok"] = all(criteria.values())
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        summary["failure"] = str(error)
    finally:
        if child is not None and child.poll() is None:
            summary["cleanup"] = stop_child(child)
        for stream in streams:
            stream.close()
    save(output / "summary.json", summary)
    print(json.dumps({"ok": summary["ok"], "failure": summary.get("failure"),
                      "criteria": summary.get("criteria")}, indent=1))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
