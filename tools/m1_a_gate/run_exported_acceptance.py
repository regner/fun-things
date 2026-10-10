#!/usr/bin/env python3
"""Run the Windows exported multiplayer shell matrix over real loopback ENet."""

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


PREFIX = "M1-A-GATE "
DIAGNOSTIC = re.compile(r"(?:SCRIPT ERROR:|ERROR:|WARNING:)")
PROCESS_TIMEOUT_SECONDS = 180
READINESS_TIMEOUT_SECONDS = 30
CASE_TIMEOUT_SECONDS = 150


@dataclass
class ManagedProcess:
    """Own one exported child, its receipt reader, and bounded cleanup."""

    name: str
    process: subprocess.Popen
    output: Path
    events: list[dict] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)
    event_queue: queue.Queue = field(default_factory=queue.Queue)
    reader: threading.Thread | None = None

    def start_reader(self) -> None:
        """Drain merged output continuously so a child cannot block on its pipe."""
        self.reader = threading.Thread(target=self._read_output, daemon=True)
        self.reader.start()

    def _read_output(self) -> None:
        """Retain all output and enqueue only valid structured acceptance events."""
        assert self.process.stdout is not None
        with (self.output / "stdout.log").open("w", encoding="utf-8", newline="\n") as stream:
            for line in self.process.stdout:
                stream.write(line)
                stream.flush()
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

    def wait_event(self, predicate, timeout: float) -> dict:
        """Wait on receipts rather than assuming a fixed process startup duration."""
        deadline = time.monotonic() + timeout
        for event in self.events:
            if predicate(event):
                return event
        while time.monotonic() < deadline:
            try:
                event = self.event_queue.get(timeout=max(0.01, deadline - time.monotonic()))
            except queue.Empty:
                break
            if predicate(event):
                return event
            if self.process.poll() is not None and self.event_queue.empty():
                break
        raise RuntimeError(f"{self.name}: expected readiness receipt was not observed")

    def finish(self, timeout: float = 5.0) -> int:
        """Wait for clean exit, then stop only this runner-owned child."""
        try:
            returncode = self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:
                returncode = self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                returncode = self.process.wait(timeout=2)
        if self.reader is not None:
            self.reader.join(timeout=2)
        return returncode

    def diagnostics(self) -> list[str]:
        """Return engine/script diagnostics from stdout and the explicit engine log."""
        engine_log = self.output / "engine.log"
        text = "\n".join(self.lines)
        if engine_log.is_file():
            text += "\n" + engine_log.read_text(encoding="utf-8", errors="replace")
        return [line for line in text.splitlines() if DIAGNOSTIC.search(line)]


