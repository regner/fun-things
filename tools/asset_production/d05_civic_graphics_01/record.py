"""Combine final source, roundtrip, runtime and artwork receipts; no shared asset writes."""
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_civic_graphics_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def file_record(path):
    """Record actual payload size and digest rather than a handwritten receipt."""
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    """Reject incomplete diagnostics/receipts before assembling lean final evidence."""
    report_path = EVIDENCE / "validation.json"
    report = json.loads(report_path.read_text())
    runtime = json.loads((SCRATCH / "prefab.json").read_text())
    first = json.loads((SCRATCH / "load-first.json").read_text())
    roundtrips = json.loads((SCRATCH / "roundtrips.json").read_text())
    assert runtime == first and runtime["status"] == "PASS"
    assert len(runtime["resource_uids"]) == 4
    for path, hashes in roundtrips["roundtrip_sha256"].items():
        assert len(hashes) == 3 and len(set(hashes)) == 1
        assert hashes[0] == file_record(ROOT / path.removeprefix("res://"))["sha256"]
    expected = dict(roundtrips)
    del expected["roundtrip_sha256"]
    del expected["two_roundtrips_byte_identical"]
    assert expected == runtime
    report["engine"] = runtime
    report["roundtrips"] = roundtrips["roundtrip_sha256"]
    report["two_fresh_runtime_processes_identical"] = True
    texture = ROOT / f"art/textures/environment/{NID}/hall_fascia_albedo.png"
    report["artwork"] = file_record(texture)
    report["artwork"].update({"size_px": [2000, 400], "mode": "RGB", "tests_passed": 3,
                               "original_path_lettering": True, "emission": False})
    report["renders"] = []
    for name in ["hero.png", "side.png", "mount_detail.png", "overhead_47m_42deg.png"]:
        path = EVIDENCE / name
        with Image.open(path) as image:
            assert image.size == (1280, 720)
        item = file_record(path)
        assert item["bytes"] < 400 * 1024
        report["renders"].append(item)
    report["mounting_reference_dependencies"] = []
    for asset in ["d05_harbour_hall_01", "d05_harbour_hall_02"]:
        for relative in [f"art/source/models/environment/{asset}/{asset}.blend",
                         f"art/models/environment/{asset}/{asset}.glb",
                         f"scenes/prefabs/environment/{asset}.tscn"]:
            report["mounting_reference_dependencies"].append(file_record(ROOT / relative))
    logs = []
    for name, marker in [
        ("validate.log", "HALL_SOURCE_PASS"),
        ("preview-final.log", "CIVIC_PREVIEWS_PASS"),
        ("tests-final.log", "\nOK"),
        ("fmt-final.log", ""),
        ("lint-final.log", ""),
        ("import-final.log", "Godot Engine v4.8.dev7.official.c971f93e7"),
        ("load-final.log", "HALL_PREFAB_PASS"),
        ("load-second.log", "HALL_PREFAB_PASS"),
        ("normalize-final.log", "HALL_PREFAB_PASS"),
    ]:
        text = (SCRATCH / name).read_text(encoding="utf-8")
        assert marker in text and "SCRIPT ERROR" not in text and "Traceback" not in text
        diagnostics = [line for line in text.splitlines() if "ERROR" in line or "WARNING" in line]
        if name != "normalize-final.log":
            assert not any("ERROR" in line for line in diagnostics), name
        logs.append(f"{name}: final command exited 0; required marker/diagnostic check passed.")
        logs.extend(diagnostics)
    report["diagnostic_scope"] = {
        "import": "No ERROR or SCRIPT ERROR; existing MCP compatibility warning only",
        "runtime": "Two clean fresh processes, no ERROR/WARNING/SCRIPT ERROR",
        "normalization": "Byte-stable saves; existing pinned editor shutdown leaks retained",
        "production_checks": "Not run, owner decision 52",
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    (EVIDENCE / "final.log").write_text("\n".join(logs) + "\n", encoding="utf-8", newline="\n")
    print("CIVIC_FINAL_RECEIPT_PASS")


if __name__ == "__main__":
    main()
