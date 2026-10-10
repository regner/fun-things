"""Consolidate final external receipts and hash this asset's lean delivered payloads."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d07_retail_buildings_02"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def read_json(path):
    """Read a required receipt; missing evidence must fail closed."""
    return json.loads(path.read_text(encoding="utf-8"))


def check_receipt(name):
    """Require successful targeted exits; retain only the known editor shutdown exception."""
    exit_code = int((SCRATCH / f"{name}.exit").read_text(encoding="utf-8"))
    assert exit_code == 0, f"{name} exited {exit_code}"
    raw = (SCRATCH / f"{name}.log").read_bytes()
    lines = raw.decode("utf-8").splitlines()
    diagnostics = [line for line in lines if "ERROR" in line or "WARNING:" in line]
    for line in diagnostics:
        if "ERROR" in line:
            # The pinned editor leaks shutdown RIDs; never excuse script/import errors.
            known_shutdown = name == "prefab-normalize" and re.fullmatch(
                r"ERROR: \d+ RID allocations of type '.+' were leaked at exit\.", line)
            assert known_shutdown, (name, line)
    return {"exit_code": exit_code, "log_sha256": hashlib.sha256(raw).hexdigest(),
            "diagnostics": diagnostics}


validation = read_json(EVIDENCE / "validation.json")
engine = read_json(SCRATCH / "prefab-fresh.json")
normalization = read_json(SCRATCH / "prefab-check.json")
checks = {name: check_receipt(name)
          for name in ("validate", "import-final", "prefab-normalize", "compile",
                       "prefab-fresh", "gdstyle-lint", "gdstyle-format")}
assert validation["reexport_byte_identical"]
raw_glb = (ROOT / f"art/models/environment/{NID}/{NID}.glb").read_bytes()
assert validation["glb_sha256"] == hashlib.sha256(raw_glb).hexdigest()
assert validation["glb_bytes"] == len(raw_glb)
assert engine["ok"] and not engine["failures"]
assert normalization["ok"] and not normalization["failures"]
assert normalization["save_reload_byte_stable"]
assert engine["prefab_uid"] == normalization["prefab_uid"]
assert engine["model_uid"] == normalization["model_uid"]
assert not checks["prefab-fresh"]["diagnostics"]
validation["engine"] = engine
validation["engine"]["save_reload_byte_stable"] = True
validation["engine"]["normalization_diagnostics"] = checks["prefab-normalize"]["diagnostics"]
validation["engine"]["final_import_diagnostics"] = checks["import-final"]["diagnostics"]
validation.pop("production_checks", None)
validation["targeted_checks"] = checks
validation["visual_review"] = {
    "renders_inspected": ["hero.png", "side.png", "frontage_detail.png", "overhead_47m_42deg.png"],
    "renderer": "Blender Cycles CPU, 24 samples, denoised, AgX; PNG compression 95, no output dither",
    "viewport": [1280, 720],
    "gameplay_camera": {
        "position_godot_m": [0, 47, 0], "vertical_fov_deg": 42, "vertical_down": True,
        "note": "Complete single-roof store at actual scale; front/north at image top",
    },
    "findings": "Blue roof and offset coral cue read; buried plum skin corrected before final export.",
    "scope": "Isolated Blender evidence, not engine lighting, world placement or device acceptance",
}
(EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
summary = (
    "FINAL TARGETED ASSET CHECK RECEIPT — raw logs remain outside the checkout\n"
    f"Asset: {NID}; review round 1 receipt refresh.\n"
    f"Blender {validation['blender']}, exporter {validation['glTF_exporter']}.\n"
    f"{validation['source_triangles']} triangles; {validation['source_vertices']} source / "
    f"{validation['glb_vertices_including_surface_splits']} GLB vertices; 1 mesh / 7 surfaces.\n"
    f"Fresh source reexport byte-identical; {validation['glb_bytes']} bytes.\n"
    f"GLB SHA-256: {validation['glb_sha256']}\n"
    "Source/export geometry and existing four render payloads unchanged by review fixes.\n"
    "Visual review retained from original production; no new render or lighting claim.\n"
    "Targeted commands (all exit 0); warning/error diagnostics retained below:\n"
    + "\n".join(f"{name}: exit {receipt['exit_code']}; log SHA-256 {receipt['log_sha256']}"
                + ("\n" + "\n".join(receipt['diagnostics']) if receipt['diagnostics'] else "")
                for name, receipt in checks.items()) + "\n\n"
    "Fresh non-editor prefab resource/physics receipt:\n"
    + (SCRATCH / "prefab-fresh.log").read_text(encoding="utf-8") + "\n"
    "Prefab pack/save/reload/resave byte-stable; identities match fresh load.\n"
    "Only targeted validation is required; no full-project production checks were run.\n"
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
]
files = []
for path in paths:
    for item in (sorted(path.rglob("*")) if path.is_dir() else [path]):
        if item.is_file() and item.name != "manifest.json" and "__pycache__" not in item.parts:
            data = item.read_bytes()
            files.append({"path": item.relative_to(ROOT).as_posix(), "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()})
manifest = {
    "asset_id": "d07_retail_buildings.02",
    "producer": "Commissioned isolated asset-production worker",
    "scope": "Every asset payload except this manifest; sibling handoff covered by sibling manifest",
    "files": sorted(files, key=lambda item: item["path"]),
}
(EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
print(f"Recorded {len(files)} payload hashes; targeted checks all pass.")
