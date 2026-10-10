"""Compact review renders and inventory every shop delivery file except the manifest itself."""
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d02_corner_shop_02"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
MANIFEST = EVIDENCE / "manifest.json"


def payload_paths():
    """Discover only this record's produced source, exports, tools, prefab and lean evidence."""
    paths = [ROOT / f"docs/assets/production/{ASSET}.md",
             ROOT / "docs/assets/production/d02_corner_shop_01.md",
             ROOT / "docs/assets/production/d02_corner_shop_01-evidence/manifest.json"]
    paths.extend((ROOT / "scenes/prefabs/environment").glob(ASSET + "*.tscn*"))
    for directory in (ROOT / f"art/source/models/environment/{ASSET}",
                      ROOT / f"art/models/environment/{ASSET}",
                      ROOT / f"tools/asset_production/{ASSET}", EVIDENCE):
        paths.extend(p for p in directory.rglob("*") if p.is_file()
                     and p != MANIFEST and "__pycache__" not in p.parts)
    return sorted(set(paths))


def inventory():
    """Hash source-linked payload bytes, retaining relative paths for independent readback."""
    return [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size,
             "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in payload_paths()]


if "--verify" in sys.argv:
    expected = json.loads(MANIFEST.read_text())["files"]
    assert expected == inventory(), "Delivery paths, sizes or hashes changed"
    print("D02_CORNER_SHOP_02_MANIFEST_VERIFIED", len(expected), "payload files")
else:
    checks = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(f"C:/tmp/ft/assets/{ASSET}/checks")
    summary = json.loads((checks / "summary.json").read_text())
    assert summary["ok"], "Production checks did not pass"
    images = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / (name + ".png")
        image = Image.open(path)
        assert image.size == (1280, 720)
        image = ImageOps.posterize(image.convert("RGB"), bits=7)
        image.save(path, optimize=True, compress_level=9)
        images.append({"file": path.name, "size_px": [1280, 720], "bytes": path.stat().st_size})
    path = EVIDENCE / "validation.json"
    data = json.loads(path.read_text())
    assert data["godot"]["physics"]["authority_replay_within_2mm"]
    assert data["godot"]["save_reload_byte_stable"]
    data["production_checks"] = summary["results"]
    data["renders"] = images
    data["render_encoding"] = "RGB 7 significant bits per channel; PNG compression 9"
    data["gameplay_camera"] = {
        "renderer": "Blender Cycles CPU / AgX; not an engine gameplay capture",
        "position_blender_m": [0, 0, 47], "rotation_radians": [0, 0, 0],
        "vertical_fov_degrees": 42, "projection": "perspective",
        "note": "Centred annex; camera remains vertical-down and fixed yaw",
    }
    path.write_text(json.dumps(data, indent=2) + "\n", newline="\n")
    manifest = {"asset": "d02_corner_shop.02", "producer": "commissioned implementation specialist",
                "hash_algorithm": "SHA-256", "self_excluded": True, "files": inventory()}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
    print("D02_CORNER_SHOP_02_MANIFEST_WRITTEN", len(manifest["files"]), "payload files")
