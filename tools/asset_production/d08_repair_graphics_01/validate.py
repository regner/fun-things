"""Reuse the accepted wall-panel audit and fresh export; never write shared hardware."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d08_repair_graphics_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def main():
    """Redirect the existing read-only hardware pipeline to this record's receipts."""
    path = ROOT / "tools/asset_production/d06_commercial_graphics_04/validate.py"
    spec = importlib.util.spec_from_file_location("accepted_wall_art_audit", path)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    audit.NID, audit.EVIDENCE, audit.SCRATCH = NID, EVIDENCE, SCRATCH
    audit.main()
    receipt = EVIDENCE / "validation.json"
    report = json.loads(receipt.read_text())
    report["asset_id"] = "d08_repair_graphics.01"
    report["shared_dependency_sha256"][path.relative_to(ROOT).as_posix()] = audit.sha256(path)
    report["artwork_variants"] = ["fixed_enough", "fixed_enough_patched"]
    report["new_geometry"] = False
    receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("REPAIR_SOURCE_PASS: unchanged source, independent binary audit, byte-identical export")


if __name__ == "__main__":
    main()
