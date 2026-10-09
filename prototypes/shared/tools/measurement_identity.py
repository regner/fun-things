"""Shared repository, source, invocation, and parameter binding for measurement runners."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable


def _git(root: Path, *arguments: str) -> str:
    """Run one bounded read-only Git query in the repository root."""
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    return result.stdout.strip()


def repository_identity(root: Path) -> dict[str, object]:
    """Return the committed revision, tree, and complete working-tree status."""
    return {
        "commit": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "status_porcelain": _git(root, "status", "--porcelain").splitlines(),
    }


def _tracked_paths(root: Path, source: Path) -> list[Path]:
    """List only committed files beneath one repository-relative source path."""
    relative = source.relative_to(root).as_posix()
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", relative],
        cwd=root,
        capture_output=True,
        timeout=10,
        check=True,
    )
    return [root / value.decode("utf-8") for value in result.stdout.split(b"\0") if value]


def _source_files(root: Path, sources: Iterable[str | Path]) -> list[Path]:
    """Expand sources into a stable inventory of committed files only."""
    files: set[Path] = set()
    resolved_root = root.resolve()
    for source in sources:
        path = (root / source).resolve()
        if not path.is_relative_to(resolved_root):
            raise ValueError(f"measurement source is outside repository: {source}")
        if not path.exists():
            raise FileNotFoundError(f"measurement source does not exist: {source}")
        tracked = _tracked_paths(resolved_root, path)
        if path.is_file() and path not in tracked:
            raise ValueError(f"measurement source is not committed: {source}")
        files.update(candidate for candidate in tracked if candidate.is_file())
    return sorted(files, key=lambda path: path.relative_to(resolved_root).as_posix())


def source_fingerprints(
    root: Path, sources: Iterable[str | Path]
) -> dict[str, dict[str, int | str]]:
    """Hash runner, helper, and staged-input source bytes in a stable manifest."""
    resolved_root = root.resolve()
    return {
        path.relative_to(resolved_root).as_posix(): {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size,
        }
        for path in _source_files(root, sources)
    }


def _json_value(value: Any) -> Any:
    """Convert paths and nested argument values to strict JSON-compatible values."""
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    json.dumps(value)
    return value


def measurement_identity(
    root: Path,
    sources: Iterable[str | Path],
    effective_parameters: dict[str, Any],
    *,
    argv: list[str] | None = None,
    cwd: str | Path | None = None,
) -> dict[str, object]:
    """Bind one result to repository state, source bytes, invocation, and parameters."""
    return {
        "repository": repository_identity(root),
        "measurement_sources": source_fingerprints(root, sources),
        "invocation": {
            "argv": list(sys.argv if argv is None else argv),
            "cwd": str(Path(os.getcwd() if cwd is None else cwd).resolve()),
            "effective_parameters": _json_value(effective_parameters),
        },
    }
