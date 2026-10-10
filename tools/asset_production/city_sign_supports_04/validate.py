"""Check the saved wayfinding post, decoded GLB geometry/UVs and byte-identical reexport."""
import hashlib
import json
import math
from pathlib import Path
import runpy
import struct
import sys

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "city_sign_supports_04"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
GLB = ROOT / f"art/models/environment/{NID}/{NID}.glb"
SCRATCH = Path("C:/tmp/ft/assets") / NID / "reexport"


def close(actual, expected, tolerance=0.00001):
    """Compare measurements to documented provisional literals, not authoring formulas."""
    assert len(actual) == len(expected)
    assert all(abs(a - b) <= tolerance for a, b in zip(actual, expected)), (actual, expected)


def accessor(index):
    """Read actual binary accessor values, including interleaved byte strides."""
    entry = document["accessors"][index]
    view = document["bufferViews"][entry["bufferView"]]
    width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[entry["type"]]
    fmt = "<" + {5126: "f", 5125: "I", 5123: "H", 5121: "B"}[entry["componentType"]] * width
    stride = view.get("byteStride", struct.calcsize(fmt))
    start = view.get("byteOffset", 0) + entry.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, start + i * stride) for i in range(entry["count"])]


bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
assert bpy.app.version_string == "5.2.2 LTS"
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
collection = bpy.data.collections[f"export_{NID}"]
assert {obj.name for obj in collection.objects} == {
    "CitySignSupports04", "CitySignSupports04_Hardware", "CitySignSupports04_ArtworkLower",
    "CitySignSupports04_ArtworkMiddle", "CitySignSupports04_ArtworkUpper"
}
source_meshes, coordinates = [], []
for obj in collection.objects:
    close(obj.location, (0, 0, 0))
    close(obj.rotation_euler, (0, 0, 0))
    close(obj.scale, (1, 1, 1))
    if obj.type != "MESH":
        continue
    assert obj.parent.name == "CitySignSupports04"
    assert not obj.modifiers
    mesh = obj.data
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    degenerate = sum(face.calc_area() <= 1e-10 for face in bm.faces)
    assert not any(not edge.is_contiguous for edge in bm.edges)
    assert bm.calc_volume(signed=True) > 0
    bm.free()
    assert nonmanifold == 0 and degenerate == 0
    assert all(abs(normal.vector.length - 1) < 0.0001 for normal in mesh.corner_normals)
    assert all(math.isfinite(value) for vertex in mesh.vertices for value in vertex.co)
    coordinates.extend(tuple(vertex.co) for vertex in mesh.vertices)
    source_meshes.append({
        "name": obj.name, "vertices": len(mesh.vertices), "triangles": len(mesh.loop_triangles),
        "nonmanifold_edges": nonmanifold, "degenerate_faces": degenerate,
        "unit_corner_normals": True, "materials": [mat.name for mat in mesh.materials],
    })
close([min(v[i] for v in coordinates) for i in range(3)], (-1.44, -0.20, 0))
close([max(v[i] for v in coordinates) for i in range(3)], (1.44, 0.20, 3.92))
# Each independent artwork field is upright from the same front, not mirrored with its arrow.
face_contracts = {
    "CitySignSupports04_ArtworkLower": (1.375, 2.635, 2.865),
    "CitySignSupports04_ArtworkMiddle": (-0.085, 3.085, 3.315),
    "CitySignSupports04_ArtworkUpper": (1.375, 3.535, 3.765),
}
for name, (right_edge, bottom, top) in face_contracts.items():
    carrier = bpy.data.objects[name]
    assert [m.name for m in carrier.data.materials] == ["sign_face", "mount_metal"]
    front = [p for p in carrier.data.polygons if p.material_index == 0]
    assert len(front) == 1 and front[0].normal.y > 0.999
    for loop in front[0].loop_indices:
        v = carrier.data.vertices[carrier.data.loops[loop].vertex_index].co
        uv = carrier.data.uv_layers["UVMap"].data[loop].uv
        close(uv, ((right_edge - v.x) / 1.29, (v.z - bottom) / 0.23))
        assert abs(v.y - 0.184) < 0.00001
raw = GLB.read_bytes()
magic, version, total = struct.unpack_from("<4sII", raw)
assert magic == b"glTF" and version == 2 and total == len(raw)
length, kind = struct.unpack_from("<II", raw, 12)
assert kind == 0x4E4F534A
document = json.loads(raw[20:20 + length])
binary_length, binary_kind = struct.unpack_from("<II", raw, 20 + length)
assert binary_kind == 0x004E4942
binary = raw[28 + length:28 + length + binary_length]
for unused in ("images", "textures", "skins", "animations", "cameras"):
    assert not document.get(unused)
