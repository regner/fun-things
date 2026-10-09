"""Validate saved source, actual GLB topology/normals, and byte-identical reexport."""
import hashlib
import json
import math
import struct
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_entertainment_hall_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
GLB = ROOT / f"art/models/environment/{NID}/{NID}.glb"
EXPECTED_MIN = [-5.0, 3.6, -11.8]
EXPECTED_MAX = [5.0, 4.05, -8.85]


def accessor_values(doc, binary, index):
    """Read interleaved or packed numeric GLB accessors for independent validation."""
    accessor = doc["accessors"][index]
    view = doc["bufferViews"][accessor["bufferView"]]
    formats = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}
    widths = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
    fmt = "<" + formats[accessor["componentType"]] * widths[accessor["type"]]
    stride = view.get("byteStride", struct.calcsize(fmt))
    offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, offset + i * stride)
            for i in range(accessor["count"])]


bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
assert bpy.app.version_string == "5.2.2 LTS"
collection = bpy.data.collections[f"export_{NID}"]
assert {o.name for o in collection.objects} == {
    "D06EntertainmentHall03", "D06EntertainmentHall03_Mesh"}
obj = bpy.data.objects["D06EntertainmentHall03_Mesh"]
mesh = obj.data
for member in collection.objects:
    assert tuple(member.location) == (0, 0, 0)
    assert tuple(member.scale) == (1, 1, 1)
    assert tuple(member.rotation_euler) == (0, 0, 0)
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
assert not obj.modifiers
assert all(math.isfinite(v) for vert in mesh.vertices for v in vert.co)
source_normal_error = max(abs(n.vector.length - 1) for n in mesh.corner_normals)
assert source_normal_error < .0001
mesh.calc_loop_triangles()
bm = bmesh.new()
bm.from_mesh(mesh)
nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
degenerate = sum(face.calc_area() <= 1e-10 for face in bm.faces)
assert nonmanifold == 0, nonmanifold
assert degenerate == 0, degenerate
assert bm.calc_volume(signed=True) > 0, "Outward-facing solid winding"
# The closed slab is one connected component, including its continuous diffuser band.
for selected_slot in (None, 1):
    remaining = {face for face in bm.faces if selected_slot is None or face.material_index == selected_slot}
    stack = [remaining.pop()]
    while stack:
        face = stack.pop()
        neighbours = {other for edge in face.edges for other in edge.link_faces} & remaining
        remaining.difference_update(neighbours)
        stack.extend(neighbours)
    assert not remaining, "Disconnected canopy or diffuser"
bm.free()
coords = [(v.co.x, v.co.z, -v.co.y) for v in mesh.vertices]
lo = [min(v[i] for v in coords) for i in range(3)]
hi = [max(v[i] for v in coords) for i in range(3)]
for actual, expected in zip(lo + hi, EXPECTED_MIN + EXPECTED_MAX):
    assert abs(actual - expected) < .001, (actual, expected)
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
assert len(metadata["nodes"]) == 2
assert len(metadata["meshes"]) == 1
for node in metadata["nodes"]:
    assert node.get("scale", [1, 1, 1]) == [1, 1, 1]
    assert "rotation" not in node and "translation" not in node
all_positions = []
normal_errors = []
glb_triangles = 0
glb_degenerate = 0
for primitive in metadata["meshes"][0]["primitives"]:
    positions = accessor_values(metadata, binary, primitive["attributes"]["POSITION"])
    normals = accessor_values(metadata, binary, primitive["attributes"]["NORMAL"])
    indices = [row[0] for row in accessor_values(metadata, binary, primitive["indices"])]
    normal_errors += [abs(Vector(value).length - 1) for value in normals]
    for offset in range(0, len(indices), 3):
        a, b, c = [Vector(positions[i]) for i in indices[offset:offset + 3]]
        glb_degenerate += (b - a).cross(c - a).length / 2 <= 1e-10
    glb_triangles += len(indices) // 3
    all_positions += positions
assert glb_degenerate == 0, glb_degenerate
assert max(normal_errors) < .0001
assert glb_triangles == len(mesh.loop_triangles)
glb_lo = [min(v[i] for v in all_positions) for i in range(3)]
glb_hi = [max(v[i] for v in all_positions) for i in range(3)]
for actual, expected in zip(glb_lo + glb_hi, EXPECTED_MIN + EXPECTED_MAX):
    assert abs(actual - expected) < .001
