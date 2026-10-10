"""Validate saved cloth topology, actual GLB buffers, mounting fit and fresh reexports."""
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
NID = "d03_laundry_frames_03"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EXPECTED = {
    "sheet": ([-.7101, -1.0404, -.1719], [.7101, .0241, .1714]),
    "towel": ([-.3801, -.8005, -.1558], [.3801, .0241, .1554]),
}


def receipt(path):
    """Measure hashes and byte counts from final payloads."""
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def accessor(asset, binary, index):
    """Decode binary strided accessors rather than trusting advertised GLB bounds."""
    item = asset["accessors"][index]
    view = asset["bufferViews"][item["bufferView"]]
    code = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}[item["componentType"]]
    fmt = "<" + code * {"SCALAR": 1, "VEC3": 3}[item["type"]]
    stride = view.get("byteStride", struct.calcsize(fmt))
    start = view.get("byteOffset", 0) + item.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, start + i * stride) for i in range(item["count"])]


def bounds(points):
    """Measure finite coordinate extents in the caller's explicit axis system."""
    assert all(math.isfinite(v) for point in points for v in point)
    return ([min(v[i] for v in points) for i in range(3)],
            [max(v[i] for v in points) for i in range(3)])


def line_edge_clearance(mesh):
    """Measure every shell edge against the infinite top-centre mounting line."""
    distances = []
    for edge in mesh.edges:
        a, b = [Vector((mesh.vertices[i].co.y, mesh.vertices[i].co.z)) for i in edge.vertices]
        delta = b - a
        t = max(0, min(1, -a.dot(delta) / delta.length_squared)) if delta.length_squared else 0
        distances.append((a + t * delta).length)
    return min(distances)


bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
assert bpy.context.scene.name == "ClothSources"
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
assert len(bpy.data.libraries) == 1
library = bpy.data.libraries[0]
assert library.filepath.replace("\\", "/") == (
    "//../d03_laundry_frames_01/d03_laundry_frames_01.blend"
), repr(library.filepath)
assert Path(bpy.path.abspath(library.filepath)).is_file()
report = {"status": "PASS", "blender": bpy.app.version_string,
          "blender_build": bpy.app.build_hash.decode(), "gltf_exporter": "5.2.40",
          "source": receipt(SOURCE), "variants": {}}

