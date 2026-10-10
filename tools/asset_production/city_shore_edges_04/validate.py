"""Check six source solids, literal bounds, sibling mating sections and actual GLB binary data."""
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
ASSET = "city_shore_edges_04"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
reexport = Path(sys.argv[sys.argv.index("--") + 1])
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
report = {"asset": "city_shore_edges.04", "blender": bpy.app.version_string,
          "build_hash": bpy.app.build_hash.decode(), "variants": {},
          "dimension_tolerance_m": .001, "section_tolerance_m": .000001}


def accessor(metadata, binary, index):
    """Decode buffer components to check real positions, normals and triangles."""
    acc = metadata["accessors"][index]
    view = metadata["bufferViews"][acc["bufferView"]]
    fmt = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}[acc["componentType"]]
    count = {"VEC3": 3, "VEC2": 2, "SCALAR": 1}[acc["type"]]
    size = struct.calcsize("<" + fmt * count)
    start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    return [struct.unpack_from("<" + fmt * count, binary,
            start + i * view.get("byteStride", size)) for i in range(acc["count"])]


def compare_sections(actual, expected):
    """Match every section point bidirectionally without depending on vertex ordering."""
    assert len(actual) == len(expected), (len(actual), len(expected))
    error = max(min(math.dist(a, b) for b in expected) for a in actual)
    reverse = max(min(math.dist(a, b) for b in actual) for a in expected)
    assert max(error, reverse) < 1e-6, (error, reverse)
    return max(error, reverse)


for family, number, width, bottom, top in (
    ("wall", "01", .72, 0, 1), ("quay", "02", 1.2, -2.4, 0),
    ("rock", "03", 1.6, -.6, .65),
):
    sibling = "city_shore_edges_" + number
    source = ROOT / f"art/source/models/environment/{sibling}/{sibling}.blend"
    with bpy.data.libraries.load(str(source), link=False) as (available, loaded):
        loaded.objects = ["CityShoreEdges" + number + "_Mesh"]
    sibling_mesh = loaded.objects[0].data
    expected_section = [(v.co.y, v.co.z) for v in sibling_mesh.vertices
                        if abs(v.co.x + 2) < 1e-6]
    for variant in ("corner", "end"):
        suffix = family + "_" + variant
        name = "CityShoreEdges04_" + suffix
        collection = bpy.data.collections["export_" + ASSET + "_" + suffix]
        assert {o.name for o in collection.objects} == {name, name + "_Mesh"}
        assert all(o.matrix_local == Matrix.Identity(4) for o in collection.objects)
        obj = bpy.data.objects[name + "_Mesh"]
        assert not obj.modifiers
        mesh = obj.data
        mesh.calc_loop_triangles()
        assert all(math.isfinite(c) for v in mesh.vertices for c in v.co)
        assert all(abs(n.vector.length - 1) < 1e-4 for n in mesh.corner_normals)
        bm = bmesh.new()
        bm.from_mesh(mesh)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges)
        assert bm.calc_volume(signed=True) > 0
        bm.free()
        assert all(p.area > 1e-10 for p in mesh.polygons)
        join = -2 if variant == "corner" else -.5
        section = [(v.co.y, v.co.z) for v in mesh.vertices if abs(v.co.x - join) < 1e-6]
        error = compare_sections(section, expected_section)
        if variant == "corner":
            exit_section = [(-v.co.x, v.co.z) for v in mesh.vertices if abs(v.co.y - 2) < 1e-6]
            error = max(error, compare_sections(exit_section, expected_section))
        low = [-2, bottom, -2] if variant == "corner" else [-.5, bottom, -width / 2]
        high = [width / 2, top, width / 2] if variant == "corner" else [.5, top, width / 2]
        source_points = [Vector((v.co.x, v.co.z, -v.co.y)) for v in mesh.vertices]
        source_low = [min(v[i] for v in source_points) for i in range(3)]
        source_high = [max(v[i] for v in source_points) for i in range(3)]
        assert all(abs(a - b) < .001 for a, b in zip(source_low + source_high, low + high))
        path = ROOT / f"art/models/environment/{ASSET}/{ASSET}_{suffix}.glb"
        raw = path.read_bytes()
        magic, version, total = struct.unpack_from("<4sII", raw)
        assert magic == b"glTF" and version == 2 and total == len(raw)
        length, kind = struct.unpack_from("<II", raw, 12)
        assert kind == 0x4E4F534A
        metadata = json.loads(raw[20:20 + length])
        binary = raw[28 + length:]
        assert not any(metadata.get(k) for k in ("skins", "animations", "images", "textures", "cameras"))
        assert len(metadata["meshes"]) == 1 and len(metadata["nodes"]) == 2
        assert all(not any(k in n for k in ("rotation", "scale", "translation")) for n in metadata["nodes"])
        assert all(not m.get("doubleSided", False) for m in metadata["materials"])
        points, triangles, vertices = [], 0, 0
        for primitive in metadata["meshes"][0]["primitives"]:
            positions = [Vector(v) for v in accessor(metadata, binary, primitive["attributes"]["POSITION"])]
            normals = [Vector(v) for v in accessor(metadata, binary, primitive["attributes"]["NORMAL"])]
            indices = [v[0] for v in accessor(metadata, binary, primitive["indices"])]
            assert all(abs(n.length - 1) < 1e-4 for n in normals)
            for index in range(0, len(indices), 3):
                a, b, c = indices[index:index + 3]
                cross = (positions[b] - positions[a]).cross(positions[c] - positions[a])
                assert cross.length > 2e-10, (suffix, index)
                assert cross.dot(normals[a] + normals[b] + normals[c]) > 0
            points.extend(positions)
            triangles += len(indices) // 3
            vertices += len(positions)
        assert triangles == len(mesh.loop_triangles)
        assert all(min((point - source_point).length for source_point in source_points) < 1e-5
                   for point in points), "Export positions differ from saved source"
        actual_low = [min(p[i] for p in points) for i in range(3)]
        actual_high = [max(p[i] for p in points) for i in range(3)]
        assert all(abs(a - b) < .001 for a, b in zip(actual_low + actual_high, low + high))
        assert (reexport / path.name).read_bytes() == raw, "Fresh-process export differs"
        surfaces = len(metadata["meshes"][0]["primitives"])
        assert surfaces == (2 if family == "rock" else 4)
        report["variants"][suffix] = {
            "vertices": len(mesh.vertices), "triangles": triangles, "mesh_count": 1,
            "surfaces": surfaces, "glb_vertices": vertices, "degenerate_faces": 0,
            "nonmanifold_edges": 0, "unit_normals": True, "consistent_winding": True,
            "applied_transforms": True, "godot_aabb": {"min": actual_low, "max": actual_high},
            "dimensions_godot_m": [b - a for a, b in zip(low, high)], "pivot": [0, 0, 0],
            "mating_section_vertices": len(section), "max_section_error_m": error,
            "end_profile_blender_yz": section, "sibling_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "fresh_reexport_byte_identical": True, "glb_sha256": hashlib.sha256(raw).hexdigest(),
            "glb_bytes": len(raw), "materials": metadata["materials"],
        }
report["status"] = "PASS six source/export variants; engine and placement are separate gates"
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps({k: {n: v[n] for n in ("triangles", "vertices", "surfaces", "glb_bytes")}
                  for k, v in report["variants"].items()}, indent=2))