assert len(metadata["materials"]) == 2
assert all(not mat.get("doubleSided", False) for mat in metadata["materials"])
assert all(mat.get("alphaMode", "OPAQUE") == "OPAQUE" for mat in metadata["materials"])

# Export from the freshly opened committed source into an external scratch directory.
outdir = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv
          else Path(f"C:/tmp/ft/assets/{NID}/reexport"))
assert not outdir.resolve().is_relative_to(ROOT)
sys.argv = [sys.argv[0], "--", str(outdir)]
exec(compile((Path(__file__).parent / "export.py").read_text(), "export.py", "exec"))
fresh = (outdir / f"{NID}.glb").read_bytes()
assert fresh == raw, "Fresh reexport differs from committed GLB"

# Real preceding family geometry tests centered-camera visibility without approximating roofs.
family_bvhs = []
family_hashes = {}
for suffix in ("01", "02"):
    family_id = f"d06_entertainment_hall_{suffix}"
    source = ROOT / f"art/source/models/environment/{family_id}/{family_id}.blend"
    family_hashes[family_id] = hashlib.sha256(source.read_bytes()).hexdigest()
    with bpy.data.libraries.load(str(source), link=False) as (available, requested):
        requested.objects = [f"D06EntertainmentHall{suffix}_Mesh"]
    context = requested.objects[0].data
    family_bvhs.append(BVHTree.FromPolygons([v.co for v in context.vertices],
                                           [p.vertices for p in context.polygons]))
canopy_bvh = BVHTree.FromPolygons([v.co for v in mesh.vertices], [p.vertices for p in mesh.polygons])
camera = Vector((0, 0, 47))
visibility_samples = []
for x, y in ((-3.8, 11.5), (0, 11.5), (3.8, 11.5)):
    direction = (Vector((x, y, 4.05)) - camera).normalized()
    hit = canopy_bvh.ray_cast(camera, direction)
    assert hit[0] is not None
    assert mesh.polygons[hit[2]].material_index == 1, "Camera must see cyan shoulder"
    for other in family_bvhs:
        context_hit = other.ray_cast(camera, direction)
        assert context_hit[0] is None or hit[3] < context_hit[3], "Family hides canopy accent"
    visibility_samples.append({"blender_xy": [x, y], "cyan_visible": True})
assert canopy_bvh.ray_cast(camera, Vector((0, 0, -1)))[0] is None
# A horizontal ray at the actual .01 facade height confirms the slab embeds at the wall.
contact = canopy_bvh.ray_cast(Vector((0, 8.0, 3.8)), Vector((0, 1, 0)))
assert contact[0] is not None and abs(contact[0].y - 8.85) < .001
report = {
    "status": "PASS: source and GLB; engine/gameplay gates recorded separately",
    "blender": bpy.app.version_string,
    "build_hash": bpy.app.build_hash.decode(),
    "glTF_exporter": "5.2.40",
    "source_vertices": len(mesh.vertices),
    "connected_canopy_and_diffuser": True,
    "family_source_sha256": family_hashes,
    "camera_primary_ray_samples": visibility_samples,
    "roof_centre_unobstructed": True,
    "source_triangles": len(mesh.loop_triangles),
    "source_degenerate_faces": degenerate,
    "source_nonmanifold_edges": nonmanifold,
    "source_max_normal_length_error": source_normal_error,
    "glb_vertices_including_surface_splits": len(all_positions),
    "glb_triangles": glb_triangles,
    "glb_degenerate_triangles": glb_degenerate,
    "glb_max_normal_length_error": max(normal_errors),
    "mesh_count": 1,
    "surface_count": 2,
    "aabb_godot": {"min": glb_lo, "max": glb_hi, "size": [b - a for a, b in zip(glb_lo, glb_hi)]},
    "expected_aabb_godot": {"min": EXPECTED_MIN, "max": EXPECTED_MAX},
    "envelope_tolerance_m": .001,
    "hall_ground_datum_pivot": [0, 0, 0],
    "materials": metadata["materials"],
    "reexport_byte_identical": True,
    "glb_sha256": hashlib.sha256(raw).hexdigest(),
    "glb_bytes": len(raw),
    "interfaces_godot": {"wall_contact_m": [0, 3.6, -9], "rear_contact_z_m": -contact[0].y, "ring_vertical_gap_m": 2.7, "projection_from_contact_m": 2.8},
}
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps(report, indent=2))
