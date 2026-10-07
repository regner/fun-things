#!/usr/bin/env python3
"""Run the bounded two-process ENet session-contract proof without Steam or MCP addons."""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import signal
import socket
import struct
import subprocess
import tempfile
import time

from script_checks import (ROOT, DIAGNOSTIC, checked_command, compile_all,
                           engine_version, environment)

POLL_SECONDS = 0.02
STOP_SECONDS = 2.0
MAX_DATAGRAM = 65535
MOVEMENT_CHANNEL = 4  # Godot's two reserved ENet channels + application channel 3 - 1.
COMMAND_SIZES = {1: 8, 2: 48, 3: 44, 4: 8, 5: 4, 6: 6, 7: 8,
                 8: 24, 9: 8, 10: 12, 11: 16, 12: 24}


def movement_datagram(data):
    """Inspect ENet framing only; never decode or rewrite the Godot RPC payload."""
    if len(data) < 2:
        return False
    header = struct.unpack_from("!H", data)[0]
    if header & 0x4000:
        raise RuntimeError("compressed ENet packet unsupported by this focused proxy")
    offset = 4 if header & 0x8000 else 2
    movement = False
    while offset + 4 <= len(data):
        command = data[offset] & 0x0F
        channel = data[offset + 1]
        size = COMMAND_SIZES.get(command)
        if size is None or offset + size > len(data):
            raise RuntimeError("unrecognized/truncated ENet command")
        length = 0
        if command == 6:
            length = struct.unpack_from("!H", data, offset + 4)[0]
        elif command in {7, 9, 8, 12}:
            length = struct.unpack_from("!H", data, offset + 6)[0]
        movement |= command == 7 and channel == MOVEMENT_CHANNEL
        offset += size + length
    if offset != len(data):
        raise RuntimeError("invalid ENet command extent")
    return movement


class Proxy:
    """One loopback client route, with a bounded deterministic movement fault schedule."""

    def __init__(self, host_port, proxy_port, log):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.socket.bind(("127.0.0.1", proxy_port))
        except OSError:
            self.socket.close()
            raise
        self.socket.setblocking(False)
        self.host = ("127.0.0.1", host_port)
        self.client = None
        self.armed = False
        self.count = 0
        self.held = None
        self.held_at = 0.0
        self.events = []
        self.log = log

    def record(self, event, datagram_bytes=None):
        self.events.append(event)
        self.log.write(json.dumps({"event": event, "time": time.monotonic(),
                                  "datagram_bytes": datagram_bytes}) + "\n")
        self.log.flush()

    def poll(self):
        # A stale held packet cannot outlive the run or silently hold forever.
        if self.held is not None and time.monotonic() - self.held_at > 2:
            raise RuntimeError("proxy reorder deadline")
        for _ in range(64):
            try:
                data, source = self.socket.recvfrom(MAX_DATAGRAM)
            except BlockingIOError:
                return
            if source != self.host:
                self.client = source
                self.socket.sendto(data, self.host)
                continue
            if self.client is None:
                raise RuntimeError("host datagram before client route")
            if self.armed and movement_datagram(data):
                self.count += 1
                if self.count == 1:
                    self.held = data
                    self.held_at = time.monotonic()
                    self.record("hold_subset_A", len(data))
                    continue
                if self.count == 2:
                    self.socket.sendto(data, self.client)
                    self.socket.sendto(self.held, self.client)
                    self.held = None
                    self.record("deliver_B_then_A", len(data))
                    continue
                if self.count == 3:
                    self.record("drop_subset_A", len(data))
                    continue
                self.record("refresh_subset", len(data))
            self.socket.sendto(data, self.client)


