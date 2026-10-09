"""Validate source topology, literal approved bounds, GLB data and exact fresh reexport."""
import hashlib
import json
import math
from pathlib import Path
import runpy
import struct
import sys

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_poster_drum_02"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
GLB = ROOT / f"art/models/environment/{NID}/{NID}.glb"
SCRATCH = Path("C:/tmp/ft/assets") / NID / "reexport"


def close(actual, expected, tolerance=0.00001):
    """Compare independent literal expectations, not authoring formulas."""
    assert len(actual) == len(expected)
    assert all(abs(a - b) <= tolerance for a, b in zip(actual, expected)), (actual, expected)


def accessor(index):
    """Decode the exported float or unsigned integer accessor including byte stride."""
    entry = document["accessors"][index]
    view = document["bufferViews"][entry["bufferView"]]
    width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[entry["type"]]
    fmt = "<" + {5126: "f", 5125: "I", 5123: "H"}[entry["componentType"]] * width
    stride = view.get("byteStride", struct.calcsize(fmt))
    start = view.get("byteOffset", 0) + entry.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, start + i * stride) for i in range(entry["count"])]


def body_signature(obj):
    """Capture the full family-body geometry, shading, UVs and material contract."""
    mesh = obj.data
    return {
        "vertices": [tuple(v.co) for v in mesh.vertices],
        "faces": [tuple(p.vertices) for p in mesh.polygons],
        "smooth": [p.use_smooth for p in mesh.polygons],
        "material_indices": [p.material_index for p in mesh.polygons],
        "normals": [tuple(n.vector) for n in mesh.corner_normals],
        "uv": [tuple(uv.uv) for uv in mesh.uv_layers.active.data],
        "materials": [(m.name, tuple(m.diffuse_color),
                       m.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value,
                       m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value)
                      for m in mesh.materials],
    }


family_source = ROOT / (
    "art/source/models/environment/d06_poster_drum_01/d06_poster_drum_01.blend"
)
bpy.ops.wm.open_mainfile(filepath=str(family_source))
family_body = body_signature(bpy.data.objects["D06PosterDrum01_Body"])
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
assert bpy.app.version_string == "5.2.2 LTS"
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
collection = bpy.data.collections[f"export_{NID}"]
assert {obj.name for obj in collection.objects} == {
    "D06PosterDrum02", "D06PosterDrum02_Body", "D06PosterDrum02_Cap"
}
source_meshes = []
all_coordinates = []
for obj in collection.objects:
    close(obj.location, (0, 0, 0))
    close(obj.rotation_euler, (0, 0, 0))
    close(obj.scale, (1, 1, 1))
    if obj.type != "MESH":
        continue
    assert not obj.modifiers
    mesh = obj.data
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    degenerate = sum(face.calc_area() <= 1e-10 for face in bm.faces)
    bm.free()
    assert nonmanifold == 0 and degenerate == 0
    assert all(abs(normal.vector.length - 1) < 0.0001 for normal in mesh.corner_normals)
    assert all(math.isfinite(value) for vertex in mesh.vertices for value in vertex.co)
    all_coordinates.extend(tuple(vertex.co) for vertex in mesh.vertices)
    source_meshes.append({
        "name": obj.name, "vertices": len(mesh.vertices), "triangles": len(mesh.loop_triangles),
        "nonmanifold_edges": nonmanifold, "degenerate_faces": degenerate,
        "unit_corner_normals": True, "materials": [mat.name for mat in mesh.materials],
    })
