"""Combine final low-directory receipts; reuse the existing exact-payload inventory tool."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image, ImageColor

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_corporate_graphics_02"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
MANIFEST = EVIDENCE / "manifest.json"
spec = importlib.util.spec_from_file_location(
    "payload_inventory", ROOT / "tools/asset_production/d06_commercial_graphics_01/manifest.py")
inventory_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory_tool)
inventory_tool.MANIFEST = MANIFEST
inventory_tool.OWNED = [path.replace("d06_commercial_graphics_01", NID)
                        for path in inventory_tool.OWNED]


def digest(path):
    """Compute a file's exact final SHA-256 without trusting an older producer claim."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect():
    """Check final artifacts and logs before combining measured source and engine evidence."""
    report = json.loads((EVIDENCE / "validation.json").read_text())
    engine = json.loads((SCRATCH / "prefab.json").read_text())
    normalization = json.loads((SCRATCH / "normalization.json").read_text())
    assert report["status"] == engine["status"] == normalization["status"] == "PASS"
    assert normalization["byte_stable_scene_material_roundtrips"] == 2
    for key in ("prefab_uid", "material_uid", "model_uid", "prefab_sha256", "material_sha256"):
        assert engine[key] == normalization[key]
    prefab = ROOT / f"scenes/prefabs/environment/{NID}.tscn"
    material = ROOT / f"art/materials/environment/{NID}/directory.tres"
    assert digest(prefab) == engine["prefab_sha256"]
    assert digest(material) == engine["material_sha256"]
    for relative, expected in report["shared_dependency_sha256"].items():
        assert digest(ROOT / relative) == expected, relative
    glb = ROOT / "art/models/environment/city_sign_supports_02/city_sign_supports_02.glb"
    assert digest(glb) == report["glb_sha256"]
    assert glb.read_bytes() == (SCRATCH / "reexport" / glb.name).read_bytes()
    for name in ("import-final.log", "prefab.log"):
        text = (SCRATCH / name).read_text(encoding="utf-8")
        assert "ERROR:" not in text and "SCRIPT ERROR" not in text, name
        assert "4.8.dev7.official.c971f93e7" in text, name
    normalization_log = (SCRATCH / "normalize.log").read_text(encoding="utf-8")
    assert "SCRIPT ERROR" not in normalization_log
    assert "DIRECTORY_PREFAB_PASS" in normalization_log
    tests = (SCRATCH / "artwork-tests.log").read_text(encoding="utf-8")
    assert "Ran 4 tests" in tests and "\nOK\n" in tests
    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as image:
            assert image.size == (1280, 720)
        assert path.stat().st_size < 410000
        renders.append({"file": path.name, "dimensions_px": [1280, 720],
                        "bytes": path.stat().st_size})
    texture = ROOT / f"art/textures/environment/{NID}/directory_albedo.png"
    with Image.open(texture) as image:
        counts = {color: count for count, color in image.getcolors(image.width * image.height)}
        total = image.width * image.height
    report.update({
        "engine": engine, "normalization": normalization, "artwork_tests_passed": 4,
        "final_import_no_errors": True, "runtime_load_no_errors": True,
        "render_evidence": renders,
        "texture": {"path": texture.relative_to(ROOT).as_posix(),
                    "bytes": texture.stat().st_size, "sha256": digest(texture),
                    "field_fraction": counts[ImageColor.getrgb("#15263D")] / total,
                    "magenta_fraction": counts[ImageColor.getrgb("#EB62B7")] / total},
        "editor_shutdown_limitation": "Assertions passed; scan-abort and RID/ObjectDB leaks at exit",
        "validation_policy": "Owner decision 52: asset-scoped checks, not global production suite",
    })
    (EVIDENCE / "validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")


def main():
    """Write only on --write; otherwise verify the complete retained payload and dependencies."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        collect()
    validation = json.loads((EVIDENCE / "validation.json").read_text())
    dependencies = []
    for relative, expected in sorted(validation["shared_dependency_sha256"].items()):
        path = ROOT / relative
        assert digest(path) == expected, relative
        dependencies.append({"path": relative, "sha256": expected, "bytes": path.stat().st_size})
    manifest = {
        "asset_id": "d04_corporate_graphics.02", "algorithm": "SHA-256",
        "exclusions": ["manifest.json self-hash", "uncommitted Python cache and external scratch"],
        "files": inventory_tool.inventory(), "unchanged_dependencies": dependencies,
    }
    if args.write:
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    else:
        assert json.loads(MANIFEST.read_text()) == manifest, "Stale/missing/extra payload"
    print(f"DIRECTORY_MANIFEST_PASS: {len(manifest['files'])} payload files; dependencies unchanged")


if __name__ == "__main__":
    main()
