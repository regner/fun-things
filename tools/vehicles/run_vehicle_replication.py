#!/usr/bin/env python3
"""Run bounded production vehicle prediction profiles over real separate ENet processes."""

import argparse
from dataclasses import dataclass, field
import heapq
import json
import os
from pathlib import Path
import queue
import random
import shutil
import socket
import subprocess
import threading
import time


PREFIX = "M1-B1.1 "
PROCESS_TIMEOUT_SECONDS = 60
READINESS_TIMEOUT_SECONDS = 30
RESULT_TIMEOUT_SECONDS = 50
TARGET_CORRECTION_P95_METRES = 0.5
PROFILES = {
    "direct": (0, 0, 0.0),
    "normal": (75, 30, 0.02),
    "adverse": (125, 50, 0.05),
}


@dataclass
class ManagedProcess:
    """Own one Godot child, continuous output drain, and structured receipts."""

    name: str
    process: subprocess.Popen
    output: Path
    events: list[dict] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)
    events_queue: queue.Queue = field(default_factory=queue.Queue)
    reader: threading.Thread | None = None

    def start_reader(self) -> None:
        """Drain process output immediately so receipt waits never block its pipe."""
        self.reader = threading.Thread(target=self._read_output, daemon=True)
        self.reader.start()

    def _read_output(self) -> None:
        """Retain complete output and queue only valid vehicle receipts."""
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
                self.events_queue.put(event)

    def wait_event(self, name: str, timeout_seconds: float) -> dict:
        """Wait for one named readiness/result receipt instead of using a fixed sleep."""
        deadline = time.monotonic() + timeout_seconds
        for event in self.events:
            if event.get("event") == name:
                return event
        while time.monotonic() < deadline:
            try:
                event = self.events_queue.get(timeout=max(0.01, deadline - time.monotonic()))
            except queue.Empty:
                break
            if event.get("event") == name:
                return event
            if self.process.poll() is not None and self.events_queue.empty():
                break
        raise RuntimeError(f"{self.name}: missing {name} receipt")

    def finish(self) -> int:
        """Wait briefly, then terminate only this runner-owned child if necessary."""
        try:
            returncode = self.process.wait(timeout=5)
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


class DatagramProxy:
    """Inject seeded one-way delay, jitter, and loss without changing ENet payloads."""

    def __init__(
        self,
        bind_port: int,
        host_port: int,
        delay_msec: int,
        jitter_msec: int,
        loss: float,
        seed: int,
    ):
        self.bind_address = ("127.0.0.1", bind_port)
        self.host_address = ("127.0.0.1", host_port)
        self.delay_msec = delay_msec
        self.jitter_msec = jitter_msec
        self.loss = loss
        self.random = random.Random(seed)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.bind_address)
        self.socket.settimeout(0.01)
        self.client_address: tuple[str, int] | None = None
        self.pending: list[tuple[float, int, bytes, tuple[str, int]]] = []
        self.sequence = 0
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        """Begin forwarding before the client attempts its ENet connection."""
        self.thread.start()

    def close(self) -> None:
        """Stop the runner-owned forwarding socket and drain thread."""
        self.stop_event.set()
        self.thread.join(timeout=2)
        self.socket.close()

    def _run(self) -> None:
        """Schedule both directions under the same seeded profile."""
        while not self.stop_event.is_set():
            try:
                payload, source = self.socket.recvfrom(65_535)
                self._schedule(payload, source)
            except socket.timeout:
                pass
            except ConnectionResetError:
                # Windows reports an ICMP response from a recently closed UDP peer
                # on the next receive; ENet reconnect traffic remains valid.
                pass
            self._send_due()

    def _schedule(self, payload: bytes, source: tuple[str, int]) -> None:
        """Drop or enqueue one datagram with a bounded nonnegative delay."""
        if source == self.host_address:
            if self.client_address is None:
                return
            target = self.client_address
        else:
            self.client_address = source
            target = self.host_address
        if self.random.random() < self.loss:
            return
        jitter = self.random.uniform(-self.jitter_msec, self.jitter_msec)
        delay_seconds = max(0.0, self.delay_msec + jitter) / 1000.0
        self.sequence += 1
        heapq.heappush(
            self.pending,
            (time.monotonic() + delay_seconds, self.sequence, payload, target),
        )

    def _send_due(self) -> None:
        """Forward every datagram whose scheduled wall-clock time has arrived."""
        now = time.monotonic()
        while self.pending and self.pending[0][0] <= now:
            _deadline, _sequence, payload, target = heapq.heappop(self.pending)
            self.socket.sendto(payload, target)


