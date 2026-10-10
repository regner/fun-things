"""Validate the saved tower, actual GLB accessors, and fresh byte-identical export."""
import hashlib
import json
import math
import struct
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_towers_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
GLB = ROOT / f"art/models/environment/{NID}/{NID}.glb"
EXPECTED_MIN = [-12, 0, -10.2]
EXPECTED_MAX = [12, 43.2, 9]
SECTIONS = {
    "D04Towers03_Lobby": ([-12, 0, -10.2], [12, 6, 9]),
    "D04Towers03_Facade": ([-11, 6, -8], [11, 38.4, 8]),
    "D04Towers03_Crown": ([-12, 38.4, -9], [12, 43.2, 9]),
}


def accessor_values(doc, binary, index):
    """Read actual packed or interleaved numeric GLB accessor values."""
    accessor = doc["accessors"][index]
    view = doc["bufferViews"][accessor["bufferView"]]
    formats = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}
    widths = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
    fmt = "<" + formats[accessor["componentType"]] * widths[accessor["type"]]
    stride = view.get("byteStride", struct.calcsize(fmt))
    offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, offset + i * stride)
            for i in range(accessor["count"])]


def bounds(points):
    """Measure an AABB independently from the exported coordinates."""
    low = [min(v[i] for v in points) for i in range(3)]
    high = [max(v[i] for v in points) for i in range(3)]
    return {"min": low, "max": high, "size": [b - a for a, b in zip(low, high)]}


def expect_bounds(actual, low, high):
    """Compare against literal metre-space contract values, not authoring formulas."""
    for measured, expected in zip(actual["min"] + actual["max"], low + high):
        assert abs(measured - expected) < .001, (measured, expected)


bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
assert bpy.app.version_string == "5.2.2 LTS"
collection = bpy.data.collections[f"export_{NID}"]
assert {o.name for o in collection.objects} == {"D04Towers03", *SECTIONS}
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
sections = {}
source_points = []
for obj in collection.objects:
    assert tuple(obj.location) == (0, 0, 0)
    assert tuple(obj.scale) == (1, 1, 1)
    assert tuple(obj.rotation_euler) == (0, 0, 0)
    if obj.type != "MESH":
        continue
    assert obj.parent.name == "D04Towers03"
    assert not obj.modifiers
    mesh = obj.data
    assert all(math.isfinite(value) for vert in mesh.vertices for value in vert.co)
    normal_error = max(abs(n.vector.length - 1) for n in mesh.corner_normals)
    assert normal_error < .0001
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    degenerate = sum(face.calc_area() <= 1e-10 for face in bm.faces)
    assert nonmanifold == 0, (obj.name, nonmanifold)
    assert degenerate == 0, (obj.name, degenerate)
    bm.free()
    points = [(v.co.x, v.co.z, -v.co.y) for v in mesh.vertices]
    measured = bounds(points)
    expect_bounds(measured, *SECTIONS[obj.name])
    source_points += points
    sections[obj.name] = {
        "vertices": len(mesh.vertices), "triangles": len(mesh.loop_triangles),
        "degenerate_faces": degenerate, "nonmanifold_edges": nonmanifold,
        "normal_length_max_error": normal_error, "aabb_godot": measured,
        "materials": [mat.name for mat in mesh.materials],
    }
expect_bounds(bounds(source_points), EXPECTED_MIN, EXPECTED_MAX)
# Check the defining silhouette independently of the authoring helper and AABB.
crown = bpy.data.objects["D04Towers03_Crown"].data
cyan_slot = next(i for i, mat in enumerate(crown.materials)
                 if mat.name == "glassward_crown_cyan")
rim_indices = {index for face in crown.polygons if face.material_index == cyan_slot
               for index in face.vertices}
rim_points = [crown.vertices[index].co for index in rim_indices]
# Literal rounded rectangle: outer corner centres (+/-6,+/-3), radius 6 m.
# A chamfer could share the same AABB; sampled support planes prove genuinely curved corners.
assert all(math.hypot(max(abs(v.x) - 6, 0), max(abs(v.y) - 3, 0)) <= 6.001
           for v in rim_points)
support_errors = []
for x_sign in (-1, 1):
    for y_sign in (-1, 1):
        for degrees in (15, 30, 45, 60, 75):
            dx, dy = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
            support = max(x_sign * v.x * dx + y_sign * v.y * dy for v in rim_points)
            expected = 6 * dx + 3 * dy + 6
            support_errors.append(abs(support - expected))
assert max(support_errors) < .001, support_errors
expect_bounds(bounds([(v.x, v.z, -v.y) for v in rim_points]),
              [-12, 42.3, -9], [12, 43.2, 9])
