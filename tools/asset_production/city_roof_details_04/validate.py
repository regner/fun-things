"""Audit saved source and binary GLB geometry against independent provisional dimensions."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_roof_details_04"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
collection = bpy.data.collections["export_" + ASSET]
assert {o.name for o in collection.objects} == {"CityRoofDetails04", "CityRoofDetails04_Mesh"}
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
for obj in collection.objects:
    assert obj.matrix_local == Matrix.Identity(4)
obj = bpy.data.objects["CityRoofDetails04_Mesh"]
assert not obj.modifiers
mesh = obj.data
mesh.calc_loop_triangles()
assert all(math.isfinite(v) for vertex in mesh.vertices for v in vertex.co)
assert all(abs(n.vector.length - 1) < 1e-4 for n in mesh.corner_normals)
bm = bmesh.new()
bm.from_mesh(mesh)
nonmanifold = sum(not e.is_manifold for e in bm.edges)
degenerate = sum(p.area <= 1e-10 for p in mesh.polygons)
assert nonmanifold == 0 and degenerate == 0
assert all(e.is_contiguous for e in bm.edges)
assert bm.calc_volume(signed=True) > 0
bm.free()
low = [min(v.co[i] for v in mesh.vertices) for i in range(3)]
high = [max(v.co[i] for v in mesh.vertices) for i in range(3)]
assert all(abs(a - b) < .001 for a, b in zip(low + high,
    [-.65, -.75, -.433012702, .65, .75, 1.96]))
# Independent ray expectations prove a sloped apron and a visibly recessed, closed flue.
from mathutils.bvhtree import BVHTree
bm = bmesh.new()
bm.from_mesh(mesh)
tree = BVHTree.FromBMesh(bm)
ray_heights = []
for y, expected in [(-.65, -.340277675), (.65, .410277675)]:
    hit, normal, index, distance = tree.ray_cast(Vector((.56, y, 3)), Vector((0, 0, -1)))
    assert hit is not None and abs(hit.z - expected) < .00001
    ray_heights.append(hit.z)
hit, normal, index, distance = tree.ray_cast(Vector((0, 0, 3)), Vector((0, 0, -1)))
assert hit is not None and abs(hit.z - 1.416) < .00001
flue_floor_height = hit.z
bm.free()
path = ROOT / f"art/models/environment/{ASSET}/{ASSET}.glb"
raw = path.read_bytes()
magic, version, total = struct.unpack_from("<4sII", raw)
assert magic == b"glTF" and version == 2 and total == len(raw)
length, kind = struct.unpack_from("<II", raw, 12)
assert kind == 0x4E4F534A
metadata = json.loads(raw[20:20 + length])
binary = raw[28 + length:]


def accessor(index):
    """Read actual binary components rather than trusting accessor min/max metadata."""
    acc = metadata["accessors"][index]
    view = metadata["bufferViews"][acc["bufferView"]]
    fmt = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}[acc["componentType"]]
    count = {"VEC3": 3, "VEC2": 2, "SCALAR": 1}[acc["type"]]
    size = struct.calcsize("<" + fmt * count)
    start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    return [struct.unpack_from("<" + fmt * count, binary,
            start + i * view.get("byteStride", size)) for i in range(acc["count"])]


assert not any(metadata.get(k) for k in ("skins", "animations", "images", "textures", "cameras"))
assert len(metadata["meshes"]) == 1 and len(metadata["nodes"]) == 2
assert all("rotation" not in n and "scale" not in n and "translation" not in n
           for n in metadata["nodes"])
expected_materials = {"chimney_dark_petrol", "chimney_folded_metal", "chimney_shadow"}
assert {m["name"] for m in metadata["materials"]} == expected_materials
assert all(not m.get("doubleSided", False) for m in metadata["materials"])
points, triangles, vertices = [], 0, 0
for primitive in metadata["meshes"][0]["primitives"]:
    positions = [Vector(v) for v in accessor(primitive["attributes"]["POSITION"])]
    normals = [Vector(v) for v in accessor(primitive["attributes"]["NORMAL"])]
    indices = [v[0] for v in accessor(primitive["indices"])]
    assert all(abs(n.length - 1) < 1e-4 for n in normals)
    for index in range(0, len(indices), 3):
        a, b, c = indices[index:index + 3]
        cross = (positions[b] - positions[a]).cross(positions[c] - positions[a])
        assert cross.length > 2e-10
        assert cross.dot(normals[a] + normals[b] + normals[c]) > 0
    points.extend(positions)
    triangles += len(indices) // 3
    vertices += len(positions)
assert triangles == len(mesh.loop_triangles)
actual_low = [min(p[i] for p in points) for i in range(3)]
actual_high = [max(p[i] for p in points) for i in range(3)]
assert all(abs(a - b) < .001 for a, b in zip(actual_low + actual_high,
    [-.65, -.433012702, -.75, .65, 1.96, .75]))
reexport = Path(sys.argv[sys.argv.index("--") + 1])
assert reexport.read_bytes() == raw, "Fresh-process export differs"
report = {
    "asset": "city_roof_details.04", "blender": bpy.app.version_string,
    "build_hash": bpy.app.build_hash.decode(), "vertices": len(mesh.vertices),
    "triangles": triangles, "mesh_count": 1,
    "surfaces": len(metadata["meshes"][0]["primitives"]), "glb_vertices": vertices,
    "degenerate_faces": degenerate, "nonmanifold_edges": nonmanifold,
    "unit_normals": True, "consistent_winding": True, "applied_transforms": True,
    "source_aabb": {"min": low, "max": high},
    "godot_aabb": {"min": actual_low, "max": actual_high},
    "dimensions_godot_m": [1.30, 2.393012702, 1.50], "dimension_tolerance_m": .001,
    "pivot": [0, 0, 0], "datum": "30-degree roof plane centre; Godot -Z uphill; not lowest point",
    "fresh_reexport_byte_identical": True,
    "roof_pitch_deg": 30, "apron_ray_heights_m": ray_heights,
    "flue_floor_height_m": flue_floor_height, "flue_recess_depth_m": 1.96 - flue_floor_height,
    "glb_sha256": hashlib.sha256(raw).hexdigest(), "glb_bytes": len(raw),
    "materials": metadata["materials"], "status": "PASS source and export",
}
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps(report, indent=2))
