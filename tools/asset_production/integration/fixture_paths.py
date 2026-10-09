"""Resolve the intentional asset-check move while preserving reviewed fixture identities."""

import hashlib
from pathlib import Path
import re

OLD_PREFIX = "tests/fixtures/asset_production/"
NEW_PREFIX = "tests/assets/asset_production/"
EXPECTED_SCENE_UIDS = {
    "batch_01_camera.tscn": "uid://ckn4gl5tx6oqi",
    "batch_01_close.tscn": "uid://v0d5akcqmv4r",
    "batch_01_repeat.tscn": "uid://bff0wc268obb",
    "batch_02_camera.tscn": "uid://hik8rg1e7j6e",
    "batch_02_close.tscn": "uid://d27hv7x7ugabm",
    "batch_02_repeat.tscn": "uid://we2vmj4uabkr",
    "batch_02_roof.tscn": "uid://5ta1kvmrqh12",
    "batch_02_trunks.tscn": "uid://b1bvfmpmlaxrj",
    "batch_03_camera.tscn": "uid://bivmh70n4vcpd",
    "batch_03_close.tscn": "uid://rvmcd6iaiu1x",
    "batch_03_frontage.tscn": "uid://c5f38dwws3tw7",
    "batch_03_process.tscn": "uid://dyk0o4lw71dmu",
    "batch_03_repeat.tscn": "uid://dajjx35ikceqf",
    "batch_03_upper_wall.tscn": "uid://ctp2hp6c84jnj",
}


def current_relative_path(recorded_path):
    """Map a retained pre-cleanup path to its current production asset-check location."""
    normalized = recorded_path.removeprefix("res://")
    if normalized.startswith(OLD_PREFIX):
        return normalized.replace(OLD_PREFIX, NEW_PREFIX, 1)
    return normalized


def current_path(root, recorded_path):
    """Return the current filesystem path represented by one retained evidence path."""
    return root / current_relative_path(recorded_path)


def assert_preserved_scene_uid(root, recorded_path):
    """Assert that an intentionally changed fixture retained its reviewed saved identity."""
    path = current_path(root, recorded_path)
    expected = EXPECTED_SCENE_UIDS[path.name]
    match = re.search(r'uid="([^"]+)"', path.read_text(encoding="utf-8").splitlines()[0])
    assert match is not None and match.group(1) == expected, recorded_path


def assert_reviewed_roundtrips(root, rows):
    """Check unchanged bytes and use saved UID identity for intentionally migrated fixtures."""
    for recorded_path, expected_hash in rows.items():
        normalized = recorded_path.removeprefix("res://")
        if normalized.startswith(OLD_PREFIX):
            assert_preserved_scene_uid(root, recorded_path)
            continue

        payload = current_path(root, recorded_path).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == expected_hash, recorded_path