def stop_children(children):
    """Signal only Popen objects created by this runner; never scan or kill by name."""
    for child in children:
        if child.poll() is None:
            child.terminate()
    deadline = time.monotonic() + STOP_SECONDS
    for child in children:
        try:
            child.wait(timeout=max(0.01, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=STOP_SECONDS)


def stage_fixture(directory):
    """Mirror the actual saved fixture, excluding every platform/native/dev addon."""
    project = directory / "project"
    project.mkdir()
    shutil.copytree(ROOT / "tests/fixtures/s03", project / "tests/fixtures/s03")
    (project / "project.godot").write_text(
        'config_version=5\n[application]\nconfig/name="S03 contract proof"\n'
        'run/main_scene="res://tests/fixtures/s03/boot.tscn"\n'
        '[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
    return project


def run(args, directory):
    started = time.monotonic()
    version = engine_version(args.godot)
    project = stage_fixture(directory)
    if not checked_command([args.godot, "--headless", "--editor", "--path", str(project),
                            "--import", "--quit", "--log-file", str(directory / "import.engine.log")],
                           directory / "import.log", environment(directory / "import-user")):
        raise RuntimeError("fixture import failed; see import.log")
    # Explicitly compile the source worktree's entire owned-script discovery set.
    if not compile_all(args.godot, directory):
        raise RuntimeError("owned-script compilation failed; see compilation.json")
    children = []
    logs = {}
    results = {}
    readiness = None
    offsets = {"host": 0, "client": 0}
    deadline = time.monotonic() + args.deadline
    proxy_log = (directory / "proxy.jsonl").open("w")
    proxy = Proxy(args.port, args.proxy_port, proxy_log)
    commands = {}
    try:
        def start(role, port):
            user = directory / role / "user"
            log_dir = directory / role / "logs"
            log_dir.mkdir(parents=True)
            command = [args.godot, "--headless", "--path", str(project),
                       "--log-file", str(log_dir / "engine.log"), "--",
                       "--role=" + role, "--port=" + str(port)]
            commands[role] = command
            logs[role] = (log_dir / "stdout.log").open("w")
            child = subprocess.Popen(command, stdout=logs[role], stderr=subprocess.STDOUT,
                                     env=environment(user))
            children.append(child)
            return child

        host = start("host", args.port)
        client = None
        while time.monotonic() < deadline:
            proxy.poll()
            for role in list(logs):
                # Read complete lines only: a partial readiness record is not readiness.
                with (directory / role / "logs/stdout.log").open() as output:
                    output.seek(offsets[role])
                    while True:
                        position = output.tell()
                        line = output.readline()
                        if not line.endswith("\n"):
                            offsets[role] = position
                            break
                        offsets[role] = output.tell()
                        if not line.startswith("S03 "):
                            continue
                        record = json.loads(line[4:])
                        if record["event"] == "ready" and role == "host":
                            readiness = record
                        elif record["event"] == "snapshots" and role == "host":
                            proxy.armed = True
                            proxy.record("armed")
                        elif record["event"] == "result":
                            results[role] = record
                            if record.get("ok") is not True:
                                raise RuntimeError(f"{role} assertion: {record.get('failure')}")
            if readiness and client is None:
                client = start("client", args.proxy_port)
            if len(results) == 2 and all(child.poll() is not None for child in children):
                break
            for index, child in enumerate(children):
                role = "host" if index == 0 else "client"
                if child.poll() is not None and role not in results:
                    raise RuntimeError(f"{role} exited before a result ({child.returncode})")
            time.sleep(POLL_SECONDS)
        else:
            raise RuntimeError("runner wall-clock deadline; inspect retained process logs")
        if any(child.returncode != 0 for child in children):
            raise RuntimeError("nonzero process exit")
        for role in logs:
            for filename in ["stdout.log", "engine.log"]:
                text = (directory / role / "logs" / filename).read_text(errors="replace")
                if DIAGNOSTIC.search(text):
                    raise RuntimeError(f"{role}/{filename} contains engine/script diagnostics")
        if proxy.count != 5 or proxy.events.count("refresh_subset") != 2:
            raise RuntimeError(f"native movement fault schedule incomplete: {proxy.events}")
        if results["host"]["user_dir"] == results["client"]["user_dir"]:
            raise RuntimeError("process user directories overlap")
        return {"ok": True, "engine": version, "commands": commands, "results": results,
                "ready": readiness, "proxy": proxy.events,
                "ports": {"host": args.port, "proxy": args.proxy_port},
                "platform": platform.platform(), "duration_seconds": time.monotonic() - started,
                "process_ids": [child.pid for child in children],
                "fixture_sha256": {
                    path.relative_to(project).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in sorted((project / "tests/fixtures/s03").iterdir()) if path.is_file()
                }}
    finally:
        stop_children(children)
        for output in logs.values():
            output.close()
        proxy.socket.close()
        proxy_log.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot") or "godot")
    parser.add_argument("--port", type=int, default=24680)
    parser.add_argument("--proxy-port", type=int, default=24681)
    parser.add_argument("--deadline", type=float, default=25)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535 or not 1 <= args.proxy_port <= 65535:
        parser.error("ports must be 1..65535")
    if args.port == args.proxy_port or not 1 <= args.deadline <= 120:
        parser.error("ports must differ; deadline must be 1..120 seconds")
    directory = (args.output or Path(tempfile.mkdtemp(prefix="s03-run-"))).resolve()
    if directory.is_relative_to(ROOT):
        parser.error("evidence output must be outside the checkout")
    directory.mkdir(parents=True, exist_ok=True)
    # Avoid accidentally mixing two attempts' readiness/results.
    if any(directory.iterdir()):
        parser.error("output must be a fresh empty directory")
    print(f"S03 evidence: {directory}", flush=True)
    def interrupted(_signal, _frame):
        raise KeyboardInterrupt
    previous_handler = signal.signal(signal.SIGTERM, interrupted)
    try:
        result = run(args, directory)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        result = {"ok": False, "failure": str(error)}
    except KeyboardInterrupt:
        result = {"ok": False, "failure": "runner interrupted; own children stopped"}
    finally:
        signal.signal(signal.SIGTERM, previous_handler)
    (directory / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
