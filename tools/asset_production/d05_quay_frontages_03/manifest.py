"""Compact isolated renders and hash only this asset's complete delivery payload."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_quay_frontages_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
MANIFEST = EVIDENCE / "manifest.json"


def payload_paths():
    """Inventory the owned source, export, prefab, scripts, handoff and lean evidence."""
    paths = [ROOT / f"docs/assets/production/{NID}.md"]
    paths.extend((ROOT / "scenes/prefabs/environment").glob(NID + "*.tscn*"))
    for directory in (ROOT / f"art/source/models/environment/{NID}",
                      ROOT / f"art/models/environment/{NID}",
                      ROOT / f"tools/asset_production/{NID}", EVIDENCE):
        paths.extend(p for p in directory.rglob("*") if p.is_file()
                     and p != MANIFEST and "__pycache__" not in p.parts)
    return sorted(set(paths))


def inventory():
    """Record portable relative paths and SHA-256 of every required payload."""
    return [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size,
             "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in payload_paths()]


def prepare_evidence():
    """Compact PNG encoding without resizing and attach final validation observations."""
    from PIL import Image, ImageOps

    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / (name + ".png")
        image = Image.open(path)
        assert image.size == (1280, 720)
        image = ImageOps.posterize(image.convert("RGB"), bits=6)
        image.save(path, optimize=True, compress_level=9)
        renders.append({"file": path.name, "size_px": [1280, 720], "bytes": path.stat().st_size})
    path = EVIDENCE / "validation.json"
    data = json.loads(path.read_text())
    assert data["fresh_reexport_byte_identical"]
    assert data["godot"]["physics"]["authority_replay_within_2mm"]
    assert data["godot"]["save_reload_byte_stable"]
    data["renders"] = renders
    data["render_encoding"] = "RGB 6 significant bits per channel; PNG compression 9"
    data["gameplay_camera"] = {
        "renderer": "Blender Cycles CPU / AgX, 32 samples; not an engine gameplay capture",
        "position_blender_m": [0, 0, 47], "rotation_radians": [0, 0, 0],
        "vertical_fov_degrees": 42, "projection": "perspective", "resolution": [1280, 720],
    }
    data["validation_scope"] = {
        "production_checks": "Not run: common brief / owner decision 52 for unplaced assets",
        "source_export": "PASS; pinned saved-source fresh-process byte comparison",
        "headless_prefab": "PASS; registered dependency UIDs, two saves, ActorMotion authority/replay",
        "style": "PASS; pinned gdstyle fmt --check and --max-line-length 100 --max-warnings 0",
        "independent_review_world_device": "pending",
    }
    path.write_text(json.dumps(data, indent=2) + "\n", newline="\n")


if "--prepare-evidence" in sys.argv:
    prepare_evidence()
elif "--verify" in sys.argv:
    expected = json.loads(MANIFEST.read_text())["files"]
    assert expected == inventory(), "Delivery file set, sizes or hashes changed"
    print("D05_QUAY_FRONTAGES_03_MANIFEST_VERIFIED", len(expected), "payload files")
else:
    data = {"asset": "d05_quay_frontages.03", "producer": "commissioned implementation specialist",
            "hash_algorithm": "SHA-256", "self_excluded": True, "files": inventory()}
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n", newline="\n")
    print("D05_QUAY_FRONTAGES_03_MANIFEST_WRITTEN", len(data["files"]), "payload files")
