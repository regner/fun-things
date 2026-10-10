"""Run the reused carrier's source/binary audit without writing any carrier-owned path."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "city_parking_furniture_04"
HARDWARE = "city_traffic_fixtures_03"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence/validation.json"


def main():
    """Redirect only receipts and fresh exports, preserving all shared dependency bytes."""
    paths = [ROOT / f"art/source/models/environment/{HARDWARE}/{HARDWARE}.blend",
             ROOT / f"art/models/environment/{HARDWARE}/{HARDWARE}.glb",
             ROOT / f"art/models/environment/{HARDWARE}/{HARDWARE}.glb.import",
             ROOT / f"scenes/prefabs/environment/{HARDWARE}.tscn"]
    before = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in paths}
    script = ROOT / f"tools/asset_production/{HARDWARE}/validate.py"
    spec = importlib.util.spec_from_file_location("road_support_validation", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    module.SCRATCH = SCRATCH / "reexport"
    module.EVIDENCE = SCRATCH / "shared_source_validation.json"
    module.main()
    assert before == {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in paths}, "Shared hardware was changed"
    report = json.loads(module.EVIDENCE.read_text())
    report.update({"asset": "city_parking_furniture.04", "new_geometry": False,
                   "reused_hardware": HARDWARE, "shared_dependency_sha256": before,
                   "shared_dependencies_unchanged": True})
    # Keep separate engine/check receipts when refreshing the source audit.
    if EVIDENCE.exists():
        previous = json.loads(EVIDENCE.read_text())
        for key in ("godot", "production_checks", "artwork", "renders"):
            if key in previous:
                report[key] = previous[key]
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("BUS_STOP_SOURCE_PASS: existing source topology, UV landmarks and byte-identical export")


if __name__ == "__main__":
    main()
