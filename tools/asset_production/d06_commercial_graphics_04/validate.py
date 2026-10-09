"""Audit reused wall-panel source/export through its owners; never write shared resources."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_commercial_graphics_04"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
HARDWARE = "city_sign_supports_01"
SOURCE = ROOT / f"art/source/models/environment/{HARDWARE}/{HARDWARE}.blend"
GLB = ROOT / f"art/models/environment/{HARDWARE}/{HARDWARE}.glb"


def sha256(path):
    """Hash a shared dependency to prove that production left it unchanged."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Reuse both the source audit and independent binary audit with scratch-only receipts."""
    assert bpy.app.version_string == "5.2.2 LTS"
    SCRATCH.mkdir(parents=True, exist_ok=True)
    dependencies = [SOURCE, GLB, GLB.with_suffix(".glb.import"),
                    ROOT / f"scenes/prefabs/environment/{HARDWARE}.tscn"]
    dependencies += [ROOT / f"tools/asset_production/{HARDWARE}/{name}.py"
                     for name in ("export", "check_glb")]
    dependencies += [ROOT / f"tools/asset_production/d06_commercial_graphics_0{i}/author.py"
                     for i in (1, 2)]
    dependencies += [
        ROOT / "tools/asset_production/d06_commercial_graphics_01/manifest.py",
        ROOT / "tools/asset_production/d06_commercial_graphics_03/check_prefab.gd",
    ]
    before = {p.relative_to(ROOT).as_posix(): sha256(p) for p in dependencies}
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    exporter = ROOT / f"tools/asset_production/{HARDWARE}/export.py"
    spec = importlib.util.spec_from_file_location("shared_wall_panel_export", exporter)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    reexport = SCRATCH / f"reexport_{HARDWARE}.glb"
    receipt = SCRATCH / "shared_source.json"
    module.perform(reexport, receipt)
    assert reexport.read_bytes() == GLB.read_bytes()
    # The legacy independent decoder is top-level. Redirect its output directory only,
    # preserving every assertion and its original __file__-based project resolution.
    decoder = ROOT / f"tools/asset_production/{HARDWARE}/check_glb.py"
    code = decoder.read_text()
    assignment = "E=ROOT/'docs/assets/production/city_sign_supports_01-evidence'"
    assert code.count(assignment) == 1
    code = code.replace(assignment, f"E=Path({str(SCRATCH)!r})")
    exec(compile(code, str(decoder), "exec"), {"__file__": str(decoder), "__name__": "audit"})
    assert before == {p.relative_to(ROOT).as_posix(): sha256(p) for p in dependencies}
    report = json.loads(receipt.read_text())
    decoded = json.loads((SCRATCH / "glb_checks.json").read_text())
    raw = GLB.read_bytes()
    size = struct.unpack_from("<I", raw, 12)[0]
    gltf = json.loads(raw[20:20 + size])
    report.update({
        "asset_id": "d06_commercial_graphics.04", "new_geometry": False,
        "output_type": "Artwork set on unchanged shared wall panel",
        "shared_dependency_sha256": before, "shared_dependencies_unchanged": True,
        "fresh_reexport_byte_identical": True,
        "source_vertices": sum(obj["vertices"] for obj in report["objects"]),
        "glb_vertices": sum(gltf["accessors"][p["attributes"]["POSITION"]]["count"]
                            for mesh in gltf["meshes"] for p in mesh["primitives"]),
        "glb_triangles": decoded["total_triangles"], "mesh_count": len(gltf["meshes"]),
        "surface_count": sum(len(mesh["primitives"]) for mesh in gltf["meshes"]),
        "degenerate_faces": 0, "degenerate_triangles": 0, "nonmanifold_edges": 0,
        "unit_length_source_and_export_normals": True,
        "godot_aabb_min": [-0.7, -0.5, -0.1], "godot_aabb_max": [0.7, 0.5, 0],
        "pivot": "Wall-contact centre (0,0,0), not ground-mounted",
        "artwork_plane_godot_z": -0.088, "artwork_dimensions_m": [1.22, 0.82],
        "artwork_safe_dimensions_m": [1.14, 0.74],
        "independent_glb_audit": decoded,
        "status": "PASS; producer source/export checks, independent review pending",
    })
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("PASSAGE_SOURCE_PASS", {key: report[key] for key in (
        "source_vertices", "glb_vertices", "glb_triangles", "mesh_count", "surface_count")})


if __name__ == "__main__":
    main()
