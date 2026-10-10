"""Validate source topology, actual GLB buffers, dimensions and byte-identical reexport."""
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
NID = "d03_laundry_frames_01"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EXPORT = ROOT / f"art/models/environment/{NID}/{NID}.glb"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EXPECTED_MIN = [-1.95, 0, -.66]
EXPECTED_MAX = [1.95, 2.24, .66]
MATERIALS = ["laundry_muted_teal_metal", "laundry_dark_fittings", "laundry_pale_line"]


def receipt(path):
    """Hash actual bytes, not timestamps or upstream claims."""
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def accessor(asset, binary, index):
    """Decode strided binary accessors so topology and normals are independently checked."""
    item = asset["accessors"][index]
    view = asset["bufferViews"][item["bufferView"]]
    code = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}[item["componentType"]]
    fmt = "<" + code * {"SCALAR": 1, "VEC3": 3}[item["type"]]
    stride = view.get("byteStride", struct.calcsize(fmt))
    start = view.get("byteOffset", 0) + item.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, start + i * stride) for i in range(item["count"])]


bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
collection = bpy.data.collections[f"export_{NID}"]
assert set(o.name for o in collection.objects) == {"D03LaundryFrames01", "D03LaundryFrames01_Mesh"}
for obj in collection.objects:
    assert tuple(obj.location) == (0, 0, 0)
    assert tuple(obj.rotation_euler) == (0, 0, 0)
    assert tuple(obj.scale) == (1, 1, 1)
    assert not obj.modifiers
mesh = bpy.data.objects["D03LaundryFrames01_Mesh"].data
mesh.calc_loop_triangles()
bm = bmesh.new()
bm.from_mesh(mesh)
nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
bm.free()
degenerate = sum(face.area <= 1e-10 for face in mesh.polygons)
assert nonmanifold == degenerate == 0
assert all(math.isfinite(v) for vert in mesh.vertices for v in vert.co)
normal_error = max(abs(n.vector.length - 1) for n in mesh.corner_normals)
assert normal_error < .0001
coords = [Vector((v.co.x, v.co.z, -v.co.y)) for v in mesh.vertices]
low = [min(v[i] for v in coords) for i in range(3)]
high = [max(v[i] for v in coords) for i in range(3)]
assert all(abs(a - b) < .00001 for a, b in zip(low + high, EXPECTED_MIN + EXPECTED_MAX))
assert [mat.name for mat in mesh.materials] == MATERIALS

# Three actual line components must fit the documented cloth mount axes, not a second formula.
line_vertices = {i for face in mesh.polygons if face.material_index == 2 for i in face.vertices}
line_points = [coords[i] for i in line_vertices]
for z in (-.48, 0, .48):
    points = [v for v in line_points if abs(v.z - z) < .02]
    assert len(points) == 24
    assert abs(min(v.x for v in points) + 1.8) < .00001
    assert abs(max(v.x for v in points) - 1.8) < .00001
    assert abs(sum(v.y for v in points) / len(points) - 2.18) < .00001
    assert all(abs(math.hypot(v.y - 2.18, v.z - z) - .014) < .00001 for v in points)

sys.argv = [__file__, "--", str(SCRATCH / "reexport")]
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
raw = EXPORT.read_bytes()
assert (SCRATCH / f"reexport/{NID}.glb").read_bytes() == raw
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
assert len(primitives) == 3
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
assert all(abs(Vector(n).length - 1) < .0001 for n in normals)
glb_min = [min(v[i] for v in positions) for i in range(3)]
glb_max = [max(v[i] for v in positions) for i in range(3)]
assert all(abs(a - b) < .00001 for a, b in zip(glb_min + glb_max, EXPECTED_MIN + EXPECTED_MAX))
assert triangles == len(mesh.loop_triangles)
assert [mat["name"] for mat in asset["materials"]] == MATERIALS
assert all(not mat.get("doubleSided", False) and mat.get("alphaMode", "OPAQUE") == "OPAQUE"
           for mat in asset["materials"])
report = {
    "status": "PASS", "blender": bpy.app.version_string,
    "blender_build": bpy.app.build_hash.decode(), "gltf_exporter": "5.2.40",
    "source": receipt(SOURCE), "export": receipt(EXPORT),
    "source_vertices": len(mesh.vertices), "export_vertices": len(positions),
    "triangles": triangles, "mesh_count": 1, "surface_count": 3,
    "source_degenerate_faces": degenerate, "nonmanifold_edges": nonmanifold,
    "glb_degenerate_triangles": glb_degenerate, "maximum_source_normal_error": normal_error,
    "glb_unit_normals": True, "godot_aabb_min": glb_min, "godot_aabb_max": glb_max,
    "dimensions_m": [b - a for a, b in zip(glb_min, glb_max)], "pivot": [0, 0, 0],
    "dimension_tolerance_m": .001, "axis_mapping_tolerance_m": .00001,
    "fresh_reexport_byte_identical": True, "materials": asset["materials"],
    "cloth_interface": {"line_y_m": 2.18, "line_z_m": [-.48, 0, .48],
                        "line_radius_m": .014, "usable_x_m": [-1.6, 1.6],
                        "source_line_vertices_checked": len(line_points)},
    "godot": json.loads((SCRATCH / "prefab-check.json").read_text()),
    "renders": {"resolution": [1280, 720], "compression": 95,
                "renderer": "Blender Cycles CPU", "samples": 32,
                "overhead_height_m": 47, "vertical_fov_degrees": 42,
                "direction": "vertical-down north-up", "dither_intensity": 0},
}
assert report["godot"]["ok"]
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps(report, indent=2))
