"""Record lean final asset receipts and hashes; run after final checks and handoff edits."""
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_academic_buildings_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def read_json(path):
    """Read a completed source or headless engine receipt."""
    return json.loads(path.read_text(encoding="utf-8"))


def errors(path):
    """Reject actual engine errors, not just nonzero process exits."""
    return [line for line in path.read_text(encoding="utf-8").splitlines()
            if re.search(r"(?:ERROR:|SCRIPT ERROR:)", line)]


validation = read_json(EVIDENCE / "validation.json")
first = read_json(SCRATCH / "prefab-check.json")
second = read_json(SCRATCH / "prefab-second-process.json")
assert first["ok"] and not first["failures"]
assert first == second, "Separate headless processes differ"
normalization = read_json(SCRATCH / "roundtrip.json")
assert normalization["ok"] and normalization["save_reload_byte_stable"]
assert first["prefab_uid"] == normalization["prefab_uid"]
assert first["model_uid"] == normalization["model_uid"]
normalization_errors = errors(SCRATCH / "roundtrip.log")
assert all("RID allocations of type" in line and "leaked at exit" in line
           for line in normalization_errors), normalization_errors
assert len(first["physics_shape_queries"]) == 13
for name in ("import-final", "prefab-check", "prefab-second-process"):
    assert not errors(SCRATCH / f"{name}.log"), name
assert "1 file already formatted" in (SCRATCH / "format.log").read_text(encoding="utf-8")
assert "no issues found" in (SCRATCH / "style.log").read_text(encoding="utf-8")
glb = ROOT / f"art/models/environment/{NID}/{NID}.glb"
assert hashlib.sha256(glb.read_bytes()).hexdigest() == validation["glb_sha256"]
assert glb.stat().st_size == validation["glb_bytes"]
assert validation["reexport_byte_identical"]
validation["engine"] = first
validation["engine"]["second_fresh_process_exact_match"] = True
validation["engine"]["save_reload_byte_stable"] = True
validation["engine"]["normalization_shutdown_errors"] = normalization_errors
validation["checks"] = {
    "final_headless_import_error_lines": [],
    "owned_gdscript_format": "PASS",
    "owned_gdscript_lint": "PASS: zero warnings",
    "production_checks_run": False,
    "editor_normalization": "Exit 0, stable bytes/UIDs and valid resource receipt, but editor shutdown "
        "RID/ObjectDB leak diagnostics retained. Runtime load/physics and final import logs are clean.",
    "runtime_save_limitation": "Runtime-only ResourceSaver strips UIDs after cache refresh on this "
        "pin; checker now rejects runtime normalization. Original generated UIDs restored and "
        "headless editor-normalized; final import and read-only runtime checks pass.",
}
renders = []
for name in ("hero", "side", "entrance_clock_detail", "overhead_47m_42deg"):
    path = EVIDENCE / f"{name}.png"
    raw = path.read_bytes()
    assert raw[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack_from(">II", raw, 16)
    expected = (1280, 720) if name == "overhead_47m_42deg" else (1120, 630)
    assert (width, height) == expected
    assert len(raw) < 420 * 1024
    renders.append({"file": path.name, "width": width, "height": height, "bytes": len(raw)})
validation["visual_review"] = {
    "renders_inspected": renders,
    "observation": "Complete U roof/open-court silhouette reads in hero; ordered windows and "
        "closed amber arch read in detail. Planar tower cap corrected before final render. "
        "Calibrated overhead is a local court crop, not a whole-building overview.",
    "renderer": "Blender Cycles CPU, 32 samples, AgX; not engine visual acceptance",
    "gameplay_camera": {"blender_position_m": [0, -3, 47], "rotation_radians": [0, 0, 0],
                        "vertical_fov_degrees": 42, "projection": "perspective"},
    "png": "RGB8, compression 95, dither disabled, no post-processing",
}
(EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
summary = (
    "FINAL ASSET RECEIPT: d01_academic_buildings.01\n"
    "Blender author and validator: exit 0; 5.2.2 LTS / exporter 5.2.40.\n"
    "28,758 triangles, 15,547 source vertices, 21,604 exported vertices, one mesh, nine surfaces.\n"
    "Zero degenerate source faces / GLB triangles and zero non-manifold source edges.\n"
    "Unit normals, metre scale, identity transforms, independent bounds and byte reexport PASS.\n"
    "Four final renders inspected; tower planar shading and detail framing corrected.\n"
    "Initial multi-segment micro-bevels reduced without changing silhouette or envelope.\n"
    "Author notices: Blender 6.0 future use_nodes deprecation warnings, no failed asset operation.\n"
    "Headless editor normalization: exit 0; byte-stable save/reload and original UIDs preserved.\n"
    "Editor shutdown RID/ObjectDB leaks remain diagnostics, not a clean-log claim.\n"
    "Runtime-only save stripped scene/dependency UIDs after cache refresh; checker now rejects\n"
    "runtime normalization. Original generated UIDs restored before editor normalization.\n"
    "Initial gdstyle fmt --check requested formatting; corrected, final format/lint pass.\n"
    "Final import: exit 0, no ERROR/SCRIPT ERROR lines.\n"
    "Two fresh runtime checks: exit 0, clean error logs, byte-identical receipts.\n"
    "Linked model, UIDs, bounds, opaque materials and two-save byte stability PASS.\n"
    "13 shape expectations, court-to-door ray and six production ActorMotion cases PASS.\n"
    "Authority/replay agree; transport, placement, car handling and device acceptance remain pending.\n"
    "No production_checks.py run (decision 52).\n\n"
    + (SCRATCH / "format.log").read_text(encoding="utf-8")
    + (SCRATCH / "style.log").read_text(encoding="utf-8")
    + "\nEditor normalization shutdown errors (retained):\n"
    + "\n".join(normalization_errors)
    + "\nFinal runtime receipt:\n"
    + (SCRATCH / "prefab-check.log").read_text(encoding="utf-8")
)
(EVIDENCE / "final.log").write_text(summary, encoding="utf-8", newline="\n")
paths = [ROOT / f"art/source/models/environment/{NID}",
         ROOT / f"art/models/environment/{NID}", ROOT / f"tools/asset_production/{NID}",
         EVIDENCE, ROOT / f"docs/assets/production/{NID}.md",
         ROOT / f"scenes/prefabs/environment/{NID}.tscn"]
files = []
for path in paths:
    for item in (sorted(path.rglob("*")) if path.is_dir() else [path]):
        if item.is_file() and item.name != "manifest.json" and "__pycache__" not in item.parts:
            raw = item.read_bytes()
            files.append({"path": item.relative_to(ROOT).as_posix(), "bytes": len(raw),
                          "sha256": hashlib.sha256(raw).hexdigest()})
manifest = {"asset_id": "d01_academic_buildings.01",
            "producer": "Commissioned isolated asset-production worker",
            "scope": "Every produced payload except this self-referential manifest; no scratch files",
            "files": sorted(files, key=lambda item: item["path"])}
(EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
print(f"PASS: final geometry, engine, style and render receipts; {len(files)} payload hashes")