sys.argv = [__file__, "--", str(SCRATCH / "reexport")]
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
for variant, (expected_min, expected_max) in EXPECTED.items():
    collection = bpy.data.collections[f"export_{NID}_{variant}"]
    name = "D03LaundryFrames03" + variant.title()
    assert set(o.name for o in collection.objects) == {name, name + "_Mesh"}
    for obj in collection.objects:
        assert tuple(obj.location) == (0, 0, 0)
        assert tuple(obj.rotation_euler) == (0, 0, 0)
        assert tuple(obj.scale) == (1, 1, 1)
        assert not obj.modifiers
    mesh = bpy.data.objects[name + "_Mesh"].data
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    bm.free()
    degenerate = sum(face.area <= 1e-10 for face in mesh.polygons)
    assert nonmanifold == degenerate == 0
    source_error = max(abs(n.vector.length - 1) for n in mesh.corner_normals)
    assert source_error < .0001
    coords = [Vector((v.co.x, v.co.z, -v.co.y)) for v in mesh.vertices]
    low, high = bounds(coords)
    assert all(abs(a - b) < .001 for a, b in zip(low + high, expected_min + expected_max))
    clearance = line_edge_clearance(mesh)
    assert clearance > .014, (variant, clearance)
    materials = [f"laundry_{variant}_body", f"laundry_{variant}_hem"]
    assert [mat.name for mat in mesh.materials] == materials

    path = ROOT / f"art/models/environment/{NID}/{NID}_{variant}.glb"
    raw = path.read_bytes()
    assert (SCRATCH / f"reexport/{NID}_{variant}.glb").read_bytes() == raw
    magic, version, length = struct.unpack_from("<4sII", raw)
    assert magic == b"glTF" and version == 2 and length == len(raw)
    json_size, kind = struct.unpack_from("<II", raw, 12)
    assert kind == 0x4E4F534A
    asset = json.loads(raw[20:20 + json_size])
    bin_size, kind = struct.unpack_from("<II", raw, 20 + json_size)
    assert kind == 0x004E4942
    binary = raw[28 + json_size:28 + json_size + bin_size]
    assert not any(asset.get(k) for k in ("images", "textures", "animations", "skins", "cameras"))
    assert len(asset["meshes"]) == 1 and len(asset["nodes"]) == 2
    for node in asset["nodes"]:
        assert node.get("scale", [1, 1, 1]) == [1, 1, 1]
        assert "rotation" not in node and "translation" not in node
    primitives = asset["meshes"][0]["primitives"]
    assert len(primitives) == 2
    positions, normals = [], []
    triangles, glb_degenerate = 0, 0
    for primitive in primitives:
        assert primitive.get("mode", 4) == 4
        points = accessor(asset, binary, primitive["attributes"]["POSITION"])
        positions.extend(points)
        normals.extend(accessor(asset, binary, primitive["attributes"]["NORMAL"]))
        indices = [v[0] for v in accessor(asset, binary, primitive["indices"])]
        triangles += len(indices) // 3
        for i in range(0, len(indices), 3):
            a, b, c = [Vector(points[j]) for j in indices[i:i + 3]]
            glb_degenerate += (b - a).cross(c - a).length / 2 <= 1e-10
    assert glb_degenerate == 0
    glb_normal_error = max(abs(Vector(n).length - 1) for n in normals)
    assert glb_normal_error < .0001
    glb_min, glb_max = bounds(positions)
    assert all(abs(a - b) < .00001 for a, b in zip(glb_min + glb_max, low + high))
    assert triangles == len(mesh.loop_triangles)
    assert [mat["name"] for mat in asset["materials"]] == materials
    assert all(not mat.get("doubleSided", False) and mat.get("alphaMode", "OPAQUE") == "OPAQUE"
               for mat in asset["materials"])
    report["variants"][variant] = {
        "export": receipt(path), "source_vertices": len(mesh.vertices),
        "export_vertices": len(positions), "triangles": triangles, "mesh_count": 1,
        "surface_count": 2, "source_degenerate_faces": degenerate,
        "nonmanifold_edges": nonmanifold, "glb_degenerate_triangles": glb_degenerate,
        "maximum_source_normal_error": source_error, "maximum_glb_normal_error": glb_normal_error,
        "godot_aabb_min": glb_min, "godot_aabb_max": glb_max,
        "dimensions_m": [b - a for a, b in zip(glb_min, glb_max)],
        "pivot": [0, 0, 0], "pivot_contract": "top-centre mounting line axis, not ground",
        "minimum_shell_edge_radius_from_line_m": clearance, "carrier_line_radius_m": .014,
        "dimension_tolerance_m": .001, "axis_mapping_tolerance_m": .00001,
        "fresh_reexport_byte_identical": True, "materials": asset["materials"],
    }

report["godot"] = json.loads((SCRATCH / "prefab-check.json").read_text())
assert report["godot"]["ok"]
for path, entry in report["godot"]["roundtrip"].items():
    if path.startswith("res://"):
        assert entry["byte_stable"] and entry["stable_reload_count"] == 2
        assert hashlib.sha256((ROOT / path[6:]).read_bytes()).hexdigest() == entry["sha256"]
report["existing_dependencies_not_produced"] = [receipt(ROOT / path) for path in (
    "art/source/models/environment/d03_laundry_frames_01/d03_laundry_frames_01.blend",
    "art/models/environment/d03_laundry_frames_01/d03_laundry_frames_01.glb",
    "scenes/prefabs/environment/d03_laundry_frames_01.tscn",
)]
report["renders"] = {"resolution": [1280, 720], "compression": 95,
                     "renderer": "Blender Cycles CPU", "samples": 32,
                     "overhead_height_m": 47, "vertical_fov_degrees": 42,
                     "direction": "vertical-down north-up", "dither_intensity": 0,
                     "studio": "Mounted source collection instances on linked existing frame"}
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps(report, indent=2))
