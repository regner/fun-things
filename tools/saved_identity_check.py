#!/usr/bin/env python3
"""Reject incomplete or mismatched identities in tracked Godot resources."""

from dataclasses import dataclass
from pathlib import Path
import re
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PREFIXES = ("addons/", "prototypes/", "docs/")
# Remove this temporary exception after the m1-p1fix and m1-b12 lanes land.
ALLOWLIST = frozenset(
    {
        "scenes/entities/player.tscn",
        "scenes/local/local_rig.tscn",
        "scenes/match/match.tscn",
        "scenes/ui/hud.tscn",
        "scenes/ui/main_menu.tscn",
        "scenes/ui/session_status.tscn",
        "scenes/ui/settings_menu.tscn",
        "tests/integration/replication/replication_process.tscn",
        "tests/integration/session/session_process.tscn",
        "tests/integration/vehicles/vehicle_replication_process.tscn",
    }
)
UID_PATTERN = r"uid://[a-y0-8]+"
HEADER_PATTERN = re.compile(
    rf'^\[(?:gd_scene|gd_resource)\b[^\]]*\buid="({UID_PATTERN})"[^\]]*\]$'
)
ATTRIBUTE_PATTERN = re.compile(r'(\w+)="([^"]*)"')
NODE_UID_PATTERN = re.compile(r"(?:^|\s)unique_id=[1-9][0-9]*(?:\s|\])")
UID_ALPHABET = "abcdefghijklmnopqrstuvwxy012345678"


@dataclass(frozen=True, order=True)
class Finding:
    """One source-located saved-identity contract violation."""

    path: str
    line: int
    message: str

    def format(self) -> str:
        """Render a finding in compiler-style path:line form."""
        return f"{self.path}:{self.line}: {self.message}"


def tracked_paths(root: Path = ROOT) -> list[str]:
    """Return repository-relative tracked paths using Git as the scope authority."""
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        capture_output=True,
        check=True,
    )
    return sorted(
        path.decode("utf-8")
        for path in result.stdout.split(b"\0")
        if path
    )


def is_in_scope(path: str) -> bool:
    """Return whether a tracked path belongs to the project-owned identity scope."""
    return not path.startswith(EXCLUDED_PREFIXES) and path not in ALLOWLIST


def _uid_text(value: int) -> str:
    """Encode the base-34 integer representation used by Godot ResourceUID."""
    digits = ""
    while True:
        digits = UID_ALPHABET[value % len(UID_ALPHABET)] + digits
        value //= len(UID_ALPHABET)
        if value == 0:
            return "uid://" + digits


def _binary_resource_uid(path: Path) -> str | None:
    """Read a Godot binary resource header UID without consulting a local cache."""
    data = path.read_bytes()
    if len(data) < 40 or data[:4] != b"RSRC":
        return None

    endian = "<" if data[4:8] == b"\0\0\0\0" else ">"
    string_size = struct.unpack_from(endian + "I", data, 24)[0]
    uid_offset = 28 + string_size + 8 + 4
    if uid_offset + 8 > len(data):
        return None
    uid = struct.unpack_from(endian + "Q", data, uid_offset)[0]
    return _uid_text(uid) if uid else None


def _text_uid(path: Path, pattern: re.Pattern[str]) -> str | None:
    """Return the first UID matching a text metadata format."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    match = pattern.search(text)
    return match.group(1) if match else None


def target_uid(root: Path, relative_path: str, tracked: set[str]) -> str | None:
    """Resolve a dependency UID from its committed source metadata or binary header."""
    source = root / relative_path
    uid_sidecar = relative_path + ".uid"
    if uid_sidecar in tracked:
        return _text_uid(root / uid_sidecar, re.compile(rf"^({UID_PATTERN})\s*$", re.MULTILINE))

    import_sidecar = relative_path + ".import"
    if import_sidecar in tracked:
        return _text_uid(
            root / import_sidecar,
            re.compile(rf'^uid="({UID_PATTERN})"\s*$', re.MULTILINE),
        )

    if source.suffix in {".tscn", ".tres"} and source.is_file():
        first_line = source.read_text(encoding="utf-8").splitlines()[0]
        match = HEADER_PATTERN.match(first_line)
        return match.group(1) if match else None
    if source.suffix == ".res" and source.is_file():
        return _binary_resource_uid(source)
    return None


def _resource_findings(
    root: Path,
    relative_path: str,
    tracked: set[str],
) -> list[Finding]:
    """Check one text scene or resource and return all source-located violations."""
    findings: list[Finding] = []
    lines = (root / relative_path).read_text(encoding="utf-8").splitlines()
    if not lines or not HEADER_PATTERN.match(lines[0]):
        findings.append(Finding(relative_path, 1, "missing or invalid saved resource header UID"))

    for line_number, line in enumerate(lines, start=1):
        if line.startswith("[ext_resource "):
            attributes = dict(ATTRIBUTE_PATTERN.findall(line))
            dependency = attributes.get("path", "")
            dependency_path = dependency.removeprefix("res://")
            if dependency_path in ALLOWLIST:
                continue
            actual_uid = attributes.get("uid")
            expected_uid = target_uid(root, dependency_path, tracked)
            if actual_uid is None:
                findings.append(Finding(relative_path, line_number, "external resource has no UID"))
            elif expected_uid is None:
                findings.append(
                    Finding(
                        relative_path,
                        line_number,
                        f"dependency has no tracked UID metadata: {dependency}",
                    )
                )
            elif actual_uid != expected_uid:
                findings.append(
                    Finding(
                        relative_path,
                        line_number,
                        f"dependency UID {actual_uid} does not match {expected_uid}: {dependency}",
                    )
                )
        elif (
            relative_path.endswith(".tscn")
            and line.startswith("[node ")
            and not NODE_UID_PATTERN.search(line)
            and " instance_placeholder=" not in line
        ):
            findings.append(Finding(relative_path, line_number, "node has no unique_id"))
    return findings


def collect_findings(root: Path = ROOT, paths: list[str] | None = None) -> list[Finding]:
    """Check all tracked project-owned saved identities and return sorted findings."""
    tracked = set(paths if paths is not None else tracked_paths(root))
    findings: list[Finding] = []
    for relative_path in sorted(tracked):
        if not is_in_scope(relative_path):
            continue
        if relative_path.endswith((".tscn", ".tres")):
            findings.extend(_resource_findings(root, relative_path, tracked))
        elif relative_path.endswith(".gd"):
            sidecar = relative_path + ".uid"
            if sidecar not in tracked:
                findings.append(Finding(relative_path, 1, "tracked GDScript has no tracked .gd.uid"))
            elif target_uid(root, relative_path, tracked) is None:
                findings.append(Finding(sidecar, 1, "missing or invalid GDScript UID"))
    return sorted(findings)


def main() -> int:
    """Print exact violations and return nonzero when the saved identity check fails."""
    findings = collect_findings()
    for finding in findings:
        print(finding.format())
    if findings:
        print(f"Saved identity check failed: {len(findings)} finding(s).")
        return 1
    print("Saved identity check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
