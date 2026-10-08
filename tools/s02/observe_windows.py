#!/usr/bin/env python3
"""Collect bounded automatic-draw and native-focus S02 evidence on Windows."""

import argparse
import ctypes
import hashlib
import json
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

DRAW_SCRIPT = "res://tests/fixtures/s02/observe_windows.gd"
FOCUS_SCENE = "res://tests/fixtures/s02/focus_runner.tscn"
IMPORT_SECONDS = 90
DRAW_SECONDS = 20.0
FOCUS_SECONDS = 12.0
CLEANUP_SECONDS = 2.0
POLL_SECONDS = 0.05
MAX_FOCUS_ATTEMPTS = 2


def identity(path):
    """Hash actual bytes for source and capture binding."""
    return {
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def save(path, value):
    """Write deterministic JSON with LF endings."""
    path.write_text(json.dumps(value, indent=2) + "\n", newline="\n")


def stage(output):
    """Copy the S02 runtime closure without addons, authoring sources or editor harnesses."""
    project = output / "project"
    fixtures = project / "tests/fixtures/s02"
    shutil.copytree(
        ROOT / "tests/fixtures/s02",
        fixtures,
        ignore=shutil.ignore_patterns("editor_harness.tscn", "capture_s02.gd", "check_s02.gd"),
    )
    models = project / "art/models/spikes"
    models.mkdir(parents=True)
    for path in sorted((ROOT / "art/models/spikes").glob("s02_*.*")):
        shutil.copy2(path, models / path.name)
    settings = (ROOT / "project.godot").read_text()
    settings = re.sub(r"(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)", "", settings)
    settings = settings.replace('config/icon="res://icon.svg"\n', "")
    (project / "project.godot").write_text(settings, newline="\n")
    ledger = {
        path.relative_to(project).as_posix(): identity(path)
        for path in sorted(project.rglob("*"))
        if path.is_file()
    }
    save(output / "copy-ledger.json", ledger)
    return project, ledger


def foreground_window():
    """Read the current native foreground HWND, owning PID and title without changing focus."""
    if platform.system() != "Windows":
        return {"available": False, "reason": "not Windows"}
    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return {"available": True, "hwnd": "0x0", "pid": 0, "title": ""}
    pid = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    length = user32.GetWindowTextLengthW(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return {
        "available": True,
        "hwnd": hex(hwnd),
        "pid": pid.value,
        "title": buffer.value,
    }


def prefixed_rows(path, prefix):
    """Decode complete JSON rows with the requested fixture prefix."""
    if not path.exists():
        return []
    found = []
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith(prefix):
            continue
        try:
            found.append(json.loads(line.removeprefix(prefix)))
        except json.JSONDecodeError:
            found.append({"event": "unparsed", "line": line})
    return found


def stop_child(child):
    """Wait briefly, terminate and then kill only the exact child if still live."""
    actions = []
    for action in ("grace", "terminate", "kill"):
        if child.poll() is not None:
            break
        if action != "grace":
            try:
                getattr(child, action)()
                actions.append(action)
            except OSError as error:
                actions.append(f"{action} failed: {error}")
        try:
            child.wait(timeout=CLEANUP_SECONDS)
        except subprocess.TimeoutExpired:
            actions.append(action + " timeout")
    return actions, child.poll() is not None


def run_window(project, folder, godot, arguments, deadline_seconds):
    """Launch one graphical child and retain foreground ownership throughout its lifetime."""
    folder.mkdir(parents=True)
    command = [
        godot,
        "--path",
        str(project),
        "--windowed",
        "--resolution",
        "1280x800",
        "--position",
        "80,80",
        "--log-file",
        str(folder / "engine.log"),
        *arguments,
    ]
    before = foreground_window()
    started = time.monotonic()
    timeline = []
    with (folder / "stdout.log").open("wb") as stdout, (
        folder / "stderr.log"
    ).open("wb") as stderr:
        child = subprocess.Popen(
            command,
            cwd=project,
            stdout=stdout,
            stderr=stderr,
            env=environment(folder / "user"),
        )
        timed_out = False
        while child.poll() is None and time.monotonic() - started < deadline_seconds:
            timeline.append({
                "offset_seconds": time.monotonic() - started,
                **foreground_window(),
            })
            time.sleep(POLL_SECONDS)
        if child.poll() is None:
            timed_out = True
        cleanup, reaped = stop_child(child)
    after = foreground_window()
    text = "".join(
        (folder / name).read_text(errors="replace")
        for name in ("stdout.log", "stderr.log", "engine.log")
        if (folder / name).exists()
    )
    return {
        "argv": command,
        "pid": child.pid,
        "exit": child.returncode,
        "timed_out": timed_out,
        "cleanup": cleanup,
        "reaped": reaped,
        "duration_seconds": time.monotonic() - started,
        "foreground_before": before,
        "foreground_after": after,
        "foreground_timeline": timeline,
        "diagnostics": [line for line in text.splitlines() if DIAGNOSTIC.search(line)],
        "stderr_empty": not (folder / "stderr.log").read_bytes(),
    }


def foreign_focus_stolen(attempt):
    """Detect a sustained new foreign foreground owner during the restore/check interval."""
    own_pid = attempt["process"]["pid"]
    before_pid = attempt["process"]["foreground_before"].get("pid")
    run = 0
    for row in attempt["process"]["foreground_timeline"]:
        if not 3.25 <= row["offset_seconds"] <= 4.75:
            continue
        pid = row.get("pid")
        if pid not in (None, 0, own_pid, before_pid):
            run += 1
            if run >= 3:
                return True
        else:
            run = 0
    return False


def collect_draw(project, output, godot):
    """Run the automatic observer and copy its selected viewport PNGs into evidence."""
    folder = output / "draw"
    process = run_window(project, folder, godot, ["--script", DRAW_SCRIPT], DRAW_SECONDS)
    rows = prefixed_rows(folder / "stdout.log", "S02_DRAW ")
    results = [row for row in rows if row.get("event") == "result"]
    captures = []
    for path in sorted((folder / "user").rglob("s02-draw-*.png")):
        target = folder / path.name
        shutil.copy2(path, target)
        captures.append({"name": target.name, **identity(target)})
    result = results[-1] if results else None
    criteria = {
        "result_ok": result is not None and result.get("ok") is True,
        "exit_zero": process["exit"] == 0,
        "not_timed_out": not process["timed_out"],
        "no_diagnostics": not process["diagnostics"],
        "stderr_empty": process["stderr_empty"],
        "three_captures": len(captures) == 3,
        "reaped": process["reaped"],
    }
    return {
        "ok": all(criteria.values()),
        "process": process,
        "criteria": criteria,
        "result": result,
        "frame_rows": len([row for row in rows if row.get("event") == "frame"]),
        "captures": captures,
    }


def collect_focus(project, output, godot):
    """Run native minimize/restore once, retrying only after a recorded foreign focus steal."""
    attempts = []
    for index in range(1, MAX_FOCUS_ATTEMPTS + 1):
        folder = output / f"focus-{index}"
        process = run_window(project, folder, godot, [FOCUS_SCENE], FOCUS_SECONDS)
        rows = prefixed_rows(folder / "stdout.log", "S02_FOCUS_RESULT ")
        samples = prefixed_rows(folder / "stdout.log", "S02_FOCUS ")
        fixture_result = rows[-1] if rows else None
        attempt = {
            "process": process,
            "fixture_result": fixture_result,
            "sample_count": len(samples),
            "samples": samples,
        }
        attempt["foreign_focus_stolen"] = foreign_focus_stolen(attempt)
        criteria = {
            "fixture_result": fixture_result is not None,
            "focus_out_in": fixture_result is not None
            and fixture_result.get("os_focus_loss") is True
            and not fixture_result.get("failures"),
            "exit_zero": process["exit"] == 0,
            "not_timed_out": not process["timed_out"],
            "no_diagnostics": not process["diagnostics"],
            "stderr_empty": process["stderr_empty"],
            "reaped": process["reaped"],
        }
        attempt["criteria"] = criteria
        attempt["ok"] = all(criteria.values())
        attempts.append(attempt)
        if attempt["ok"] or not attempt["foreign_focus_stolen"]:
            break
    return {
        "ok": attempts[-1]["ok"],
        "attempts": attempts,
        "retry_used": len(attempts) > 1,
        "retry_reason": "foreign foreground owner" if len(attempts) > 1 else None,
    }


def main():
    """Stage, import and execute one draw observation plus one bounded focus observation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if platform.system() != "Windows":
        parser.error("this observation requires Windows")
    if args.godot is None:
        parser.error("godot not found on PATH; pass --godot")
    output = (args.output or Path(tempfile.mkdtemp(prefix="s02-windows-"))).resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("output must be a fresh empty directory")
    print(f"S02 Windows evidence: {output}", flush=True)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(
        [
            "git",
            "status",
            "--porcelain",
            "--",
            "tests/fixtures/s02",
            "art/models/spikes",
            "project.godot",
            "tools/s02/observe_windows.py",
        ],
        cwd=ROOT,
        text=True,
    ).strip()
    summary = {
        "ok": False,
        "revision": revision,
        "dirty_inputs": dirty,
        "platform": platform.platform(),
        "python": sys.version,
        "foreground_preflight": foreground_window(),
    }
    project = None
    ledger = {}
    try:
        version = subprocess.run(
            [args.godot, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        ).stdout.strip()
        if version != PIN:
            raise RuntimeError(f"expected {PIN}, got {version}")
        summary["engine"] = {"version": version, **identity(Path(args.godot))}
        project, ledger = stage(output)
        import_log = output / "import.log"
        with import_log.open("wb") as stream:
            code = subprocess.run(
                [
                    args.godot,
                    "--headless",
                    "--editor",
                    "--path",
                    str(project),
                    "--import",
                    "--quit",
                ],
                stdout=stream,
                stderr=subprocess.STDOUT,
                env=environment(output / "import-user"),
                timeout=IMPORT_SECONDS,
            ).returncode
        diagnostics = [
            line
            for line in import_log.read_text(errors="replace").splitlines()
            if DIAGNOSTIC.search(line)
        ]
        summary["import"] = {"exit": code, "diagnostics": diagnostics}
        if code != 0 or diagnostics:
            raise RuntimeError("import failed or reported diagnostics")
        summary["draw"] = collect_draw(project, output, args.godot)
        summary["focus"] = collect_focus(project, output, args.godot)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        summary["failure"] = str(error)
    unchanged = project is not None and all(
        identity(project / name) == expected for name, expected in ledger.items()
    )
    summary["inputs_preserved"] = unchanged
    summary["foreground_postflight"] = foreground_window()
    criteria = {
        "clean_inputs": not dirty,
        "inputs_preserved": unchanged,
        "draw": summary.get("draw", {}).get("ok", False),
        "focus": summary.get("focus", {}).get("ok", False),
    }
    summary["criteria"] = criteria
    summary["ok"] = "failure" not in summary and all(criteria.values())
    save(output / "result.json", summary)
    print(json.dumps({
        "ok": summary["ok"],
        "failure": summary.get("failure"),
        "criteria": criteria,
        "draw": summary.get("draw", {}).get("criteria"),
        "focus_attempts": len(summary.get("focus", {}).get("attempts", [])),
    }, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
