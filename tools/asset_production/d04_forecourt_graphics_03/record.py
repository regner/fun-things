"""Combine bounded receipts and reuse the existing exact-payload SHA-256 inventory."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_forecourt_graphics_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
MANIFEST = EVIDENCE / "manifest.json"
spec = importlib.util.spec_from_file_location(
    "payload_inventory", ROOT / "tools/asset_production/d06_commercial_graphics_01/manifest.py")
inventory_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory_tool)
inventory_tool.MANIFEST = MANIFEST
inventory_tool.OWNED = [path.replace("d06_commercial_graphics_01", NID)
                        for path in inventory_tool.OWNED] + [
    f"art/source/models/environment/{NID}", f"art/models/environment/{NID}"]
DEPENDENCIES = [
    "tools/asset_production/d04_forecourt_graphics_01/artwork.py",
    "tools/assets/blender/export_settings.json",
    "tools/asset_production/d06_commercial_graphics_01/manifest.py",
    "tools/asset_production/d01_sports_surface_03/validate.py",
    "tools/asset_production/city_ground_finishes_01/preview.py",
    "art/source/models/environment/city_ground_finishes_01/city_ground_finishes_01.blend",
    "art/textures/environment/city_ground_finishes_01/plain_plaza_paving_albedo.png",
    "art/source/models/characters/coral_courier/coral_courier.blend",
    "art/models/characters/coral_courier/coral_courier.glb",
    "art/source/models/vehicles/car_latch_a/car_latch_a.blend",
    "art/models/vehicles/car_latch_a/car_latch_a.glb",
]


def digest(path):
    """Hash actual retained bytes, not exporter metadata or an older receipt."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect():
    """Require current source/export, engine, artwork and render evidence before recording."""
    report = json.loads((EVIDENCE / "validation.json").read_text())
    engine = json.loads((SCRATCH / "prefab-check.json").read_text())
    normalized = json.loads((SCRATCH / "roundtrip.json").read_text())
    assert report["source_status"] == "PASS" and engine["ok"] and normalized["ok"]
    assert normalized["roundtrip_1_byte_stable"] and normalized["roundtrip_2_byte_stable"]
    for key in ("prefab_sha256", "material_sha256", f"{NID}.tscn_uid", "quiet_inset_emblem.tres_uid"):
        assert engine[key] == normalized[key], key
    assert digest(ROOT / f"scenes/prefabs/environment/{NID}.tscn") == engine["prefab_sha256"]
    assert digest(ROOT / f"art/materials/environment/{NID}/quiet_inset_emblem.tres") == engine["material_sha256"]
    glb = ROOT / f"art/models/environment/{NID}/{NID}.glb"
    assert digest(glb) == report["glb_sha256"]
    assert glb.read_bytes() == (SCRATCH / "reexport" / glb.name).read_bytes()
    texture = ROOT / f"art/textures/environment/{NID}/quiet_inset_emblem_albedo.png"
    assert digest(texture) == report["texture_sha256"]
    for name in ("import-final.log", "prefab.log"):
        text = (SCRATCH / name).read_text(encoding="utf-8")
        assert "ERROR:" not in text and "SCRIPT ERROR" not in text, name
        assert "4.8.dev7.official.c971f93e7" in text
    tests = (SCRATCH / "artwork-tests.log").read_text(encoding="utf-8")
    assert "Ran 5 tests" in tests and "\nOK\n" in tests
    assert "no issues found" in (SCRATCH / "lint.log").read_text(encoding="utf-8")
    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as image:
            assert image.size == (1280, 720) and image.mode == "RGB"
        assert path.stat().st_size < 410000
        renders.append({"file": path.name, "size": [1280, 720], "bytes": path.stat().st_size})
    with Image.open(texture) as image:
        counts = {color: count for count, color in image.getcolors(image.width * image.height)}
        total = image.width * image.height
    report.update({
        "engine": engine, "normalization": normalized,
        "artwork_tests_passed": 5, "gdstyle_zero_warnings": True,
        "final_import_no_errors": True, "runtime_load_no_errors": True,
        "texture": {"size": [512, 512], "channels": "RGB8 sRGB", "bytes": texture.stat().st_size,
                    "texels_per_metre": 64, "pale_fraction": counts[(197, 203, 202)] / total,
                    "cyan_fraction": counts[(87, 217, 229)] / total},
        "renders": renders,
        "editor_shutdown_limitation": "Exit 0 and assertions pass; scan-abort and RID/ObjectDB leaks",
        "limitations": ["No saved world placement, actor/car traversal, network or device acceptance",
                        "Isolated Blender visual evidence is not a Godot renderer/camera-motion test"],
        "dependency_sha256": {path: digest(ROOT / path) for path in DEPENDENCIES},
    })
    (EVIDENCE / "validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")


def main():
    """Write explicitly after the final handoff edit; otherwise verify every retained payload."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        collect()
    report = json.loads((EVIDENCE / "validation.json").read_text())
    dependencies = []
    for relative, expected in sorted(report["dependency_sha256"].items()):
        path = ROOT / relative
        assert digest(path) == expected, relative
        dependencies.append({"path": relative, "sha256": expected, "bytes": path.stat().st_size})
    manifest = {"asset_id": "d04_forecourt_graphics.03", "algorithm": "SHA-256",
                "exclusions": ["manifest.json self-hash", "uncommitted Python cache and external scratch"],
                "files": inventory_tool.inventory(), "unchanged_dependencies": dependencies}
    if args.write:
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    else:
        assert json.loads(MANIFEST.read_text()) == manifest, "Stale/missing/extra payload"
    print(f"EMBLEM_MANIFEST_PASS: {len(manifest['files'])} payload files; dependencies unchanged")


if __name__ == "__main__":
    main()
