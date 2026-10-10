"""Audit the reused wall panel through its existing exporter and independent GLB decoder."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d08_repair_graphics_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def sha256(path):
    """Protect reused project source, scripts and prefab dependencies from accidental writes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Redirect only receipt/export destinations; never save the shared Blender source."""
    path = ROOT / "tools/asset_production/d06_commercial_graphics_04/validate.py"
    dependencies = [path] + [ROOT / relative for relative in (
        "tools/asset_production/d08_repair_graphics_01/author.py",
        "tools/asset_production/d08_repair_graphics_01/check_prefab.gd",
        "tools/asset_production/d06_commercial_graphics_04/check_prefab.gd",
        "tools/assets/blender/export_settings.json",
    )]
    before = {p.relative_to(ROOT).as_posix(): sha256(p) for p in dependencies}
    spec = importlib.util.spec_from_file_location("accepted_wall_art_audit", path)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    audit.NID, audit.EVIDENCE, audit.SCRATCH = NID, EVIDENCE, SCRATCH
    audit.main()
    assert before == {p.relative_to(ROOT).as_posix(): sha256(p) for p in dependencies}
    receipt = EVIDENCE / "validation.json"
    report = json.loads(receipt.read_text())
    report["asset_id"] = "d08_repair_graphics.03"
    report["shared_dependency_sha256"].update(before)
    report["artwork_variants"] = ["service_warning", "service_warning_patched"]
    report["new_geometry"] = False
    receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("WARNING_SOURCE_PASS: source, independent binary audit, byte-identical fresh export")


if __name__ == "__main__":
    main()
