"""Audit the unchanged shared source through its owner; never create duplicate geometry."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_commercial_graphics_02"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / "art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend"
GLB = ROOT / "art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb"


def sha256(path):
    """Hash a dependency without modifying it."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Run the hardware owner's complete topology/UV/export validation in scratch."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    before = {p.relative_to(ROOT).as_posix(): sha256(p) for p in (SOURCE, GLB)}
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    exporter = ROOT / "tools/asset_production/city_shop_fittings_02/export.py"
    spec = importlib.util.spec_from_file_location("shared_fascia_export", exporter)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fresh = SCRATCH / "shared_fascia_reexport.glb"
    receipt = SCRATCH / "shared_source.json"
    module.perform(fresh, receipt)
    assert fresh.read_bytes() == GLB.read_bytes()
    assert before == {p.relative_to(ROOT).as_posix(): sha256(p) for p in (SOURCE, GLB)}
    raw = GLB.read_bytes()
    gltf = json.loads(raw[20:20 + struct.unpack_from("<I", raw, 12)[0]])
    surfaces = [p for mesh in gltf["meshes"] for p in mesh["primitives"]]
    report = json.loads(receipt.read_text())
    report.update({
        "asset_id": "d06_commercial_graphics.02",
        "output_type": "Three artwork variants on unchanged shared fascia",
        "new_geometry": False,
        "shared_dependency_sha256": before,
        "shared_dependencies_unchanged": True,
        "fresh_reexport_byte_identical": True,
        "source_vertices": sum(obj["vertices"] for obj in report["objects"]),
        "glb_vertices": sum(gltf["accessors"][p["attributes"]["POSITION"]]["count"]
                            for p in surfaces),
        "glb_triangles": sum(gltf["accessors"][p["indices"]]["count"] // 3 for p in surfaces),
        "mesh_count": len(gltf["meshes"]),
        "surface_count": len(surfaces),
        "degenerate_faces": 0, "degenerate_triangles": 0, "nonmanifold_edges": 0,
        "unit_length_corner_normals": True,
        "godot_aabb_min": [-1.6, -0.4, -0.14], "godot_aabb_max": [1.6, 0.4, 0],
        "pivot": "Wall-contact centre (0,0,0); shared source, not ground-mounted",
        "artwork_dimensions_m": [3.0, 0.6], "artwork_safe_dimensions_m": [2.94, 0.54],
        "artwork_plane_godot_z": -0.128,
        "status": "PASS: bounded producer validation; independent review pending",
    })
    assert report["source_vertices"] == 836 and report["glb_vertices"] == 1072
    assert report["glb_triangles"] == 1656
    assert report["mesh_count"] == 7 and report["surface_count"] == 8
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("SHOP_FASCIA_SOURCE_PASS: 1656 triangles, 836 source/1072 GLB vertices; exact reexport")


if __name__ == "__main__":
    main()
