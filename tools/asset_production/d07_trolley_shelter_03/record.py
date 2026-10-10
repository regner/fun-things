"""Record passing suite results, compact review PNGs and hash the assembly's final payloads."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d07_trolley_shelter_03"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
SIBLING_DOC = "docs/assets/production/d07_trolley_shelter_02.md"
SIBLING_MANIFEST = "docs/assets/production/d07_trolley_shelter_02-evidence/manifest.json"


def entry(path):
    """Hash current bytes with a portable repository-relative identity."""
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    """Retain only completed checks and final evidence, never caches or scratch retries."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checks", type=Path, required=True)
    args = parser.parse_args()
    summary = json.loads((args.checks / "summary.json").read_text(encoding="utf-8"))
    assert summary["ok"], "Production suite must pass"
    path = EVIDENCE / "validation.json"
    validation = json.loads(path.read_text(encoding="utf-8"))
    assert validation["source_export_status"] == "passed"
    assert validation["godot"]["two_save_reload_roundtrips_byte_stable"]
    validation["production_checks"] = summary["results"]
    validation["evidence_renders"] = {}
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        image_path = EVIDENCE / f"{name}.png"
        with Image.open(image_path) as image:
            assert image.size == (1280, 720)
            image.convert("RGB").point(lambda value: (value >> 2) << 2).save(
                image_path, optimize=True, compress_level=9)
        validation["evidence_renders"][name] = {
            "size_px": [1280, 720], "bytes": image_path.stat().st_size,
            "source": "isolated Blender Cycles; six-significant-bit RGB review PNG",
        }
    path.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8", newline="\n")
    # Verify the approved handoff-only amendment; this recorder does not write sibling files.
    sibling_manifest = json.loads((ROOT / SIBLING_MANIFEST).read_text(encoding="utf-8"))
    assert next(item for item in sibling_manifest["files"] if item["path"] == SIBLING_DOC) == entry(
        ROOT / SIBLING_DOC), "Refresh the approved sibling doc hash before recording"
    paths = [ROOT / f"docs/assets/production/{ASSET}.md",
             ROOT / f"scenes/prefabs/environment/{ASSET}.tscn",
             ROOT / SIBLING_DOC, ROOT / SIBLING_MANIFEST]
    for directory in (ROOT / f"tools/asset_production/{ASSET}", EVIDENCE):
        paths.extend(p for p in directory.rglob("*") if p.is_file()
                     and "__pycache__" not in p.parts and p.name != "manifest.json")
    dependencies = [
        "tools/assets/blender/export_settings.json",
        "tools/asset_production/d07_trolley_shelter_01/author.py",
        "tools/asset_production/d07_trolley_shelter_01/validate.py",
        "tools/asset_production/d07_trolley_shelter_02/validate.py",
        "tools/asset_production/d07_trolley_shelter_02/export.py",
        "tools/asset_production/d07_trolley_shelter_02/check.gd",
        "art/source/models/environment/d07_trolley_shelter_02/d07_trolley_shelter_02.blend",
        "art/models/environment/d07_trolley_shelter_02/d07_trolley_shelter_02.glb",
        "art/models/environment/d07_trolley_shelter_02/d07_trolley_shelter_02.glb.import",
        "scenes/prefabs/environment/d07_trolley_shelter_02.tscn",
        "scenes/prefabs/environment/d07_trolley_shelter_01.tscn",
        "art/models/environment/d07_trolley_shelter_01/d07_trolley_shelter_01.glb",
        "art/models/environment/d07_trolley_shelter_01/d07_trolley_shelter_01.glb.import",
    ]
    manifest = {
        "asset": "d07_trolley_shelter.03", "producer": "commissioned implementation specialist",
        "scope": "Every delivered payload except this manifest, including two approved sibling handoff amendments",
        "files": [entry(p) for p in sorted(set(paths))],
        "read_only_dependencies": [entry(ROOT / p) for p in dependencies],
    }
    (EVIDENCE / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Recorded {len(manifest['files'])} payloads and {len(dependencies)} read-only dependencies")


if __name__ == "__main__":
    main()
