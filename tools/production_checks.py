#!/usr/bin/env python3
"""Run the canonical production script, Python, and GUT checks."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from script_checks import PIN, engine_version, environment

ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC = re.compile(r"(?:SCRIPT ERROR:|ERROR:|WARNING:)")
GUT_VERSION = "9.7.1"


def run_command(command, log, *, cwd=ROOT, env=None, timeout=180, reject_diagnostics=True):
    """Run one bounded child and retain enough output to review its result."""
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
        return False, None

    text = log.read_text(encoding="utf-8", errors="replace")
    if "--log-file" in command:
        engine_log = Path(command[command.index("--log-file") + 1])
        if engine_log.exists():
            text += engine_log.read_text(encoding="utf-8", errors="replace")
    passed = result.returncode == 0
    if reject_diagnostics:
        passed = passed and not DIAGNOSTIC.search(text)
    return passed, result.returncode


def gut_command(godot, project, junit_path=None, diagnostic_failure=False, test_dirs=None):
    """Build the test-only GUT CLI command without enabling its editor plugin."""
    command = [
        godot,
        "--headless",
        "--path",
        str(project),
        "--script",
        "res://addons/gut/gut_cmdln.gd",
    ]
    if diagnostic_failure:
        command.extend([
            "-gconfig=",
            "-gdir=res://tests/diagnostic/gut_failure",
            "-gexit",
            "-gdisable_colors",
        ])
    elif test_dirs:
        command.append("-gconfig=")
        command.extend(f"-gdir=res://{test_dir}" for test_dir in test_dirs)
        command.extend(["-ginclude_subdirs", "-gexit", "-gdisable_colors"])
    if junit_path is not None and not diagnostic_failure:
        command.append(f"-gjunit_xml_file={junit_path.as_posix()}")
    return command


def verify_gut_pin():
    """Reject an unreviewed vendor version before any test execution."""
    plugin = (ROOT / "addons/gut/plugin.cfg").read_text(encoding="utf-8")
    return f'version="{GUT_VERSION}"' in plugin


def main():
    """Run all production checks and return nonzero when any required layer fails."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot") or "godot")
    parser.add_argument("--gdstyle", default=shutil.which("gdstyle") or "gdstyle")
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--gut-dir",
        action="append",
        default=[],
        help="run only a tests/unit subdirectory; may be repeated",
    )
    args = parser.parse_args()
    for test_dir in args.gut_dir:
        normalized = Path(test_dir).as_posix().strip("/")
        if not normalized.startswith("tests/unit/") or ".." in Path(normalized).parts:
            parser.error("--gut-dir must name a subdirectory below tests/unit")
    gut_dirs = [Path(test_dir).as_posix().strip("/") for test_dir in args.gut_dir]

    output = (args.output or Path(tempfile.mkdtemp(prefix="production-checks-"))).resolve()
    if output.is_relative_to(ROOT):
        parser.error("evidence output must be outside the checkout")
    if output.exists() and any(output.iterdir()):
        parser.error("output must be a fresh empty directory")
    output.mkdir(parents=True, exist_ok=True)
    print(f"Production check evidence: {output}", flush=True)

    try:
        version = engine_version(args.godot)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        (output / "summary.json").write_text(
            json.dumps({"ok": False, "engine": str(error)}, indent=2) + "\n",
            encoding="utf-8",
        )
        print(error)
        return 1

    results = {
        "engine": {"ok": version == PIN, "version": version},
        "gut_pin": {"ok": verify_gut_pin(), "version": GUT_VERSION},
    }
    commands = {}

    script_output = output / "script-checks"
    script_command = [
        os.fspath(Path(sys.executable)),
        os.fspath(ROOT / "tools/script_checks.py"),
        "--godot",
        args.godot,
        "--gdstyle",
        args.gdstyle,
        "--output",
        os.fspath(script_output),
    ]
    commands["owned_scripts"] = script_command
    passed, returncode = run_command(
        script_command,
        output / "script-checks.log",
        timeout=240,
        reject_diagnostics=False,
    )
    results["owned_scripts"] = {"ok": passed, "returncode": returncode}

    python_command = [
        os.fspath(Path(sys.executable)),
        "-m",
        "unittest",
        "discover",
        "-s",
        "tools",
        "-p",
        "*test*.py",
    ]
    commands["python_tests"] = python_command
    passed, returncode = run_command(
        python_command,
        output / "python-tests.log",
        timeout=180,
        reject_diagnostics=False,
    )
    results["python_tests"] = {"ok": passed, "returncode": returncode}

    project = script_output / "compiler-project"
    if project.is_dir():
        gut_env = environment(output / "gut-user")
        import_command = [
            args.godot,
            "--headless",
            "--editor",
            "--path",
            os.fspath(project),
            "--import",
            "--quit",
            "--log-file",
            os.fspath(output / "gut-import.engine.log"),
        ]
        commands["gut_import"] = import_command
        passed, returncode = run_command(
            import_command,
            output / "gut-import.log",
            cwd=project,
            env=gut_env,
            timeout=120,
        )
        results["gut_import"] = {"ok": passed, "returncode": returncode}

        default_command = gut_command(
            args.godot,
            project,
            output / "gut-results.xml",
            test_dirs=gut_dirs,
        )
        default_command[1:1] = ["--log-file", os.fspath(output / "gut.engine.log")]
        commands["gut_tests"] = default_command
        passed, returncode = run_command(
            default_command,
            output / "gut.log",
            cwd=project,
            env=gut_env,
            timeout=120,
        )
        results["gut_tests"] = {"ok": passed, "returncode": returncode}

        negative_command = gut_command(args.godot, project, diagnostic_failure=True)
        negative_command[1:1] = ["--log-file", os.fspath(output / "gut-negative.engine.log")]
        commands["gut_negative"] = negative_command
        _passed, returncode = run_command(
            negative_command,
            output / "gut-negative.log",
            cwd=project,
            env=gut_env,
            timeout=120,
            reject_diagnostics=False,
        )
        negative_text = (output / "gut-negative.log").read_text(
            encoding="utf-8", errors="replace"
        )
        negative_detected = returncode not in (None, 0) and "intentional GUT failure" in negative_text
        results["gut_negative"] = {
            "ok": negative_detected,
            "observed_returncode": returncode,
        }
    else:
        for name in ("gut_import", "gut_tests", "gut_negative"):
            results[name] = {"ok": False, "reason": "script-check mirror unavailable"}

    overall = all(row["ok"] for row in results.values())
    summary = {"ok": overall, "commands": commands, "results": results}
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(results, indent=2))
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
