"""Reuse the sibling's exact shared-carrier assertions without touching sibling evidence."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_campus_graphics_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SPEC = importlib.util.spec_from_file_location(
    "campus_low_validation", ROOT / "tools/asset_production/d01_campus_graphics_02/validate.py")
shared = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(shared)


def main():
    """Measure and byte-compare the unchanged carrier, writing only this route-set receipt."""
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    shared.EVIDENCE = EVIDENCE
    # The sibling resolves export.py beside __file__; redirect to our scratch-only delegate.
    shared.__file__ = __file__
    shared.main()
    path = EVIDENCE / "validation.json"
    report = json.loads(path.read_text())
    report["asset_id"] = "d01_campus_graphics.03"
    report["artwork"]["variants"] = ["left", "ahead", "right"]
    report["geometry_counts_scope"] = "per unchanged reused carrier; three alternative prefabs"
    path.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8", newline="\n")
    print("ROUTE_SET_SOURCE_PASS")


if __name__ == "__main__":
    main()
