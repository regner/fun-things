#!/usr/bin/env python3
"""Run the vendored road generator's clean-import, persistence, and graphical preflight."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from script_checks import PIN, engine_version, environment
ROOT = Path(__file__).resolve().parents[1]
SAFE_WINDOW_FPS = 60
DIAGNOSTIC = re.compile(r"(?:SCRIPT ERROR:|ERROR:|WARNING:)")
SCENE = "res://tests/integration/road_generator/preflight.tscn"
IMPORT_KNOWN_DIAGNOSTICS = {
    "WARNING: 'res://addons/road-generator/resources/road_texture.material': "
    "In external resource #0, invalid UID: 'uid://dw2fxo5lrwyag' - using text path "
    "instead: 'res://addons/road-generator/resources/road_texture@2x.png'.",
    "ERROR: 1 RID allocations of type "
    "'N13RendererDummy15MaterialStorage13DummyMaterialE' were leaked at exit.",
    "ERROR: 1 RID allocations of type "
    "'N13RendererDummy15MaterialStorage11DummyShaderE' were leaked at exit.",
    "ERROR: 1 RID allocations of type 'N13RendererDummy9DummyMeshE' were leaked at exit.",
    "ERROR: 1 RID allocations of type 'N17RendererSceneCull8InstanceE' were leaked at exit.",
    "ERROR: Pages in use exist at exit in PagedAllocator: "
    "N20RasterizerSceneDummy21GeometryInstanceDummyE",
    "WARNING: Leaked instance dependency: Bug - did not call instance_notify_deleted when freeing.",
    "WARNING: 4 ObjectDB instances were leaked at exit (run with `--verbose` for details).",
}



def capped_window_arguments() -> list[str]:
    """Return the explicit Godot arguments required for a 60 FPS window cap."""
    return ["--max-fps", str(SAFE_WINDOW_FPS)]


def require_capped_window(command: list[str]) -> None:
    """Reject a windowed command unless it contains exactly the approved FPS cap."""
    values = [command[index + 1] for index, value in enumerate(command[:-1])
              if value == "--max-fps"]
    if values != [str(SAFE_WINDOW_FPS)]:
        raise ValueError(f"windowed Godot requires exactly --max-fps {SAFE_WINDOW_FPS}")

def classify_diagnostics(text, known_diagnostics=()):
    """Split diagnostics into explicitly recorded known lines and all other failures."""
    diagnostics = [line for line in text.splitlines() if DIAGNOSTIC.search(line)]
    known = [line for line in diagnostics if line in known_diagnostics]
    unexpected = [line for line in diagnostics if line not in known_diagnostics]
    return known, unexpected


def run_command(command, log, *, cwd, env, timeout, known_diagnostics=()):
    """Run one bounded child and reject nonzero exit or unexpected diagnostics."""
    try:
        with log.open("w", encoding="utf-8") as output:
            result = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                stdout=output,
                stderr=subprocess.STDOUT,
                timeout=timeout,
                check=False,
            )
    except subprocess.TimeoutExpired:
        with log.open("a", encoding="utf-8") as output:
            output.write("\nCHECK DEADLINE EXCEEDED\n")
        return False, None, [], ["CHECK DEADLINE EXCEEDED"]

    text = log.read_text(encoding="utf-8", errors="replace")
    if "--log-file" in command:
        engine_log = Path(command[command.index("--log-file") + 1])
        if engine_log.is_file():
            text += engine_log.read_text(encoding="utf-8", errors="replace")
    known, unexpected = classify_diagnostics(text, known_diagnostics)
    return result.returncode == 0 and not unexpected, result.returncode, known, unexpected


def stage_project(destination):
    """Create a dependency-minimal clean project around the committed vendor and fixture."""
    shutil.copytree(ROOT / "addons/road-generator", destination / "addons/road-generator")
    fixture = destination / "tests/integration/road_generator"
    fixture.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / "tests/integration/road_generator", fixture)
    (destination / "project.godot").write_text(
        """config_version=5

