#!/usr/bin/env python3
"""Run bounded real-process ENet prediction under direct or impaired delivery."""

import argparse
import heapq
import json
import os
from pathlib import Path
import random
import shutil
import socket
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parents[3]
SUCCESS = "M1-A2.3 "
HOST_READY = "M1-A2.3 host_ready "
HOST_READY_TIMEOUT_SECONDS = 30.0
PROFILES = {
    "direct": {"one_way_ms": 0.0, "jitter_ms": 0.0, "loss": 0.0},
    "lifecycle": {"one_way_ms": 0.0, "jitter_ms": 0.0, "loss": 0.0},
    "normal": {"one_way_ms": 75.0, "jitter_ms": 30.0, "loss": 0.02},
    "adverse": {"one_way_ms": 125.0, "jitter_ms": 50.0, "loss": 0.05},
}


class DatagramImpairmentProxy:
    """Forward ENet datagrams with seeded finite delay, jitter, and independent loss."""

    def __init__(self, host_port, profile):
        self.host = ("127.0.0.1", host_port)
        self.profile = profile
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("127.0.0.1", 0))
        self.socket.settimeout(0.002)
        self.port = self.socket.getsockname()[1]
        self.client = None
        self.pending = []
        self.random = random.Random(731)
        self.running = False
        self.thread = None
        self.forwarded = 0
        self.dropped = 0

    def start(self):
        """Start the owned proxy thread before the client sends its first packet."""
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def close(self):
        """Stop only this runner's proxy and release its one UDP endpoint."""
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=2)
        self.socket.close()

    def _run(self):
        """Poll, schedule, and forward bounded datagrams without blocking child cleanup."""
        while self.running:
            self._receive_one()
            now = time.monotonic()
            while self.pending and self.pending[0][0] <= now:
                _due, payload, target = heapq.heappop(self.pending)
                self.socket.sendto(payload, target)
                self.forwarded += 1

    def _receive_one(self):
        """Schedule one available datagram and apply the selected seeded loss profile."""
        try:
            payload, source = self.socket.recvfrom(65535)
        except (ConnectionResetError, socket.timeout):
            # Windows reports an ICMP reset on this unconnected proxy socket; ENet retries.
            return
        if source == self.host:
            if self.client is None:
                return
            target = self.client
        else:
            self.client = source
            target = self.host
        if self.random.random() < self.profile["loss"]:
            self.dropped += 1
            return
        delay_ms = self.profile["one_way_ms"] + self.random.uniform(
            -self.profile["jitter_ms"], self.profile["jitter_ms"]
        )
        heapq.heappush(
            self.pending,
            (time.monotonic() + max(0.0, delay_ms) / 1000.0, payload, target),
        )


