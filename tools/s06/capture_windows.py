#!/usr/bin/env python3
"""Capture saved S06 layout, minimap and public-route frames in two windowed camera views."""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from script_checks import DIAGNOSTIC, PIN, environment  # noqa: E402

FIXTURES = ["s02", "s03", "s04", "s06"]
MODELS = ["s02_*", "s04_*", "s06_*"]
SCENES = {
    "camera-42": "res://tests/fixtures/s06/intersection.tscn",
    "camera-50": "res://tests/fixtures/s06/intersection_wide.tscn",
}
ROUTES = ["foot", "east_to_north", "west_to_south"]
CAPTURE_TICKS = {
    "foot": [120, 240, 360],
    "east_to_north": [180, 360, 540],
    "west_to_south": [180, 360, 540],
}
IMPORT_SECONDS = 120
OBSERVATION_SECONDS = 90
STOP_SECONDS = 2


def identity(path):
    """Hash actual bytes for an input or retained capture."""
    return {"bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def save(path, value):
    """Write strict JSON with LF endings."""
    path.write_text(json.dumps(value, indent=2) + "\n", newline="\n")


def stage(output):
    """Copy the saved fixture closure, models and observer into an external project."""
    project = output / "project"
    for fixture in FIXTURES:
        shutil.copytree(ROOT / "tests/fixtures" / fixture,
                        project / "tests/fixtures" / fixture)
    models = project / "art/models/spikes"
    models.mkdir(parents=True)
    for pattern in MODELS:
        for path in (ROOT / "art/models/spikes").glob(pattern):
            if path.is_file():
                shutil.copy2(path, models / path.name)
    for tool in ["s01", "s02", "s04"]:
        shutil.copytree(ROOT / "tools" / tool, project / "tools" / tool)
    observer = ROOT / "tools/s06/capture_observer.gd"
    target = project / "tools/s06/capture_observer.gd"
    target.parent.mkdir(parents=True)
    shutil.copy2(observer, target)
    sidecar = observer.with_suffix(observer.suffix + ".uid")
    if sidecar.exists():
        shutil.copy2(sidecar, target.with_suffix(target.suffix + ".uid"))
    settings = (ROOT / "project.godot").read_text()
    settings = re.sub(r"(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)", "", settings)
    settings = settings.replace('config/icon="res://icon.svg"\n', "")
    (project / "project.godot").write_text(settings, newline="\n")
    ledger = {path.relative_to(project).as_posix(): identity(path)
              for path in sorted(project.rglob("*")) if path.is_file()}
    save(output / "copy-ledger.json", ledger)
    return project, ledger


def run_observer(godot, output, project, label, scene):
    """Launch one owned windowed child and stop only that child if its budget expires."""
    folder = output / label
    folder.mkdir()
    command = [godot, "--path", str(project), "--windowed", "--resolution", "1280x800",
               "--position", "40,40", "--log-file", str(folder / "engine.log"),
               "--script", "res://tools/s06/capture_observer.gd", "--",
               f"--scene={scene}", f"--label={label}", f"--output={folder}"]
    record = {"argv": command, "cleanup": []}
    with (folder / "stdout.log").open("wb") as stdout, (
            folder / "stderr.log").open("wb") as stderr:
        child = subprocess.Popen(command, cwd=project, stdout=stdout, stderr=stderr,
                                 env=environment(output / "runtime-user" / label))
        record["pid"] = child.pid
        try:
            record["exit"] = child.wait(timeout=OBSERVATION_SECONDS)
        except subprocess.TimeoutExpired:
            child.terminate()
            record["cleanup"].append("terminate")
            try:
                record["exit"] = child.wait(timeout=STOP_SECONDS)
            except subprocess.TimeoutExpired:
                child.kill()
                record["cleanup"].append("kill")
                record["exit"] = child.wait(timeout=STOP_SECONDS)
            record["timeout"] = True
    record["reaped"] = child.poll() is not None
    text = "".join((folder / name).read_text(errors="replace")
                   for name in ["stdout.log", "stderr.log", "engine.log"]
                   if (folder / name).exists())
    record["diagnostics"] = [line for line in text.splitlines() if DIAGNOSTIC.search(line)]
    receipt_path = folder / "observation.json"
    record["observation"] = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
    return record


def observation_criteria(label, record, folder):
    """Check complete frame, route and marker/body receipts for one saved camera scene."""
    observation = record.get("observation") or {}
    captures = observation.get("captures", [])
    expected = ["static"] + [f"{route}-{tick:03d}"
                              for route in ROUTES for tick in CAPTURE_TICKS[route]]
    capture_names = [row.get("capture") for row in captures]
    pngs = []
    for row in captures:
        path = folder / row.get("png", "")
        if path.is_file():
            pngs.append({"path": path.name, **identity(path)})
    routes = observation.get("routes", {})
    route_results = all(routes.get(route, {}).get("samples", 0) > max(CAPTURE_TICKS[route])
                        and routes[route].get("timed_out") is False for route in ROUTES)
    return {
        "exit_zero": record.get("exit") == 0,
        "reaped": record.get("reaped") is True,
        "no_diagnostics": not record.get("diagnostics"),
        "observer_ok": observation.get("ok") is True,
        "capture_names": capture_names == expected,
        "route_results": route_results,
        "pngs_1280x800": len(pngs) == len(expected) and all(
            row.get("save_error") == 0 and row.get("viewport_px") == [1280, 800]
            for row in captures),
        "markers_match_bodies": len(captures) == len(expected) and all(
            row.get("marker_body_distance_m", 1.0) <= 0.000001
            and row.get("marker_body_distance_px", 1.0) <= 0.000001
            for row in captures),
        "pngs": pngs,
        "label_matches": observation.get("scene") == label,
    }


def main():
    """Spend one import and one automatic windowed observation per saved camera scene."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.godot is None:
        parser.error("godot not found on PATH; pass --godot")
    output = (args.output or Path(tempfile.mkdtemp(prefix="s06-windows-"))).resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("output must be a fresh empty directory")
    print(f"S06 Windows captures: {output}", flush=True)

    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                       text=True).strip()
    dirty = subprocess.check_output([
        "git", "status", "--porcelain", "--", "project.godot", "tests/fixtures/s02",
        "tests/fixtures/s03", "tests/fixtures/s04", "tests/fixtures/s06",
        "art/models/spikes", "tools/s01", "tools/s02", "tools/s04",
        "tools/s06/capture_observer.gd", "tools/s06/capture_windows.py",
        "tools/script_checks.py",
    ], cwd=ROOT, text=True).strip()
    runner_sources = {
        name: identity(ROOT / name)
        for name in ["tools/s06/capture_windows.py", "tools/script_checks.py"]
    }
    result = {"ok": False, "revision": revision, "dirty_inputs": dirty,
              "runner_sources": runner_sources, "platform": platform.platform(),
              "python": sys.version, "observations": {}}
    try:
        version = subprocess.run([args.godot, "--version"], capture_output=True, text=True,
                                 timeout=10, check=True).stdout.strip()
        if version != PIN:
            raise RuntimeError(f"expected {PIN}, got {version}")
        result["engine"] = {"version": version, **identity(Path(args.godot))}
        project, ledger = stage(output)
        import_log = output / "import.log"
        with import_log.open("wb") as stream:
            import_code = subprocess.run([
                args.godot, "--headless", "--editor", "--path", str(project),
                "--import", "--quit", "--log-file", str(output / "import.engine.log"),
            ], stdout=stream, stderr=subprocess.STDOUT,
                env=environment(output / "import-user"), timeout=IMPORT_SECONDS).returncode
        import_text = import_log.read_text(errors="replace")
        engine_log = output / "import.engine.log"
        if engine_log.exists():
            import_text += engine_log.read_text(errors="replace")
        import_diagnostics = [line for line in import_text.splitlines()
                              if DIAGNOSTIC.search(line)]
        result["import"] = {"exit": import_code, "diagnostics": import_diagnostics}
        if import_code != 0 or import_diagnostics:
            raise RuntimeError("import failed or reported diagnostics")
        for label, scene in SCENES.items():
            record = run_observer(args.godot, output, project, label, scene)
            record["criteria"] = observation_criteria(label, record, output / label)
            result["observations"][label] = record
        preserved = all((project / name).is_file()
                        and identity(project / name) == value for name, value in ledger.items())
        criteria = {
            "clean_inputs": not dirty,
            "import_clean": import_code == 0 and not import_diagnostics,
            "observations": all(all(value for key, value in row["criteria"].items()
                                    if key != "pngs")
                                for row in result["observations"].values()),
            "inputs_preserved": preserved,
        }
        result["criteria"] = criteria
        result["ok"] = all(criteria.values())
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        result["failure"] = str(error)
    save(output / "result.json", result)
    print(json.dumps({"ok": result["ok"], "failure": result.get("failure"),
                      "criteria": result.get("criteria")}, indent=1))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
