"""Check saved source, actual GLB accessors, seams and fresh-export reproducibility."""
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
NID = "d03_apartment_family_08"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EXPORT = ROOT / f"art/models/environment/{NID}/{NID}.glb"
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
collection = bpy.data.collections[f"export_{NID}"]
assert set(o.name for o in collection.objects) == {"D03ApartmentFamily08", "D03ApartmentFamily08_Mesh"}
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
for obj in collection.objects:
    assert tuple(obj.location) == (0, 0, 0)
    assert tuple(obj.scale) == (1, 1, 1)
    assert tuple(obj.rotation_euler) == (0, 0, 0)
    assert not obj.modifiers
model = bpy.data.objects["D03ApartmentFamily08_Mesh"]
mesh = model.data
mesh.calc_loop_triangles()
bm = bmesh.new()
bm.from_mesh(mesh)
nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
bm.free()
degenerate = sum(face.area <= 1e-10 for face in mesh.polygons)
assert nonmanifold == degenerate == 0
assert all(math.isfinite(v) for vert in mesh.vertices for v in vert.co)
normal_error = max(abs(normal.vector.length - 1) for normal in mesh.corner_normals)
assert normal_error < .0001
coords = [model.matrix_world @ v.co for v in mesh.vertices]
source_min = [min(v[i] for v in coords) for i in range(3)]
source_max = [max(v[i] for v in coords) for i in range(3)]
expected_min, expected_max = [-3, 0, -6.18], [3, 3.2, 6.18]
converted = [source_min[0], source_min[2], -source_max[1],
             source_max[0], source_max[2], -source_min[1]]
assert all(abs(a - b) < .00001 for a, b in zip(converted, expected_min + expected_max))
# Literal structural connector corners protect flush X and height joins independently of author.py.
for x in (-3, 3):
    for y in (-6, 6):
        for z in (0, 3.2):
            assert any((v - Vector((x, y, z))).length < .00001 for v in coords)
# Independently enumerate the six closed glass solids; this protects entrance/core treatment
# as well as the ordinary rear windows, not merely the unchanged structural envelope.
glass_slot = next(i for i, mat in enumerate(mesh.materials)
                  if mat.name == "terrace_petrol_closed_glass")
glass_faces = [face for face in mesh.polygons if face.material_index == glass_slot]
remaining = set(v for face in glass_faces for v in face.vertices)
neighbours = {v: set() for v in remaining}
for face in glass_faces:
    for vertex in face.vertices:
        neighbours[vertex].update(face.vertices)
glass_bounds = []
while remaining:
    pending = [remaining.pop()]
    island = set(pending)
    while pending:
        vertex = pending.pop()
        found = neighbours[vertex] & remaining
        remaining.difference_update(found)
        island.update(found)
        pending.extend(found)
    points = [Vector((coords[i].x, coords[i].z, -coords[i].y)) for i in island]
    glass_bounds.append([min(v[i] for v in points) for i in range(3)] +
                        [max(v[i] for v in points) for i in range(3)])
expected_glass_bounds = [
    [-2.55, 1.00, 6.094, -.45, 2.55, 6.105],
    [.45, 1.00, 6.094, 2.55, 2.55, 6.105],
    [-1.98, .035, -6.116, -.94, 2.30, -6.104],
    [-.86, .035, -6.116, .18, 2.30, -6.104],
    [-1.98, 2.39, -6.116, .18, 2.49, -6.104],
    [1.24, .48, -6.108, 2.36, 2.90, -6.094],
]
assert len(glass_bounds) == len(expected_glass_bounds)
for expected in expected_glass_bounds:
    assert any(all(abs(a - b) < .00001 for a, b in zip(actual, expected))
               for actual in glass_bounds), expected
raw = EXPORT.read_bytes()
magic, version, length = struct.unpack_from("<4sII", raw)
assert magic == b"glTF" and version == 2 and length == len(raw)
json_size, kind = struct.unpack_from("<II", raw, 12)
assert kind == 0x4E4F534A
asset = json.loads(raw[20:20 + json_size])
bin_size, kind = struct.unpack_from("<II", raw, 20 + json_size)
assert kind == 0x004E4942
binary = raw[28 + json_size:28 + json_size + bin_size]
assert not any(asset.get(key) for key in ("images", "textures", "animations", "skins", "cameras"))
assert len(asset["meshes"]) == 1 and len(asset["nodes"]) == 2
for node in asset["nodes"]:
    assert node.get("scale", [1, 1, 1]) == [1, 1, 1]
    assert "rotation" not in node and "translation" not in node


