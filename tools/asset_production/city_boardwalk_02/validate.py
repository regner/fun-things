"""Check saved bend topology and binary GLBs against independent interface expectations."""
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_boardwalk_02"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
# Literal nominal Godot bounds, independent of the author's geometry helpers.
# The 12 mm bound tolerance admits end half-seams and 4 mm timber roundovers.
EXPECTED = {
    "": (90, 32, [-1.8, -.24, -7.8], [6, 0, 0], [6, 0, -6]),
    "_45": (45, 16, [-1.8, -.24, -5.515432893],
            [3.030151519, 0, 0], [1.757359313, 0, -4.242640687]),
    "_22p5": (22.5, 8, [-1.8, -.24, -2.984930772],
              [2.119705963, 0, 0], [.456722805, 0, -2.296100594]),
}
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
reexport = Path(sys.argv[sys.argv.index("--") + 1])
report = {"asset": "city_boardwalk.02", "blender": bpy.app.version_string,
          "build_hash": bpy.app.build_hash.decode(), "exports": {}}


def accessor(doc, binary, index):
    """Read real binary components, following the accepted straight-member audit convention."""
    acc = doc["accessors"][index]
    view = doc["bufferViews"][acc["bufferView"]]
    fmt = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}[acc["componentType"]]
    count = {"VEC3": 3, "VEC2": 2, "SCALAR": 1}[acc["type"]]
    size = struct.calcsize("<" + fmt * count)
    start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    return [struct.unpack_from("<" + fmt * count, binary,
            start + i * view.get("byteStride", size)) for i in range(acc["count"])]


def bounds(points):
    """Measure extrema from coordinates rather than metadata."""
    return [[operation(p[i] for p in points) for i in range(3)]
            for operation in (min, max)]


for suffix, (angle, count, expected_min, expected_max, exit_point) in EXPECTED.items():
    name = ASSET + suffix
    root_name = "CityBoardwalk02" + suffix
    collection = bpy.data.collections["export_" + name]
    assert {o.name for o in collection.objects} == {root_name, root_name + "_Mesh"}
    for obj in collection.objects:
        assert obj.matrix_local == Matrix.Identity(4)
    mesh = bpy.data.objects[root_name + "_Mesh"].data
    assert not bpy.data.objects[root_name + "_Mesh"].modifiers
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
    source_points = [Vector((v.co.x, v.co.z, -v.co.y)) for v in mesh.vertices]
    source_bounds = bounds(source_points)
    assert all(abs(a - b) < .012 for a, b in zip(
        source_bounds[0] + source_bounds[1], expected_min + expected_max))
    assert abs(source_bounds[0][1] + .24) < .001 and abs(source_bounds[1][1]) < .001
    for polygon in mesh.polygons:
        if mesh.materials[polygon.material_index].name.startswith("boardwalk_timber_"):
            assert all(-.081 < mesh.vertices[i].co.z < .001 for i in polygon.vertices)
    path = ROOT / f"art/models/environment/{ASSET}/{name}.glb"
    raw = path.read_bytes()
    magic, version, total = struct.unpack_from("<4sII", raw)
    assert magic == b"glTF" and version == 2 and total == len(raw)
    length, kind = struct.unpack_from("<II", raw, 12)
    assert kind == 0x4E4F534A
    doc = json.loads(raw[20:20 + length])
    binary = raw[28 + length:]
    assert not any(doc.get(k) for k in ("skins", "animations", "images", "textures", "cameras"))
    assert len(doc["meshes"]) == 1 and len(doc["nodes"]) == 2
    assert all(not any(k in n for k in ("rotation", "scale", "translation")) for n in doc["nodes"])
    assert [m["name"] for m in doc["materials"]] == [
        "boardwalk_underdeck_slate", "boardwalk_timber_warm",
        "boardwalk_timber_light", "boardwalk_timber_muted"]
    assert all(not m.get("doubleSided", False) for m in doc["materials"])
    points, triangles, vertices = [], 0, 0
    for primitive in doc["meshes"][0]["primitives"]:
        positions = [Vector(v) for v in accessor(doc, binary, primitive["attributes"]["POSITION"])]
        normals = [Vector(v) for v in accessor(doc, binary, primitive["attributes"]["NORMAL"])]
        indices = [v[0] for v in accessor(doc, binary, primitive["indices"])]
        assert all(abs(n.length - 1) < 1e-4 for n in normals)
        for i in range(0, len(indices), 3):
            a, b, c = indices[i:i + 3]
            cross = (positions[b] - positions[a]).cross(positions[c] - positions[a])
            assert cross.length > 2e-10, (name, "degenerate exported triangle")
            assert cross.dot(normals[a] + normals[b] + normals[c]) > 0
        points.extend(positions)
        triangles += len(indices) // 3
        vertices += len(positions)
    assert triangles == len(mesh.loop_triangles)
    actual_bounds = bounds(points)
    assert all(abs(a - b) < 1e-5 for a, b in zip(
        actual_bounds[0] + actual_bounds[1], source_bounds[0] + source_bounds[1]))
    assert (reexport / path.name).read_bytes() == raw, "Fresh-process export differs"
    report["exports"][name] = {
        "angle_degrees": angle, "radial_timber_count": count,
        "source_vertices": len(mesh.vertices), "glb_vertices": vertices,
        "triangles": triangles, "mesh_count": 1,
        "surfaces": len(doc["meshes"][0]["primitives"]),
        "degenerate_faces": degenerate, "nonmanifold_edges": nonmanifold,
        "unit_normals": True, "consistent_winding": True, "applied_transforms": True,
        "source_godot_aabb": source_bounds, "actual_glb_aabb": actual_bounds,
        "nominal_godot_aabb": [expected_min, expected_max],
        "nominal_bound_tolerance_m": .012, "source_glb_tolerance_m": .00001,
        "pivot_entry_m": [0, 0, 0], "exit_centre_m": exit_point,
        "width_m": 3.6, "depth_m": .24, "centre_radius_m": 6,
        "deck_surface_datum_m": 0, "underside_datum_m": -.24,
        "fresh_reexport_byte_identical": True,
        "glb_sha256": hashlib.sha256(raw).hexdigest(), "glb_bytes": len(raw),
        "materials": doc["materials"],
    }
