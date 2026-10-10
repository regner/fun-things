#!/usr/bin/env python3
"""Launch an exported host and client side by side for a bounded owner playtest."""

import argparse
import json
from pathlib import Path
import shutil
import sys

from run_exported_acceptance import (
    ExportedAcceptanceRunner,
    READINESS_TIMEOUT_SECONDS,
)


def main() -> int:
    """Await both real ENet Match receipts, then leave both windows to the owner."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    executable = args.executable.resolve()
    output = args.output.resolve()
    if not executable.is_file():
        parser.error("--executable does not exist")
    if output.exists() and any(output.iterdir()):
        parser.error("--output must be a fresh empty directory")
    timeout_executable = shutil.which("timeout")
    if timeout_executable is None:
        parser.error("GNU timeout is required for every exported process")
    output.mkdir(parents=True, exist_ok=True)

    runner = ExportedAcceptanceRunner(executable, output, timeout_executable)
    try:
        host, client = runner.pair("owner-playtest", "playtest")
        host_ready = host.wait_event(runner.event("match_ready"), READINESS_TIMEOUT_SECONDS)
        client_ready = client.wait_event(runner.event("match_ready"), READINESS_TIMEOUT_SECONDS)
        receipt = {
            "ok": host_ready.get("brackett_loaded") and client_ready.get("brackett_loaded"),
            "port": next(
                event["port"] for event in host.events if event.get("event") == "host_ready"
            ),
            "controls": "Focus either window; WASD walks and the mouse aims.",
            "process_timeout_seconds": 180,
        }
        (output / "ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(receipt, indent=2), flush=True)
        print("Close both windows when finished; each is hard-bounded to 180 seconds.", flush=True)
        exits = {"client": client.finish(timeout=180), "host": host.finish(timeout=5)}
        return 0 if receipt["ok"] and all(code in (0, 124) for code in exits.values()) else 1
    finally:
        runner.cleanup()


if __name__ == "__main__":
    sys.exit(main())
