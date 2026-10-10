"""Reuse the accepted fascia source audit and independent binary decoder, scratch-only."""
import importlib.util
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_corporate_graphics_03"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
HARDWARE = "city_shop_fittings_02"


def main():
    """Preserve all existing source/UV/topology assertions and protect reused dependencies."""
    tool = ROOT / "tools/asset_production/d06_commercial_graphics_01/validate.py"
    spec = importlib.util.spec_from_file_location("fascia_audit", tool)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    audit.NID, audit.SCRATCH, audit.EVIDENCE = NID, SCRATCH, EVIDENCE
    dependencies = [
        f"art/source/models/environment/{HARDWARE}/{HARDWARE}.blend",
        f"art/models/environment/{HARDWARE}/{HARDWARE}.glb",
        f"art/models/environment/{HARDWARE}/{HARDWARE}.glb.import",
        f"scenes/prefabs/environment/{HARDWARE}.tscn",
        f"tools/asset_production/{HARDWARE}/export.py",
        f"tools/asset_production/{HARDWARE}/check_glb.py",
        "tools/assets/blender/export_settings.json",
        "tools/asset_production/d06_commercial_graphics_01/validate.py",
        "tools/asset_production/d06_commercial_graphics_01/manifest.py",
        "tools/asset_production/d06_commercial_graphics_01/author.py",
        "tools/asset_production/d06_commercial_graphics_02/author.py",
        "tools/asset_production/d04_corporate_graphics_01/artwork.py",
        "tools/asset_production/d08_repair_graphics_01/check_prefab.gd",
        "tools/asset_production/d06_commercial_graphics_04/check_prefab.gd",
        "tools/asset_production/d06_commercial_graphics_03/check_prefab.gd",
    ]
    before = {path: audit.sha256(ROOT / path) for path in dependencies}
    audit.main()
    # The independent decoder expects this scratch filename; no shared output is overwritten.
    (SCRATCH / f"reexport_{HARDWARE}.glb").write_bytes(
        (SCRATCH / "shared_fascia_reexport.glb").read_bytes())
    decoder = ROOT / f"tools/asset_production/{HARDWARE}/check_glb.py"
    argv = sys.argv
    try:
        sys.argv = [str(decoder), str(SCRATCH)]
        runpy.run_path(str(decoder), run_name="__main__")
    finally:
        sys.argv = argv
    assert before == {path: audit.sha256(ROOT / path) for path in dependencies}
    report = json.loads((EVIDENCE / "validation.json").read_text())
    binary = json.loads((SCRATCH / "glb_checks.json").read_text())
    report.update({
        "asset_id": "d04_corporate_graphics.03", "status": "PASS",
        "shared_dependency_sha256": before, "glb_sha256": binary["sha256"],
        "glb_bytes": binary["bytes"], "independent_binary_audit": binary,
        "artwork_variants": ["entry_wordmark"], "texture_size": [2000, 400],
        "texture_channels": "RGB sRGB albedo",
    })
    (EVIDENCE / "validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("WORDMARK_SOURCE_PASS: unchanged fascia; source/binary audit; byte-identical export")


if __name__ == "__main__":
    main()
