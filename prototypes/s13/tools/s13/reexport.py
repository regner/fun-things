#!/usr/bin/env python3
"""Re-export S13's committed Blender source and require the committed GLB to match."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "art/source/models/characters/s13_humanoid.blend"
TARGET = ROOT / "art/models/characters/s13_humanoid.glb"


def inspect_glb(path):
    """Return the JSON chunk from one binary glTF file."""
    data = path.read_bytes()
    magic, version, _length = struct.unpack_from("<4sII", data)
    if magic != b"glTF" or version != 2:
        raise RuntimeError("invalid GLB header")
    chunk_length, chunk_type = struct.unpack_from("<I4s", data, 12)
    if chunk_type != b"JSON":
        raise RuntimeError("GLB does not begin with JSON")
    return json.loads(data[20:20 + chunk_length].decode("utf-8"))


def main():
    """Run one bounded Blender child, validate output, and retain fingerprints."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", default=(
        shutil.which("blender") or
        "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
    ))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = (args.output or Path(tempfile.mkdtemp(prefix="s13-reexport-"))).resolve()
    if output.is_relative_to(ROOT):
        parser.error("output must be outside the checkout")
    if output.exists() and any(output.iterdir()):
        parser.error("output must be fresh and empty")
    output.mkdir(parents=True, exist_ok=True)
    scratch = output / "s13_humanoid.glb"
    command = [args.blender, "-b", str(SOURCE), "--python-exit-code", "1", "--python",
               str(ROOT / "tools/s13/export_humanoid.py"), "--", str(scratch)]
    environment = os.environ.copy()
    environment["ALSOFT_DRIVERS"] = "null"
    with (output / "blender.log").open("wb") as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT,
                                env=environment, timeout=120, check=False)
    model = inspect_glb(scratch) if result.returncode == 0 and scratch.exists() else {}
    animations = sorted(animation["name"] for animation in model.get("animations", []))
    extensions = model.get("extensionsUsed", [])
    images = model.get("images", [])
    matches = scratch.exists() and TARGET.exists() and scratch.read_bytes() == TARGET.read_bytes()
    record = {
        "ok": result.returncode == 0 and animations == ["death", "idle", "run", "walk"]
              and not extensions and not images and matches,
        "command": command,
        "exit": result.returncode,
        "animations": animations,
        "extensions": extensions,
        "images": images,
        "byte_identical": matches,
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "export_sha256": hashlib.sha256(scratch.read_bytes()).hexdigest() if scratch.exists() else None,
        "committed_export_sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest()
        if TARGET.exists() else None,
    }
    (output / "result.json").write_text(json.dumps(record, indent=2) + "\n", newline="\n")
    print(json.dumps({"ok": record["ok"], "output": str(output)}))
    return 0 if record["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
