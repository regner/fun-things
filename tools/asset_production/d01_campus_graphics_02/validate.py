"""Audit unchanged carrier geometry/UVs and a fresh shared-contract reexport."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import struct

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_campus_graphics_02"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / "art/source/models/environment/city_sign_supports_02/city_sign_supports_02.blend"
GLB = ROOT / "art/models/environment/city_sign_supports_02/city_sign_supports_02.glb"
BASE = ROOT / "scenes/prefabs/environment/city_sign_supports_02.tscn"


# Reuse the tested decoder and numeric/hash helpers rather than a private copy.
HELPERS = ROOT / "tools/asset_production/d01_campus_graphics_01/validate.py"
spec = importlib.util.spec_from_file_location("campus_geometry_helpers", HELPERS)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
close, digest, accessor = helpers.close, helpers.digest, helpers.accessor


def main():
    """Measure existing source and binary; require exact reexport and unchanged dependencies."""
    dependencies = [digest(p) for p in (SOURCE, GLB, BASE)]
    spec = importlib.util.spec_from_file_location("campus_export", Path(__file__).with_name("export.py"))
    exporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exporter)
    fresh = exporter.export_shared()
    assert fresh.read_bytes() == GLB.read_bytes()
    collection = bpy.data.collections["export_city_sign_supports_02"]
    assert {o.name for o in collection.objects} == {
        "CitySignSupports02", "CitySignSupports02_Hardware", "CitySignSupports02_ArtworkCarrier"
    }
    assert bpy.context.scene.unit_settings.system == "METRIC"
    assert bpy.context.scene.unit_settings.scale_length == 1
    source_vertices = triangles = 0
    for obj in collection.objects:
        close(obj.location, (0, 0, 0))
        close(obj.rotation_euler, (0, 0, 0))
        close(obj.scale, (1, 1, 1))
        if obj.type != "MESH":
            continue
        assert not obj.modifiers and obj.parent.name == "CitySignSupports02"
        mesh = obj.data
        mesh.calc_loop_triangles()
        source_vertices += len(mesh.vertices)
        triangles += len(mesh.loop_triangles)
        bm = bmesh.new()
        bm.from_mesh(mesh)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges)
        assert all(f.calc_area() > 1e-10 for f in bm.faces)
        assert bm.calc_volume(signed=True) > 0
        bm.free()
        assert all(abs(n.vector.length-1) < 0.0001 for n in mesh.corner_normals)
    raw = GLB.read_bytes()
    length = struct.unpack_from("<I", raw, 12)[0]
    document = json.loads(raw[20:20+length])
    binary = raw[28+length:]
    assert len(document["meshes"]) == 2 and len(document["nodes"]) == 3
    assert not any(document.get(k) for k in ("images", "textures", "skins", "animations"))
    positions = []
    glb_vertices = glb_triangles = surfaces = face_surfaces = 0
    for mesh in document["meshes"]:
        for surface_index, surface in enumerate(mesh["primitives"]):
            points = accessor(document, binary, surface["attributes"]["POSITION"])
            normals = accessor(document, binary, surface["attributes"]["NORMAL"])
            indices = [v[0] for v in accessor(document, binary, surface["indices"])]
            positions.extend(points)
            glb_vertices += len(points)
            glb_triangles += len(indices)//3
            surfaces += 1
            assert all(abs(math.sqrt(sum(v*v for v in n))-1) < 0.0001 for n in normals)
            for i in range(0, len(indices), 3):
                a, b, c = (Vector(points[indices[i+j]]) for j in range(3))
                cross = (b-a).cross(c-a)
                assert cross.length_squared > 1e-20
                assert cross.dot(sum((Vector(normals[indices[i+j]]) for j in range(3)), Vector())) > 0
            mat = document["materials"][surface["material"]]["name"]
            if mat == "sign_face":
                face_surfaces += 1
                assert mesh["name"] == "CitySignSupports02_ArtworkCarrier" and surface_index == 0
                uvs = accessor(document, binary, surface["attributes"]["TEXCOORD_0"])
                for p, uv, n in zip(points, uvs, normals):
                    close(uv, ((0.72-p[0])/1.44, (1.27-p[1])/0.39))
                    close(n, (0, 0, -1))
                    assert abs(p[2]+0.071) < 0.00001
    minimum = [min(v[i] for v in positions) for i in range(3)]
    maximum = [max(v[i] for v in positions) for i in range(3)]
    close(minimum, (-0.80, 0, -0.20))
    close(maximum, (0.80, 1.35, 0.20))
    assert (source_vertices, triangles, glb_vertices, glb_triangles, surfaces, face_surfaces) == (
        1244, 2448, 1596, 2448, 5, 1)
    assert dependencies == [digest(p) for p in (SOURCE, GLB, BASE)]
    report = {
        "asset_id": "d01_campus_graphics.02", "status": "PASS",
        "blender": bpy.app.version_string, "build": bpy.app.build_hash.decode(),
        "new_geometry": False, "dependencies": dependencies, "dependencies_unchanged": True,
        "fresh_reexport_byte_identical": True, "glb_bytes": len(raw),
        "glb_sha256": hashlib.sha256(raw).hexdigest(), "source_vertices": source_vertices,
        "glb_vertices": glb_vertices, "triangles": triangles, "meshes": 2, "surfaces": 5,
        "degenerate_source_faces": 0, "degenerate_glb_triangles": 0, "nonmanifold_edges": 0,
        "unit_source_and_export_normals": True, "outward_winding": True,
        "godot_aabb": {"min": minimum, "max": maximum}, "dimensions_m": [1.60, 1.35, 0.40],
        "pivot": [0, 0, 0], "ground_datum_m": 0, "tolerance_m": 0.001,
        "artwork": {"face_size_m": [1.44, 0.39], "safe_size_m": [1.38, 0.33],
                    "plane_godot_z": -0.071, "uv_verified_upright_unmirrored": True,
                    "override_slot": 0, "texture_size": [1440, 390]},
    }
    (EVIDENCE / "validation.json").write_text(
        json.dumps(report, indent=2)+"\n", encoding="utf-8", newline="\n")
    print("CAMPUS_SOURCE_PASS", json.dumps(report))


if __name__ == "__main__":
    main()
