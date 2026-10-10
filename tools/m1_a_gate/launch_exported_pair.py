#!/usr/bin/env python3
"""Launch an exported host and client side by side for a bounded owner playtest."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys

from run_exported_acceptance import (
    ExportedAcceptanceRunner,
    READINESS_TIMEOUT_SECONDS,
)


def _default_output() -> Path:
    """Return a fresh owner-run directory without requiring shell-specific syntax."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    return Path("C:/tmp/ft/m1-a-gate-owner-pair") / stamp


def _powershell_example(executable: Path) -> str:
    """Quote the current executable path for a directly pasteable PowerShell command."""
    quoted = str(executable).replace("'", "''")
    return (
        "python .\\tools\\m1_a_gate\\launch_exported_pair.py "
        f"--executable '{quoted}'"
    )


def main() -> int:
    """Await both real ENet Match receipts, then leave both windows to the owner."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    executable = args.executable.resolve()
    output = (args.output if args.output is not None else _default_output()).resolve()
    if not executable.is_file():
        parser.error("--executable does not exist")
    if output.exists() and any(output.iterdir()):
        parser.error("--output must be a fresh empty directory")
    output.mkdir(parents=True, exist_ok=True)
    print(f"PowerShell example: {_powershell_example(executable)}", flush=True)
    print(f"Output: {output}", flush=True)

    runner = ExportedAcceptanceRunner(executable, output)
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
        bounded = {
            "client": client.hard_timed_out or exits["client"] == 0,
            "host": host.hard_timed_out or exits["host"] == 0,
        }
        return 0 if receipt["ok"] and all(bounded.values()) else 1
    finally:
        runner.cleanup()


if __name__ == "__main__":
    sys.exit(main())
