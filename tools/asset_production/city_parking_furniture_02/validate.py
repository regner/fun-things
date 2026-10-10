"""Run the carrier owner's full audit with output-only redirection; leave hardware unchanged."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "city_parking_furniture_02"
HARDWARE = "city_sign_supports_02"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"


def identity(path):
    """Identify dependency bytes before and after the read-only reuse check."""
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def main():
    """Reuse every topology, UV, winding, bounds and fresh-export assertion without copying it."""
    paths = [f"art/source/models/environment/{HARDWARE}/{HARDWARE}.blend",
             f"art/models/environment/{HARDWARE}/{HARDWARE}.glb",
             f"art/models/environment/{HARDWARE}/{HARDWARE}.glb.import",
             f"scenes/prefabs/environment/{HARDWARE}.tscn",
             f"tools/asset_production/{HARDWARE}/validate.py",
             f"tools/asset_production/{HARDWARE}/export.py",
             f"tools/asset_production/{HARDWARE}/check_prefab.gd",
             "tools/assets/blender/export_settings.json",
             "tools/asset_production/d07_retail_graphics_03/author.py",
             "tools/asset_production/d07_retail_graphics_01/author.py",
             "tools/asset_production/d06_commercial_graphics_03/check_prefab.gd"]
    before = {p: identity(ROOT / p) for p in paths}
    validator = ROOT / f"tools/asset_production/{HARDWARE}/validate.py"
    code = validator.read_text()
    # The existing top-level validator has no output arguments. Redirect only its two
    # output constants, preserving __file__, all measurements and every assertion.
    for assignment, replacement in [
        ('EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"',
         f'EVIDENCE = Path({str(SCRATCH)!r})'),
        ('SCRATCH = Path("C:/tmp/ft/assets") / NID / "reexport"',
         f'SCRATCH = Path({str(SCRATCH / "reexport")!r})'),
    ]:
        assert code.count(assignment) == 1, "Shared validator output contract changed"
        code = code.replace(assignment, replacement)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    exec(compile(code, str(validator), "exec"), {"__file__": str(validator), "__name__": "audit"})
    assert before == {p: identity(ROOT / p) for p in paths}
    report = json.loads((SCRATCH / "validation.json").read_text())
    report.update({"asset_id": "city_parking_furniture.02", "new_geometry": False,
                   "output_type": "Assembly reference with approved derived 48:13 artwork",
                   "unchanged_dependencies": before,
                   "shared_source": paths[0], "shared_glb": paths[1]})
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("PARKING_ASSEMBLY_SOURCE_PASS: shared audit and byte-identical fresh reexport")


if __name__ == "__main__":
    main()
