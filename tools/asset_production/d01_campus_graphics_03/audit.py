"""Collect route-set evidence and verify an exact final payload/dependency manifest."""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import platform

import PIL
from PIL import Image

import author

ROOT, NID = author.ROOT, author.NID
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
MANIFEST = EVIDENCE / "manifest.json"
SPEC = importlib.util.spec_from_file_location(
    "campus_inventory", ROOT / "tools/asset_production/d01_campus_graphics_02/audit.py")
shared = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(shared)
# Reuse the existing campus hash/inventory helper, but scope every write to this asset.
shared.OWNED += [f"scenes/prefabs/environment/{NID}_{v}.tscn" for v in ("left", "right")]
entry, inventory = shared.entry, shared.inventory


def collect():
    """Join final receipts only after all three real resource and PNG byte comparisons pass."""
    report = json.loads((EVIDENCE / "validation.json").read_text())
    normalized = json.loads((SCRATCH / "normalize.json").read_text())
    runtime = json.loads((SCRATCH / "prefab.json").read_text())
    assert normalized["status"] == runtime["status"] == "PASS"
    assert normalized["stable_roundtrips"] == 2
    assert [v["variant"] for v in runtime["variants"]] == list(author.VARIANTS)
    for saved, live in zip(normalized["variants"], runtime["variants"]):
        for key, path_key in (("roundtrip_sha256", "prefab"),
                              ("material_roundtrip_sha256", "material")):
            path = ROOT / saved[path_key].removeprefix("res://")
            assert saved[key] == [entry(path)["sha256"]]*3
        for key in ("variant", "prefab_uid", "material_uid"):
            assert saved[key] == live[key]
    for name in ("import-final", "runtime"):
        text = (SCRATCH / f"{name}.log").read_text(encoding="utf-8")
        assert "ERROR:" not in text and "SCRIPT ERROR:" not in text
        if name == "runtime":
            assert "WARNING:" not in text and "ROUTE_SET_PREFAB_PASS" in text
    textures = []
    for variant in author.VARIANTS:
        path = author.OUTPUT_DIR / f"route_{variant}_albedo.png"
        output = io.BytesIO()
        author.create_artwork(variant).save(output, format="PNG", compress_level=9)
        assert output.getvalue() == path.read_bytes()
        textures.append(entry(path))
    report["engine"] = {"normalization": normalized, "runtime": runtime,
                        "final_import_no_errors": True, "runtime_no_diagnostics": True,
                        "pin": "4.8.dev7.official.c971f93e7"}
    inputs = [author.FAMILY_SOURCE, author.family.FAMILY_SOURCE,
              author.family.family.LETTERS,
              ROOT / "tools/asset_production/d06_commercial_graphics_01/author.py"]
    report["artwork"].update({
        "textures": textures, "fresh_pngs_byte_identical": True,
        "python": platform.python_version(), "pillow": PIL.__version__,
        "source_inputs": [entry(p) for p in inputs],
    })
    report["shared_validation_tools"] = [entry(ROOT / p) for p in (
        "tools/asset_production/d01_campus_graphics_02/validate.py",
        "tools/asset_production/d01_campus_graphics_01/validate.py",
        "tools/asset_production/d01_campus_graphics_02/export.py",
        "tools/asset_production/city_sign_supports_02/export.py",
        "tools/assets/blender/export_settings.json",
        "tools/asset_production/d01_campus_graphics_02/check_prefab.gd",
        "tools/asset_production/d06_commercial_graphics_03/check_prefab.gd",
        "tools/asset_production/d01_campus_graphics_02/audit.py",
    )]
    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as image:
            assert image.size == (1280, 720) and image.mode == "RGB"
        assert path.stat().st_size < 400_000
        renders.append(entry(path))
    report["renders"] = renders
    (EVIDENCE / "validation.json").write_text(
        json.dumps(report, indent=2)+"\n", encoding="utf-8", newline="\n")
    print("ROUTE_SET_EVIDENCE_PASS: three textures, six stable resources, engine and renders")


def main():
    """Write the manifest last, or verify every payload and unchanged dependency exactly."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.collect:
        collect()
        return
    validation = json.loads((EVIDENCE / "validation.json").read_text())
    dependencies = (validation["dependencies"] + validation["artwork"]["source_inputs"]
                    + validation["shared_validation_tools"])
    assert dependencies == [entry(ROOT / item["path"]) for item in dependencies]
    report = {"asset_id": "d01_campus_graphics.03", "algorithm": "SHA-256",
              "exclusions": ["manifest.json (self-hash)", "__pycache__ (uncommitted)"],
              "unchanged_dependencies": dependencies, "files": inventory()}
    if args.write:
        MANIFEST.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8", newline="\n")
    else:
        assert json.loads(MANIFEST.read_text()) == report, "Payload inventory/hash mismatch"
    print(f"ROUTE_SET_MANIFEST_PASS: {len(report['files'])} payload files")


if __name__ == "__main__":
    main()