# Audit the SAVED gameplay collision independently: exact shared float32 vertices,
# two oppositely directed uses of every edge, no degenerate faces, outward winding.
# This distinguishes Jolt exact-edge ray precision from a genuinely cracked surface.
report["saved_collision"] = {}
for suffix, (angle, count, _low, _high, _exit) in EXPECTED.items():
    name = ASSET + suffix
    scene = (ROOT / f"scenes/prefabs/environment/{name}.tscn").read_text()
    payload = re.search(r"data = PackedVector3Array\(([^)]*)\)", scene).group(1)
    scalars = [struct.unpack("f", struct.pack("f", float(v)))[0] for v in payload.split(",")]
    points = [tuple(scalars[i:i + 3]) for i in range(0, len(scalars), 3)]
    assert len(points) == (count * 8 + 4) * 3
    edges, top_area = {}, 0
    for i in range(0, len(points), 3):
        a, b, c = points[i:i + 3]
        cross = (Vector(b) - Vector(a)).cross(Vector(c) - Vector(a))
        assert cross.length > 1e-8
        if all(abs(p[1]) < 1e-6 for p in (a, b, c)):
            assert cross.y < 0, "Godot clockwise top winding"
            top_area += cross.length / 2
        for u, v in ((a, b), (b, c), (c, a)):
            key = tuple(sorted((u, v)))
            edges.setdefault(key, []).append((u, v))
    assert all(len(uses) == 2 and uses[0] == tuple(reversed(uses[1]))
               for uses in edges.values()), "Saved collision is not watertight"
    nominal_area = {90: 33.929200659, 45: 16.964600329, 22.5: 8.482300165}[angle]
    assert abs(top_area - nominal_area) < .02
    assert min(p[1] for p in points) == struct.unpack("f", struct.pack("f", -.24))[0]
    assert max(p[1] for p in points) == 0
    report["saved_collision"][name] = {
        "triangles": len(points) // 3, "unique_vertices": len(set(points)),
        "nonmanifold_or_open_edges": 0, "degenerate_triangles": 0,
        "exact_float32_shared_edges": True, "top_area_m2": top_area,
        "datum_m": 0, "underside_m": -.24,
    }
report["status"] = "PASS source, binary export and saved watertight collision; engine checked separately"
EVIDENCE.mkdir(parents=True, exist_ok=True)
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps(report, indent=2))