def accessor(index):
    """Decode actual binary accessor values rather than trusting JSON bounds alone."""
    item = asset["accessors"][index]
    view = asset["bufferViews"][item["bufferView"]]
    code = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}[item["componentType"]]
    components = {"SCALAR": 1, "VEC3": 3}[item["type"]]
    fmt = "<" + code * components
    stride = view.get("byteStride", struct.calcsize(fmt))
    start = view.get("byteOffset", 0) + item.get("byteOffset", 0)
    return [struct.unpack_from(fmt, binary, start + i * stride) for i in range(item["count"])]


primitives = asset["meshes"][0]["primitives"]
assert len(primitives) == 5
positions, normals = [], []
triangles, glb_degenerate = 0, 0
for primitive in primitives:
    assert primitive.get("mode", 4) == 4
    points = accessor(primitive["attributes"]["POSITION"])
    positions.extend(points)
    normals.extend(accessor(primitive["attributes"]["NORMAL"]))
    indices = [v[0] for v in accessor(primitive["indices"])]
    triangles += len(indices) // 3
    for i in range(0, len(indices), 3):
        a, b, c = [Vector(points[j]) for j in indices[i:i + 3]]
        glb_degenerate += (b - a).cross(c - a).length / 2 <= 1e-10
assert glb_degenerate == 0
assert all(abs(Vector(n).length - 1) < .0001 for n in normals)
glb_min = [min(v[i] for v in positions) for i in range(3)]
glb_max = [max(v[i] for v in positions) for i in range(3)]
assert all(abs(a - b) < .00001 for a, b in zip(glb_min + glb_max, expected_min + expected_max))
assert triangles == len(mesh.loop_triangles)
expected_materials = ["terrace_bluegrey_render", "terrace_pale_frame",
                      "terrace_teal_spandrel", "terrace_petrol_closed_glass", "terrace_warm_entry"]
assert [mat["name"] for mat in asset["materials"]] == expected_materials
assert all(not mat.get("doubleSided", False) and mat.get("alphaMode", "OPAQUE") == "OPAQUE"
           for mat in asset["materials"])
# Reexport from the saved source using the same shared settings, into scratch only.
sys.argv = [__file__, "--", str(SCRATCH / "reexport")]
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
assert (SCRATCH / f"reexport/{NID}.glb").read_bytes() == raw
report = {
    "status": "PASS", "blender": bpy.app.version_string,
    "blender_build": bpy.app.build_hash.decode(), "gltf_exporter": "5.2.40",
    "source_vertices": len(mesh.vertices), "triangles": triangles,
    "export_vertices": len(positions), "mesh_count": 1, "surface_count": len(primitives),
    "source_degenerate_faces": degenerate, "nonmanifold_edges": nonmanifold,
    "glb_degenerate_triangles": glb_degenerate, "maximum_source_normal_length_error": normal_error,
    "glb_unit_normals": True, "godot_aabb_min": glb_min, "godot_aabb_max": glb_max,
    "dimensions_m": [b - a for a, b in zip(glb_min, glb_max)], "pivot": [0, 0, 0],
    "dimension_tolerance_m": .001, "axis_mapping_tolerance_m": .00001,
    "join_corners_exact": True, "module_pitch_m": [6, 3.2, 12],
    "closed_glass_solid_bounds_godot": glass_bounds, "entrance_core_glazing_bounds_pass": True,
    "source": {"path": SOURCE.relative_to(ROOT).as_posix(), "bytes": SOURCE.stat().st_size,
               "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest()},
    "export": {"path": EXPORT.relative_to(ROOT).as_posix(), "bytes": len(raw),
               "sha256": hashlib.sha256(raw).hexdigest()},
    "fresh_reexport_byte_identical": True, "materials": asset["materials"],
    "renders": {"resolution": [1280, 720], "compression": 95, "renderer": "Blender Cycles CPU",
                "samples": 32, "dither_intensity": 0,
                "overhead_height_m": 47, "vertical_fov_degrees": 42},
}
engine_receipt = SCRATCH / "prefab-check.json"
assert engine_receipt.exists(), "Run prefab normalization/runtime checks first"
report["godot"] = json.loads(engine_receipt.read_text())
assert report["godot"]["ok"]
assert report["godot"]["roundtrip"]["save_reload_byte_stable"]
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps(report, indent=2))
