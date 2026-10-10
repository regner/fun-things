#!/usr/bin/env python3
"""Run the Windows exported multiplayer shell matrix over real loopback ENet."""

import argparse
from dataclasses import dataclass, field
import heapq
import json
import os
from pathlib import Path
import queue
import random
import re
import socket
import subprocess
import threading
import time


PREFIX = "M1-A-GATE "
DIAGNOSTIC = re.compile(r"(?:SCRIPT ERROR:|ERROR:|WARNING:)")
PROCESS_TIMEOUT_SECONDS = 180
READINESS_TIMEOUT_SECONDS = 30
CASE_TIMEOUT_SECONDS = 150
EXPECTED_AUTH_TIMEOUT_MSEC = 750
PREDICTION_HISTORY_CAPACITY = 120
PREDICTED_DISPLACEMENT_MINIMUM_METRES = 0.01
SMOOTHING_DISPLACEMENT_MINIMUM_METRES = 0.001
MAX_REMOTE_FRAME_JUMP_METRES = 0.5
MINIMUM_WINDOW_DISTANCE_METRES = 0.2
MINIMUM_CLIENT_HOST_DISTANCE_RATIO = 0.3
NORMAL_DELAY_MSEC = 75.0
NORMAL_JITTER_MSEC = 30.0
NORMAL_LOSS = 0.02
MAX_PROXY_QUEUE = 1024


