"""Incremental complete-line readers for polling runner logs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def appended_complete_lines(path: Path, state: dict[str, int]) -> list[str]:
    """Read only complete lines appended after the retained byte offset."""
    key = str(path.resolve())
    offset = state.setdefault(key, 0)
    if not path.exists():
        return []
    lines = []
    with path.open("rb") as stream:
        stream.seek(offset)
        while True:
            position = stream.tell()
            line = stream.readline()
            if not line:
                state[key] = position
                break
            if not line.endswith(b"\n"):
                state[key] = position
                break
            state[key] = stream.tell()
            lines.append(line.decode(errors="replace"))
    return lines


def prefixed_json_records(
    path: Path, prefix: bytes, state: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Return cached records after reading only newly appended complete log lines."""
    key = str(path.resolve())
    cursor = state.setdefault(key, {"offset": 0, "records": []})
    if not path.exists():
        return list(cursor["records"])

    with path.open("rb") as stream:
        stream.seek(cursor["offset"])
        while True:
            position = stream.tell()
            line = stream.readline()
            if not line:
                cursor["offset"] = position
                break
            if not line.endswith(b"\n"):
                cursor["offset"] = position
                break
            cursor["offset"] = stream.tell()
            if line.startswith(prefix):
                cursor["records"].append(json.loads(line[len(prefix):]))
    return list(cursor["records"])
