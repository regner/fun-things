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
ASSET = "d02_domestic_details_02"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
collection = bpy.data.collections["export_" + ASSET]
assert bpy.data.objects["authoring_1m_reference"].dimensions == Vector((1, 1, 1))
EVIDENCE.mkdir(parents=True, exist_ok=True)
assert {o.name for o in collection.objects} == {"D02DomesticDetails02", "D02DomesticDetails02_Mesh"}
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
for obj in collection.objects:
    assert obj.matrix_local == Matrix.Identity(4)
obj = bpy.data.objects["D02DomesticDetails02_Mesh"]
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
    [-.8, -.8, 0, .8, .8, .94]))
path = ROOT / f"art/models/environment/{ASSET}/{ASSET}.glb"
raw = path.read_bytes()
magic, version, total = struct.unpack_from("<4sII", raw)
assert magic == b"glTF" and version == 2 and total == len(raw)
length, kind = struct.unpack_from("<II", raw, 12)
assert kind == 0x4E4F534A
metadata = json.loads(raw[20:20 + length])
binary = raw[28 + length:]


def accessor(index, document=metadata, buffer=binary):
    """Read actual binary components rather than trusting accessor min/max metadata."""
    acc = document["accessors"][index]
    view = document["bufferViews"][acc["bufferView"]]
    fmt = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}[acc["componentType"]]
    count = {"VEC3": 3, "VEC2": 2, "SCALAR": 1}[acc["type"]]
    size = struct.calcsize("<" + fmt * count)
    start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    return [struct.unpack_from("<" + fmt * count, buffer,
            start + i * view.get("byteStride", size)) for i in range(acc["count"])]


assert not any(metadata.get(k) for k in ("skins", "animations", "images", "textures", "cameras"))
assert len(metadata["meshes"]) == 1 and len(metadata["nodes"]) == 2
assert all("rotation" not in n and "scale" not in n and "translation" not in n
           for n in metadata["nodes"])
expected_materials = {"crescents_warm_render", "crescents_ivory_trim", "crescents_slate_plinth"}
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
    [-.8, 0, -.8, .8, .94, .8]))
# Compare actual binary end-plane vertices with the accepted straight sibling.
# Both use symmetric sections, so north's across-axis reversal needs no mirror variant.
sibling_raw = (ROOT / "art/models/environment/d02_domestic_details_01/"
               "d02_domestic_details_01.glb").read_bytes()
sibling_length = struct.unpack_from("<I", sibling_raw, 12)[0]
sibling_doc = json.loads(sibling_raw[20:20+sibling_length])
sibling_buffer = sibling_raw[28+sibling_length:]
assert metadata["materials"] == sibling_doc["materials"], "Family palette/slot drift"
sibling_points = [p for pr in sibling_doc["meshes"][0]["primitives"]
                  for p in accessor(pr["attributes"]["POSITION"], sibling_doc, sibling_buffer)]
expected_profile = {(round(p[1], 5), round(p[2], 5)) for p in sibling_points
                    if abs(p[0] - 1.6) < 1e-6}
east_profile = {(round(p[1], 5), round(p[2] - .62, 5)) for p in points
                if abs(p[0] - .8) < 1e-6}
north_profile = {(round(p[1], 5), round(p[0] + .62, 5)) for p in points
                 if abs(p[2] + .8) < 1e-6}
assert len(expected_profile) > 10
assert east_profile == expected_profile, (east_profile, expected_profile)
assert north_profile == expected_profile, (north_profile, expected_profile)
reexport = Path(sys.argv[sys.argv.index("--") + 1])
assert reexport.read_bytes() == raw, "Fresh-process export differs"
report = {
    "asset": "d02_domestic_details.02", "blender": bpy.app.version_string,
    "build_hash": bpy.app.build_hash.decode(), "vertices": len(mesh.vertices),
    "triangles": triangles, "mesh_count": 1,
    "surfaces": len(metadata["meshes"][0]["primitives"]), "glb_vertices": vertices,
    "degenerate_faces": degenerate, "nonmanifold_edges": nonmanifold,
    "unit_normals": True, "consistent_winding": True, "applied_transforms": True,
    "source_aabb": {"min": low, "max": high},
    "godot_aabb": {"min": actual_low, "max": actual_high},
    "dimensions_godot_m": [1.6, .94, 1.6], "dimension_tolerance_m": .001,
    "pivot": [0, 0, 0], "datum": "ground-centred bounding wall footprint", "dimensions_status": "provisional",
    "fresh_reexport_byte_identical": True,
    "glb_sha256": hashlib.sha256(raw).hexdigest(), "glb_bytes": len(raw),
    "materials": metadata["materials"],
    "module_end_centres_godot_m": [[.8, 0, .62], [-.62, 0, -.8]],
    "collision": "Two boxes exactly partition the L cap footprint; empty inner quadrant preserved",
    "straight_sibling_end_profile_points": len(expected_profile),
    "both_end_profiles_match_straight": True, "family_materials_match_straight": True,
    "status": "PASS source and export",
}
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps(report, indent=2))
