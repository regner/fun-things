#!/usr/bin/env python3
"""Run a bounded two-process ENet baseline and state-apply case."""

import argparse
import os
from pathlib import Path
import shutil
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
SUCCESS = "M1-A2.2 RESULT"


def available_port():
    """Reserve an ephemeral UDP port long enough to select the test endpoint."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def command(godot, role, port, log_path):
    """Build one hard-timeout-wrapped pinned-engine child command."""
    timeout = shutil.which("timeout")
    if timeout is None:
        raise RuntimeError("GNU timeout is required for every Godot invocation")
    return [
        timeout,
        "20",
        godot,
        "--headless",
        "--path",
        os.fspath(ROOT),
        "--log-file",
        os.fspath(log_path),
        "res://tests/integration/replication/replication_process.tscn",
        "--",
        f"--role={role}",
        f"--port={port}",
    ]


def main():
    """Launch host then client, inspect logs, and stop only owned children."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot") or "godot")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must stay outside the checkout")
    if output.exists() and any(output.iterdir()):
        parser.error("output must be a fresh empty directory")
    output.mkdir(parents=True, exist_ok=True)

    port = available_port()
    children = []
    streams = []
    try:
        for role in ("host", "client"):
            stdout_path = output / f"{role}.stdout.log"
            stream = stdout_path.open("w", encoding="utf-8")
            streams.append(stream)
            child = subprocess.Popen(
                command(args.godot, role, port, output / f"{role}.engine.log"),
                cwd=ROOT,
                stdout=stream,
                stderr=subprocess.STDOUT,
            )
            children.append((role, child, stdout_path))
            if role == "host":
                time.sleep(0.35)

        failed = []
        for role, child, _stdout_path in children:
            try:
                returncode = child.wait(timeout=25)
            except subprocess.TimeoutExpired:
                child.terminate()
                returncode = child.wait(timeout=3)
            if returncode != 0:
                failed.append(f"{role} exit {returncode}")
    finally:
        for _role, child, _stdout_path in children:
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=3)
        for stream in streams:
            stream.close()

    diagnostics = []
    for role, _child, stdout_path in children:
        text = stdout_path.read_text(encoding="utf-8", errors="replace")
        engine_text = (output / f"{role}.engine.log").read_text(
            encoding="utf-8", errors="replace"
        )
        if SUCCESS not in text or '"ok":true' not in text:
            failed.append(f"{role} missing success receipt")
        for marker in ("SCRIPT ERROR:", "ERROR:", "WARNING:"):
            if marker in text or marker in engine_text:
                diagnostics.append(f"{role} emitted {marker}")

    if failed or diagnostics:
        print("; ".join(failed + diagnostics))
        return 1
    print(f"M1-A2.2 ENet integration passed on UDP {port}; evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
