"""Run the support owner's topology/UV/export audit read-only, retaining owned evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d07_retail_graphics_02"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
DEPENDENCIES = [
    "art/source/models/environment/d07_sign_island_02/d07_sign_island_02.blend",
    "art/models/environment/d07_sign_island_02/d07_sign_island_02.glb",
    "art/models/environment/d07_sign_island_02/d07_sign_island_02.glb.import",
    "scenes/prefabs/environment/d07_sign_island_02.tscn",
    "tools/asset_production/d07_sign_island_02/validate.py",
    "tools/asset_production/d07_sign_island_02/export.py",
    "tools/assets/blender/export_settings.json",
    "tools/asset_production/d07_retail_graphics_01/author.py",
]


def dependencies():
    """Fingerprint unchanged carrier and family-recipe dependencies before and after use."""
    return {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in DEPENDENCIES}


def main():
    """Redirect only audit outputs, then execute the existing geometry owner's assertions."""
    before = dependencies()
    path = ROOT / "tools/asset_production/d07_sign_island_02/validate.py"
    spec = importlib.util.spec_from_file_location("sign_support_validator", path)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    audit.EVIDENCE = EVIDENCE / "validation.json"
    audit.SCRATCH = Path(f"C:/tmp/ft/assets/{NID}/reexport")
    audit.main()
    assert dependencies() == before, "Reused source/export/prefab must remain unchanged"
    report = json.loads(audit.EVIDENCE.read_text())
    report.update({
        "asset": "d07_retail_graphics.02",
        "output_type": "Artwork set; unchanged support prefab with one face override",
        "new_geometry": False,
        "shared_glb": DEPENDENCIES[1],
        "shared_glb_sha256": report["glb_sha256"],
        "shared_glb_bytes": report["glb_bytes"],
        "shared_dependency_sha256": before,
        "shared_dependencies_unchanged": True,
    })
    audit.EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("SIGN_FACE_SOURCE_PASS: existing topology, normals, UVs and fresh-export bytes")


if __name__ == "__main__":
    main()
