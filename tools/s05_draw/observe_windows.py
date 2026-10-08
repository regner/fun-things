#!/usr/bin/env python3
"""Run the saved S05 draw observer as one windowed host/live/settled-late set on Windows.

Stages the committed S02/S03/S04/S05/S05-effect/S05-draw fixtures and their linked models
into a fresh external project, imports once headless, then launches three real graphical
ENet processes against the saved observation camera. Nothing is installed or retried; one
absolute budget bounds the set. See docs/spikes/s05-windows-draw.md.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from script_checks import DIAGNOSTIC, PIN, environment  # noqa: E402

SCENE = "res://tests/fixtures/s05_draw/burst.tscn"
FIXTURES = ["s02", "s03", "s04", "s05", "s05_effect", "s05_draw"]
MODELS = ["s02_*.*", "s04_*.*", "s05_*.*"]
IMPORT_SECONDS = 120
SET_SECONDS = 45.0
CLEANUP_SECONDS = 2.0
WINDOW_X = {"host": 0, "client": 640, "late": 1280}


def identity(path):
    """Hash actual bytes."""
    return {"bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def save(path, value):
    """Write strict JSON with LF endings."""
    path.write_text(json.dumps(value, indent=2) + "\n", newline="\n")


def stage(output):
    """Copy committed runtime fixtures/models; exclude editor harnesses, addons and sources."""
    project = output / "project"
    ignore = shutil.ignore_patterns("editor_harness.tscn")
    for fixture in FIXTURES:
        shutil.copytree(ROOT / "tests/fixtures" / fixture, project / "tests/fixtures" / fixture,
                        ignore=ignore)
    # The class cache still names S05's editor-only probe helper; it is unused at runtime.
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


def rows(path):
    """Decode complete S05 rows only."""
    if not path.exists():
        return []
    text = path.read_text(errors="replace")
    end = text.rfind("\n") + 1
    found = []
    for line in text[:end].splitlines():
        if line.startswith("S05 "):
            try:
                found.append(json.loads(line[4:]))
            except json.JSONDecodeError:
                found.append({"event": "unparsed"})
    return found


def cleanup(children, deadline):
    """Shared graceful wait, terminate then kill; observed exits own reap truth."""
    actions = []
    for action in ["grace", "terminate", "kill"]:
        live = [(role, child) for role, child in children.items() if child.poll() is None]
        if not live:
            break
        for role, child in live:
            if action != "grace":
                getattr(child, action)()
                actions.append({"role": role, "action": action})
        stage_end = min(time.monotonic() + CLEANUP_SECONDS, deadline)
        for _, child in live:
            try:
                child.wait(timeout=max(0.0, stage_end - time.monotonic()))
            except subprocess.TimeoutExpired:
                pass
    return actions, all(child.poll() is not None for child in children.values())


def main():
    """Spend one import and one three-process windowed set."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--godot", default=shutil.which("godot"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.godot is None:
        parser.error("godot not found on PATH; pass --godot")
    output = (args.output or Path(tempfile.mkdtemp(prefix="s05-draw-win-"))).resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("output must be a fresh empty directory")
    print(f"S05 Windows draw evidence: {output}", flush=True)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--", "tests", "art",
                                     "project.godot"], cwd=ROOT, text=True).strip()
    result = {"ok": False, "revision": revision, "dirty_inputs": dirty, "processes": {}}
    children, streams = {}, []
    project = None
    ledger = {}
    started = time.monotonic()
    try:
        version = subprocess.run([args.godot, "--version"], capture_output=True, text=True,
                                 timeout=10, check=True).stdout.strip()
        if version != PIN:
            raise RuntimeError(f"expected {PIN}, got {version}")
        result["engine"] = {"version": version, **identity(Path(args.godot))}
        project, ledger = stage(output)
        log = output / "import.log"
        with log.open("wb") as stream:
            code = subprocess.run([args.godot, "--headless", "--editor", "--path", str(project),
                                   "--import", "--quit"], stdout=stream, stderr=subprocess.STDOUT,
                                  env=environment(output / "import-user"),
                                  timeout=IMPORT_SECONDS).returncode
        import_diagnostics = [line for line in log.read_text(errors="replace").splitlines()
                              if DIAGNOSTIC.search(line)]
        result["import"] = {"exit": code, "diagnostics": import_diagnostics}
        if code != 0 or import_diagnostics:
            raise RuntimeError("import failed or reported diagnostics")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        started = time.monotonic()
        deadline = started + SET_SECONDS
        work_end = deadline - 3 * CLEANUP_SECONDS - 1

        def start(role):
            folder = output / role
            folder.mkdir()
            command = [args.godot, "--path", str(project), "--windowed", "--position",
                       f"{WINDOW_X[role]},40", "--log-file", str(folder / "engine.log"), SCENE,
                       "--", f"--role={role}", f"--port={port}"]
            out, err = (folder / "stdout").open("wb"), (folder / "stderr").open("wb")
            streams.extend([out, err])
            child = subprocess.Popen(command, cwd=project, stdout=out, stderr=err,
                                     env=environment(folder / "user"))
            children[role] = child
            result["processes"][role] = {"argv": command, "pid": child.pid,
                                         "start_offset_s": time.monotonic() - started}

        start("host")
        while time.monotonic() < work_end:
            for role, child in children.items():
                if any(row.get("event") == "failure" for row in rows(output / role / "stdout")):
                    raise RuntimeError("fixture expectation failure: " + role)
                if child.poll() is not None and child.returncode != 0:
                    raise RuntimeError(f"nonzero exit: {role} {child.returncode}")
            host = rows(output / "host/stdout")
            if any(row.get("event") == "ready" for row in host) and "client" not in children:
                start("client")
            if any(row.get("event") == "settled" for row in host) and "late" not in children:
                start("late")
            if len(children) == 3 and all(c.poll() is not None for c in children.values()):
                break
            if children["host"].poll() is not None and "late" not in children:
                raise RuntimeError("host left before settled-late launch")
            time.sleep(0.02)
        else:
            raise RuntimeError("work deadline expired")
        result["collection_ok"] = True
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        result["failure"] = str(error)
    finally:
        actions, reaped = cleanup(children, started + SET_SECONDS)
        for stream in streams:
            stream.close()
    result.update(cleanup=actions, reaped=reaped,
                  duration_s=time.monotonic() - started,
                  exits={role: child.returncode for role, child in children.items()})
    diagnostics, observations = {}, {}
    for role in children:
        folder = output / role
        text = "".join((folder / name).read_text(errors="replace")
                       for name in ["stdout", "stderr", "engine.log"] if (folder / name).exists())
        diagnostics[role] = [line for line in text.splitlines() if DIAGNOSTIC.search(line)]
        draw = sorted((folder / "user").rglob("draw.jsonl"))
        frames = []
        if draw:
            frames = [json.loads(line) for line in draw[0].read_text().splitlines() if line]
            for png in draw[0].parent.glob("*.png"):
                shutil.copy2(png, folder / png.name)
            shutil.copy2(draw[0], folder / "draw.jsonl")
        final = [row for row in frames if row.get("kind") == "result"]
        captured = [row["png"] for row in frames if row.get("kind") == "frame" and "png" in row]
        observations[role] = {
            "result": final[-1] if final else None,
            "captures": captured,
            "max_visible": max((row["presentation"]["visible"] for row in frames
                                if row.get("kind") == "frame"), default=None),
            "can_draw": sorted({row["can_draw"] for row in frames if "can_draw" in row}),
            "fixture_result": [row for row in rows(folder / "stdout")
                               if row.get("event") == "result"]}
    result.update(diagnostics=diagnostics, observations=observations)
    unchanged = project is not None and all(identity(project / name) == value
                                            for name, value in ledger.items())
    result["inputs_preserved"] = unchanged
    criteria = {
        "collection": result.get("collection_ok", False),
        "exits_zero": all(code == 0 for code in result["exits"].values()) and len(children) == 3,
        "no_diagnostics": not any(diagnostics.values()),
        "fixture_results_ok": all(obs["fixture_result"] and obs["fixture_result"][-1].get("ok")
                                  for obs in observations.values()),
        "draw_results_clean": all(obs["result"] and not obs["result"]["render_failures"]
                                  for obs in observations.values()),
        "live_burst_drawn": any(png["stage"] == "burst" and png["save_error"] == 0
                                for obs in observations.values() for png in obs["captures"]),
        "late_hydrated_drawn": any(png["stage"] == "hydrated" and png["save_error"] == 0
                                   for png in observations.get("late", {}).get("captures", [])),
        "reaped": reaped, "inputs_preserved": unchanged,
        # Staging copies the working tree, so only clean inputs bind evidence to the revision.
        "clean_inputs": not dirty,
    }
    result["criteria"] = criteria
    result["ok"] = all(criteria.values())
    save(output / "result.json", result)
    print(json.dumps({"ok": result["ok"], "failure": result.get("failure"),
                      "criteria": criteria}, indent=1))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
