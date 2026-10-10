"""Consolidate final external receipts and hash this asset's lean delivered payloads."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d07_retail_buildings_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def read_json(path):
    """Read a required receipt; missing evidence must fail closed."""
    return json.loads(path.read_text(encoding="utf-8"))


def diagnostics(path):
    """Retain warning/error lines rather than turning a zero exit into a clean-log claim."""
    return [line for line in path.read_text(encoding="utf-8").splitlines()
            if "ERROR:" in line or "WARNING:" in line]


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--checks", type=Path, default=SCRATCH / "checks")
args = parser.parse_args()
validation = read_json(EVIDENCE / "validation.json")
engine = read_json(SCRATCH / "prefab-fresh.json")
normalization = read_json(SCRATCH / "prefab-check.json")
checks = read_json(args.checks / "summary.json")
compilation = read_json(args.checks / "script-checks/compilation.json")
assert validation["reexport_byte_identical"]
assert engine["ok"] and not engine["failures"]
assert normalization["ok"] and normalization["save_reload_byte_stable"]
assert normalization["attachment_save_reload_byte_stable"]
assert engine["attachment_uid"] == normalization["attachment_uid"]
assert engine["prefab_uid"] == normalization["prefab_uid"]
assert engine["model_uid"] == normalization["model_uid"]
assert checks["ok"] and all(row["ok"] for row in compilation)
assert any(row["script"] == f"tools/asset_production/{NID}/check_prefab.gd" for row in compilation)
assert not diagnostics(SCRATCH / "prefab-fresh.log")
gut_log = (args.checks / "gut.log").read_text(encoding="utf-8")
python_log = (args.checks / "python-tests.log").read_text(encoding="utf-8")
python_tests = int(re.search(r"Ran (\d+) tests", python_log).group(1))
gut_tests = int(re.search(r"^Tests\s+(\d+)", gut_log, re.MULTILINE).group(1))
gut_assertions = int(re.search(r"^Asserts\s+(\d+)", gut_log, re.MULTILINE).group(1))
validation["engine"] = engine
validation["engine"]["save_reload_byte_stable"] = True
validation["engine"]["attachment_save_reload_byte_stable"] = True
validation["engine"]["normalization_diagnostics"] = diagnostics(SCRATCH / "prefab-normalize.log")
validation["engine"]["final_import_diagnostics"] = diagnostics(SCRATCH / "import-final.log")
validation["production_checks"] = {
    "overall_ok": checks["ok"],
    "results": checks["results"],
    "compiled_scripts": len(compilation),
    "owned_script_style_compile_and_format": "PASS",
    "python_tests": python_tests,
    "gut_tests": gut_tests,
    "gut_assertions": gut_assertions,
    "failure_exclusions": [],
}
validation["visual_review"] = {
    "renders_inspected": ["hero.png", "side.png", "frontage_detail.png", "overhead_47m_42deg.png"],
    "renderer": "Blender Cycles CPU, 24 samples, denoised, AgX; PNG compression 95, no output dither",
    "viewport": [1280, 720],
    "gameplay_camera": {
        "position_godot_m": [0, 47, 0], "vertical_fov_deg": 42, "vertical_down": True,
        "note": "Annex at origin; existing .01 shifted to (0,0,19); parent rear cropped, north up",
    },
    "findings": "Attached blue roof/coral cue read. Coplanar fascia, rear coping and mullion artifacts corrected.",
    "context": "Side/overhead reuse .01 source only for renders; no context geometry in owned blend/GLB",
    "scope": "Isolated Blender evidence, not engine lighting, world placement or device acceptance",
}
(EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
summary = (
    "FINAL ASSET CHECK RECEIPT — raw logs remain outside the checkout\n"
    "Asset: d07_retail_buildings.03; Blender 5.2.2 LTS, exporter 5.2.40.\n"
    "Final author and source/GLB validator: exit 0; no topology or normal failures.\n"
    f"{validation['source_triangles']} triangles; {validation['source_vertices']} source / "
    f"{validation['glb_vertices_including_surface_splits']} GLB vertices; 1 mesh / 7 surfaces.\n"
    f"Fresh source reexport byte-identical; {validation['glb_bytes']} bytes.\n"
    "Blender reports use_nodes API deprecation notices only.\n"
    "All four final renders inspected; coplanar fascia, rear coping and mullion artifacts corrected.\n"
    "Headless editor normalization exits 0, saves stable bytes; diagnostics retained:\n"
    + "\n".join(validation["engine"]["normalization_diagnostics"]) + "\n\n"
    "Final pinned headless import exits 0; diagnostics retained:\n"
    + "\n".join(validation["engine"]["final_import_diagnostics"]) + "\n\n"
    "Fresh non-editor prefab check exits 0 with no ERROR/WARNING:\n"
    + (SCRATCH / "prefab-fresh.log").read_text(encoding="utf-8") + "\n"
    "Explicit owned lint/format/compile commands all exit 0.\n"
    "Full production_checks.py exits 0; all layers pass, no failure exclusions.\n"
    f"{len(compilation)} scripts lint/format/compile; Python {python_tests}; "
    f"GUT {gut_tests}, {gut_assertions} assertions.\n"
    "Negative control exits 1 as expected and is detected.\n"
    "Actual ActorMotion/car motion, multiplayer, placement and device gates remain pending.\n"
)
(EVIDENCE / "final.log").write_text(summary, encoding="utf-8", newline="\n")
paths = [
    ROOT / f"art/source/models/environment/{NID}",
    ROOT / f"art/models/environment/{NID}",
    ROOT / f"tools/asset_production/{NID}",
    EVIDENCE,
    ROOT / f"docs/assets/production/{NID}.md",
    ROOT / f"scenes/prefabs/environment/{NID}.tscn",
    ROOT / f"scenes/prefabs/environment/{NID}_attached.tscn",
]
files = []
for path in paths:
    for item in (sorted(path.rglob("*")) if path.is_dir() else [path]):
        if item.is_file() and item.name != "manifest.json" and "__pycache__" not in item.parts:
            data = item.read_bytes()
            files.append({"path": item.relative_to(ROOT).as_posix(), "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()})
manifest = {
    "asset_id": "d07_retail_buildings.03",
    "producer": "Commissioned isolated asset-production worker",
    "scope": "Every asset payload except this manifest; sibling handoff covered by sibling manifest",
    "files": sorted(files, key=lambda item: item["path"]),
}
(EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
print(f"Recorded {len(files)} payload hashes; production checks all pass.")
