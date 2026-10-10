#!/usr/bin/env python3
"""Build and inspect the four committed desktop export presets with pinned templates."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from s08_x.inspect_exports import inspect


ROOT = Path(__file__).resolve().parents[1]
ENGINE_VERSION = "4.8.dev7.official.c971f93e7"
TEMPLATE_DIRECTORY = "4.8.dev7"
TEMPLATE_HASHES = {
    "linux_debug.x86_64": "8b2871a1e2f8baf482282422f7e64cd7cfcc713eb53d8db671025b041bb23eb9",
    "linux_release.x86_64": "c436b976ff5ac2e5f3197732ba7d9462267573e5a108782f84928d0606885695",
    "windows_debug_x86_64.exe": "c3287ae1c7fad6f6f2e0e09b0ebbb1321b49ec2423b74d513f12649e4c03bff6",
    "windows_release_x86_64.exe": "b538554df997ea699122d5b31f2ea8929301bcf3017e12dba664d85d351f60cd",
}
EXPORTS = (
    ("Windows Debug", "debug", "windows-debug/FunThingsDebug.exe"),
    ("Windows Release", "release", "windows-release/FunThings.exe"),
    ("Linux Debug", "debug", "linux-debug/FunThingsDebug.x86_64"),
    ("Linux Release", "release", "linux-release/FunThings.x86_64"),
)
MISSING_DEPENDENCY_MARKERS = (
    "could not resolve resource",
    "failed loading resource",
    "missing dependency",
    "no loader found for resource",
)


def sha256(path: Path) -> str:
    """Return one complete file's SHA-256 identity."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def default_template_root() -> Path:
    """Resolve Godot's platform template root without writing inside the checkout."""
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise RuntimeError("APPDATA is required to locate Godot export templates")
        return Path(appdata) / "Godot" / "export_templates" / TEMPLATE_DIRECTORY
    data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    return data_home / "godot" / "export_templates" / TEMPLATE_DIRECTORY


def verify_templates(template_root: Path) -> dict:
    """Require exact official template member hashes for the pinned engine release."""
    members = {}
    failures = []
    version_path = template_root / "version.txt"
    version = version_path.read_text(encoding="utf-8").strip() if version_path.is_file() else ""
    if version != "4.8.dev7":
        failures.append(f"template version is {version!r}, expected '4.8.dev7'")
    for name, expected_hash in TEMPLATE_HASHES.items():
        path = template_root / name
        actual_hash = sha256(path) if path.is_file() else ""
        members[name] = {"sha256": actual_hash, "expected_sha256": expected_hash}
        if actual_hash != expected_hash:
            failures.append(f"template identity mismatch: {name}")
    return {
        "ok": not failures,
        "directory": template_root.as_posix(),
        "version": version,
        "members": members,
        "failures": failures,
    }


def timeout_command(timeout_executable: str, seconds: int, command: list[str]) -> list[str]:
    """Wrap one invocation in the required external hard timeout."""
    return [timeout_executable, f"{seconds}s", *command]


def missing_dependency_lines(text: str) -> list[str]:
    """Return only dependency-resolution diagnostics, not unrelated editor teardown noise."""
    return [
        line for line in text.splitlines()
        if any(marker in line.lower() for marker in MISSING_DEPENDENCY_MARKERS)
    ]


def run_logged(command: list[str], log_path: Path, cwd: Path, timeout_seconds: int) -> dict:
    """Run one bounded command and retain merged output plus duration."""
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_seconds + 10,
        check=False,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(completed.stdout, encoding="utf-8")
    dependency_failures = missing_dependency_lines(completed.stdout)
    return {
        "command": command,
        "duration_seconds": round(time.monotonic() - started, 3),
        "exit_code": completed.returncode,
        "log": log_path.as_posix(),
        "missing_dependency_diagnostics": dependency_failures,
        "ok": completed.returncode == 0 and not dependency_failures,
    }


def build_exports(
    godot: str,
    output: Path,
    project: Path,
    timeout_executable: str,
) -> dict:
    """Export every committed desktop preset and inspect all resulting packages."""
    version_receipt = run_logged(
        timeout_command(timeout_executable, 30, [godot, "--version"]),
        output / "godot-version.log",
        project,
        30,
    )
    version_text = (output / "godot-version.log").read_text(encoding="utf-8").strip()
    version_receipt["version"] = version_text
    version_receipt["ok"] = version_receipt["ok"] and version_text == ENGINE_VERSION
    if not version_receipt["ok"]:
        return {
            "ok": False,
            "engine": version_receipt,
            "exports": [],
            "package_inspection": {
                "ok": False,
                "skipped": "pinned engine identity failed",
            },
        }

    export_receipts = []
    for preset, mode, relative_output in EXPORTS:
        destination = output / relative_output
        destination.parent.mkdir(parents=True, exist_ok=True)
        command = [
            godot,
            "--headless",
            "--path",
            os.fspath(project),
            f"--export-{mode}",
            preset,
            os.fspath(destination),
        ]
        export_receipts.append(
            {
                "preset": preset,
                **run_logged(
                    timeout_command(timeout_executable, 600, command),
                    output / "logs" / f"{preset.lower().replace(' ', '-')}.log",
                    project,
                    600,
                ),
            }
        )

    inspection = inspect(output, project)
    (output / "package-inspection.json").write_text(
        json.dumps(inspection, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "ok": (
            version_receipt["ok"]
            and all(receipt["ok"] for receipt in export_receipts)
            and inspection["ok"]
        ),
        "engine": version_receipt,
        "exports": export_receipts,
        "package_inspection": inspection,
    }


def main() -> int:
    """Validate pins, export to an external fresh root, and retain one summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot") or "godot")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--project", type=Path, default=ROOT)
    parser.add_argument("--template-root", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    project = args.project.resolve()
    if output.is_relative_to(project):
        parser.error("--output must stay outside the checkout")
    if output.exists() and any(output.iterdir()):
        parser.error("--output must be a fresh empty directory")
    output.mkdir(parents=True, exist_ok=True)
    timeout_executable = shutil.which("timeout")
    if timeout_executable is None:
        parser.error("GNU timeout is required for every Godot invocation")

    templates = verify_templates(
        (args.template_root or default_template_root()).resolve()
    )
    if templates["ok"]:
        builds = build_exports(
            args.godot,
            output,
            project,
            timeout_executable,
        )
    else:
        builds = {"ok": False, "skipped": "template identity failed"}
    summary = {"ok": templates["ok"] and builds["ok"], "templates": templates, "builds": builds}
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