class ExportedAcceptanceRunner:
    """Coordinate exported processes with isolated writable roots and receipts."""

    def __init__(
        self,
        executable: Path,
        output: Path,
        timeout_executable: str,
        rendering_driver: str = "",
    ):
        self.executable = executable
        self.output = output
        self.timeout_executable = timeout_executable
        self.rendering_driver = rendering_driver
        self.children: list[ManagedProcess] = []

    @staticmethod
    def allocate_port() -> int:
        """Select an unused loopback UDP port immediately before a case."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.bind(("127.0.0.1", 0))
            return probe.getsockname()[1]

    def launch(self, case: str, role: str, scenario: str, port: int) -> ManagedProcess:
        """Launch one capped windowed export under the hard process timeout."""
        process_output = self.output / case / role
        process_output.mkdir(parents=True, exist_ok=True)
        user_root = process_output / "user"
        user_root.mkdir()
        env = os.environ.copy()
        env.update({
            "APPDATA": os.fspath(user_root / "appdata"),
            "LOCALAPPDATA": os.fspath(user_root / "localappdata"),
            "XDG_DATA_HOME": os.fspath(user_root / "xdg-data"),
            "XDG_CONFIG_HOME": os.fspath(user_root / "xdg-config"),
            "XDG_CACHE_HOME": os.fspath(user_root / "xdg-cache"),
        })
        x_position = 20 if role == "host" else 660
        engine_arguments = [
            "--position",
            f"{x_position},40",
            "--resolution",
            "620x760",
            "--max-fps",
            "60",
        ]
        if self.rendering_driver:
            engine_arguments.extend(["--rendering-driver", self.rendering_driver])
        command = [
            self.timeout_executable,
            f"{PROCESS_TIMEOUT_SECONDS}s",
            os.fspath(self.executable),
            *engine_arguments,
            "--log-file",
            os.fspath(process_output / "engine.log"),
            "--",
            f"--m1-a-gate-role={role}",
            f"--m1-a-gate-scenario={scenario}",
            f"--m1-a-gate-port={port}",
        ]
        process = subprocess.Popen(
            command,
            cwd=self.executable.parent,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        child = ManagedProcess(role, process, process_output)
        child.start_reader()
        self.children.append(child)
        (process_output / "command.json").write_text(
            json.dumps(command, indent=2) + "\n", encoding="utf-8"
        )
        return child

    @staticmethod
    def event(name: str):
        """Build a structured-event predicate."""
        return lambda event: event.get("event") == name

    def settle(self, children: list[ManagedProcess]) -> dict:
        """Require clean exits and diagnostic-free runtime logs."""
        exits = {child.name: child.finish() for child in children}
        if any(code != 0 for code in exits.values()):
            raise RuntimeError(f"nonzero exported exits: {exits}")
        diagnostics = {
            child.name: child.diagnostics()
            for child in children
            if child.diagnostics()
        }
        if diagnostics:
            raise RuntimeError(f"runtime diagnostics: {diagnostics}")
        return exits

    def pair(self, case: str, scenario: str) -> tuple[ManagedProcess, ManagedProcess]:
        """Start a host, await endpoint readiness, then start its client."""
        port = self.allocate_port()
        host = self.launch(case, "host", scenario, port)
        host.wait_event(self.event("host_ready"), READINESS_TIMEOUT_SECONDS)
        client = self.launch(case, "client", scenario, port)
        return host, client

    def case_gameplay(self) -> dict:
        """Prove admission, both walkers, smoothing, respawn, reset, and teardown."""
        host, client = self.pair("gameplay", "gameplay")
        client.wait_event(self.event("match_ready"), READINESS_TIMEOUT_SECONDS)
        client_result = client.wait_event(self.event("finished"), CASE_TIMEOUT_SECONDS)
        host_result = host.wait_event(self.event("finished"), READINESS_TIMEOUT_SECONDS)
        required_true = (
            "brackett_loaded",
            "client_moved",
            "dead_observed",
            "host_moved",
            "prediction_bounded",
            "remote_smoothed",
            "reset_observed",
            "respawn_observed",
            "steam_class_absent",
            "steam_singleton_absent",
        )
        for role, receipt in (("host", host_result), ("client", client_result)):
            if not receipt.get("ok"):
                raise RuntimeError(f"gameplay {role} failed: {receipt}")
            missing = [field for field in required_true if not receipt.get(field)]
            if role == "host":
                missing = [field for field in missing if field != "remote_smoothed"]
            else:
                missing = [field for field in missing if field != "host_moved"]
            if missing:
                raise RuntimeError(f"gameplay {role} missing receipts: {missing}")
        return {
            "exits": self.settle([client, host]),
            "receipts": {"host": host_result, "client": client_result},
        }

    def case_expected_failure(self, case: str, scenario: str, detail: str) -> dict:
        """Require one normalized exported admission failure and clean host cleanup."""
        host, client = self.pair(case, scenario)
        client_result = client.wait_event(self.event("finished"), CASE_TIMEOUT_SECONDS)
        host_result = host.wait_event(self.event("finished"), READINESS_TIMEOUT_SECONDS)
        if not client_result.get("ok") or client_result.get("detail") != detail:
            raise RuntimeError(f"{case}: wrong client result: {client_result}")
        if not host_result.get("ok") or not host_result.get("peer_seen"):
            raise RuntimeError(f"{case}: host did not observe peer cleanup: {host_result}")
        return {
            "exits": self.settle([client, host]),
            "receipts": {"host": host_result, "client": client_result},
        }

    def case_host_loss(self) -> dict:
        """Exit an admitted exported host and require HOST_LOST on its client."""
        host, client = self.pair("host_loss", "host_loss")
        host.wait_event(self.event("host_loss_exit"), CASE_TIMEOUT_SECONDS)
        client_result = client.wait_event(self.event("finished"), READINESS_TIMEOUT_SECONDS)
        if not client_result.get("ok") or client_result.get("detail") != "HOST_LOST":
            raise RuntimeError(f"host_loss: wrong client result: {client_result}")
        return {
            "exits": self.settle([client, host]),
            "receipts": {"client": client_result},
        }

    def cleanup(self) -> None:
        """Stop only children launched by this runner after any case failure."""
        for child in self.children:
            if child.process.poll() is None:
                child.finish(timeout=0.2)


def main() -> int:
    """Run the complete exported Windows matrix and retain one concise summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rendering-driver", default="")
    args = parser.parse_args()
    executable = args.executable.resolve()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("--output must be a fresh empty directory")
    if not executable.is_file():
        parser.error("--executable does not exist")
    timeout_executable = shutil.which("timeout")
    if timeout_executable is None:
        parser.error("GNU timeout is required for every exported process")
    output.mkdir(parents=True, exist_ok=True)

    runner = ExportedAcceptanceRunner(
        executable,
        output,
        timeout_executable,
        args.rendering_driver,
    )
    cases = (
        ("gameplay", runner.case_gameplay),
        (
            "incompatible",
            lambda: runner.case_expected_failure(
                "incompatible", "incompatible", "INCOMPATIBLE"
            ),
        ),
        (
            "admission_timeout",
            lambda: runner.case_expected_failure(
                "admission_timeout", "admission_timeout", "HANDSHAKE_TIMEOUT"
            ),
        ),
        ("host_loss", runner.case_host_loss),
    )
    results = {}
    try:
        for name, case in cases:
            started = time.monotonic()
            try:
                results[name] = {
                    "ok": True,
                    **case(),
                    "elapsed_seconds": round(time.monotonic() - started, 3),
                }
            except Exception as error:  # Preserve the failing case receipt for review.
                results[name] = {
                    "ok": False,
                    "error": str(error),
                    "elapsed_seconds": round(time.monotonic() - started, 3),
                }
                break
    finally:
        runner.cleanup()

    summary = {
        "ok": len(results) == len(cases) and all(row["ok"] for row in results.values()),
        "executable": executable.as_posix(),
        "cases": results,
        "timing_context": "contended functional run; not performance evidence",
    }
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
