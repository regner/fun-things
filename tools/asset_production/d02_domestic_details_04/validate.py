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
ASSET = "d02_domestic_details_04"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
collection = bpy.data.collections["export_" + ASSET]
assert bpy.data.objects["authoring_1m_reference"].dimensions == Vector((1, 1, 1))
EVIDENCE.mkdir(parents=True, exist_ok=True)
assert {o.name for o in collection.objects} == {"D02DomesticDetails04", "D02DomesticDetails04_Mesh"}
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
for obj in collection.objects:
    assert obj.matrix_local == Matrix.Identity(4)
obj = bpy.data.objects["D02DomesticDetails04_Mesh"]
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
print("SOURCE_BOUNDS", low, high, flush=True)
assert all(abs(a - b) < .001 for a, b in zip(low + high,
    [-1, -.575, 2.6, 1, .575, 3.25]))
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
expected_materials = {"crescents_sage_enamel", "crescents_ivory_trim", "crescents_slate_plinth"}
assert {m["name"] for m in metadata["materials"]} == expected_materials
assert all(not m.get("doubleSided", False) for m in metadata["materials"])
# The delivered mailbox owns the matching metal/trim palette; compare actual export values.
sibling = ROOT / "art/models/environment/d02_domestic_details_03/d02_domestic_details_03.glb"
sibling_raw = sibling.read_bytes()
sibling_length = struct.unpack_from("<I", sibling_raw, 12)[0]
sibling_metadata = json.loads(sibling_raw[20:20 + sibling_length])
sibling_materials = {m["name"]: m for m in sibling_metadata["materials"]}
assert all(m == sibling_materials[m["name"]] for m in metadata["materials"])
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
    [-1, 2.6, -.575, 1, 3.25, .575]))
reexport = Path(sys.argv[sys.argv.index("--") + 1])
assert reexport.read_bytes() == raw, "Fresh-process export differs"
report = {
    "asset": "d02_domestic_details.04", "blender": bpy.app.version_string,
    "build_hash": bpy.app.build_hash.decode(), "vertices": len(mesh.vertices),
    "triangles": triangles, "mesh_count": 1,
    "surfaces": len(metadata["meshes"][0]["primitives"]), "glb_vertices": vertices,
    "degenerate_faces": degenerate, "nonmanifold_edges": nonmanifold,
    "unit_normals": True, "consistent_winding": True, "applied_transforms": True,
    "source_aabb": {"min": low, "max": high},
    "godot_aabb": {"min": actual_low, "max": actual_high},
    "dimensions_godot_m": [2, .65, 1.15], "dimension_tolerance_m": .001,
    "pivot": [0, 0, 0], "datum": "ground-projected footprint centre; wall Z=+.575; mesh minimum Y=2.6", "dimensions_status": "provisional",
    "fresh_reexport_byte_identical": True,
    "glb_sha256": hashlib.sha256(raw).hexdigest(), "glb_bytes": len(raw),
    "materials": metadata["materials"],
    "materials_match_mailbox_sibling": True,
    "collision_boxes": [],
    "overhead_only": True, "minimum_ground_clearance_m": 2.6,
    "status": "PASS source and export",
}
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps(report, indent=2))