minimum = [min(vertex[i] for vertex in all_coordinates) for i in range(3)]
maximum = [max(vertex[i] for vertex in all_coordinates) for i in range(3)]
close(minimum, (-0.45, -0.45, 0))
close(maximum, (0.45, 0.45, 1.53))
cap = bpy.data.objects["D06PosterDrum02_Cap"]
assert abs(min(v.co.z for v in cap.data.vertices) - 1.35) < 0.00001
body = bpy.data.objects["D06PosterDrum02_Body"]
assert body_signature(body) == family_body, "The appended family body must remain unchanged"
seat_vertices = [v.co for v in cap.data.vertices if abs(v.co.z - 1.35) < 0.00001]
assert len(seat_vertices) == 64
assert all(abs(math.hypot(v.x, v.y) - 0.42) < 0.00001 for v in seat_vertices)
assert [m.name for m in cap.data.materials] == ["drum_frame_petrol", "cap_inset_coral"]
assert sum(p.material_index == 1 for p in cap.data.polygons) == 64
wrap_faces = [p for p in body.data.polygons if p.material_index == 1]
assert len(wrap_faces) == 64
uvs = [tuple(body.data.uv_layers.active.data[i].uv) for p in wrap_faces for i in p.loop_indices]
close([min(uv[i] for uv in uvs) for i in range(2)], (0, 0))
close([max(uv[i] for uv in uvs) for i in range(2)], (1, 1))
wrap_z = [body.data.vertices[i].co.z for p in wrap_faces for i in p.vertices]
close((min(wrap_z), max(wrap_z)), (0.24, 1.28))
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
assert len(document["nodes"]) == 3 and len(document["meshes"]) == 2
assert {m["name"] for m in document["materials"]} == {
    "drum_frame_petrol", "poster_wrap", "cap_inset_coral"
}
assert all(not any(m.get("emissiveFactor", [0, 0, 0])) for m in document["materials"])
assert all(not mat.get("doubleSided", False) for mat in document["materials"])
assert all(mat.get("alphaMode", "OPAQUE") == "OPAQUE" for mat in document["materials"])
for node in document["nodes"]:
    close(node.get("scale", (1, 1, 1)), (1, 1, 1))
    close(node.get("translation", (0, 0, 0)), (0, 0, 0))
    close(node.get("rotation", (0, 0, 0, 1)), (0, 0, 0, 1))
positions = []
triangles = 0
vertices = 0
surfaces = 0
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
            a, b, c = (points[indices[index + j]] for j in range(3))
            ab = [b[j] - a[j] for j in range(3)]
            ac = [c[j] - a[j] for j in range(3)]
            cross = (ab[1] * ac[2] - ab[2] * ac[1],
                     ab[2] * ac[0] - ab[0] * ac[2],
                     ab[0] * ac[1] - ab[1] * ac[0])
            assert sum(v * v for v in cross) > 1e-20
        material_name = document["materials"][primitive["material"]]["name"]
        if material_name == "poster_wrap":
            coordinates = accessor(primitive["attributes"]["TEXCOORD_0"])
            close([min(uv[i] for uv in coordinates) for i in range(2)], (0, 0))
            close([max(uv[i] for uv in coordinates) for i in range(2)], (1, 1))
            close([min(p[1] for p in points), max(p[1] for p in points)], (0.24, 1.28))
glb_minimum = [min(point[i] for point in positions) for i in range(3)]
glb_maximum = [max(point[i] for point in positions) for i in range(3)]
close(glb_minimum, (-0.45, 0, -0.45))
close(glb_maximum, (0.45, 1.53, 0.45))
assert triangles == sum(mesh["triangles"] for mesh in source_meshes)
assert surfaces == 4
# Export from the freshly reopened .blend, never from transient authoring state.
sys.argv = ["export.py", "--", str(SCRATCH)]
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
assert (SCRATCH / GLB.name).read_bytes() == raw
report = {
    "status": "PASS", "blender": bpy.app.version_string,
    "blender_build": bpy.app.build_hash.decode(), "gltf_exporter": "5.2.40",
    "source_meshes": source_meshes,
    "source_vertices": sum(mesh["vertices"] for mesh in source_meshes),
    "triangles": triangles, "glb_vertices": vertices, "meshes": 2, "surfaces": surfaces,
    "nonmanifold_edges": 0, "degenerate_faces": 0, "degenerate_glb_triangles": 0,
    "unit_source_and_export_normals": True,
    "godot_aabb": {"min": glb_minimum, "max": glb_maximum},
    "dimensions_m": [0.9, 1.53, 0.9], "pivot": [0, 0, 0], "ground_datum_m": 0,
    "dimension_tolerance_m": 0.001, "coordinate_tolerance_m": 0.00001,
    "wrap_uv": {"min": [0, 0], "max": [1, 1], "seam": "Godot +Z", "front_u": 0.5,
                "radius_m": 0.397, "bottom_m": 0.24, "top_m": 1.28,
                "glb_v_direction": "0 top / 1 bottom (glTF texture convention)"},
    "cap_seating_height_m": 1.35, "cap_seating_radius_m": 0.42,
    "unchanged_appended_family_body": True,
    "family_source": family_source.relative_to(ROOT).as_posix(),
    "family_source_sha256": hashlib.sha256(family_source.read_bytes()).hexdigest(),
    "glb_bytes": len(raw), "glb_sha256": hashlib.sha256(raw).hexdigest(),
    "fresh_reexport_byte_identical": True, "materials": document["materials"],
}
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