def available_port():
    """Reserve an ephemeral UDP port long enough to select the test endpoint."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def command(godot, role, port, log_path, *, windowed=False, capture_dir=None):
    """Build one hard-timeout-wrapped and 60-FPS-capped pinned-engine child command."""
    timeout = shutil.which("timeout")
    if timeout is None:
        raise RuntimeError("GNU timeout is required for every Godot invocation")
    result = [timeout, "60", godot]
    if not windowed:
        result.append("--headless")
    result.extend(
        [
            "--max-fps",
            "60",
            "--path",
            os.fspath(ROOT),
            "--log-file",
            os.fspath(log_path),
            "res://tests/integration/replication/replication_process.tscn",
            "--",
            f"--role={role}",
            f"--port={port}",
        ]
    )
    if capture_dir is not None:
        result.append(f"--capture-dir={capture_dir.as_posix()}")
    return result


def await_host_ready(child, stdout_path):
    """Wait for the post-create_server receipt without assuming startup speed."""
    deadline = time.monotonic() + HOST_READY_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        text = stdout_path.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if not line.startswith(HOST_READY):
                continue
            try:
                receipt = json.loads(line.removeprefix(HOST_READY))
            except json.JSONDecodeError:
                return None
            if receipt.get("ok") and receipt.get("event") == "host_ready":
                return receipt
            return None
        if child.poll() is not None:
            return None
        time.sleep(0.05)
    return None


def main():
    """Launch host and client, inspect bounded outcomes, and stop only owned children."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", default=shutil.which("godot") or "godot")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--profile", choices=PROFILES, default="direct")
    parser.add_argument("--windowed", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must stay outside the checkout")
    if output.exists() and any(output.iterdir()):
        parser.error("output must be a fresh empty directory")
    output.mkdir(parents=True, exist_ok=True)

    host_port = available_port()
    proxy = None
    client_port = host_port
    if args.profile != "direct":
        proxy = DatagramImpairmentProxy(host_port, PROFILES[args.profile])
        proxy.start()
        client_port = proxy.port

    children = []
    streams = []
    exit_codes = {}
    failed = []
    host_ready = None
    try:
        for role in ("host", "client"):
            stdout_path = output / f"{role}.stdout.log"
            stream = stdout_path.open("w", encoding="utf-8")
            streams.append(stream)
            port = host_port if role == "host" else client_port
            capture_dir = output / "captures" if args.windowed and role == "client" else None
            child = subprocess.Popen(
                command(
                    args.godot,
                    role,
                    port,
                    output / f"{role}.engine.log",
                    windowed=args.windowed,
                    capture_dir=capture_dir,
                ),
                cwd=ROOT,
                stdout=stream,
                stderr=subprocess.STDOUT,
            )
            children.append((role, child, stdout_path))
            if role == "host":
                host_ready = await_host_ready(child, stdout_path)
                if host_ready is None:
                    failed.append("host readiness timeout")
                    break

        for role, child, _stdout_path in children:
            try:
                returncode = child.wait(timeout=45)
            except subprocess.TimeoutExpired:
                child.terminate()
                returncode = child.wait(timeout=3)
            exit_codes[role] = returncode
            if returncode != 0:
                failed.append(f"{role} exit {returncode}")
    finally:
        for role, child, _stdout_path in children:
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=3)
            exit_codes.setdefault(role, child.returncode)
        for stream in streams:
            stream.close()
        if proxy is not None:
            proxy.close()

    diagnostics = []
    receipts = {}
    for role, _child, stdout_path in children:
        text = stdout_path.read_text(encoding="utf-8", errors="replace")
        engine_text = (output / f"{role}.engine.log").read_text(
            encoding="utf-8", errors="replace"
        )
        receipt_prefix = f"{SUCCESS}{role} "
        receipt_lines = [
            line for line in text.splitlines() if line.startswith(receipt_prefix)
        ]
        try:
            receipts[role] = json.loads(receipt_lines[-1].split(" ", 2)[2])
        except (IndexError, json.JSONDecodeError):
            failed.append(f"{role} missing success receipt")
            receipts[role] = {}
        if not receipts[role].get("ok") or not receipts[role].get("boundary_proved"):
            failed.append(f"{role} missing bounded-command proof")
        for field in (
            "dead_observed",
            "respawn_observed",
            "old_generation_proved",
            "reset_observed",
            "input_reopened",
        ):
            if not receipts[role].get(field):
                failed.append(f"{role} missing lifecycle proof: {field}")
        if role == "client" and not receipts[role].get("prediction_bounded"):
            failed.append("client prediction was not bounded")
        if role == "client" and not receipts[role].get("remote_continuous"):
            failed.append("client remote presentation was not continuous")
        if role == "host":
            rejections = receipts[role].get("command_rejections", {})
            if rejections.get("PACKET_SIZE", 0) < 1:
                failed.append("host missing oversize RPC rejection")
            if rejections.get("MALFORMED_COMMAND", 0) < 1:
                failed.append("host missing malformed RPC rejection")
        for marker in ("SCRIPT ERROR:", "ERROR:", "WARNING:"):
            if marker in text or marker in engine_text:
                diagnostics.append(f"{role} emitted {marker}")

    captures = sorted((output / "captures").glob("*.png"))
    if args.windowed and len(captures) < 2:
        failed.append("windowed run captured fewer than two continuity frames")
    ok = not failed and not diagnostics
    (output / "result.json").write_text(
        json.dumps(
            {
                "captures": [path.name for path in captures],
                "diagnostics": diagnostics,
                "exit_codes": exit_codes,
                "failures": failed,
                "host_ready": host_ready,
                "ok": ok,
                "port": host_port,
                "profile": args.profile,
                "profile_settings": PROFILES[args.profile],
                "proxy": (
                    None
                    if proxy is None
                    else {"dropped": proxy.dropped, "forwarded": proxy.forwarded}
                ),
                "receipts": receipts,
                "windowed": args.windowed,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    if not ok:
        print("; ".join(failed + diagnostics))
        return 1
    print(
        f"M1-A2.3 {args.profile} ENet prediction passed on UDP {host_port}; "
        f"evidence: {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
