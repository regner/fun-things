"""Independently audit the saved source, actual GLB buffers and serialized collision ribbons."""
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
ASSET = "city_boardwalk_03"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
# Literal independent nominal bounds, not imported from the geometry recipe.
EXPECTED = {
    "": ([0, -.24, -3], [.1, 0, 3], 0),
    "_terminal": ([0, -.24, -1.9], [.1, 0, 1.9], 0),
    "_outer_90": ([-1.9, -.24, -7.9], [6, 0, 0], 32),
    "_inner_90": ([1.8, -.24, -4.2], [6, 0, 0], 32),
    "_outer_45": ([-1.9, -.24, -5.586143571], [.484567107, 0, 0], 16),
    "_inner_45": ([1.8, -.24, -2.969848481], [3.100862197, 0, 0], 16),
    "_outer_22p5": ([-1.9, -.24, -3.023199116], [-1.206260354, 0, 0], 8),
    "_inner_22p5": ([1.8, -.24, -1.607270416], [2.212093917, 0, 0], 8),
}
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
reexport = Path(sys.argv[sys.argv.index("--") + 1])
report = {"asset": "city_boardwalk.03", "blender": bpy.app.version_string,
          "build_hash": bpy.app.build_hash.decode(), "exports": {}, "saved_collision": {}}


def accessor(doc, binary, index):
    """Decode actual strided binary data using the accepted family audit convention."""
    acc = doc["accessors"][index]
    view = doc["bufferViews"][acc["bufferView"]]
    fmt = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}[acc["componentType"]]
    count = {"VEC3": 3, "VEC2": 2, "SCALAR": 1}[acc["type"]]
    size = struct.calcsize("<" + fmt * count)
    start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    return [struct.unpack_from("<" + fmt * count, binary,
            start + i * view.get("byteStride", size)) for i in range(acc["count"])]


def bounds(points):
    """Measure extrema directly from geometry coordinates."""
    return [[operation(p[i] for p in points) for i in range(3)]
            for operation in (min, max)]


