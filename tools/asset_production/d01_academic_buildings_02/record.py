"""Combine final receipts and hash every deliverable after handoff edits and final import."""
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_academic_buildings_02"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")


def read_json(path):
    """Read a completed source or headless engine receipt."""
    return json.loads(path.read_text(encoding="utf-8"))


def diagnostics(path, pattern=r"(?:ERROR:|SCRIPT ERROR:)"):
    """Keep matching diagnostics visible rather than relying only on process exit status."""
    return [line for line in path.read_text(encoding="utf-8").splitlines()
            if re.search(pattern, line)]


validation = read_json(EVIDENCE / "validation.json")
first = read_json(SCRATCH / "prefab-check.json")
second = read_json(SCRATCH / "prefab-second-process.json")
assert first["ok"] and not first["failures"]
assert first == second, "Separate headless processes differ"
normalization = read_json(SCRATCH / "roundtrip.json")
assert normalization["ok"] and normalization["save_reload_byte_stable"]
assert first["prefab_uid"] == normalization["prefab_uid"]
assert first["model_uid"] == normalization["model_uid"]
normalization_errors = diagnostics(SCRATCH / "roundtrip.log")
assert all("RID allocations of type" in line and "leaked at exit" in line
           for line in normalization_errors), normalization_errors
normalization_diagnostics = diagnostics(SCRATCH / "roundtrip.log", r"(?:ERROR:|WARNING:)")
assert len(first["physics_shape_queries"]) == 13
for name in ("import-initial", "import-final", "prefab-check", "prefab-second-process"):
    assert not diagnostics(SCRATCH / f"{name}.log"), name
assert "1 file already formatted" in (SCRATCH / "format.log").read_text(encoding="utf-8")
assert "no issues found" in (SCRATCH / "style.log").read_text(encoding="utf-8")
glb = ROOT / f"art/models/environment/{NID}/{NID}.glb"
assert hashlib.sha256(glb.read_bytes()).hexdigest() == validation["glb_sha256"]
assert glb.stat().st_size == validation["glb_bytes"]
assert validation["reexport_byte_identical"]
validation["engine"] = first
validation["engine"]["second_fresh_process_exact_match"] = True
validation["engine"]["save_reload_byte_stable"] = True
validation["engine"]["normalization_diagnostics"] = normalization_diagnostics
validation["checks"] = {
    "final_headless_import_error_lines": [],
    "owned_gdscript_format": "PASS",
    "owned_gdscript_lint": "PASS: zero warnings",
    "production_checks_run": False,
    "editor_normalization": "Exit 0 and stable saved bytes/UIDs. Custom headless editor shutdown "
        "reports scan-thread/RID/ObjectDB diagnostics, retained below; not a clean-log claim. "
        "The final import and both runtime resource/physics checks have no error lines.",
}
renders = []
for name in ("hero", "side", "entrance_detail", "overhead_47m_42deg"):
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
    "observation": "Long two-storey bar and single central cross-gable read without signs. "
        "Ordered pale windows, green pediments and closed amber portal match the hall family. "
        "Full roof fits the calibrated overhead; roof fields stay quiet without scattered props. "
        "Detail isolates the closed portal, not a traversable entrance.",
    "renderer": "Blender Cycles CPU, 32 samples, AgX; not engine visual acceptance",
    "gameplay_camera": {"blender_position_m": [0, 0, 47], "rotation_radians": [0, 0, 0],
                        "vertical_fov_degrees": 42, "projection": "perspective"},
    "png": "RGB8, compression 95, dither disabled, no post-processing",
}
(EVIDENCE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
summary = (
    "FINAL ASSET RECEIPT: d01_academic_buildings.02\n"
    "Blender author and validator: exit 0; 5.2.2 LTS / exporter 5.2.40.\n"
    f"{validation['source_triangles']:,} triangles; {validation['source_vertices']:,} source vertices; "
    f"{validation['glb_vertices_including_surface_splits']:,} exported vertices; one mesh/eight surfaces.\n"
    "Zero degenerate source faces/GLB triangles; zero non-manifold source edges.\n"
    "Unit normals, metre scale, identity transforms, bounds and byte-identical reexport PASS.\n"
    "Four final renders inspected; all RGB8 PNG, compression95, at or below1280x720.\n"
    "Author notices: Blender 6.0 future use_nodes deprecations; no failed asset operation.\n"
    "Blender --version reports one tiny unfreed block; author/validator shutdowns are clean.\n"
    "Headless editor normalization: exit0; byte-stable save/reload and generated UIDs preserved.\n"
    "Editor shutdown scan-thread/RID/ObjectDB diagnostics remain, not a clean-log claim.\n"
    "Initial lint: one max-local-variables warning; split collision inspection, final lint clean.\n"
    "Final import: exit0, no ERROR/SCRIPT ERROR lines.\n"
    "Two fresh runtime checks: exit0, clean error logs, identical resource/physics receipts.\n"
    "Linked ancestry, UIDs, bounds, opaque materials and two-save byte stability PASS.\n"
    "13 shape expectations, closed-entry ray and six production ActorMotion cases PASS.\n"
    "Authority/replay agree; transport, placement, car handling and device acceptance pending.\n"
    "No production_checks.py run (decision52).\n\n"
    + (SCRATCH / "format.log").read_text(encoding="utf-8")
    + (SCRATCH / "style.log").read_text(encoding="utf-8")
    + "\nEditor normalization diagnostics (retained):\n"
    + "\n".join(normalization_diagnostics)
    + "\nFinal runtime receipt:\n"
    + (SCRATCH / "prefab-check.log").read_text(encoding="utf-8")
)
(EVIDENCE / "final.log").write_text(summary, encoding="utf-8", newline="\n")
# Handoff hash and byte count must come from the final receipt, not an intermediate export.
doc = ROOT / f"docs/assets/production/{NID}.md"
handoff = doc.read_text(encoding="utf-8")
assert re.findall(r"\b[0-9a-f]{64}\b", handoff) == [validation["glb_sha256"]]
assert f"{validation['glb_bytes']:,} bytes" in handoff
paths = [ROOT / f"art/source/models/environment/{NID}",
         ROOT / f"art/models/environment/{NID}", ROOT / f"tools/asset_production/{NID}",
         EVIDENCE, doc, ROOT / f"scenes/prefabs/environment/{NID}.tscn"]
files = []
for path in paths:
    for item in (sorted(path.rglob("*")) if path.is_dir() else [path]):
        if item.is_file() and item.name != "manifest.json" and "__pycache__" not in item.parts:
            raw = item.read_bytes()
            files.append({"path": item.relative_to(ROOT).as_posix(), "bytes": len(raw),
                          "sha256": hashlib.sha256(raw).hexdigest()})
manifest = {"asset_id": "d01_academic_buildings.02",
            "producer": "Commissioned isolated asset-production worker",
            "scope": "Every produced payload except this self-referential manifest; no scratch files",
            "files": sorted(files, key=lambda item: item["path"])}
(EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", newline="\n")
print(f"PASS: final geometry, engine, style and render receipts; {len(files)} payload hashes")