class NetworkProfileProxy:
    """Route one real ENet pair through bounded deterministic delay, jitter, and loss."""

    def __init__(self, host_port: int, output: Path):
        self.host = ("127.0.0.1", host_port)
        self.client = None
        self.output = output
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("127.0.0.1", 0))
        self.socket.settimeout(0.002)
        self.port = self.socket.getsockname()[1]
        self.queue = []
        self.serial = 0
        self.received = 0
        self.delivered = 0
        self.dropped = 0
        self.failure = ""
        self.enabled = False
        self.running = True
        self.random = {
            "up": random.Random(731),
            "down": random.Random(947),
        }
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self) -> None:
        """Poll and deliver bounded datagrams until the owning runner closes the route."""
        try:
            while self.running:
                now = time.monotonic()
                try:
                    data, sender = self.socket.recvfrom(65535)
                except socket.timeout:
                    data = None
                    sender = None
                except OSError:
                    break
                if data is not None:
                    self._enqueue(data, sender, now)
                self._deliver(now)
        except Exception as error:  # Retain route failures for the acceptance summary.
            self.failure = str(error)
        finally:
            self._write_receipt()

    def _enqueue(self, data: bytes, sender, now: float) -> None:
        """Apply the selected normal profile independently in each direction."""
        self.received += 1
        if sender == self.host:
            if self.client is None:
                return
            direction = "down"
            target = self.client
        else:
            self.client = sender
            direction = "up"
            target = self.host
        if not self.enabled:
            self.socket.sendto(data, target)
            self.delivered += 1
            return

        rng = self.random[direction]
        self.serial += 1
        lost = rng.random() < NORMAL_LOSS
        delay = max(
            0.0,
            NORMAL_DELAY_MSEC + rng.uniform(-NORMAL_JITTER_MSEC, NORMAL_JITTER_MSEC),
        )
        if lost:
            self.dropped += 1
            return
        if len(self.queue) >= MAX_PROXY_QUEUE:
            raise RuntimeError("normal-profile proxy queue limit exceeded")
        heapq.heappush(
            self.queue,
            (now + delay / 1000.0, self.serial, data, target),
        )

    def _deliver(self, now: float) -> None:
        """Forward every due packet without blocking the bounded receive loop."""
        while self.queue and self.queue[0][0] <= now:
            _due, _serial, data, target = heapq.heappop(self.queue)
            self.socket.sendto(data, target)
            self.delivered += 1

    def enable(self) -> None:
        """Start impairment after admission so the profile covers the sustained play interval."""
        self.enabled = True

    def close(self) -> None:
        """Stop this runner-owned route and retain its measured packet counts."""
        self.running = False
        self.thread.join(timeout=2)
        self.socket.close()
        if self.thread.is_alive() and not self.failure:
            self.failure = "proxy thread did not stop"
        self._write_receipt()

    def _write_receipt(self) -> None:
        """Write the configured and observed profile without claiming quiet timing."""
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.output.write_text(
            json.dumps(
                {
                    "delay_msec": NORMAL_DELAY_MSEC,
                    "jitter_msec": NORMAL_JITTER_MSEC,
                    "loss": NORMAL_LOSS,
                    "received": self.received,
                    "delivered": self.delivered,
                    "dropped": self.dropped,
                    "failure": self.failure,
                    "enabled": self.enabled,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


def exported_process_command(
    executable: Path,
    engine_arguments: list[str],
    process_output: Path,
    role: str,
    scenario: str,
    port: int,
) -> list[str]:
    """Build one exported invocation bounded by the Python-owned process watchdog."""
    return [
        os.fspath(executable),
        *engine_arguments,
        "--log-file",
        os.fspath(process_output / "engine.log"),
        "--",
        f"--m1-a-gate-role={role}",
        f"--m1-a-gate-scenario={scenario}",
        f"--m1-a-gate-port={port}",
    ]


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
    watchdog: threading.Thread | None = None
    hard_timed_out: bool = False

    def start_reader(self) -> None:
        """Drain output and enforce the process lifetime without an external utility."""
        self.reader = threading.Thread(target=self._read_output, daemon=True)
        self.reader.start()
        self.watchdog = threading.Thread(target=self._enforce_timeout, daemon=True)
        self.watchdog.start()

    def _enforce_timeout(self) -> None:
        """Terminate only this child when its Python-owned hard deadline expires."""
        try:
            self.process.wait(timeout=PROCESS_TIMEOUT_SECONDS)
            return
        except subprocess.TimeoutExpired:
            self.hard_timed_out = True
        self.process.terminate()
        try:
            self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=2)

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
        rendering_driver: str = "",
    ):
        self.executable = executable
        self.output = output
        self.rendering_driver = rendering_driver
        self.children: list[ManagedProcess] = []
        self.proxies: list[NetworkProfileProxy] = []
        self.profile_by_case: dict[str, NetworkProfileProxy] = {}

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
        command = exported_process_command(
            self.executable,
            engine_arguments,
            process_output,
            role,
            scenario,
            port,
        )
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

    def pair(
        self,
        case: str,
        scenario: str,
        profile: str = "direct",
    ) -> tuple[ManagedProcess, ManagedProcess]:
        """Start a ready host, then connect its client directly or through normal profile."""
        host_port = self.allocate_port()
        host = self.launch(case, "host", scenario, host_port)
        host.wait_event(self.event("host_ready"), READINESS_TIMEOUT_SECONDS)
        client_port = host_port
        if profile == "normal":
            proxy = NetworkProfileProxy(host_port, self.output / case / "profile.json")
            self.proxies.append(proxy)
            self.profile_by_case[case] = proxy
            client_port = proxy.port
        elif profile != "direct":
            raise ValueError(f"unknown network profile: {profile}")
        client = self.launch(case, "client", scenario, client_port)
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
        prediction_fields = (
            "prediction_succeeded",
            "prediction_before_authority_receipt",
        )
        if any(not client_result.get(field) for field in prediction_fields):
            raise RuntimeError(f"gameplay prediction was not observed: {client_result}")
        peak_history = client_result.get("prediction_peak_history", 0)
        predicted_displacement = client_result.get(
            "prediction_unacknowledged_displacement_metres", 0.0
        )
        if (
            not 0 < peak_history <= PREDICTION_HISTORY_CAPACITY
            or predicted_displacement <= PREDICTED_DISPLACEMENT_MINIMUM_METRES
        ):
            raise RuntimeError(f"gameplay prediction measurements invalid: {client_result}")
        stationary_frames = client_result.get("remote_stationary_root_frames", 0)
        stationary_displacement = client_result.get(
            "remote_stationary_display_displacement_metres", 0.0
        )
        maximum_jump = client_result.get("remote_display_max_jump_metres", 1.0)
        if (
            stationary_frames < 1
            or stationary_displacement <= SMOOTHING_DISPLACEMENT_MINIMUM_METRES
        ):
            raise RuntimeError(f"gameplay smoothing was not independently observed: {client_result}")
        if not 0.0 < maximum_jump <= MAX_REMOTE_FRAME_JUMP_METRES:
            raise RuntimeError(f"gameplay smoothing jump was not bounded: {client_result}")
        return {
            "exits": self.settle([client, host]),
            "receipts": {"host": host_result, "client": client_result},
        }

    def case_sustained(self, profile: str) -> dict:
        """Require ten seconds of continuous client movement and replicated mouse-facing."""
        case = f"sustained_{profile}"
        host, client = self.pair(case, "sustained", profile)
        client.wait_event(self.event("match_ready"), READINESS_TIMEOUT_SECONDS)
        if profile == "normal":
            self.profile_by_case[case].enable()
        client_result = client.wait_event(self.event("finished"), CASE_TIMEOUT_SECONDS)
        host_result = host.wait_event(self.event("finished"), READINESS_TIMEOUT_SECONDS)
        for role, receipt in (("host", host_result), ("client", client_result)):
            if not receipt.get("ok"):
                raise RuntimeError(f"{case} {role} failed: {receipt}")
            host_distance = receipt.get("sustained_host_distance_metres", 0.0)
            client_distance = receipt.get("sustained_client_distance_metres", 0.0)
            if receipt.get("sustained_duration_seconds", 0.0) < 10.0:
                raise RuntimeError(f"{case} {role} ended before ten seconds: {receipt}")
            if (
                host_distance <= 1.0
                or client_distance < host_distance * MINIMUM_CLIENT_HOST_DISTANCE_RATIO
            ):
                raise RuntimeError(f"{case} {role} distance ratio failed: {receipt}")
            if not receipt.get("sustained_facing_converged"):
                raise RuntimeError(f"{case} {role} remote facing did not converge: {receipt}")
            if receipt.get("sustained_facing_span_radians", 0.0) < 1.5:
                raise RuntimeError(f"{case} {role} moving aim target was not tracked: {receipt}")
        if (
            client_result.get("sustained_continuity_window_failures") != 0
            or client_result.get("sustained_minimum_window_metres", 0.0)
            < MINIMUM_WINDOW_DISTANCE_METRES
        ):
            raise RuntimeError(f"{case} client presentation stalled: {client_result}")
        return {
            "exits": self.settle([client, host]),
            "profile": profile,
            "receipts": {"host": host_result, "client": client_result},
        }

    def case_expected_failure(self, case: str, scenario: str, detail: str) -> dict:
        """Require one normalized exported admission failure and clean host cleanup."""
        host, client = self.pair(case, scenario)
        auth_waiting = None
        if scenario == "admission_timeout":
            auth_waiting = client.wait_event(
                self.event("auth_waiting"), READINESS_TIMEOUT_SECONDS
            )
            if (
                not auth_waiting.get("ok")
                or auth_waiting.get("started_msec", 0) <= 0
                or auth_waiting.get("timeout_msec") != EXPECTED_AUTH_TIMEOUT_MSEC
            ):
                raise RuntimeError(f"{case}: invalid auth readiness: {auth_waiting}")
        client_result = client.wait_event(self.event("finished"), CASE_TIMEOUT_SECONDS)
        host_result = host.wait_event(self.event("finished"), READINESS_TIMEOUT_SECONDS)
        if not client_result.get("ok") or client_result.get("detail") != detail:
            raise RuntimeError(f"{case}: wrong client result: {client_result}")
        if not host_result.get("ok") or not host_result.get("peer_seen"):
            raise RuntimeError(f"{case}: host did not observe peer cleanup: {host_result}")
        if scenario == "admission_timeout" and (
            not client_result.get("auth_waiting")
            or client_result.get("auth_failure_elapsed_msec", 0)
            < client_result.get("auth_timeout_msec", 1)
        ):
            raise RuntimeError(f"{case}: timeout deadline was not proved: {client_result}")
        receipts = {"host": host_result, "client": client_result}
        if auth_waiting is not None:
            receipts["auth_waiting"] = auth_waiting
        return {
            "exits": self.settle([client, host]),
            "receipts": receipts,
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
        """Stop only children and profile routes launched by this runner."""
        for child in self.children:
            if child.process.poll() is None:
                child.finish(timeout=0.2)
        for proxy in self.proxies:
            proxy.close()


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
    output.mkdir(parents=True, exist_ok=True)

    runner = ExportedAcceptanceRunner(executable, output, args.rendering_driver)
    cases = (
        ("gameplay", runner.case_gameplay),
        ("sustained_direct", lambda: runner.case_sustained("direct")),
        ("sustained_normal", lambda: runner.case_sustained("normal")),
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
