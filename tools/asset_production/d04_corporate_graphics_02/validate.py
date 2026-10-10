"""Execute the existing low-panel source/binary audit with scratch-only writes."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_corporate_graphics_02"
HARDWARE = "city_sign_supports_02"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def sha256(path):
    """Protect the shared source/export, tooling and inherited prefab from mutation."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Redirect only legacy output assignments, preserving every existing audit assertion."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    dependencies = [
        f"art/source/models/environment/{HARDWARE}/{HARDWARE}.blend",
        f"art/models/environment/{HARDWARE}/{HARDWARE}.glb",
        f"art/models/environment/{HARDWARE}/{HARDWARE}.glb.import",
        f"scenes/prefabs/environment/{HARDWARE}.tscn",
        f"tools/asset_production/{HARDWARE}/validate.py",
        f"tools/asset_production/{HARDWARE}/export.py",
        "tools/assets/blender/export_settings.json",
        "tools/asset_production/d04_corporate_graphics_01/artwork.py",
        "tools/asset_production/d06_commercial_graphics_02/author.py",
        "tools/asset_production/d06_commercial_graphics_01/author.py",
        "tools/asset_production/d06_commercial_graphics_01/manifest.py",
        "tools/asset_production/d08_repair_graphics_02/check_prefab.gd",
        "tools/asset_production/d08_repair_graphics_01/check_prefab.gd",
        "tools/asset_production/d06_commercial_graphics_04/check_prefab.gd",
        "tools/asset_production/d06_commercial_graphics_03/check_prefab.gd",
    ]
    before = {path: sha256(ROOT / path) for path in dependencies}
    validator = ROOT / f"tools/asset_production/{HARDWARE}/validate.py"
    code = validator.read_text()
    redirects = {
        'EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"':
            f"EVIDENCE = Path({str(SCRATCH)!r})",
        'SCRATCH = Path("C:/tmp/ft/assets") / NID / "reexport"':
            f"SCRATCH = Path({str(SCRATCH / 'reexport')!r})",
    }
    for original, replacement in redirects.items():
        assert code.count(original) == 1
        code = code.replace(original, replacement)
    exec(compile(code, str(validator), "exec"),
         {"__file__": str(validator), "__name__": "hardware_audit"})
    assert before == {path: sha256(ROOT / path) for path in dependencies}
    report = json.loads((SCRATCH / "validation.json").read_text())
    report.update({
        "asset_id": "d04_corporate_graphics.02", "new_geometry": False,
        "output_type": "Artwork set on unchanged low freestanding panel",
        "shared_dependency_sha256": before, "shared_dependencies_unchanged": True,
        "artwork_variants": ["directory"],
        "texture_size": [1440, 390], "texture_channels": "RGB sRGB albedo",
    })
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("DIRECTORY_SOURCE_PASS: unchanged hardware; source/binary audit; byte-identical export")


if __name__ == "__main__":
    main()
