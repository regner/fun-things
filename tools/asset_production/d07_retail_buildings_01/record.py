"""Record final external checks and hash this asset's lean delivered payloads."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d07_retail_buildings_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def read_json(path):
    """Read a source or engine receipt without silently supplying missing evidence."""
    return json.loads(path.read_text(encoding="utf-8"))


validation = read_json(EVIDENCE / "validation.json")
engine = read_json(SCRATCH / "prefab-fresh.json")
normalization = read_json(SCRATCH / "prefab-check.json")
checks = read_json(SCRATCH / "checks-final2/summary.json")
compilation = read_json(SCRATCH / "checks-final2/script-checks/compilation.json")
assert validation["reexport_byte_identical"]
assert engine["ok"] and not engine["failures"]
assert normalization["save_reload_byte_stable"]
assert engine["prefab_uid"] == normalization["prefab_uid"]
assert engine["model_uid"] == normalization["model_uid"]
assert checks["ok"] and all(row["ok"] for row in compilation)
assert any(row["script"] == f"tools/asset_production/{NID}/check_prefab.gd" for row in compilation)
fresh_log = (SCRATCH / "prefab-fresh.log").read_text()
assert not any(marker in fresh_log for marker in ("ERROR:", "WARNING:"))
validation["engine"] = engine
validation["engine"]["save_reload_byte_stable"] = True
validation["engine"]["normalization_diagnostics"] = (
    "Corrected editor normalization exits 0 and saves stable bytes but reports shutdown "
    "RID/ObjectDB leaks and the existing MCP compatibility warning. Fresh runtime checks are clean."
)
validation["production_checks"] = {
    "overall_ok": checks["ok"],
    "results": checks["results"],
    "compiled_scripts": len(compilation),
    "owned_script_style_compile_and_format": "PASS",
    "python_tests": 17,
    "gut_tests": 165,
    "gut_assertions": 6918,
    "failure_exclusions": [],
}
validation["visual_review"] = {
    "renders_inspected": ["hero.png", "side.png", "frontage_detail.png", "overhead_47m_42deg.png"],
    "renderer": "Blender Cycles CPU, 24 samples, denoised, AgX; PNG compression 95, no output dither",
    "viewport": [1280, 720],
    "gameplay_camera": {
        "position_godot_m": [0, 47, -19], "vertical_fov_deg": 42, "vertical_down": True,
        "note": "Entrance-centred actual-scale crop; whole giant building cannot fit at this height",
    },
    "findings": "Three roof tiers and coral cue read; initial coplanar stripe corrected in source.",
    "scope": "Isolated Blender evidence, not engine lighting, world placement or device acceptance",
}
(EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
normalize_log = (SCRATCH / "prefab-normalize-final.log").read_text()
diagnostics = "\n".join(line for line in normalize_log.splitlines()
                        if "ERROR:" in line or "WARNING:" in line)
summary = (
    "FINAL ASSET CHECK RECEIPT — full scratch logs remain outside the checkout\n"
    "Asset: d07_retail_buildings.01; Blender 5.2.2 LTS, exporter 5.2.40.\n"
    "Final author and source/GLB validator: exit 0; no topology or normal failures.\n"
    "6,804 triangles; 3,528 source / 4,536 GLB vertices; 1 mesh / 7 surfaces.\n"
    "Fresh source reexport byte-identical; 189,408 bytes.\n"
    "Blender use_nodes deprecation notices only.\n"
    "All four final renders inspected; original coplanar coral/roof stripe corrected.\n"
    "Initial editor normalization: timeout exit 124 while awaiting filesystem signal.\n"
    "Corrected bounded polling/deadline: normalization exits 0, saves stable bytes.\n"
    "Editor diagnostics retained (not claimed clean):\n" + diagnostics + "\n\n"
    "Final pinned headless import: exit 0; existing MCP 4.8 compatibility warning.\n"
    "Fresh non-editor prefab check: exit 0; no ERROR/WARNING:\n" + fresh_log + "\n"
    "Intermediate checks-final: owned max-local-variables warning; helper extraction fixed it.\n"
    "Final production_checks.py (checks-final2): exit 0; all layers pass with no exclusions.\n"
    "218 GDScripts lint/format/compile; Python 17/17; GUT 165/165, 6,918 assertions.\n"
    "Negative control exits 1 as expected and is detected.\n"
    "Actual ActorMotion/car motion, multiplayer transport, placement and device gates pending.\n"
)
(EVIDENCE / "final.log").write_text(summary, encoding="utf-8", newline="\n")
paths = [
    ROOT / f"art/source/models/environment/{NID}",
    ROOT / f"art/models/environment/{NID}",
    ROOT / f"tools/asset_production/{NID}",
    EVIDENCE,
    ROOT / f"docs/assets/production/{NID}.md",
    ROOT / f"scenes/prefabs/environment/{NID}.tscn",
]
files = []
for path in paths:
    for item in (sorted(path.rglob("*")) if path.is_dir() else [path]):
        if item.is_file() and item.name != "manifest.json" and "__pycache__" not in item.parts:
            data = item.read_bytes()
            files.append({"path": item.relative_to(ROOT).as_posix(), "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()})
manifest = {
    "asset_id": "d07_retail_buildings.01",
    "producer": "Commissioned isolated asset-production worker",
    "scope": "Every produced deliverable except this self-referential manifest; no scratch outputs",
    "files": sorted(files, key=lambda item: item["path"]),
}
(EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
print(f"Recorded {len(files)} payload hashes; production checks all pass.")
