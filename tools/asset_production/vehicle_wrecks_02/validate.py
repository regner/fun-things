"""Validate the saved wreck, actual binary GLB, live footprint and deterministic re-export."""
import json
import math
from pathlib import Path
import runpy
import sys

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "vehicle_wrecks_02"
SOURCE = ROOT / f"art/source/models/vehicles/{ASSET}/{ASSET}.blend"
EXPORT = ROOT / f"art/models/vehicles/{ASSET}/{ASSET}.glb"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence/validation.json"
SCRATCH = Path(f"C:/tmp/ft/assets/{ASSET}/reexport")


# Reuse the existing family binary readers rather than creating a second GLB parser.
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools/asset_production/vehicle_wrecks_01"))
from validate import accessor, bounds, fingerprint, glb


def main():
    """Assert every source/export constraint and write numbers only after a fresh byte match."""
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    assert scene.unit_settings.system == "METRIC" and scene.unit_settings.scale_length == 1
    collection = bpy.data.collections["export_" + ASSET]
    assert {o.name for o in collection.all_objects} == {"VehicleWrecks02", "VehicleWrecks02_Mesh"}
    for obj in collection.all_objects:
        assert tuple(obj.location) == (0, 0, 0)
        assert tuple(obj.rotation_euler) == (0, 0, 0)
        assert tuple(obj.scale) == (1, 1, 1)
        assert not obj.animation_data
    mesh = bpy.data.objects["VehicleWrecks02_Mesh"].data
    assert not bpy.data.objects["VehicleWrecks02_Mesh"].modifiers
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    degenerate = sum(face.area <= 1e-10 for face in mesh.polygons)
    triangle_degenerate = sum(face.area <= 1e-10 for face in mesh.loop_triangles)
    print("TOPOLOGY", len(mesh.vertices), len(mesh.loop_triangles), nonmanifold,
          degenerate, triangle_degenerate, flush=True)
    assert nonmanifold == degenerate == triangle_degenerate == 0
    bm.free()
    normal_error = max(abs(n.vector.length - 1) for n in mesh.corner_normals)
    assert normal_error < 1e-5
    points = [(v.co.x, v.co.z, -v.co.y) for v in mesh.vertices]
    assert all(math.isfinite(x) for p in points for x in p)
    source_bounds = bounds(points)
    # Independent accepted live-car literal bounds; origin and horizontal footprint must not jump.
    expected_min, expected_max = [-.9565, 0, -1.845], [.9565, 1.5088, 1.837]
    for actual, expected in zip(source_bounds["min"] + source_bounds["max"],
                                expected_min + expected_max):
        assert abs(actual - expected) < .002, (source_bounds, expected_min, expected_max)
    doc, binary = glb(EXPORT)
    assert len(doc["nodes"]) == 2 and len(doc["meshes"]) == 1
    assert not any(doc.get(k) for k in ("animations", "skins", "images", "textures", "cameras"))
    for node in doc["nodes"]:
        assert node.get("translation", [0, 0, 0]) == [0, 0, 0]
        assert node.get("scale", [1, 1, 1]) == [1, 1, 1]
        assert node.get("rotation", [0, 0, 0, 1]) == [0, 0, 0, 1]
    positions = []
    triangles = 0
    export_normal_error = 0.0
    primitives = doc["meshes"][0]["primitives"]
    assert len(primitives) == 8
    for primitive in primitives:
        assert primitive.get("mode", 4) == 4
        local = accessor(doc, binary, primitive["attributes"]["POSITION"])
        normals = accessor(doc, binary, primitive["attributes"]["NORMAL"])
        indices = [v[0] for v in accessor(doc, binary, primitive["indices"])]
        assert len(indices) % 3 == 0
        for i in range(0, len(indices), 3):
            a, b, c = (Vector(local[j]) for j in indices[i:i + 3])
            assert (b - a).cross(c - a).length * .5 > 1e-10
        export_normal_error = max(export_normal_error,
                                  max(abs(Vector(n).length - 1) for n in normals))
        positions.extend(local)
        triangles += len(indices) // 3
    assert export_normal_error < 1e-5
    actual_bounds = bounds(positions)
    for key in ("min", "max"):
        assert all(abs(a - b) < 1e-5 for a, b in zip(actual_bounds[key], source_bounds[key]))
    live_path = ROOT / "art/models/vehicles/car_crate_a/car_crate_a.glb"
    live, _ = glb(live_path)
    live_triangles = sum(live["accessors"][p["indices"]]["count"] // 3
                         for m in live["meshes"] for p in m["primitives"])
    assert triangles == len(mesh.loop_triangles) <= live_triangles == 11256
    assert all(not m.get("doubleSided", False) for m in doc["materials"])
    assert all(not m.get("emissiveFactor") for m in doc["materials"])
    argv = sys.argv[:]
    sys.argv = [str(Path(__file__).with_name("export.py")), "--", str(SCRATCH)]
    runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
    sys.argv = argv
    assert EXPORT.read_bytes() == (SCRATCH / EXPORT.name).read_bytes()
    previous = json.loads(EVIDENCE.read_text()) if EVIDENCE.exists() else {}
    report = {"asset": "vehicle_wrecks.02", "blender": bpy.app.version_string,
              "blender_build": bpy.app.build_hash.decode(), "exporter": "5.2.40",
              "source": fingerprint(SOURCE), "export": fingerprint(EXPORT),
              "live_source": fingerprint(ROOT / "art/source/models/vehicles/car_crate_a/car_crate_a.blend"),
              "live_export": fingerprint(live_path), "vertices": len(mesh.vertices),
              "export_vertices": len(positions), "triangles": triangles,
              "live_triangle_budget": live_triangles, "mesh_count": 1, "surface_count": len(primitives),
              "nonmanifold_edges": nonmanifold, "degenerate_faces": degenerate,
              "degenerate_triangles": triangle_degenerate, "source_normal_max_error": normal_error,
              "export_normal_max_error": export_normal_error, "godot_aabb": actual_bounds,
              "dimensions_xyz_m": [actual_bounds["max"][i] - actual_bounds["min"][i] for i in range(3)],
              "ground_pivot_m": [0, 0, 0], "bounds_tolerance_m": .002,
              "fresh_reexport_byte_identical": True, "materials": doc["materials"],
              "status": "PASS: saved source, actual GLB and fresh byte-identical export",
              "engine": previous.get("engine", {"status": "pending"})}
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: report[k] for k in ("triangles", "vertices", "godot_aabb", "status")}, indent=2))


if __name__ == "__main__":
    main()
