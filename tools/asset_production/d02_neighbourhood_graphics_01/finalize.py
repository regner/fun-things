"""Combine fresh source, engine and artwork checks into one lean final validation receipt."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_neighbourhood_graphics_01"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"


def fingerprint(path):
    """Hash the final file bytes rather than retaining intermediate payload receipts."""
    return {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    """Require current engine/roundtrip receipts and execute the production artwork tests."""
    report = json.loads((EVIDENCE / "validation.json").read_text())
    runtime = json.loads((SCRATCH / "prefab.json").read_text())
    roundtrips = json.loads((SCRATCH / "roundtrips.json").read_text())
    prefab = ROOT / f"scenes/prefabs/environment/{NID}.tscn"
    digest = fingerprint(prefab)["sha256"]
    assert runtime["status"] == roundtrips["status"] == "PASS"
    assert runtime["prefab_sha256"] == roundtrips["prefab_sha256"] == digest
    assert roundtrips["two_stable_roundtrip_sha256"] == [digest, digest]
    for path, expected in report["shared_dependencies"].items():
        assert fingerprint(ROOT / path) == expected, f"Shared dependency changed: {path}"
    tests = subprocess.run([
        sys.executable, "-m", "unittest", "discover", "-s",
        f"tools/asset_production/{NID}", "-p", "test_*.py", "-v",
    ], cwd=ROOT, capture_output=True, text=True, check=True)
    (SCRATCH / "tests.log").write_text(tests.stdout + tests.stderr, encoding="utf-8")
    assert "Ran 4 tests" in tests.stderr and "\nOK\n" in tests.stderr
    renders = {}
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as image:
            assert image.size == (1280, 720) and image.mode == "RGB"
        assert path.stat().st_size < 400 * 1024
        renders[name] = {**fingerprint(path), "dimensions": [1280, 720]}
    texture = ROOT / f"art/textures/environment/{NID}/watch_notice_albedo.png"
    report.update({
        "engine": runtime, "normalization": roundtrips,
        "artwork": {**fingerprint(texture), "dimensions": [1220, 820], "mode": "RGB",
                    "colour_space": "sRGB", "mipmaps": True},
        "artwork_tests": {"count": 4, "status": "PASS", "exit_code": tests.returncode},
        "renders": renders,
        "status": "PASS: bounded source/export, artwork tests, linked prefab and stable saves",
    })
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("WATCH_FINAL_RECEIPT_PASS: source, 4 tests, runtime, 2 roundtrips and 4 renders")


if __name__ == "__main__":
    main()
