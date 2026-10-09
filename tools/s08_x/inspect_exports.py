#!/usr/bin/env python3
"""Inspect the four S08-X desktop exports and reject development-addon leaks."""

import argparse
import hashlib
import json
from pathlib import Path
import struct


EXPORTS = {
    "windows_debug": ("windows-debug/FunThingsDebug.exe", "PE"),
    "windows_release": ("windows-release/FunThings.exe", "PE"),
    "linux_debug": ("linux-debug/FunThingsDebug.x86_64", "ELF"),
    "linux_release": ("linux-release/FunThings.x86_64", "ELF"),
}
FORBIDDEN_PREFIXES = ("addons/godot_mcp_toolkit/", "addons/godotsteam/")
FORBIDDEN_NATIVE_NAMES = frozenset({
    "steam_api.dll",
    "steam_api64.dll",
    "libsteam_api.so",
    "libsteam_api.dylib",
})
REQUIRED = ("run/main_scene", "tests/fixtures/s06/intersection")


def identity(path: Path) -> dict:
    """Return a stable identity for one complete exported file."""
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"path": path.as_posix(), "bytes": path.stat().st_size, "sha256": digest}


def executable_format(path: Path) -> str:
    """Identify only the two expected x86-64 executable container formats."""
    header = path.read_bytes()[:64]
    if header[:4] == b"\x7fELF" and header[4:6] == b"\x02\x01":
        return "ELF"
    if header[:2] == b"MZ":
        return "PE"
    return "unknown"


def pck_entries(path: Path) -> list[str]:
    """Read names from the unencrypted Godot 4 PCK directory."""
    data = path.read_bytes()
    magic, version = struct.unpack_from("<2I", data)
    if magic != 0x43504447 or version != 4:
        raise ValueError(f"unexpected PCK header: {path}")
    flags = struct.unpack_from("<I", data, 20)[0]
    if flags & 1:
        raise ValueError(f"encrypted PCK is not inspectable: {path}")
    directory_offset = struct.unpack_from("<Q", data, 32)[0]
    count = struct.unpack_from("<I", data, directory_offset)[0]
    position = directory_offset + 4
    entries = []
    for _index in range(count):
        length = struct.unpack_from("<I", data, position)[0]
        position += 4
        name = data[position:position + length].rstrip(b"\0").decode("utf-8")
        position += length + 36
        entries.append(name.removeprefix("res://"))
    return entries


def is_forbidden_export_path(path: str) -> bool:
    """Identify MCP and all bundled GodotSteam/Steamworks export artifacts."""
    normalized = path.replace("\\", "/").removeprefix("res://").lower()
    basename = normalized.rsplit("/", maxsplit=1)[-1]
    if normalized.startswith(FORBIDDEN_PREFIXES):
        return True
    if basename == ".mcp.json" or "godotsteam" in basename:
        return True
    return any(basename == name or basename.startswith(name + ".")
               for name in FORBIDDEN_NATIVE_NAMES)


def find_forbidden_output_files(directory: Path) -> list[str]:
    """List forbidden native/development artifacts beside one exported executable."""
    files = [path.relative_to(directory).as_posix()
             for path in directory.rglob("*") if path.is_file()]
    return [path for path in files if is_forbidden_export_path(path)]


def inspect(root: Path) -> dict:
    """Validate all configured exports and return their hashes and package membership."""
    result = {"ok": True, "exports": {}}
    for label, (relative, expected_format) in EXPORTS.items():
        executable = root / relative
        package = executable.with_suffix(".pck")
        entries = pck_entries(package)
        leaks = [entry for entry in entries if is_forbidden_export_path(entry)]
        missing = [required for required in REQUIRED
                   if not any(required in entry for entry in entries)]
        actual_format = executable_format(executable)
        output_leaks = find_forbidden_output_files(executable.parent)
        passed = actual_format == expected_format and not leaks and not missing and not output_leaks
        result["exports"][label] = {
            "ok": passed,
            "executable": identity(executable),
            "package": identity(package),
            "format": actual_format,
            "pck_entry_count": len(entries),
            "required_matches": {
                required: [entry for entry in entries if required in entry]
                for required in REQUIRED
            },
            "forbidden_pck_entries": leaks,
            "forbidden_output_files": output_leaks,
        }
        result["ok"] = result["ok"] and passed
    return result


def main() -> int:
    """Parse arguments, retain one JSON receipt, and signal contract failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