class VehicleProfileRunner:
    """Launch direct or proxied host/client pairs and validate their receipts."""

    def __init__(self, godot: str, timeout_executable: str, output: Path):
        self.godot = godot
        self.timeout_executable = timeout_executable
        self.output = output
        self.children: list[ManagedProcess] = []

    @staticmethod
    def allocate_port() -> int:
        """Reserve then release one loopback UDP port immediately before use."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.bind(("127.0.0.1", 0))
            return probe.getsockname()[1]

    def launch(
        self, profile: str, scenario: str, role: str, port: int
    ) -> ManagedProcess:
        """Start one headless production-process harness under the hard timeout."""
        process_output = self.output / profile / scenario / role
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
        command = [
            self.timeout_executable,
            f"{PROCESS_TIMEOUT_SECONDS}s",
            self.godot,
            "--headless",
            "--path",
            os.fspath(Path.cwd()),
            "--max-fps",
            "60",
            "--log-file",
            os.fspath(process_output / "engine.log"),
            "res://tests/integration/vehicles/vehicle_replication_process.tscn",
            "--",
            f"--role={role}",
            f"--port={port}",
            f"--scenario={scenario}",
        ]
        process = subprocess.Popen(
            command,
            cwd=Path.cwd(),
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

    def run_profile(self, profile: str) -> dict:
        """Require readiness, complete gameplay receipts, clean exits, and raw p95."""
        delay, jitter, loss = PROFILES[profile]
        host_port = self.allocate_port()
        client_port = host_port
        proxy = None
        if profile != "direct":
            client_port = self.allocate_port()
            proxy = DatagramProxy(client_port, host_port, delay, jitter, loss, 731)
            proxy.start()
        host = self.launch(profile, "gameplay", "host", host_port)
        host.wait_event("host_ready", READINESS_TIMEOUT_SECONDS)
        client = self.launch(profile, "gameplay", "client", client_port)
        try:
            client_result = client.wait_event("finished", RESULT_TIMEOUT_SECONDS)
            host_result = host.wait_event("finished", RESULT_TIMEOUT_SECONDS)
        finally:
            if proxy is not None:
                proxy.close()
        exits = {"host": host.finish(), "client": client.finish()}
        if exits != {"host": 0, "client": 0}:
            raise RuntimeError(f"{profile}: nonzero exits {exits}")
        if not host_result.get("ok") or not client_result.get("ok"):
            raise RuntimeError(f"{profile}: failed receipt {host_result} {client_result}")
        prediction = client_result.get("prediction", {})
        client_phases = client_result.get("phase_outcomes", {})
        host_phases = host_result.get("phase_outcomes", {})
        expected_phases = {"straight", "turn", "brake", "reverse", "handbrake"}
        if (
            int(client_result.get("movement_receipts", 0)) <= 1
            or int(prediction.get("acknowledgement", 0)) <= 1
            or int(prediction.get("reconciliation_count", 0)) <= 1
            or set(client_phases) != expected_phases
            or set(host_phases) != expected_phases
            or not all(client_phases.values())
            or not all(host_phases.values())
            or not host_result.get("wall_contact_observed")
            or not host_result.get("moving_contact_observed")
        ):
            raise RuntimeError(f"{profile}: incomplete authority/outcome proof")
        correction = float(
            client_result.get("prediction", {}).get("p95_correction_metres", 0.0)
        )
        lifecycle_races = {
            "reset_during_entry": self.run_lifecycle_race(profile, "reset_race"),
            "seated_disconnect": self.run_lifecycle_race(profile, "disconnect_race"),
        }
        result = {
            "profile": profile,
            "delay_msec": delay,
            "jitter_msec": jitter,
            "loss": loss,
            "correction_p95_metres": correction,
            "target_metres": TARGET_CORRECTION_P95_METRES,
            "target_met": correction <= TARGET_CORRECTION_P95_METRES,
            "target_analysis": (
                "target met"
                if correction <= TARGET_CORRECTION_P95_METRES
                else (
                    "raw reconciliation corrections remain above target during "
                    "control-phase changes at this profile's RTT and loss"
                )
            ),
            "host": host_result,
            "client": client_result,
            "exits": exits,
            "lifecycle_races": lifecycle_races,
        }
        profile_path = self.output / profile / "result.json"
        profile_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return result

    def run_lifecycle_race(self, profile: str, scenario: str) -> dict:
        """Run one reset or disconnect race through another real profiled ENet pair."""
        delay, jitter, loss = PROFILES[profile]
        host_port = self.allocate_port()
        client_port = host_port
        proxy = None
        if profile != "direct":
            client_port = self.allocate_port()
            proxy = DatagramProxy(client_port, host_port, delay, jitter, loss, 731)
            proxy.start()
        host = self.launch(profile, scenario, "host", host_port)
        host.wait_event("host_ready", READINESS_TIMEOUT_SECONDS)
        client = self.launch(profile, scenario, "client", client_port)
        try:
            if scenario == "disconnect_race":
                client_source = client.wait_event(
                    "disconnect_source_ready", RESULT_TIMEOUT_SECONDS
                )
                client_exit = client.finish()
                host_result = host.wait_event("finished", RESULT_TIMEOUT_SECONDS)
                client_result = client_source
            else:
                client_result = client.wait_event("finished", RESULT_TIMEOUT_SECONDS)
                host_result = host.wait_event("finished", RESULT_TIMEOUT_SECONDS)
                client_exit = client.finish()
        finally:
            if proxy is not None:
                proxy.close()
        host_exit = host.finish()
        exits = {"host": host_exit, "client": client_exit}
        if exits != {"host": 0, "client": 0}:
            raise RuntimeError(f"{profile}/{scenario}: nonzero exits {exits}")
        if not host_result.get("ok") or not client_result.get("ok"):
            raise RuntimeError(
                f"{profile}/{scenario}: failed receipt {host_result} {client_result}"
            )
        if scenario == "reset_race":
            for receipt in (host_result, client_result):
                if (
                    not receipt.get("reset_during_entry_observed")
                    or receipt.get("old_action_survived")
                    or receipt.get("pending_actions") != 0
                ):
                    raise RuntimeError(
                        f"{profile}/{scenario}: stale entry survived {receipt}"
                    )
        elif (
            not client_result.get("seated")
            or not host_result.get("disconnect_coast_observed")
            or not host_result.get("driver_cleared")
            or host_result.get("final_speed_mps", 1e9)
            >= host_result.get("initial_speed_mps", 0.0)
        ):
            raise RuntimeError(f"{profile}/{scenario}: coast proof failed")
        return {
            "host": host_result,
            "client": client_result,
            "exits": exits,
        }


def parse_args() -> argparse.Namespace:
    """Parse bounded profile and external evidence options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        action="append",
        choices=sorted(PROFILES),
        dest="profiles",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--godot", default=shutil.which("godot") or "godot")
    parser.add_argument("--timeout", default=shutil.which("timeout") or "timeout")
    return parser.parse_args()


def main() -> int:
    """Run requested profiles while preserving failed target measurements honestly."""
    args = parse_args()
    output = args.output.resolve()
    if output.is_relative_to(Path.cwd().resolve()):
        raise SystemExit("output must be outside the checkout")
    if output.exists() and any(output.iterdir()):
        raise SystemExit("output must be a fresh empty directory")
    output.mkdir(parents=True, exist_ok=True)
    profiles = args.profiles or list(PROFILES)
    runner = VehicleProfileRunner(args.godot, args.timeout, output)
    results = []
    try:
        for profile in profiles:
            results.append(runner.run_profile(profile))
    finally:
        for child in runner.children:
            if child.process.poll() is None:
                child.finish()
    summary = {
        "ok": len(results) == len(profiles),
        "profiles": results,
        "all_targets_met": all(result["target_met"] for result in results),
    }
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
