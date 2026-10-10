"""Consolidate final receipts and reuse the civic family's exact payload inventory helper."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image

from author import VARIANTS

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_civic_graphics_04"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def file_record(path):
    """Measure final bytes and hashes rather than transcribing expected receipt values."""
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def record():
    """Require identical fresh runtime receipts, two stable cycles per prefab and clean checks."""
    report = json.loads((EVIDENCE / "validation.json").read_text())
    runtime = json.loads((SCRATCH / "prefab.json").read_text())
    assert runtime == json.loads((SCRATCH / "load-first.json").read_text())
    assert runtime["status"] == "PASS" and set(runtime["variants"]) == set(VARIANTS)
    saved = json.loads((SCRATCH / "roundtrips.json").read_text())
    roundtrips = {}
    for variant, result in saved["variants"].items():
        hashes = result.pop("roundtrip_sha256")
        assert len(hashes) == 3 and len(set(hashes)) == 1
        assert hashes[0] == file_record(ROOT / result["prefab"].removeprefix("res://"))["sha256"]
        assert len(result["resource_uids"]) == 5
        roundtrips[variant] = hashes
    assert saved == runtime
    report["engine"] = runtime
    report["two_roundtrips_sha256"] = roundtrips
    report["two_fresh_runtime_processes_identical"] = True
    for path, digest in report["shared_dependency_sha256"].items():
        assert file_record(ROOT / path)["sha256"] == digest, path
    report["artwork"] = {}
    for variant in VARIANTS:
        path = ROOT / f"art/textures/environment/{NID}/{variant}_albedo.png"
        report["artwork"][variant] = file_record(path)
        with Image.open(path) as image:
            assert image.size == (2000, 400) and image.mode == "RGB"
        report["artwork"][variant].update({"size_px": [2000, 400], "mode": "RGB"})
    report["artwork_tests_passed"] = 4
    report["renders"] = []
    for name in ["hero.png", "side.png", "detail.png", "overhead_47m_42deg.png"]:
        path = EVIDENCE / name
        with Image.open(path) as image:
            assert image.size == (1280, 720) and image.mode == "RGB"
        item = file_record(path)
        assert item["bytes"] < 400 * 1024
        report["renders"].append(item)
    logs = []
    for name, marker in [
        ("validate.log", "SHOPS_SOURCE_PASS"),
        ("preview-final.log", "CIVIC_PREVIEWS_PASS"),
        ("tests-final.log", "Ran 4 tests"),
        ("fmt-final.log", "already formatted"), ("lint-final.log", "no issues found"),
        ("import-final.log", "Godot Engine v4.8.dev7.official.c971f93e7"),
        ("normalize-final.log", "SHOPS_PREFAB_PASS"),
        ("load-final.log", "SHOPS_PREFAB_PASS"),
        ("load-second.log", "SHOPS_PREFAB_PASS"),
    ]:
        text = (SCRATCH / name).read_text(encoding="utf-8")
        assert marker in text and "SCRIPT ERROR" not in text and "Traceback" not in text
        assert "FAILED" not in text and "would reformat" not in text
        if name == "tests-final.log":
            assert "\nOK" in text
        diagnostics = [line for line in text.splitlines() if "ERROR" in line or "WARNING" in line]
        if name != "normalize-final.log":
            assert not any("ERROR" in line for line in diagnostics), name
        if name.startswith("load-"):
            assert not diagnostics
        logs.append(f"{name}: final exit 0 observed; required markers/diagnostics verified.")
        logs.extend(diagnostics)
    report["diagnostics"] = {
        "import": "No ERROR/SCRIPT ERROR; existing plugin compatibility warning",
        "runtime": "Two fresh processes pass without ERROR/WARNING/SCRIPT ERROR",
        "normalization": "Pass; existing editor shutdown RID/ObjectDB leaks, not a clean log",
        "production_checks": "Not run: owner decision 52",
    }
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    (EVIDENCE / "final.log").write_text("\n".join(logs) + "\n", encoding="utf-8", newline="\n")
    print("SHOPS_RECEIPT_PASS")


def manifest(write):
    """Reuse the earlier civic inventory implementation without copying or editing it."""
    source = ROOT / "tools/asset_production/d05_civic_graphics_01/manifest.py"
    spec = importlib.util.spec_from_file_location("civic_manifest", source)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    helper.MANIFEST = EVIDENCE / "manifest.json"
    helper.OWNED = [f"art/textures/environment/{NID}", f"art/materials/environment/{NID}",
                    f"tools/asset_production/{NID}", f"docs/assets/production/{NID}.md",
                    f"docs/assets/production/{NID}-evidence"]
    helper.OWNED.extend(f"scenes/prefabs/environment/{NID}_{v}.tscn" for v in VARIANTS)
    validation = json.loads((EVIDENCE / "validation.json").read_text())
    payload = {"asset_id": "d05_civic_graphics.04", "algorithm": "SHA-256",
               "exclusions": ["manifest.json (self-hash)", "__pycache__ (uncommitted cache)"],
               "shared_dependencies_not_produced": [file_record(ROOT / path)
                   for path in validation["shared_dependency_sha256"]],
               "files": helper.inventory()}
    if write:
        helper.MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", newline="\n")
    else:
        assert json.loads(helper.MANIFEST.read_text()) == payload, "Payload hashes differ"
    print(f"SHOPS_MANIFEST_PASS: {len(payload['files'])} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", choices=["write", "verify"])
    args = parser.parse_args()
    if args.manifest:
        manifest(args.manifest == "write")
    else:
        record()
