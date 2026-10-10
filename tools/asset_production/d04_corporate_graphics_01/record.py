"""Collect final owned receipts and write/verify a complete, lean SHA-256 manifest."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_corporate_graphics_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
MANIFEST = EVIDENCE / "manifest.json"


def inventory():
    """Hash every payload except the manifest itself and uncommitted Python cache."""
    roots = [ROOT / f"art/{kind}/environment/{NID}" for kind in
             ("source/models", "models", "materials", "textures")]
    roots += [ROOT / f"tools/asset_production/{NID}", EVIDENCE,
              ROOT / f"docs/assets/production/{NID}.md",
              ROOT / f"scenes/prefabs/environment/{NID}.tscn"]
    files = []
    for path in roots:
        for item in sorted(path.rglob("*")) if path.is_dir() else [path]:
            if not item.is_file() or item == MANIFEST or "__pycache__" in item.parts:
                continue
            data = item.read_bytes()
            files.append({"path": item.relative_to(ROOT).as_posix(), "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()})
    return sorted(files, key=lambda item: item["path"])


def collect():
    """Combine independently generated final engine/source receipts without false passes."""
    path = EVIDENCE / "validation.json"
    report = json.loads(path.read_text())
    engine = json.loads((SCRATCH / "prefab.json").read_text())
    normalization = json.loads((SCRATCH / "normalization.json").read_text())
    assert engine["status"] == normalization["status"] == report["status"] == "PASS"
    assert normalization["stable_roundtrips"] == 2
    for key in ("prefab_uid", "model_uid", "material_uid"):
        assert engine[key] == normalization[key]
    glb = ROOT / f"art/models/environment/{NID}/{NID}.glb"
    assert hashlib.sha256(glb.read_bytes()).hexdigest() == report["glb"]["sha256"]
    assert glb.read_bytes() == (SCRATCH / f"reexport/{NID}.glb").read_bytes()
    for log in ("import-final.log", "prefab.log"):
        content = (SCRATCH / log).read_text(encoding="utf-8")
        assert "ERROR:" not in content and "SCRIPT ERROR" not in content, log
    assert "Ran 4 tests" in (SCRATCH / "artwork-tests.log").read_text()
    assert "\nOK\n" in (SCRATCH / "artwork-tests.log").read_text()
    renders = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        image_path = EVIDENCE / f"{name}.png"
        with Image.open(image_path) as image:
            assert image.size == (1280, 720)
        assert image_path.stat().st_size < 410000
        renders.append({"name": image_path.name, "size": [1280, 720],
                        "bytes": image_path.stat().st_size})
    report.update(engine=engine, normalization=normalization, artwork_tests_passed=4,
                  render_evidence=renders, final_import_no_errors=True,
                  engine_load_no_errors=True, new_gameplay_or_collision=False,
                  validation_policy="Owner decision 52: asset-scoped checks only")
    path.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8", newline="\n")


def main():
    """Use --write after the last import/doc change, otherwise verify without writing."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        collect()
    manifest = {"asset_id": "d04_corporate_graphics.01", "algorithm": "SHA-256",
                "exclusions": ["manifest.json self-hash", "uncommitted __pycache__ and scratch"],
                "files": inventory()}
    if args.write:
        MANIFEST.write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8", newline="\n")
    else:
        assert json.loads(MANIFEST.read_text()) == manifest, "Stale/missing/extra payload"
    print(f"CORPORATE_MANIFEST_PASS: {len(manifest['files'])} payload files")


if __name__ == "__main__":
    main()
