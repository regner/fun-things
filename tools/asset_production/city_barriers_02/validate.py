"""Measure reused rail geometry and fresh-export its two dependencies without changing them."""
import hashlib
import json
import math
import struct
from pathlib import Path

import bmesh
import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
KIT = "city_quay_furniture_02"
EVIDENCE = ROOT / "docs/assets/production/city_barriers_02-evidence"
SCRATCH = Path("C:/tmp/ft/assets/city_barriers_02/reexport")


def main():
    """Assert the source contract and record actual assembled counts, bounds and byte identity."""
    assert bpy.app.version_string == "5.2.2 LTS"
    assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
    source = ROOT / f"art/source/models/environment/{KIT}/{KIT}.blend"
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source))
    assert bpy.context.scene.unit_settings.system == "METRIC"
    assert bpy.context.scene.unit_settings.scale_length == 1
    settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
    settings.update(export_animations=False, export_skins=False)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    components = {}
    coordinates = []
    for component, offsets in (("straight", [0]), ("post_landward", [-1.5, 1.5])):
        collection = f"export_{KIT}_{component}"
        obj = bpy.data.objects[f"CityQuayFurniture02_{component}_Mesh"]
        assert len(bpy.data.collections[collection].objects) == 2
        for member in (obj, obj.parent):
            assert all(abs(v - 1) < 1e-6 for v in member.scale)
            assert all(abs(v) < 1e-6 for v in (*member.location, *member.rotation_euler))
        assert not obj.modifiers
        mesh = obj.data
        mesh.calc_loop_triangles()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
        bm.free()
        degenerate = sum(face.area <= 1e-10 for face in mesh.polygons)
        degenerate_triangles = sum(tri.area <= 1e-10 for tri in mesh.loop_triangles)
        normal_error = max(abs(normal.vector.length - 1) for normal in mesh.corner_normals)
        assert nonmanifold == degenerate == degenerate_triangles == 0
        assert normal_error < 1e-5
        for offset in offsets:
            for vertex in mesh.vertices:
                x, y, z = obj.matrix_world @ vertex.co
                assert all(math.isfinite(value) for value in (x, y, z))
                coordinates.append((x + offset, z, -y))
        glb = ROOT / f"art/models/environment/{KIT}/{KIT}_{component}.glb"
        raw = glb.read_bytes()
        json_length = struct.unpack_from("<I", raw, 12)[0]
        document = json.loads(raw[20:20 + json_length])
        assert len(document["meshes"]) == 1
        assert not any(document.get(key) for key in ("images", "textures", "skins", "animations"))
        primitives = document["meshes"][0]["primitives"]
        triangles = sum(document["accessors"][p["indices"]]["count"] // 3 for p in primitives)
        export_vertices = sum(document["accessors"][p["attributes"]["POSITION"]]["count"]
                              for p in primitives)
        assert triangles == len(mesh.loop_triangles)
        target = SCRATCH / glb.name
        bpy.ops.export_scene.gltf(**dict(settings, collection=collection, filepath=str(target)))
        assert target.read_bytes() == raw, "Shared dependency reexport drift"
        components[component] = {
            "instances": len(offsets), "source_vertices": len(mesh.vertices),
            "source_faces": len(mesh.polygons), "triangles": triangles,
            "export_vertices": export_vertices, "meshes": 1, "surfaces": len(primitives),
            "nonmanifold_edges": nonmanifold, "degenerate_faces": degenerate,
            "degenerate_triangles": degenerate_triangles, "normal_length_max_error": normal_error,
            "fresh_export_byte_identical": True, "path": glb.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    minimum = [min(v[i] for v in coordinates) for i in range(3)]
    maximum = [max(v[i] for v in coordinates) for i in range(3)]
    assert all(abs(a - b) < .001 for a, b in zip(minimum, [-1.66, 0, -.16]))
    assert all(abs(a - b) < .001 for a, b in zip(maximum, [1.66, 1.06, .16]))
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    report = {
        "asset": "city_barriers.02", "output_type": "Assembly reference",
        "blender": bpy.app.version_string, "exporter": list(io_scene_gltf2.bl_info["version"]),
        "source": source.relative_to(ROOT).as_posix(), "source_sha256": source_hash,
        "source_unchanged": True, "new_meshes": 0, "components": components,
        "assembly": {"bounds_min_m": minimum, "bounds_max_m": maximum,
                     "size_m": [maximum[i] - minimum[i] for i in range(3)],
                     "ground_pivot_m": [0, 0, 0]},
    }
    for key in ("source_vertices", "triangles", "export_vertices", "meshes", "surfaces"):
        report["assembly"][key] = sum(c[key] * c["instances"] for c in components.values())
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print("CITY_BARRIERS_02_SOURCE_PASS", json.dumps(report))


if __name__ == "__main__":
    main()