for suffix, (low, high, stations) in EXPECTED.items():
    name, root_name = ASSET + suffix, "CityBoardwalk03" + suffix
    collection = bpy.data.collections["export_" + name]
    assert {o.name for o in collection.objects} == {root_name, root_name + "_Mesh"}
    assert all(o.matrix_local == Matrix.Identity(4) for o in collection.objects)
    obj = bpy.data.objects[root_name + "_Mesh"]
    assert not obj.modifiers
    mesh = obj.data
    mesh.calc_loop_triangles()
    assert all(math.isfinite(v) for vertex in mesh.vertices for v in vertex.co)
    assert all(abs(n.vector.length - 1) < 1e-4 for n in mesh.corner_normals)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    assert all(e.is_manifold and e.is_contiguous for e in bm.edges)
    assert bm.calc_volume(signed=True) > 0
    bm.free()
    assert all(p.area > 1e-10 for p in mesh.polygons)
    source_bounds = bounds([Vector((v.co.x, v.co.z, -v.co.y)) for v in mesh.vertices])
    assert all(abs(a - b) < .004 for a, b in zip(sum(source_bounds, []), low + high)), name
    assert abs(source_bounds[0][1] + .24) < .001 and abs(source_bounds[1][1]) < .001
    path = ROOT / f"art/models/environment/{ASSET}/{name}.glb"
    raw = path.read_bytes()
    assert struct.unpack_from("<4sII", raw) == (b"glTF", 2, len(raw))
    length, kind = struct.unpack_from("<II", raw, 12)
    assert kind == 0x4E4F534A
    doc, binary = json.loads(raw[20:20 + length]), raw[28 + length:]
    assert not any(doc.get(k) for k in ("skins", "animations", "images", "textures", "cameras"))
    assert len(doc["meshes"]) == 1 and len(doc["nodes"]) == 2
    assert all(not any(k in n for k in ("rotation", "scale", "translation")) for n in doc["nodes"])
    assert [m["name"] for m in doc["materials"]] == ["boardwalk_fascia_slate", "boardwalk_edge_trim"]
    assert all(not m.get("doubleSided", False) for m in doc["materials"])
    points, triangles, vertices = [], 0, 0
    exported_edges = {}
    for primitive in doc["meshes"][0]["primitives"]:
        positions = [Vector(v) for v in accessor(doc, binary, primitive["attributes"]["POSITION"])]
        normals = [Vector(v) for v in accessor(doc, binary, primitive["attributes"]["NORMAL"])]
        indices = [v[0] for v in accessor(doc, binary, primitive["indices"])]
        assert all(math.isfinite(v) for p in positions for v in p)
        assert all(abs(n.length - 1) < 1e-4 for n in normals)
        for i in range(0, len(indices), 3):
            a, b, c = indices[i:i + 3]
            cross = (positions[b] - positions[a]).cross(positions[c] - positions[a])
            assert cross.length > 2e-10, (name, "degenerate exported triangle")
            assert cross.dot(normals[a] + normals[b] + normals[c]) > 0
            # Weld only identical binary positions across normal/material seams.
            for u, v in ((a, b), (b, c), (c, a)):
                edge = (tuple(positions[u]), tuple(positions[v]))
                exported_edges.setdefault(tuple(sorted(edge)), []).append(edge)
        points.extend(positions)
        triangles += len(indices) // 3
        vertices += len(positions)
    assert all(len(uses) == 2 and uses[0] == tuple(reversed(uses[1]))
               for uses in exported_edges.values()), "Nonmanifold binary export after seam welding"
    actual_bounds = bounds(points)
    assert triangles == len(mesh.loop_triangles)
    assert all(abs(a - b) < 1e-5 for a, b in zip(sum(actual_bounds, []), sum(source_bounds, [])))
    assert (reexport / path.name).read_bytes() == raw, "Fresh export differs"
    report["exports"][name] = {
        "source_vertices": len(mesh.vertices), "glb_vertices": vertices, "triangles": triangles,
        "mesh_count": 1, "surfaces": len(doc["meshes"][0]["primitives"]),
        "degenerate_faces": 0, "degenerate_export_triangles": 0, "nonmanifold_edges": 0,
        "nonmanifold_export_edges_after_exact_position_weld": 0,
        "unit_normals": True, "consistent_winding": True, "applied_transforms": True,
        "source_godot_aabb": source_bounds, "actual_glb_aabb": actual_bounds,
        "nominal_godot_aabb": [low, high], "nominal_bound_tolerance_m": .004,
        "source_glb_tolerance_m": .00001, "pivot_m": [0, 0, 0],
        "pivot_kind": "deck entry centre" if stations else "backing plane centre",
        "deck_surface_datum_m": 0, "underside_datum_m": -.24,
        "fresh_reexport_byte_identical": True, "glb_sha256": hashlib.sha256(raw).hexdigest(),
        "glb_bytes": len(raw), "materials": doc["materials"],
    }
    scene = (ROOT / f"scenes/prefabs/environment/{name}.tscn").read_text()
    if not stations:
        assert 'type="BoxShape3D"' in scene
        continue
    payload = re.search(r"data = PackedVector3Array\(([^)]*)\)", scene).group(1)
    scalars = [struct.unpack("f", struct.pack("f", float(v)))[0] for v in payload.split(",")]
    points = [tuple(scalars[i:i + 3]) for i in range(0, len(scalars), 3)]
    assert len(points) == (stations * 8 + 4) * 3
    edges, top_area = {}, 0
    for i in range(0, len(points), 3):
        a, b, c = points[i:i + 3]
        cross = (Vector(b) - Vector(a)).cross(Vector(c) - Vector(a))
        assert cross.length > 1e-9
        if all(p[1] == 0 for p in (a, b, c)):
            assert cross.y < 0, "Godot top winding must be clockwise"
            top_area += cross.length / 2
        for u, v in ((a, b), (b, c), (c, a)):
            edges.setdefault(tuple(sorted((u, v))), []).append((u, v))
    assert all(len(uses) == 2 and uses[0] == tuple(reversed(uses[1])) for uses in edges.values())
    report["saved_collision"][name] = {
        "triangles": len(points) // 3, "unique_vertices": len(set(points)),
        "nonmanifold_or_open_edges": 0, "degenerate_triangles": 0,
        "exact_float32_shared_edges": True, "top_area_m2": top_area,
    }
report["status"] = "PASS source, binary exports and saved collision; Godot checked separately"
EVIDENCE.mkdir(parents=True, exist_ok=True)
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps(report, indent=2))
