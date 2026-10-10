"""Reuse the noticeboard owner's source/GLB audit, redirecting only its output paths."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_civic_graphics_02"
HARDWARE = "city_sign_supports_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
OWNER = ROOT / f"tools/asset_production/{HARDWARE}/validate.py"


def main():
    """Keep all original topology/UV assertions intact and prove shared dependencies unchanged."""
    dependencies = [
        f"art/source/models/environment/{HARDWARE}/{HARDWARE}.blend",
        f"art/models/environment/{HARDWARE}/{HARDWARE}.glb",
        f"art/models/environment/{HARDWARE}/{HARDWARE}.glb.import",
        f"scenes/prefabs/environment/{HARDWARE}.tscn",
        f"tools/asset_production/{HARDWARE}/validate.py",
        f"tools/asset_production/{HARDWARE}/export.py",
        "tools/assets/blender/export_settings.json",
        "tools/asset_production/d05_civic_graphics_01/author.py",
        "tools/asset_production/d05_civic_graphics_01/manifest.py",
        "tools/asset_production/d06_commercial_graphics_03/check_prefab.gd",
    ]
    before = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in dependencies}
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    # This legacy validator is top-level, with no callable output-path API. Follow the
    # existing graphics audit convention: change only exact output assignments in memory.
    code = OWNER.read_text()
    for old, new in {
        'EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"':
            f'EVIDENCE = Path({str(SCRATCH)!r})',
        'SCRATCH = Path("C:/tmp/ft/assets") / NID / "reexport"':
            f'SCRATCH = Path({str(SCRATCH / "reexport")!r})',
    }.items():
        assert code.count(old) == 1, "Owner audit output contract changed"
        code = code.replace(old, new)
    exec(compile(code, str(OWNER), "exec"), {"__file__": str(OWNER), "__name__": "__main__"})
    assert before == {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in dependencies}
    report = json.loads((SCRATCH / "validation.json").read_text())
    report.update({
        "asset_id": "d05_civic_graphics.02", "new_geometry": False,
        "shared_dependencies_unchanged": True, "shared_dependency_sha256": before,
        "source_audit": "All owner assertions unchanged; only output paths redirected",
        "shared_source": dependencies[0], "shared_glb": dependencies[1],
        "status": "PASS: bounded producer audit; independent review pending",
    })
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("NOTICEBOARD_SOURCE_PASS: shared topology, upright UVs, exact saved-source reexport")


if __name__ == "__main__":
    main()