raw = GLB.read_bytes()
magic, version, length = struct.unpack_from("<4sII", raw)
assert magic == b"glTF" and version == 2 and length == len(raw)
json_length, kind = struct.unpack_from("<II", raw, 12)
assert kind == 0x4E4F534A
metadata = json.loads(raw[20:20 + json_length])
bin_length, kind = struct.unpack_from("<II", raw, 20 + json_length)
assert kind == 0x004E4942
binary = raw[28 + json_length:28 + json_length + bin_length]
assert not any(metadata.get(key) for key in ("images", "textures", "animations", "skins", "cameras"))
assert len(metadata["nodes"]) == 4
assert {node["name"] for node in metadata["nodes"]} == {"D04Towers03", *SECTIONS}
assert len(metadata["meshes"]) == 3
for node in metadata["nodes"]:
    assert node.get("scale", [1, 1, 1]) == [1, 1, 1]
    assert "rotation" not in node and "translation" not in node
all_positions = []
normal_errors = []
glb_triangles = 0
glb_degenerate = 0
surfaces = 0
for mesh in metadata["meshes"]:
    surfaces += len(mesh["primitives"])
    for primitive in mesh["primitives"]:
        positions = accessor_values(metadata, binary, primitive["attributes"]["POSITION"])
        normals = accessor_values(metadata, binary, primitive["attributes"]["NORMAL"])
        indices = [row[0] for row in accessor_values(metadata, binary, primitive["indices"])]
        assert all(math.isfinite(value) for row in positions + normals for value in row)
        normal_errors += [abs(Vector(value).length - 1) for value in normals]
        for offset in range(0, len(indices), 3):
            a, b, c = [Vector(positions[i]) for i in indices[offset:offset + 3]]
            glb_degenerate += (b - a).cross(c - a).length / 2 <= 1e-10
        glb_triangles += len(indices) // 3
        all_positions += positions
assert glb_degenerate == 0, glb_degenerate
assert max(normal_errors) < .0001
assert glb_triangles == sum(row["triangles"] for row in sections.values())
expect_bounds(bounds(all_positions), EXPECTED_MIN, EXPECTED_MAX)
assert len(metadata["materials"]) == 7
assert surfaces == 12
assert all(not mat.get("doubleSided", False) for mat in metadata["materials"])
assert all(mat.get("alphaMode", "OPAQUE") == "OPAQUE" for mat in metadata["materials"])

outdir = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv
          else Path(f"C:/tmp/ft/assets/{NID}/reexport"))
assert not outdir.resolve().is_relative_to(ROOT)
sys.argv = [sys.argv[0], "--", str(outdir)]
exec(compile((Path(__file__).parent / "export.py").read_text(), "export.py", "exec"))
fresh = (outdir / f"{NID}.glb").read_bytes()
assert fresh == raw, "Fresh reexport differs from the production GLB"
report = {
    "status": "PASS: source and GLB; engine/gameplay gates recorded separately",
    "blender": bpy.app.version_string, "build_hash": bpy.app.build_hash.decode(),
    "glTF_exporter": "5.2.40", "sections": sections,
    "source_vertices": sum(row["vertices"] for row in sections.values()),
    "source_triangles": sum(row["triangles"] for row in sections.values()),
    "source_degenerate_faces": 0, "source_nonmanifold_edges": 0,
    "glb_vertices_including_surface_splits": len(all_positions),
    "glb_triangles": glb_triangles, "glb_degenerate_triangles": glb_degenerate,
    "glb_max_normal_length_error": max(normal_errors),
    "mesh_count": 3, "surface_count": surfaces, "material_count": 7,
    "aabb_godot": bounds(all_positions), "envelope_tolerance_m": .001,
    "ground_contact_pivot": [0, 0, 0], "materials": metadata["materials"],
    "reexport_byte_identical": True, "glb_sha256": hashlib.sha256(raw).hexdigest(),
    "glb_bytes": len(raw),
    "crown_shape": {
        "four_circular_corners_verified": True,
        "outer_plan_width_depth_m": [24, 18], "outer_corner_radius_m": 6,
        "inner_corner_radius_m": 5, "corner_centres_abs_x_z_m": [6, 3],
        "support_plane_checks": 20, "max_support_error_m": max(support_errors),
        "rim_width_m": 1.0, "rim_bottom_top_m": [42.3, 43.2],
        "collision": "Crown above Y=38.4 is overhead visual-only; no rooftop gameplay",
    },
    "interfaces_godot": {
        "lobby_top_m": 6, "floor_pitch_m": 3.6, "floor_count": 9,
        "three_floor_group_pitch_m": 10.8, "crown_bottom_m": 38.4,
        "crown_seat_width_depth_m": [22, 16], "height_m": 43.2,
    },
}
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps(report, indent=2))
