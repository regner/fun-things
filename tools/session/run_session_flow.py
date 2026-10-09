#!/usr/bin/env python3
"""Run bounded real-process ENet admission and cleanup cases."""

import argparse
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import queue
import re
import shutil
import socket
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
SCENE = "res://tests/integration/session/session_process.tscn"
PREFIX = "M1-A1.2 "
DIAGNOSTIC = re.compile(r"(?:SCRIPT ERROR:|ERROR:)")


@dataclass
class ManagedProcess:
    """Own one child, its output reader, structured events, and bounded cleanup."""

    name: str
    process: subprocess.Popen
    log_path: Path
    events: list[dict] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)
    event_queue: queue.Queue = field(default_factory=queue.Queue)
    reader: threading.Thread | None = None

    def start_reader(self):
        """Drain merged child output continuously so readiness cannot block on pipes."""
        self.reader = threading.Thread(target=self._read_output, daemon=True)
        self.reader.start()

    def _read_output(self):
        """Retain every line and enqueue only valid task receipts."""
        assert self.process.stdout is not None
        with self.log_path.open("w", encoding="utf-8", newline="\n") as output:
            for line in self.process.stdout:
                output.write(line)
                output.flush()
                clean = line.rstrip("\r\n")
                self.lines.append(clean)
                if not clean.startswith(PREFIX):
                    continue
                try:
                    event = json.loads(clean[len(PREFIX):])
                except json.JSONDecodeError:
                    continue
                self.events.append(event)
                self.event_queue.put(event)

    def wait_event(self, predicate, timeout):
        """Return the first matching event before one shared wall-clock deadline."""
        deadline = time.monotonic() + timeout
        for event in self.events:
            if predicate(event):
                return event
        while time.monotonic() < deadline:
            remaining = deadline - time.monotonic()
            try:
                event = self.event_queue.get(timeout=max(0.01, remaining))
            except queue.Empty:
                break
            if predicate(event):
                return event
        raise RuntimeError(f"{self.name}: expected event not observed")

    def finish(self, timeout=3.0):
        """Wait for normal exit, then stop only this runner-owned child."""
        try:
            returncode = self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:
                returncode = self.process.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                self.process.kill()
                returncode = self.process.wait(timeout=1.0)
        if self.reader is not None:
            self.reader.join(timeout=1.0)
        return returncode

    def diagnostics(self):
        """Return unexpected engine or script diagnostics from retained output."""
        return [line for line in self.lines if DIAGNOSTIC.search(line)]


