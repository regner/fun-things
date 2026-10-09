#!/usr/bin/env python3
"""Discover and explicitly compile every owned GDScript, including unused scripts."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
VENDOR = {"addons/godot_mcp_toolkit", "addons/gut", "addons/road-generator"}
DIAGNOSTIC = re.compile(r"(?:SCRIPT ERROR:|ERROR:|WARNING:)")
PIN = "4.8.dev7.official.c971f93e7"
PROJECT_IMPORT_TIMEOUT_SECONDS = 300
PROJECT_STYLE_TIMEOUT_SECONDS = 180
SCRIPT_COMPILE_TIMEOUT_SECONDS = 30


def owned_scripts(root=ROOT):
    """Honor hidden/.gdignore directories while excluding only named vendor addons."""
    found = []
    for directory, children, files in os.walk(root, followlinks=False):
        relative = Path(directory).relative_to(root)
        if ".gdignore" in files or relative.as_posix() in VENDOR:
            children[:] = []
            continue
        children[:] = sorted(name for name in children
                             if not name.startswith(".") and
                             not (Path(directory) / name).is_symlink())
        found.extend(Path(directory) / name for name in sorted(files)
                     if name.endswith(".gd") and not name.startswith("."))
    return sorted(found)


def environment(directory):
    """Give each child its own writable configuration, user data and cache."""
    env = os.environ.copy()
    # Windows Godot resolves user/config/cache roots from APPDATA/LOCALAPPDATA, not XDG.
    for variable, folder in [("XDG_DATA_HOME", "data"), ("XDG_CONFIG_HOME", "config"),
                             ("XDG_CACHE_HOME", "cache"), ("APPDATA", "appdata"),
                             ("LOCALAPPDATA", "localappdata")]:
        path = directory / folder
        path.mkdir(parents=True, exist_ok=True)
        env[variable] = str(path)
    return env


def engine_version(godot):
    result = subprocess.run([godot, "--version"], capture_output=True, text=True,
                            timeout=10, check=True)
    if result.stdout.strip() != PIN:
        raise RuntimeError(f"expected pinned engine {PIN}; got {result.stdout.strip()}")
    return result.stdout.strip()


def checked_command(command, log, env, timeout=30):
    """Retain full output; an error/warning fails even when the exit status is zero."""
    try:
        with log.open("w") as output:
            result = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT,
                                    env=env, timeout=timeout, check=False)
        text = log.read_text(errors="replace")
        if "--log-file" in command:
            engine_log = Path(command[command.index("--log-file") + 1])
            if engine_log.exists():
                text += engine_log.read_text(errors="replace")
        return result.returncode == 0 and not DIAGNOSTIC.search(text)
    except subprocess.TimeoutExpired:
        with log.open("a") as output:
            output.write("\nCHECK DEADLINE EXCEEDED\n")
        return False


def compile_project_settings(settings):
    """Disable development-only editor and MCP startup in the isolated compile mirror."""
    settings = re.sub(r"(?ms)^\[editor_plugins\]\n.*?(?=^\[|\Z)", "", settings)
    return re.sub(r"(?m)^MCPRuntimeServer=.*\n", "", settings)


def compile_all(godot, directory):
    """Import for class discovery, then compile each script in a separate engine invocation."""
    env = environment(directory / "compiler-user")
    scripts = owned_scripts()
    manifest = [path.relative_to(ROOT).as_posix() for path in scripts]
    (directory / "scripts.json").write_text(json.dumps(manifest, indent=2) + "\n")
    # A clean dependency mirror makes class discovery independent of the source
    # editor/cache. Preserve gameplay autoloads and runtime settings, but do not
    # execute editor plugins or the development-only MCP runtime during setup.
    project = directory / "compiler-project"
    mirror_dotfiles = {".gdignore", ".gutconfig.json"}
    shutil.copytree(ROOT, project, ignore=lambda _path, names: [
        name for name in names if (name.startswith(".") and name not in mirror_dotfiles)
        or name == "__pycache__"
    ])
    settings = compile_project_settings((project / "project.godot").read_text())
    (project / "project.godot").write_text(settings)
    setup_ok = checked_command([godot, "--headless", "--editor", "--path", str(project),
                                "--import", "--quit",
                                "--log-file", str(directory / "compiler-import.engine.log")],
                               directory / "compiler-import.log", env,
                               timeout=PROJECT_IMPORT_TIMEOUT_SECONDS)
    (directory / "compiler-setup.json").write_text(json.dumps({"ok": setup_ok}) + "\n")
    results = []
    for index, path in enumerate(scripts):
        relative = path.relative_to(ROOT).as_posix()
        ok = checked_command([godot, "--headless", "--path", str(project),
                              "--log-file", str(directory / f"compile-{index}.engine.log"),
                              "--check-only", "--script", "res://" + relative],
                             directory / f"compile-{index}.log", env,
                             timeout=SCRIPT_COMPILE_TIMEOUT_SECONDS)
        results.append({"script": relative, "ok": ok})
    (directory / "compilation.json").write_text(json.dumps(results, indent=2) + "\n")
    return setup_ok and bool(results) and all(row["ok"] for row in results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot") or "godot")
    parser.add_argument("--gdstyle", default=shutil.which("gdstyle") or "gdstyle")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--style-only", action="store_true")
    args = parser.parse_args()
    directory = (args.output or Path(tempfile.mkdtemp(prefix="s03-checks-"))).resolve()
    if directory.is_relative_to(ROOT):
        parser.error("evidence output must be outside the checkout")
    if directory.exists() and any(directory.iterdir()):
        parser.error("output must be a fresh empty directory")
    directory.mkdir(parents=True, exist_ok=True)
    print(f"Check evidence: {directory}", flush=True)
    scripts = [str(path) for path in owned_scripts()]
    formatting = checked_command([args.gdstyle, "fmt", "--check", *scripts],
                                 directory / "formatting.log", os.environ.copy(),
                                 timeout=PROJECT_STYLE_TIMEOUT_SECONDS)
    style = checked_command([args.gdstyle, "--max-line-length", "100", "--max-warnings", "0",
                             *scripts], directory / "style.log", os.environ.copy(),
                            timeout=PROJECT_STYLE_TIMEOUT_SECONDS)
    if not style:
        print((directory / "style.log").read_text())
    compilation = None
    if not args.style_only:
        engine_version(args.godot)
        compilation = compile_all(args.godot, directory)
    print(json.dumps({"formatting": formatting, "style": style, "compilation": compilation}))
    return 0 if formatting and style and compilation is not False else 1


if __name__ == "__main__":
    raise SystemExit(main())
