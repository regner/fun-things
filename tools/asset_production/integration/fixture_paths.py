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
EXPECTED_MIGRATED_SCENE_SHA256 = {
    "batch_01_camera.tscn": "8f7b417584ea7c0d23b6e153e71c0b658f28aa95550c7a746c4a0b409264c8a6",
    "batch_01_close.tscn": "5b7ed85cd84b459152ce44a321d485401fe6075286c2c688054c235c553f1914",
    "batch_01_repeat.tscn": "31db7d9ec42456c51b1ec9bcbe4dd6ec058d9715fcd3a1235b605397835a4c15",
    "batch_02_camera.tscn": "d2e38dd1cac28a73eae93f7fa4b16e226916d3392aac84305bf7fdef4bc1e08d",
    "batch_02_close.tscn": "8b9b18f72476b7a90dbe865c8f228317b1c87c568108956dc436d97f7fff5225",
    "batch_02_repeat.tscn": "34bdc4cce978f8b27eeb19b01a343e2da6f7b274f98fde4a032493d4e0f7ae88",
    "batch_02_roof.tscn": "cbff861783b1205ab94a733c5f1676978e94bb3390b0c1f53da6f7f34e2f86ca",
    "batch_02_trunks.tscn": "d3930321e290bd3adfc8c46d9285394953679070e2a4f7daf5bd3d0879fb5376",
    "batch_03_camera.tscn": "b9a40b94740246732b5b84346d09b04153d3e7508136a7162025f8dac7c3b522",
    "batch_03_close.tscn": "3a6decb910c2d820cbe3f4005f1b4f8ce3a5c3cd960a928b73fbcd93022c0905",
    "batch_03_frontage.tscn": "f65f1904de189fdad1895b21e0bb4e897d8ebb7b3abb1e41102534393406b5ca",
    "batch_03_process.tscn": "4da28361b5c56922d07aede592dca59ae2b3c662db52f39791eb4230f6536150",
    "batch_03_repeat.tscn": "793408eea11d10ac87a365b672fb1f1881ab68a591167f666f5c0ad83d55da99",
    "batch_03_upper_wall.tscn": "433a1863f53227337c0d0cf90770d066c314ea9b60488899dff1f3a8f5296e83",
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


def assert_preserved_scene(root, recorded_path):
    """Assert that a migrated fixture retained its approved content and saved identity."""
    path = current_path(root, recorded_path)
    payload = path.read_bytes()
    expected_uid = EXPECTED_SCENE_UIDS[path.name]
    expected_hash = EXPECTED_MIGRATED_SCENE_SHA256[path.name]
    first_line = payload.decode("utf-8").splitlines()[0]
    match = re.search(r'uid="([^"]+)"', first_line)
    assert match is not None and match.group(1) == expected_uid, recorded_path
    assert hashlib.sha256(payload).hexdigest() == expected_hash, recorded_path


def assert_reviewed_roundtrips(root, rows):
    """Check reviewed hashes plus post-migration fixture hashes and saved identities."""
    for recorded_path, expected_hash in rows.items():
        normalized = recorded_path.removeprefix("res://")
        if normalized.startswith(OLD_PREFIX):
            assert_preserved_scene(root, recorded_path)
            continue

        payload = current_path(root, recorded_path).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == expected_hash, recorded_path
