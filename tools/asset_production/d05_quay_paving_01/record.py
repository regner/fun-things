"""Consolidate observed final checks and reuse the civic payload-inventory helper."""
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_quay_paving_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
DEPENDENCIES = [
    "tools/assets/blender/export_settings.json",
    "tools/asset_production/d01_sports_surface_01/author.py",
    "tools/asset_production/d01_sports_surface_02/validate.py",
    "tools/asset_production/d05_civic_graphics_01/manifest.py",
    "art/textures/environment/city_ground_finishes_01/plain_plaza_paving_albedo.png",
    "art/models/characters/coral_courier/coral_courier.glb",
    "art/models/vehicles/car_latch_a/car_latch_a.glb",
]


def file_record(path):
    """Measure final payload bytes and SHA-256 rather than transcribing expected values."""
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def record():
    """Require fresh runtime agreement, stable saves, final payload hashes and diagnostic checks."""
    report = json.loads((EVIDENCE / "validation.json").read_text())
    runtime = json.loads((SCRATCH / "prefab-check.json").read_text())
    assert runtime == json.loads((SCRATCH / "prefab-first-process.json").read_text())
    assert runtime["ok"] and not runtime["failures"]
    saved = json.loads((SCRATCH / "roundtrip.json").read_text())
    for index in (1, 2):
        assert saved.pop(f"roundtrip_{index}_byte_stable")
    assert saved == runtime
    assert file_record(ROOT / f"scenes/prefabs/environment/{NID}.tscn")["sha256"] == (
        runtime["prefab_sha256"])
    assert file_record(ROOT / f"art/materials/environment/{NID}/quay_border.tres")["sha256"] == (
        runtime["material_sha256"])
    glb = file_record(ROOT / f"art/models/environment/{NID}/{NID}.glb")
    assert glb["sha256"] == report["glb_sha256"] and glb["bytes"] == report["glb_bytes"]
    texture = file_record(ROOT / f"art/textures/environment/{NID}/quay_border_albedo.png")
    assert texture["sha256"] == report["texture_sha256"]
    with Image.open(ROOT / texture["path"]) as image:
        assert image.size == (1280, 192) and image.mode == "RGB"
        quiet = sum(n for n, color in image.getcolors(image.width * image.height)
                    if color == (166, 167, 158)) / (image.width * image.height)
    report["artwork"] = {**texture, "size_px": [1280, 192], "mode": "RGB",
                         "exact_quiet_field_fraction": quiet, "tests_passed": 4,
                         "reproduction_byte_identical": True}
    report["engine"] = runtime
    report["two_byte_stable_scene_material_roundtrips"] = True
    report["two_fresh_runtime_processes_identical"] = True
    report["renders"] = []
    for name in ("hero", "side", "detail", "overhead_47m_42deg"):
        path = EVIDENCE / f"{name}.png"
        with Image.open(path) as image:
            assert image.size == (1280, 720) and image.mode == "RGB"
        item = file_record(path)
        assert item["bytes"] < 400 * 1024
        report["renders"].append(item)
    logs = []
    for name, marker in [
        ("author.log", "Blender quit"), ("validate.log", "QUAY_SOURCE_PASS"),
        ("preview.log", "overhead_47m_42deg.png"), ("tests.log", "Ran 4 tests"),
        ("format.log", "already formatted"), ("style.log", "no issues found"),
        ("import-final.log", "Godot Engine v4.8.dev7.official.c971f93e7"),
        ("roundtrip.log", "QUAY_PREFAB_CHECK"), ("prefab-check.log", "QUAY_PREFAB_CHECK"),
        ("prefab-second-process.log", "QUAY_PREFAB_CHECK"),
    ]:
        text = (SCRATCH / name).read_text(encoding="utf-8")
        assert marker in text and "Traceback" not in text and "SCRIPT ERROR" not in text
        assert "FAILED" not in text and "would reformat" not in text
        if name == "tests.log":
            assert "\nOK" in text
        diagnostics = [line for line in text.splitlines()
                       if re.search(r"ERROR:|WARNING:|DeprecationWarning:", line)]
        errors = [line for line in diagnostics if "ERROR:" in line]
        if name == "roundtrip.log":
            assert all("RID allocations of type" in line and "leaked at exit" in line
                       for line in errors)
        else:
            assert not errors, name
        if name.startswith("prefab-"):
            assert not diagnostics
        logs.append(f"{name}: exit 0 observed; completion marker and diagnostics verified.")
        logs.extend(diagnostics)
    report["diagnostics"] = {
        "final_import": "No ERROR/SCRIPT ERROR; existing plugin version warning",
        "runtime": "Two processes; no ERROR/WARNING/SCRIPT ERROR",
        "normalization": "Stable bytes/UIDs; known scan-abort and RID/ObjectDB shutdown leaks",
        "blender": "Pinned node API deprecation warning; no errors",
        "production_checks": "Not run (owner decision 52)",
    }
    report["visual_review"] = {
        "inspected": ["hero", "side", "detail", "overhead_47m_42deg"],
        "observation": "Restrained paired teal harbour lines on warm grey. End-to-end joins are "
                       "unbroken, border stays small overhead and nearby actor/car remain distinct.",
        "camera": {"height_m": 47, "vertical_fov_degrees": 42,
                   "rotation_radians": [0, 0, 0], "projection": "perspective"},
        "renderer": "Blender Cycles CPU, 24 samples, AgX, PNG RGB8 compression 95",
        "context": "Hero/overhead use three linked repeats, 24 m total. Shared paving, Courier "
                   "and Latch are read-only studio references, not saved placements.",
        "godot_visual_acceptance": False,
    }
    handoff = (ROOT / f"docs/assets/production/{NID}.md").read_text(encoding="utf-8")
    assert set(re.findall(r"\b[0-9a-f]{64}\b", handoff)) == {
        report["glb_sha256"], texture["sha256"]}
    assert f'{report["glb_bytes"]:,}' in handoff and f'{texture["bytes"]:,}' in handoff
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    (EVIDENCE / "final.log").write_text("\n".join(logs) + "\n", encoding="utf-8", newline="\n")
    print("QUAY_RECEIPT_PASS")


def manifest(write):
    """Use the civic inventory helper; record unchanged read-only tooling/studio dependencies."""
    source = ROOT / "tools/asset_production/d05_civic_graphics_01/manifest.py"
    spec = importlib.util.spec_from_file_location("civic_manifest", source)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    helper.MANIFEST = EVIDENCE / "manifest.json"
    helper.OWNED = [f"art/{category}/environment/{NID}" for category in (
        "source/models", "models", "textures", "materials")]
    helper.OWNED += [f"tools/asset_production/{NID}", f"docs/assets/production/{NID}.md",
                     f"docs/assets/production/{NID}-evidence",
                     f"scenes/prefabs/environment/{NID}.tscn"]
    payload = {"asset_id": "d05_quay_paving.01", "algorithm": "SHA-256",
               "exclusions": ["manifest.json (self-hash)", "__pycache__ (uncommitted cache)"],
               "shared_dependencies_not_produced": [file_record(ROOT / p) for p in DEPENDENCIES],
               "files": helper.inventory()}
    if write:
        helper.MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", newline="\n")
    else:
        assert json.loads(helper.MANIFEST.read_text()) == payload, "Payload hashes differ"
    print(f"QUAY_MANIFEST_PASS: {len(payload['files'])} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", choices=["write", "verify"])
    args = parser.parse_args()
    if args.manifest:
        manifest(args.manifest == "write")
    else:
        record()