class SessionFlowRunner:
    """Launch production host/client APIs under isolated process-local user roots."""

    def __init__(self, godot, output):
        self.godot = godot
        self.output = output
        self.children: list[ManagedProcess] = []

    def allocate_port(self):
        """Reserve and release one loopback UDP port immediately before a case."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]

    def launch(self, case, name, arguments):
        """Start one capped headless process with private Godot data and logs."""
        process_dir = self.output / case / name
        process_dir.mkdir(parents=True, exist_ok=True)
        user_dir = process_dir / "user"
        user_dir.mkdir()
        env = os.environ.copy()
        env.update(
            {
                "APPDATA": os.fspath(user_dir / "appdata"),
                "LOCALAPPDATA": os.fspath(user_dir / "localappdata"),
                "XDG_DATA_HOME": os.fspath(user_dir / "xdg-data"),
                "XDG_CONFIG_HOME": os.fspath(user_dir / "xdg-config"),
                "XDG_CACHE_HOME": os.fspath(user_dir / "xdg-cache"),
            }
        )
        command = [
            self.godot,
            "--headless",
            "--path",
            os.fspath(ROOT),
            "--log-file",
            os.fspath(process_dir / "engine.log"),
            SCENE,
            "--",
            *arguments,
        ]
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        child = ManagedProcess(name, process, process_dir / "stdout.log")
        child.start_reader()
        self.children.append(child)
        (process_dir / "command.json").write_text(
            json.dumps(command, indent=2) + "\n", encoding="utf-8"
        )
        return child

    @staticmethod
    def active(event):
        """Match one ACTIVE receipt."""
        return event.get("event") == "active"

    @staticmethod
    def finished(event):
        """Match one terminal harness receipt."""
        return event.get("event") == "finished"

    def host(self, case, port, *, capacity=4, duration_ms=1800):
        """Launch and await one host endpoint with the workaround receipt set."""
        child = self.launch(
            case,
            "host",
            [
                "--role=host",
                f"--port={port}",
                f"--capacity={capacity}",
                f"--duration-ms={duration_ms}",
            ],
        )
        event = child.wait_event(self.active, 3.0)
        if not event.get("view", {}).get("phase") == "ACTIVE":
            raise RuntimeError(f"{case}: host did not become active")
        workaround_views = [
            item for item in child.events
            if item.get("event") == "view" and item.get("phase") == "ACTIVE"
        ]
        if not workaround_views or not workaround_views[-1].get("workaround"):
            raise RuntimeError(f"{case}: ENet workaround was not observed before ACTIVE")
        return child

    def client(self, case, name, port, **options):
        """Launch one client using case-specific compatibility and behavior."""
        arguments = ["--role=client", f"--port={port}"]
        for key, value in options.items():
            arguments.append(f"--{key.replace('_', '-')}={value}")
        return self.launch(case, name, arguments)

    def settle(self, children):
        """Collect exits and reject nonzero children or engine/script diagnostics."""
        exits = {child.name: child.finish() for child in children}
        failed_exits = {name: code for name, code in exits.items() if code != 0}
        if failed_exits:
            raise RuntimeError(f"nonzero child exits: {failed_exits}")
        diagnostics = {
            child.name: child.diagnostics() for child in children if child.diagnostics()
        }
        if diagnostics:
            raise RuntimeError(f"unexpected diagnostics: {diagnostics}")
        return exits

    def case_admitted_leave(self):
        """Prove address join, admission, client leave, and reusable cleanup."""
        case = "admitted_leave"
        port = self.allocate_port()
        host = self.host(case, port, duration_ms=3500)
        client = self.client(case, "client", port, behavior="leave_rejoin")
        client.wait_event(self.active, 3.0)
        terminal = client.wait_event(self.finished, 5.0)
        if not terminal.get("ok") or terminal.get("failure"):
            raise RuntimeError(f"{case}: {terminal}")
        return self.settle([client, host])

    def case_rejection(self, case, field, value, expected):
        """Prove one explicit version or content rejection and bounded cleanup."""
        port = self.allocate_port()
        host = self.host(case, port)
        client = self.client(case, "client", port, **{field: value})
        terminal = client.wait_event(self.finished, 3.0)
        if not terminal.get("ok") or terminal.get("failure") != expected:
            raise RuntimeError(f"{case}: {terminal}")
        return self.settle([client, host])

    def case_full(self):
        """Keep one admitted client while a second receives canonical FULL."""
        case = "session_full"
        port = self.allocate_port()
        host = self.host(case, port, capacity=2, duration_ms=3000)
        first = self.client(case, "client_one", port, behavior="hold", duration_ms=2200)
        first.wait_event(self.active, 3.0)
        second = self.client(case, "client_two", port, behavior="leave")
        terminal = second.wait_event(self.finished, 3.0)
        if not terminal.get("ok") or terminal.get("failure") != "FULL":
            raise RuntimeError(f"{case}: {terminal}")
        return self.settle([second, first, host])

    def case_host_loss(self):
        """Let the host exit while admitted and require HOST_LOST cleanup."""
        case = "host_loss"
        port = self.allocate_port()
        host = self.host(case, port, duration_ms=1800)
        client = self.client(case, "client", port, behavior="wait_loss")
        client.wait_event(self.active, 3.0)
        terminal = client.wait_event(self.finished, 4.0)
        if not terminal.get("ok") or terminal.get("failure") != "HOST_LOST":
            raise RuntimeError(f"{case}: {terminal}")
        return self.settle([client, host])

    def case_handshake_abuse(self, case, behavior):
        """Reject raw unauthenticated abuse, then admit a healthy probe client."""
        port = self.allocate_port()
        host = self.host(case, port, duration_ms=3500)
        attacker = self.client(case, "attacker", port, behavior=behavior)
        sent = attacker.wait_event(
            lambda event: event.get("event") == "auth_payload_sent", 3.0
        )
        if behavior == "oversized_byte_array" and sent.get("bytes", 0) < 65536:
            raise RuntimeError(f"{case}: oversized auth payload was not sent")
        terminal = attacker.wait_event(self.finished, 3.0)
        if not terminal.get("ok") or terminal.get("failure") != "AUTH_REJECTED":
            raise RuntimeError(f"{case}: {terminal}")

        probe = self.client(case, "probe", port, behavior="leave")
        probe.wait_event(self.active, 3.0)
        probe_terminal = probe.wait_event(self.finished, 3.0)
        if not probe_terminal.get("ok") or probe_terminal.get("failure"):
            raise RuntimeError(f"{case}: host health probe failed: {probe_terminal}")
        return self.settle([attacker, probe, host])

    def case_cancel_connect(self):
        """Cancel an unreachable in-flight client before its connection deadline."""
        case = "cancel_connect"
        port = self.allocate_port()
        client = self.client(case, "client", port, behavior="cancel")
        terminal = client.wait_event(self.finished, 3.0)
        if not terminal.get("ok") or terminal.get("failure") != "CANCELED":
            raise RuntimeError(f"{case}: {terminal}")
        return self.settle([client])

    def case_unreachable(self):
        """Require an unused endpoint to fail within the configured local deadline."""
        case = "unreachable"
        port = self.allocate_port()
        client = self.client(case, "client", port, behavior="leave")
        terminal = client.wait_event(self.finished, 3.0)
        if not terminal.get("ok") or terminal.get("failure") != "CONNECT_TIMEOUT":
            raise RuntimeError(f"{case}: {terminal}")
        return self.settle([client])

    def cleanup(self):
        """Stop only children launched by this runner after any failed case."""
        for child in self.children:
            if child.process.poll() is None:
                child.finish(timeout=0.2)


def main():
    """Run the real-process matrix and retain a reviewable JSON summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot") or "godot")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("--output must be a fresh empty directory")
    output.mkdir(parents=True, exist_ok=True)

    runner = SessionFlowRunner(args.godot, output)
    results = {}
    cases = [
        ("admitted_leave", runner.case_admitted_leave),
        (
            "incompatible_protocol",
            lambda: runner.case_rejection(
                "incompatible_protocol", "protocol", 2, "INCOMPATIBLE"
            ),
        ),
        (
            "invalid_content",
            lambda: runner.case_rejection(
                "invalid_content", "content", "other", "CONTENT_INVALID"
            ),
        ),
        ("session_full", runner.case_full),
        ("host_loss", runner.case_host_loss),
        (
            "oversized_handshake_byte_array",
            lambda: runner.case_handshake_abuse(
                "oversized_handshake_byte_array", "oversized_byte_array"
            ),
        ),
        (
            "oversized_handshake_string",
            lambda: runner.case_handshake_abuse(
                "oversized_handshake_string", "oversized_string"
            ),
        ),
        (
            "repeated_handshake",
            lambda: runner.case_handshake_abuse(
                "repeated_handshake", "repeated_handshake"
            ),
        ),
        ("cancel_connect", runner.case_cancel_connect),
        ("unreachable", runner.case_unreachable),
    ]
    try:
        for name, case in cases:
            started = time.monotonic()
            try:
                exits = case()
                results[name] = {
                    "ok": True,
                    "elapsed_seconds": round(time.monotonic() - started, 3),
                    "exits": exits,
                }
            except Exception as error:  # One summary must survive a case failure.
                results[name] = {
                    "ok": False,
                    "elapsed_seconds": round(time.monotonic() - started, 3),
                    "error": str(error),
                }
                break
    finally:
        runner.cleanup()

    summary = {
        "ok": all(row["ok"] for row in results.values()),
        "timing_context": "contended wall-clock diagnostics; not performance evidence",
        "cases": results,
    }
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0 if summary["ok"] and len(results) == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
