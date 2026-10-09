"""Collect final external check receipts and hash only this asset's lean deliverables."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_entertainment_hall_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def read_json(path):
    """Read one producer or pinned-engine receipt."""
    return json.loads(path.read_text(encoding="utf-8"))


validation = read_json(EVIDENCE / "validation.json")
engine = read_json(SCRATCH / "prefab-fresh-final.json")
normalization = read_json(SCRATCH / "prefab-check.json")
checks = read_json(SCRATCH / "checks-final/summary.json")
compilation = read_json(SCRATCH / "checks-final/script-checks/compilation.json")
failed_compilation = [row["script"] for row in compilation if not row["ok"]]
assert engine["ok"] and not engine["failures"]
assert normalization["save_reload_byte_stable"]
assert engine["prefab_uid"] == normalization["prefab_uid"]
assert all(path.startswith("tests/fixtures/asset_production/") for path in failed_compilation)
assert any(row["script"] == f"tools/asset_production/{NID}/check_prefab.gd" and row["ok"]
           for row in compilation)
assert (SCRATCH / "checks-final/script-checks/style.log").read_text().find("no issues found") >= 0
fresh_log = (SCRATCH / "prefab-fresh-final.log").read_text()
assert not any(marker in fresh_log for marker in ("ERROR:", "WARNING:"))
validation["engine"] = engine
validation["engine"]["save_reload_byte_stable"] = True
validation["engine"]["normalization_diagnostics"] = (
    "Editor-mode custom SceneTree saves succeed but report shutdown RID/ObjectDB leaks; "
    "fresh runtime-mode load/query and --check-only commands exit 0 without diagnostics."
)
validation["production_checks"] = {
    "results": checks["results"],
    "overall_ok": checks["ok"],
    "failed_compilation_paths": failed_compilation,
    "formatting_failures": [
        "tests/fixtures/asset_production/batch_observation.gd",
        "tools/asset_production/integration/batch03_author.gd",
        "tools/asset_production/integration/inspector.gd",
    ],
    "owned_script_style_compile_and_format": "PASS",
    "python_tests": 9,
    "gut_tests": 9,
    "gut_assertions": 70,
}
validation["visual_review"] = {
    "renders_inspected": ["hero.png", "side.png", "entry_detail.png", "overhead_47m_42deg.png"],
    "observation": "Smooth rounded silhouette reads without the separate luminous ring; quiet roof centre.",
    "renderer": "Blender Cycles CPU, 32 samples, AgX; not an in-engine visual acceptance",
    "gameplay_camera": "Vertical down, 47 m, 42 degree vertical perspective FOV, 1280x800",
}
(EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
normalize_log = (SCRATCH / "prefab-normalize-final.log").read_text()
diagnostics = "\n".join(line for line in normalize_log.splitlines()
                         if "ERROR:" in line or "WARNING:" in line)
summary = (
    "FINAL VALIDATION RECEIPT — full scratch logs are outside the checkout\n"
    "Blender author and source/GLB validation: exit 0; topology and byte comparison pass.\n"
    "Blender 5.2 deprecation notices only; no author/validator errors.\n"
    "Godot import: exit 0; existing MCP 4.8 compatibility warning.\n"
    "Editor normalize: exit 0, UID generation and two-save stability pass.\n"
    "Editor-mode shutdown diagnostics retained (not claimed clean):\n" + diagnostics + "\n\n"
    "Fresh pinned headless runtime check (exit 0; no ERROR/WARNING):\n" + fresh_log + "\n"
    "Owned GDScript: gdstyle 0.3.0 lint/fmt and explicit compilation pass.\n"
    "Production checks: exit 1, known unrelated compile/format failures only.\n"
    "Python 9/9; GUT 9/9, 70 assertions; negative control detected.\n"
    "Initial owned lint warnings fixed; initial runtime-mode save omitted UID, corrected by editor save.\n"
    "Placement, actual player/car motion, multiplayer transport and target-device performance not tested.\n"
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
    "asset_id": "d06_entertainment_hall.01",
    "producer": "Commissioned isolated asset-production worker",
    "scope": "Every produced deliverable except this self-referential manifest; no scratch outputs",
    "files": sorted(files, key=lambda item: item["path"]),
}
(EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
print(f"Recorded {len(files)} payload hashes; known global failures retained without suppression.")
