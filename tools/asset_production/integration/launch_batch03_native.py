"""Launch one owned native comparison at physical 1280x800 and await its bounded exit."""

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
STATE = Path("/tmp/asset-register-production-editor")
MAX_FPS = 60
PROCESS_TIMEOUT_SECONDS = 180
TERMINATION_GRACE_SECONDS = 10


def write_receipts(row):
    """Persist launch ownership and completion state to private and retained receipts."""
    payload = json.dumps(row, indent=2) + "\n"
    (STATE / "batch03/native-launch.json").write_text(payload)
    retained = ROOT / f"docs/assets/production/batch_03-evidence/native-{row['label']}-launch.json"
    retained.write_text(payload)


label = sys.argv[1]
launch = json.loads((STATE / "launch.json").read_text())
assert os.readlink(f"/proc/{launch['pid']}/cwd") == str(ROOT)
parent_environment = Path(f"/proc/{launch['pid']}/environ").read_bytes().split(b"\0")
parent_environment = dict(
    value.decode().split("=", 1) for value in parent_environment if b"=" in value
)
overrides = {
    key: parent_environment[key]
    for key in ["DISPLAY", "WAYLAND_DISPLAY", "XDG_RUNTIME_DIR"]
    if key in parent_environment
}
overrides.update(
    {
        "XDG_DATA_HOME": str(STATE / "data"),
        "XDG_CONFIG_HOME": str(STATE / "config"),
        "XDG_CACHE_HOME": str(STATE / "cache"),
        "GODOT_MCP_RUNTIME_PORT": "22651",
    }
)
argv = [
    launch["argv"][0],
    "--path",
    str(ROOT),
    "--resolution",
    "1280x800",
    "--max-fps",
    str(MAX_FPS),
    f"res://tests/assets/asset_production/batch_03_{label}.tscn",
]
log = ROOT / f"docs/assets/production/batch_03-evidence/native-{label}.log"
with log.open("w") as stream:
    process = subprocess.Popen(
        argv,
        env=dict(os.environ, **overrides),
        stdout=stream,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    row = {
        "pid": process.pid,
        "argv": argv,
        "cwd": str(ROOT),
        "environment_overrides": overrides,
        "editor_pid": launch["pid"],
        "runtime_port": 22651,
        "label": label,
        "timeout_seconds": PROCESS_TIMEOUT_SECONDS,
    }
    write_receipts(row)
    print(process.pid, flush=True)

    try:
        returncode = process.wait(timeout=PROCESS_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        process.terminate()
        try:
            returncode = process.wait(timeout=TERMINATION_GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            process.kill()
            returncode = process.wait(timeout=TERMINATION_GRACE_SECONDS)
        row.update({"returncode": returncode, "timed_out": True})
        write_receipts(row)
        raise SystemExit(
            f"Batch 03 native {label} exceeded {PROCESS_TIMEOUT_SECONDS} seconds"
        )

row.update({"returncode": returncode, "timed_out": False})
write_receipts(row)
if returncode != 0:
    raise subprocess.CalledProcessError(returncode, argv)
