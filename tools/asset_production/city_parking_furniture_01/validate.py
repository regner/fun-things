"""Check saved source, binary GLB geometry, provisional bounds and fresh-export identity."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_parking_furniture_01"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence/validation.json"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EXPORT = ROOT / f"art/models/environment/{ASSET}/{ASSET}.glb"
SCRATCH = Path(f"C:/tmp/ft/assets/{ASSET}/reexport")
EXPECTED_MIN = [-0.9, 0.0, -0.15]
EXPECTED_MAX = [0.9, 0.16, 0.15]


def read_accessor(document, binary, index):
    """Decode the actual uncompressed numeric accessor, honoring offsets and stride."""
    accessor = document["accessors"][index]
    view = document["bufferViews"][accessor["bufferView"]]
    formats = {5123: "H", 5125: "I", 5126: "f"}
    widths = {"SCALAR": 1, "VEC3": 3}
    fmt = "<" + formats[accessor["componentType"]] * widths[accessor["type"]]
    stride = view.get("byteStride", struct.calcsize(fmt))
    start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, start + i * stride)
            for i in range(accessor["count"])]


def main():
    """Reject geometry or export drift before recording a passing source/export receipt."""
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    assert scene.unit_settings.system == "METRIC" and scene.unit_settings.scale_length == 1
    collection = bpy.data.collections["export_" + ASSET]
    assert {obj.name for obj in collection.objects} == {"CityParkingFurniture01", "CityParkingFurniture01_Mesh"}
    for obj in collection.objects:
        assert tuple(obj.location) == (0, 0, 0)
        assert tuple(obj.scale) == (1, 1, 1)
        assert tuple(obj.rotation_euler) == (0, 0, 0)
    obj = bpy.data.objects["CityParkingFurniture01_Mesh"]
    mesh = obj.data
    assert not obj.modifiers
    mesh.calc_loop_triangles()
    normals_error = max(abs(normal.vector.length - 1) for normal in mesh.corner_normals)
    assert normals_error < 1e-5
    bm = bmesh.new()
    bm.from_mesh(mesh)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    assert nonmanifold == 0
    volume = bm.calc_volume(signed=True)
    assert volume > 0
    bm.free()
    assert all(math.isfinite(value) for vertex in mesh.vertices for value in vertex.co)
    assert all(face.area > 1e-10 for face in mesh.polygons)
    assert all(triangle.area > 1e-10 for triangle in mesh.loop_triangles)
    assert [mat.name for mat in mesh.materials] == ["parking_rubber_petrol", "parking_safety_amber"]
    coords = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
    bounds_min = [min(v[i] for v in coords) for i in range(3)]
    bounds_max = [max(v[i] for v in coords) for i in range(3)]
    godot_min = [bounds_min[0], bounds_min[2], -bounds_max[1]]
    godot_max = [bounds_max[0], bounds_max[2], -bounds_min[1]]
    assert all(abs(a - b) < .001 for a, b in zip(godot_min + godot_max, EXPECTED_MIN + EXPECTED_MAX))
    raw = EXPORT.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", raw)
    assert magic == b"glTF" and version == 2 and length == len(raw)
    json_length, json_type = struct.unpack_from("<II", raw, 12)
    assert json_type == 0x4E4F534A
    document = json.loads(raw[20:20 + json_length])
    bin_length, bin_type = struct.unpack_from("<II", raw, 20 + json_length)
    assert bin_type == 0x004E4942
    binary = raw[28 + json_length:28 + json_length + bin_length]
    assert not any(document.get(key) for key in ("animations", "cameras", "skins", "images", "textures"))
    assert len(document["nodes"]) == 2 and len(document["meshes"]) == 1
    for node in document["nodes"]:
        assert node.get("translation", [0, 0, 0]) == [0, 0, 0]
        assert node.get("rotation", [0, 0, 0, 1]) == [0, 0, 0, 1]
        assert node.get("scale", [1, 1, 1]) == [1, 1, 1]
    primitives = document["meshes"][0]["primitives"]
    assert len(primitives) == 2
    positions = []
    vertex_count = triangle_count = 0
    export_normal_error = 0.0
    for primitive in primitives:
        assert primitive.get("mode", 4) == 4
        local = read_accessor(document, binary, primitive["attributes"]["POSITION"])
        normals = read_accessor(document, binary, primitive["attributes"]["NORMAL"])
        indices = [entry[0] for entry in read_accessor(document, binary, primitive["indices"])]
        assert len(indices) % 3 == 0
        for i in range(0, len(indices), 3):
            a, b, c = (Vector(local[j]) for j in indices[i:i + 3])
            assert (b - a).cross(c - a).length * .5 > 1e-10
        export_normal_error = max(export_normal_error, max(abs(Vector(n).length - 1) for n in normals))
        vertex_count += len(local)
        triangle_count += len(indices) // 3
        positions.extend(local)
    assert export_normal_error < 1e-5
    export_min = [min(v[i] for v in positions) for i in range(3)]
    export_max = [max(v[i] for v in positions) for i in range(3)]
    assert all(abs(a - b) < 1e-5 for a, b in zip(export_min + export_max, godot_min + godot_max))
    assert triangle_count == len(mesh.loop_triangles)
    assert {mat["name"] for mat in document["materials"]} == {mat.name for mat in mesh.materials}
    assert all(not mat.get("doubleSided", False) for mat in document["materials"])
    sys.argv = ["export.py", "--", str(SCRATCH)]
    exec(compile((Path(__file__).parent / "export.py").read_text(),
                 str(Path(__file__).parent / "export.py"), "exec"), {"__file__": __file__})
    fresh = (SCRATCH / f"{ASSET}.glb").read_bytes()
    assert fresh == raw, "Fresh export differs from committed output"
    report = {
        "asset": "city_parking_furniture.01", "blender": bpy.app.version_string,
        "blender_build": bpy.app.build_hash.decode(), "exporter": "5.2.40",
        "provisional_dimensions_m": [1.8, 0.16, 0.30], "bounds_tolerance_m": .001,
        "godot_bounds_min_m": export_min, "godot_bounds_max_m": export_max,
        "pivot_m": [0, 0, 0], "source_vertices": len(mesh.vertices),
        "source_faces": len(mesh.polygons), "triangles": triangle_count,
        "export_vertices": vertex_count, "mesh_count": 1, "surface_count": 2,
        "degenerate_faces": 0, "degenerate_triangles": 0, "nonmanifold_edges": nonmanifold,
        "source_normal_max_length_error": normals_error,
        "export_normal_max_length_error": export_normal_error, "closed_volume_m3": volume,
        "materials": document["materials"], "glb_bytes": len(raw),
        "glb_sha256": hashlib.sha256(raw).hexdigest(), "fresh_export_byte_identical": True,
        "source_export_status": "passed",
    }
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
