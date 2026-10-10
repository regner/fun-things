"""Reuse the hall's exact fascia audit without changing any earlier asset or output."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_civic_graphics_04"


def main():
    """Redirect the existing reusable audit's output globals; keep all source checks intact."""
    spec = importlib.util.spec_from_file_location(
        "fascia_audit", ROOT / "tools/asset_production/d05_civic_graphics_01/validate.py")
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    audit.SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
    audit.EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
    audit.main()
    path = audit.EVIDENCE / "validation.json"
    report = json.loads(path.read_text())
    report["asset_id"] = "d05_civic_graphics.04"
    report["output_type"] = "Three artwork variants reusing unchanged fascia geometry"
    # Include the complete reused author/check chain in the current dependency receipt.
    paths = [
        "tools/assets/blender/export_settings.json",
        "art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb.import",
        "scenes/prefabs/environment/city_shop_fittings_02.tscn",
    ]
    for sibling, scripts in {
        "city_shop_fittings_02": ["export.py", "check_glb.py"],
        "d05_civic_graphics_01": ["author.py", "validate.py", "check_prefab.gd", "manifest.py"],
        "d05_civic_graphics_02": ["author.py"],
        "d05_civic_graphics_03": ["author.py"],
    }.items():
        paths.extend(f"tools/asset_production/{sibling}/{script}" for script in scripts)
    report["shared_dependency_sha256"].update({p: audit.sha256(ROOT / p) for p in paths})
    path.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("SHOPS_SOURCE_PASS")


if __name__ == "__main__":
    main()