[application]

config/name=\"Road Generator Preflight\"
run/main_scene=\"res://tests/integration/road_generator/preflight.tscn\"
config/features=PackedStringArray(\"4.8\")

[display]

window/size/viewport_width=640
window/size/viewport_height=480

[editor_plugins]

enabled=PackedStringArray(\"res://addons/road-generator/plugin.cfg\")

[rendering]

renderer/rendering_method=\"gl_compatibility\"
renderer/rendering_method.mobile=\"gl_compatibility\"
""",
        encoding="utf-8",
    )


def preflight_command(godot, project, output, label, *, windowed):
    """Build one deterministic fixture launch with bounded external outputs."""
    result = output / f"{label}-result.json"
    saved_scene = output / f"{label}-saved.tscn"
    command = [godot]
    if windowed:
        command.extend(capped_window_arguments())
    else:
        command.append("--headless")
    command.extend([
        "--path",
        os.fspath(project),
        "--log-file",
        os.fspath(output / f"{label}.engine.log"),
        SCENE,
        "--",
        f"--result={result.as_posix()}",
        f"--saved-scene={saved_scene.as_posix()}",
    ])
    if windowed:
        command.extend([
            "--windowed-check",
            f"--capture={(output / 'windowed.png').as_posix()}",
        ])
        require_capped_window(command)
    return command


def main():
    """Parse arguments, run all preflight layers, and retain a structured summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot") or "godot")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    output = (args.output or Path(tempfile.mkdtemp(prefix="road-generator-preflight-"))).resolve()
    if output.is_relative_to(ROOT):
        parser.error("evidence output must be outside the checkout")
    if output.exists() and any(output.iterdir()):
        parser.error("output must be a fresh empty directory")
    output.mkdir(parents=True, exist_ok=True)
    print(f"Road generator preflight evidence: {output}", flush=True)

    try:
        version = engine_version(args.godot)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        (output / "summary.json").write_text(
            json.dumps({"ok": False, "engine": str(error)}, indent=2) + "\n",
            encoding="utf-8",
        )
        return 1

    project = output / "project"
    stage_project(project)
    env = environment(output / "user")
    commands = {}
    results = {"engine": {"ok": version == PIN, "version": version}}

    import_command = [
        args.godot,
        "--headless",
        "--editor",
        "--path",
        os.fspath(project),
        "--import",
        "--quit",
        "--log-file",
        os.fspath(output / "import.engine.log"),
    ]
    commands["clean_import"] = import_command
    passed, returncode, known, unexpected = run_command(
        import_command,
        output / "import.log",
        cwd=project,
        env=env,
        timeout=120,
        known_diagnostics=IMPORT_KNOWN_DIAGNOSTICS,
    )
    results["clean_import"] = {
        "ok": passed,
        "returncode": returncode,
        "known_diagnostics": known,
        "unexpected_diagnostics": unexpected,
    }

    for label, windowed in (("headless", False), ("windowed", True)):
        command = preflight_command(
            args.godot, project, output, label, windowed=windowed
        )
        commands[label] = command
        passed, returncode, known, unexpected = run_command(
            command,
            output / f"{label}.log",
            cwd=project,
            env=env,
            timeout=90,
        )
        result_path = output / f"{label}-result.json"
        semantic_result = None
        if result_path.is_file():
            semantic_result = json.loads(result_path.read_text(encoding="utf-8"))
            passed = passed and semantic_result.get("ok") is True
        else:
            passed = False
        results[label] = {
            "ok": passed,
            "returncode": returncode,
            "known_diagnostics": known,
            "unexpected_diagnostics": unexpected,
            "result": semantic_result,
        }

    overall = all(row["ok"] for row in results.values())
    summary = {"ok": overall, "commands": commands, "results": results}
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(results, indent=2))
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
