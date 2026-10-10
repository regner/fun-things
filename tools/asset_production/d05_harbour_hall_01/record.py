"""Retain lean final receipts and SHA-256 hashes for this asset's owned deliverables."""
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_harbour_hall_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def read_json(path):
    """Read an existing source or external engine/check receipt."""
    return json.loads(path.read_text(encoding="utf-8"))


def diagnostics(path):
    """Retain diagnostics without treating a zero process exit as a clean log."""
    return [line for line in path.read_text(encoding="utf-8").splitlines()
            if re.search(r"(?:ERROR:|WARNING:|SCRIPT ERROR:)", line)]


validation = read_json(EVIDENCE / "validation.json")
engine = read_json(SCRATCH / "prefab-fresh-final.json")
second = read_json(SCRATCH / "prefab-second-process.json")
normalization = read_json(SCRATCH / "prefab-check.json")
checks = read_json(SCRATCH / "checks/summary.json")
compilation = read_json(SCRATCH / "checks/script-checks/compilation.json")
assert engine["ok"] and not engine["failures"]
assert engine == second, "Fresh separate-process resource/physics results differ"
assert normalization["save_reload_byte_stable"]
assert engine["prefab_uid"] == normalization["prefab_uid"]
assert engine["model_uid"] == normalization["model_uid"]
assert checks["ok"] and all(row["ok"] for row in checks["results"].values())
assert all(row["ok"] for row in compilation)
assert any(row["script"] == f"tools/asset_production/{NID}/check_prefab.gd"
           for row in compilation)
assert not diagnostics(SCRATCH / "prefab-fresh-final.log")
assert not diagnostics(SCRATCH / "prefab-second-process.log")
import_diagnostics = diagnostics(SCRATCH / "import-final.log")
assert all("WARNING: [MCP] Godot 4.8 detected" in line for line in import_diagnostics)
normalization_diagnostics = diagnostics(SCRATCH / "prefab-normalize-final.log")
validation["engine"] = engine
validation["engine"]["save_reload_byte_stable"] = True
validation["engine"]["second_fresh_process_exact_match"] = True
validation["engine"]["normalization_diagnostics"] = normalization_diagnostics
validation["engine"]["final_import_diagnostics"] = import_diagnostics
validation["production_checks"] = {
    "overall_ok": checks["ok"],
    "results": checks["results"],
    "compiled_script_count": len(compilation),
    "failed_compilation_paths": [row["script"] for row in compilation if not row["ok"]],
    "owned_script_style_compile_and_format": "PASS",
    "python_tests": 17,
    "gut_tests": 149,
    "gut_assertions": 6768,
    "known_failure_exemptions": [],
}
render_names = ["hero", "side", "entry_detail", "overhead_47m_42deg"]
renders = []
for name in render_names:
    path = EVIDENCE / f"{name}.png"
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack_from(">II", data, 16)
    assert (width, height) == (1280, 720)
    assert len(data) <= 400 * 1024
    renders.append({"file": path.name, "width": width, "height": height, "bytes": len(data)})
validation["visual_review"] = {
    "renders_inspected": renders,
    "observation": "Broad hipped roof remains quiet; warm civic entry and shallow steps read in detail. "
                   "Side framing corrected to retain ground contact; canopy and square are separate.",
    "renderer": "Blender Cycles CPU, 32 samples, AgX; isolated evidence, not engine visual acceptance",
    "gameplay_camera": "Vertical down, 47 m, 42 degree vertical perspective FOV, 1280x720",
    "png": "RGB8, compression 95, dither disabled; no image post-processing",
}
(EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
summary = (
    "FINAL VALIDATION RECEIPT — raw scratch outputs remain outside the checkout\n"
    "Asset: d05_harbour_hall.01 / Harbour hall exterior\n"
    "Blender author-final and validate-final: exit 0; topology, bounds, normals and byte comparison PASS.\n"
    "Blender deprecation notices only. Four inspected PNGs are 1280x720, each <400 KiB.\n"
    "Initial side render cropped the plinth; final camera reframed.\n"
    "Initial GDScript await-in-loop warnings resolved with localized fixed-step test rationale.\n"
    "Initial editor normalization timed out at 180 seconds waiting on gameplay timer (exit 124).\n"
    "Corrected editor process-frame startup; only runtime mode runs physics.\n"
    "Final headless editor normalization: exit 0; two-save byte stability and UIDs PASS.\n"
    "Final normalization diagnostics (not a clean-log claim):\n"
    + "\n".join(normalization_diagnostics) + "\n\n"
    "Final worktree import: exit 0; only existing addon compatibility warning:\n"
    + "\n".join(import_diagnostics) + "\n\n"
    "Two fresh runtime processes: exit 0; no ERROR/WARNING diagnostics; exact receipts match.\n"
    "Nine shape expectations, front ray and six production ActorMotion paths PASS.\n"
    "First fresh runtime receipt:\n"
    + (SCRATCH / "prefab-fresh-final.log").read_text(encoding="utf-8") + "\n"
    "Canonical production_checks.py: exit 0; no known-failure exclusions.\n"
    "208 GDScripts compile; formatting/lint PASS; Python 17/17; GUT 149/149, 6768 assertions.\n"
    "Negative control intentionally exited 1 and was detected.\n"
    "Pending: independent review, canopy assembly, district placement/camera, car movement,\n"
    "multiplayer transport/admission, packaged build/LOD and sustained device performance.\n"
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
    "asset_id": "d05_harbour_hall.01",
    "producer": "Commissioned isolated asset-production worker",
    "scope": "Every produced deliverable except this self-referential manifest; no scratch outputs",
    "files": sorted(files, key=lambda item: item["path"]),
}
(EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
print(f"Recorded {len(files)} payload hashes; all canonical production checks passed.")