assert len(document["nodes"]) == 5 and len(document["meshes"]) == 4
assert {m["name"] for m in document["materials"]} == {
    "support_petrol", "recess_gasket", "mount_metal", "sign_face"
}
assert all(not mat.get("doubleSided", False) for mat in document["materials"])
assert all(mat.get("alphaMode", "OPAQUE") == "OPAQUE" for mat in document["materials"])
for node in document["nodes"]:
    close(node.get("scale", (1, 1, 1)), (1, 1, 1))
    close(node.get("translation", (0, 0, 0)), (0, 0, 0))
    close(node.get("rotation", (0, 0, 0, 1)), (0, 0, 0, 1))
positions = []
triangles = vertices = surfaces = face_surfaces = 0
for mesh in document["meshes"]:
    for primitive in mesh["primitives"]:
        points = accessor(primitive["attributes"]["POSITION"])
        positions.extend(points)
        vertices += len(points)
        surfaces += 1
        normals = accessor(primitive["attributes"]["NORMAL"])
        assert all(abs(math.sqrt(sum(v * v for v in n)) - 1) < 0.0001 for n in normals)
        indices = [row[0] for row in accessor(primitive["indices"])]
        triangles += len(indices) // 3
        for index in range(0, len(indices), 3):
            a, b, c = (Vector(points[indices[index + j]]) for j in range(3))
            cross = (b - a).cross(c - a)
            assert cross.length_squared > 1e-20
            average_normal = sum((Vector(normals[indices[index + j]]) for j in range(3)), Vector())
            assert cross.dot(average_normal) > 0
        material_name = document["materials"][primitive["material"]]["name"]
        if material_name == "sign_face":
            face_surfaces += 1
            assert mesh["name"] in face_contracts
            right_edge, bottom, top = face_contracts[mesh["name"]]
            uvs = accessor(primitive["attributes"]["TEXCOORD_0"])
            close([min(uv[i] for uv in uvs) for i in range(2)], (0, 0))
            close([max(uv[i] for uv in uvs) for i in range(2)], (1, 1))
            for point, uv, normal in zip(points, uvs, normals):
                close(uv, ((right_edge - point[0]) / 1.29, (top - point[1]) / 0.23))
                close(normal, (0, 0, -1))
                assert abs(point[2] + 0.184) < 0.00001
minimum = [min(point[i] for point in positions) for i in range(3)]
maximum = [max(point[i] for point in positions) for i in range(3)]
close(minimum, (-1.44, 0, -0.20))
close(maximum, (1.44, 3.92, 0.20))
assert triangles == sum(mesh["triangles"] for mesh in source_meshes)
assert surfaces == 9 and face_surfaces == 3
# Reopen was above; no transient authoring state participates in this export.
sys.argv = ["export.py", "--", str(SCRATCH)]
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
assert (SCRATCH / GLB.name).read_bytes() == raw
report = {
    "status": "PASS", "blender": bpy.app.version_string,
    "blender_build": bpy.app.build_hash.decode(), "gltf_exporter": "5.2.40",
    "source_meshes": source_meshes,
    "source_vertices": sum(mesh["vertices"] for mesh in source_meshes),
    "triangles": triangles, "glb_vertices": vertices, "meshes": 4, "surfaces": surfaces,
    "nonmanifold_edges": 0, "degenerate_faces": 0, "degenerate_glb_triangles": 0,
    "unit_source_and_export_normals": True, "glb_winding_agrees_with_normals": True,
    "godot_aabb": {"min": minimum, "max": maximum},
    "dimensions_m": [2.88, 3.92, 0.4], "pivot": [0, 0, 0], "ground_datum_m": 0,
    "dimension_tolerance_m": 0.001, "coordinate_tolerance_m": 0.00001,
    "artwork_interface": {
        "meshes": face_contracts, "slot": "sign_face", "slot_index": 0,
        "width_m": 1.29, "height_m": 0.23, "aspect_ratio": "129:23",
        "safe_copy_rectangle_m": [1.02, 0.19], "front_godot_z_m": -0.184,
        "uv_min": [0, 0], "uv_max": [1, 1],
        "glb_v_direction": "0 top / 1 bottom", "u_direction": "front-view left to right (-X)",
    },
    "glb_bytes": len(raw), "glb_sha256": hashlib.sha256(raw).hexdigest(),
    "fresh_reexport_byte_identical": True, "materials": document["materials"],
}
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
