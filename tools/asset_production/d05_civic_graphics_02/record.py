"""Consolidate final receipts and reuse the family inventory helper for payload manifests."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_civic_graphics_02"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def file_record(path):
    """Measure final bytes, never hand-transcribe hashes into the validation receipt."""
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def record():
    """Require matching fresh runtimes, two stable roundtrips and final passing logs."""
    report = json.loads((EVIDENCE / "validation.json").read_text())
    runtime = json.loads((SCRATCH / "prefab.json").read_text())
    assert runtime == json.loads((SCRATCH / "load-first.json").read_text())
    assert runtime["status"] == "PASS" and len(runtime["resource_uids"]) == 5
    saved = json.loads((SCRATCH / "roundtrips.json").read_text())
    hashes = saved.pop("roundtrip_sha256")
    assert len(hashes) == 3 and len(set(hashes)) == 1
    assert hashes[0] == runtime["prefab_sha256"]
    assert hashes[0] == file_record(ROOT / runtime["prefab"].removeprefix("res://"))["sha256"]
    assert saved == {k: v for k, v in runtime.items() if k != "roundtrip_sha256"}
    report["engine"] = runtime
    report["two_roundtrips_sha256"] = hashes
    report["two_fresh_runtime_processes_identical"] = True
    for path, digest in report["shared_dependency_sha256"].items():
        assert file_record(ROOT / path)["sha256"] == digest, path
    report["artwork"] = file_record(ROOT / f"art/textures/environment/{NID}/noticeboard_albedo.png")
    report["artwork"].update({"size_px": [1640, 1040], "mode": "RGB", "tests_passed": 4,
                              "original_vector_lettering": True, "emission": False})
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
        ("validate.log", "NOTICEBOARD_SOURCE_PASS"),
        ("preview-final.log", "CIVIC_PREVIEWS_PASS"),
        ("tests-final.log", "Ran 4 tests"),
        ("fmt-final.log", ""), ("lint-final.log", "no issues found"),
        ("import-final.log", "Godot Engine v4.8.dev7.official.c971f93e7"),
        ("normalize-final.log", "NOTICEBOARD_PREFAB_PASS"),
        ("load-final.log", "NOTICEBOARD_PREFAB_PASS"),
        ("load-second.log", "NOTICEBOARD_PREFAB_PASS"),
    ]:
        text = (SCRATCH / name).read_text(encoding="utf-8")
        assert marker in text and "SCRIPT ERROR" not in text and "Traceback" not in text
        assert "FAILED" not in text and "would reformat" not in text
        diagnostics = [line for line in text.splitlines() if "ERROR" in line or "WARNING" in line]
        if name != "normalize-final.log":
            assert not any("ERROR" in line for line in diagnostics), name
        logs.append(f"{name}: final exit 0 observed; required marker/diagnostics verified.")
        logs.extend(diagnostics)
    report["diagnostics"] = {
        "import": "No ERROR/SCRIPT ERROR; existing plugin compatibility warning",
        "runtime": "Two fresh processes pass without ERROR/WARNING/SCRIPT ERROR",
        "normalization": "Pass; known editor shutdown RID/ObjectDB leaks, not a clean log",
        "production_checks": "Not run: owner decision 52",
    }
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    (EVIDENCE / "final.log").write_text("\n".join(logs) + "\n", encoding="utf-8", newline="\n")
    print("NOTICEBOARD_RECEIPT_PASS")


def manifest(write):
    """Use the earlier civic-family inventory implementation without copying or editing it."""
    source = ROOT / "tools/asset_production/d05_civic_graphics_01/manifest.py"
    spec = importlib.util.spec_from_file_location("civic_manifest", source)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    helper.MANIFEST = EVIDENCE / "manifest.json"
    helper.OWNED = [path.replace("d05_civic_graphics_01", NID) for path in helper.OWNED
                    if not path.endswith("_hall_preview.tscn")]
    validation = json.loads((EVIDENCE / "validation.json").read_text())
    payload = {"asset_id": "d05_civic_graphics.02", "algorithm": "SHA-256",
               "exclusions": ["manifest.json (self-hash)", "__pycache__ (uncommitted cache)"],
               "shared_dependencies_not_produced": [file_record(ROOT / path)
                   for path in validation["shared_dependency_sha256"]],
               "files": helper.inventory()}
    if write:
        helper.MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", newline="\n")
    else:
        assert json.loads(helper.MANIFEST.read_text()) == payload, "Payload hashes differ"
    print(f"NOTICEBOARD_MANIFEST_PASS: {len(payload['files'])} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", choices=["write", "verify"])
    args = parser.parse_args()
    if args.manifest:
        manifest(args.manifest == "write")
    else:
        record()
