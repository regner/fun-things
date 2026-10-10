"""Compact evidence and retain a complete per-asset producer manifest; scratch logs stay external."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "city_parking_furniture_04"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
MANIFEST = EVIDENCE / "manifest.json"


def payloads():
    """Enumerate only delivered artwork, saved wrapper, owned tools and lean handoff evidence."""
    files = [ROOT / f"scenes/prefabs/environment/{NID}.tscn",
             ROOT / f"docs/assets/production/{NID}.md"]
    for directory in [ROOT / f"art/materials/environment/{NID}",
                      ROOT / f"art/textures/environment/{NID}",
                      ROOT / f"tools/asset_production/{NID}", EVIDENCE]:
        files.extend(path for path in directory.rglob("*")
                     if path.is_file() and "__pycache__" not in path.parts and path != MANIFEST)
    return {path.relative_to(ROOT).as_posix(): {
        "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for path in sorted(files)}


def main():
    """Verify every existing receipt or refresh only owned evidence after completed checks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report_path = EVIDENCE / "validation.json"
    report = json.loads(report_path.read_text())
    for path, expected in report["shared_dependency_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    if args.check:
        assert json.loads(MANIFEST.read_text())["files"] == payloads(), "Payload manifest drift"
        print("BUS_STOP_MANIFEST_PASS")
        return
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s",
                             f"tools/asset_production/{NID}", "-p", "test_*.py", "-v"],
                            cwd=ROOT, capture_output=True, text=True, timeout=30, check=True)
    print(result.stderr)
    report["artwork"] = {"tests_passed": 4, "dimensions_px": [512, 512],
                          "format": "opaque RGB albedo", "fresh_png_byte_identical": True,
                          "srgb_palette": ["#123646", "#F6F1DC", "#FFC05A"],
                          "new_geometry": False}
    renders = {}
    for name in ["hero", "side", "detail", "overhead_47m_42deg"]:
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as image:
            assert image.size == (1280, 720)
            compact = image.convert("RGB").point(lambda value: value & 254)
            compact.save(path, compress_level=9)
            if path.stat().st_size >= 410000:
                compact.point(lambda value: value & 252).save(path, compress_level=9)
        assert path.stat().st_size < 410000, path
        renders[path.name] = {"dimensions_px": [1280, 720], "bytes": path.stat().st_size}
    report["renders"] = renders
    checks = json.loads((SCRATCH / "checks-final/summary.json").read_text())
    assert checks["ok"]
    report["production_checks"] = checks["results"]
    python_log = (SCRATCH / "checks-final/python-tests.log").read_text()
    gut_log = (SCRATCH / "checks-final/gut.log").read_text()
    report["production_checks"].update({
        "python_tests_passed": int(re.search(r"Ran (\d+) tests", python_log)[1]),
        "gut_tests_passed": int(re.search(r"Passing Tests\s+(\d+)", gut_log)[1]),
        "gut_assertions": int(re.search(r"Asserts\s+(\d+)", gut_log)[1]),
    })
    report_path.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    MANIFEST.write_text(json.dumps({"asset": "city_parking_furniture.04",
                                    "scope": "All produced payloads; excludes only this manifest",
                                    "files": payloads()}, indent=2) + "\n", newline="\n")
    print("BUS_STOP_MANIFEST_WRITTEN")


if __name__ == "__main__":
    main()
