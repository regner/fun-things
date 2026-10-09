#!/usr/bin/env python3
"""Run stopped-exit and abrupt-disconnect S04 regressions in separate processes."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_s03 import stop_children
from run_s04 import stage
from script_checks import DIAGNOSTIC, ROOT, checked_command, engine_version, environment

SCENARIOS = ["stopped-exit", "abrupt-disconnect"]


def records(path):
    """Read complete structured lifecycle records from one process log."""
    return [json.loads(line.removeprefix("S04 ")) for line in path.read_text().splitlines()
            if line.startswith("S04 ")]


def run_scenario(godot, project, directory, port, scenario):
    """Run one host/client lifecycle route and reject diagnostics or missing outcomes."""
    directory.mkdir()
    children = {}
    logs = {}
    commands = {}
    deadline = time.monotonic() + 25

    def start(role):
        role_directory = directory / role
        role_directory.mkdir()
        command = [godot, "--headless", "--path", str(project),
                   "--log-file", str(role_directory / "engine.log"),
                   "res://tests/fixtures/s04/boot.tscn", "--",
                   "--role=" + role, "--port=" + str(port),
                   "--scenario=" + scenario]
        commands[role] = command
        logs[role] = (role_directory / "stdout.log").open("w")
        children[role] = subprocess.Popen(
            command, stdout=logs[role], stderr=subprocess.STDOUT,
            env=environment(role_directory / "user"))

    try:
        start("host")
        client_started = False
        while time.monotonic() < deadline:
            for output in logs.values():
                output.flush()
            host_rows = records(directory / "host/stdout.log")
            if not client_started and any(row["event"] == "ready" for row in host_rows):
                start("client")
                client_started = True
            complete = client_started and all(
                any(row["event"] == "scenario_result" for row in records(
                    directory / role / "stdout.log")) for role in ["host", "client"])
            if complete and all(child.poll() is not None for child in children.values()):
                break
            for role, child in children.items():
                if child.poll() is not None and not any(
                        row["event"] == "scenario_result" for row in records(
                            directory / role / "stdout.log")):
                    raise RuntimeError(f"{scenario} {role} exited before result")
            time.sleep(0.01)
        else:
            raise RuntimeError(f"{scenario} lifecycle deadline")

        if any(child.returncode != 0 for child in children.values()):
            raise RuntimeError(f"{scenario} process returned nonzero")
        outcomes = {}
        for role in ["host", "client"]:
            rows = records(directory / role / "stdout.log")
            outcomes[role] = next(row for row in reversed(rows)
                                  if row["event"] == "scenario_result")
            for name in ["stdout.log", "engine.log"]:
                text = (directory / role / name).read_text(errors="replace")
                if DIAGNOSTIC.search(text):
                    raise RuntimeError(f"diagnostic in {scenario} {role}/{name}")
        ok = all(row["ok"] for row in outcomes.values())
        if scenario == "stopped-exit":
            ok = ok and outcomes["client"]["rate_limit_observed"]
        elif scenario == "abrupt-disconnect":
            ok = ok and outcomes["host"]["coasting_snapshots"] > 0
        return {"ok": ok, "diagnostic_free": True, "outcomes": outcomes,
                "commands": commands,
                "exits": {role: child.returncode for role, child in children.items()}}
    finally:
        stop_children(list(children.values()))
        for output in logs.values():
            output.close()


def main():
    """Stage immutable fixture sources and retain both lifecycle regression outcomes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", required=True)
    parser.add_argument("--port", type=int, default=25320)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.port < 1 or args.port + len(SCENARIOS) > 65535:
        parser.error("port range must fit both lifecycle scenarios")
    directory = (args.output or Path(tempfile.mkdtemp(prefix="s04-lifecycle-"))).resolve()
    if directory.is_relative_to(ROOT):
        parser.error("output must be outside checkout")
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        parser.error("fresh empty output required")

    version = engine_version(args.godot)
    project = stage(directory)
    hashes = {str(path.relative_to(project)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in project.rglob("*") if path.is_file()}
    imported = checked_command(
        [args.godot, "--headless", "--editor", "--path", str(project),
         "--import", "--quit"], directory / "import.log", environment(directory / "import-user"))
    results = {}
    if imported:
        for index, scenario in enumerate(SCENARIOS):
            results[scenario] = run_scenario(
                args.godot, project, directory / scenario, args.port + index, scenario)
    unchanged = all(hashlib.sha256((project / path).read_bytes()).hexdigest() == digest
                    for path, digest in hashes.items())
    report = {"ok": imported and len(results) == len(SCENARIOS)
              and all(row["ok"] for row in results.values()) and unchanged,
              "version": version, "results": results, "source_unchanged": unchanged,
              "source_sha256": hashes}
    (directory / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in ["ok", "results", "source_unchanged"]}))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
