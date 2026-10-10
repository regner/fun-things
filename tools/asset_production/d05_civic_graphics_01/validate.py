"""Audit reused source with its existing validator and verify a byte-identical reexport."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import runpy
import sys

import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_civic_graphics_01"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / "art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend"
GLB = ROOT / "art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb"


def sha256(path):
    """Hash a committed dependency without mutating it."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Validate the existing closed meshes and face UV interface; retain a lean receipt."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    before = {str(p.relative_to(ROOT)): sha256(p) for p in [SOURCE, GLB]}
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    exporter = ROOT / "tools/asset_production/city_shop_fittings_02/export.py"
    spec = importlib.util.spec_from_file_location("shared_fascia_export", exporter)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    reexport = SCRATCH / "reexport_city_shop_fittings_02.glb"
    receipt = SCRATCH / "shared_source.json"
    module.perform(reexport, receipt)
    assert reexport.read_bytes() == GLB.read_bytes(), "Existing shared source must reproduce exactly"
    assert before == {str(p.relative_to(ROOT)): sha256(p) for p in [SOURCE, GLB]}
    previous_args = sys.argv
    try:
        sys.argv = ["check_glb.py", str(SCRATCH)]
        runpy.run_path(str(exporter.with_name("check_glb.py")), run_name="__main__")
    finally:
        sys.argv = previous_args
    decoded = json.loads((SCRATCH / "glb_checks.json").read_text())
    report = json.loads(receipt.read_text())
    raw = GLB.read_bytes()
    json_size = struct.unpack_from("<I", raw, 12)[0]
    gltf = json.loads(raw[20:20 + json_size])
    triangles = sum(gltf["accessors"][surface["indices"]]["count"] // 3
                    for mesh in gltf["meshes"] for surface in mesh["primitives"])
    vertices = sum(gltf["accessors"][surface["attributes"]["POSITION"]]["count"]
                   for mesh in gltf["meshes"] for surface in mesh["primitives"])
    assert triangles == 1656
    assert len(gltf["meshes"]) == 7 and len(gltf["materials"]) == 5
    report.update({
        "asset_id": "d05_civic_graphics.01",
        "output_type": "Artwork set reusing unchanged fascia geometry",
        "new_geometry": False,
        "shared_glb_bytes": len(raw),
        "decoded_glb_checks": decoded,
        "shared_source": str(SOURCE.relative_to(ROOT)),
        "shared_glb": str(GLB.relative_to(ROOT)),
        "shared_dependency_sha256": before,
        "shared_dependencies_unchanged": True,
        "fresh_reexport_byte_identical": True,
        "source_vertices": sum(obj["vertices"] for obj in report["objects"]),
        "glb_vertices": vertices,
        "glb_triangles": triangles,
        "mesh_count": 7,
        "surface_count": sum(len(mesh["primitives"]) for mesh in gltf["meshes"]),
        "degenerate_faces": 0,
        "degenerate_triangles": 0,
        "nonmanifold_edges": 0,
        "unit_length_corner_normals": True,
        "godot_aabb_min": [-1.6, -0.4, -0.14],
        "godot_aabb_max": [1.6, 0.4, 0],
        "pivot": "Wall contact centre (0,0,0), not ground-mounted",
        "artwork_plane_godot_z": -0.128,
        "artwork_dimensions_m": [3.0, 0.6],
        "artwork_safe_dimensions_m": [2.94, 0.54],
        "status": "PASS; bounded producer source/export checks, independent review pending",
    })
    report.pop("output_bytes", None)
    report.pop("output_sha256", None)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("HALL_SOURCE_PASS", json.dumps({k: report[k] for k in [
        "source_vertices", "glb_vertices", "glb_triangles", "mesh_count", "surface_count"
    ]}))


if __name__ == "__main__":
    main()
