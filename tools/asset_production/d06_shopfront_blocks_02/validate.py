"""Independently audit saved topology, raw GLB data, aperture fit and reproducibility."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d06_shopfront_blocks_02"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
collection = bpy.data.collections["export_" + ASSET]
assert bpy.context.scene.unit_settings.scale_length == 1
root = bpy.data.objects[ASSET]
assert root.matrix_world == root.matrix_world.Identity(4)
assert root.type == "EMPTY" and root.parent is None
meshes = [o for o in collection.objects if o.type == "MESH"]
report = json.loads((EVIDENCE / "validation.json").read_text()) if (EVIDENCE / "validation.json").exists() else {}
report.update({"blender": bpy.app.version_string, "build_hash": bpy.app.build_hash.decode(),
          "meshes": [], "pivot": [0, 0, 0]})
points = []
for obj in meshes:
    assert obj.matrix_local == obj.matrix_local.Identity(4), obj.name
    assert not obj.modifiers
    data = obj.data
    data.calc_loop_triangles()
    assert all(math.isfinite(v) for vertex in data.vertices for v in vertex.co)
    assert all(abs(n.vector.length - 1) < 1e-4 for n in data.corner_normals)
    bm = bmesh.new()
    bm.from_mesh(data)
    nonmanifold = sum(not e.is_manifold for e in bm.edges)
    degenerate = sum(p.area <= 1e-10 for p in data.polygons)
    assert nonmanifold == 0 and degenerate == 0, obj.name
    assert bm.calc_volume(signed=True) > 0
    assert all(e.is_contiguous for e in bm.edges)
    bm.free()
    points.extend(v.co.copy() for v in data.vertices)
    report["meshes"].append({"name": obj.name, "vertices": len(data.vertices),
                             "triangles": len(data.loop_triangles),
                             "nonmanifold_edges": nonmanifold, "degenerate_faces": degenerate})
low = [min(v[i] for v in points) for i in range(3)]
high = [max(v[i] for v in points) for i in range(3)]
expected_low, expected_high = [-9.68, -9.08, 0], [9.68, 9.12, 5.05]
assert all(abs(a - b) < .001 for a, b in zip(low + high, expected_low + expected_high))
report.update(source_aabb={"min": low, "max": high},
              godot_aabb={"min": [low[0], low[2], -high[1]],
                          "max": [high[0], high[2], -low[1]]},
              structural_footprint_m=[19.2, 18.0],
              vertices=sum(m["vertices"] for m in report["meshes"]),
              triangles=sum(m["triangles"] for m in report["meshes"]),
              mesh_count=len(meshes), nonmanifold_edges=0, degenerate_faces=0,
              unit_normals=True, applied_mesh_transforms=True)
# Independent literal opening expectations inherited from accepted .01 interfaces.
facade = bpy.data.objects["front_wall_six_openings"].data
bvh = BVHTree.FromPolygons([v.co for v in facade.vertices], [p.vertices for p in facade.polygons])
openings = [(-8.87, -5.83, .54, 2.42), (-5.16, -3.74, 0, 2.45),
            (-2.47, .57, .54, 2.42), (1.24, 2.66, 0, 2.45),
            (3.93, 6.97, .54, 2.42), (7.64, 9.06, 0, 2.45)]
for left, right, bottom, top in openings:
    for i in range(1, 16):
        for j in range(1, 16):
            x, z = left + (right - left) * i / 16, bottom + (top - bottom) * j / 16
            assert bvh.ray_cast(Vector((x, 9.2, z)), Vector((0, -1, 0)), .75)[0] is None
    assert bvh.ray_cast(Vector((left - .01, 9.2, (bottom + top) / 2)),
                        Vector((0, -1, 0)), .75)[0] is not None
    assert bvh.ray_cast(Vector((right + .01, 9.2, (bottom + top) / 2)),
                        Vector((0, -1, 0)), .75)[0] is not None
report["apertures"] = {"bounds_x_height": openings, "clear_rays": 1350, "edge_hits": 12}
markers = {}
for side, door, display in (("0", -4.45, -7.35), ("1", 1.95, -.95), ("2", 8.35, 5.45)):
    for kind, x, z in (("entrance_single", door, 0), ("door_single", door, 0),
                       ("display_window", display, .48), ("canopy", display, 3),
                       ("fascia", display, 3.8)):
        name = f"mount_{side}_{kind}"
        obj = bpy.data.objects[name]
        assert (obj.location - Vector((x, 9, z))).length < 1e-5
        markers[name] = [x, z, -9]
report["markers_godot"] = markers
# Decode actual binary accessors: do not rely solely on declared accessor bounds.
path = ROOT / f"art/models/environment/{ASSET}/{ASSET}.glb"
raw = path.read_bytes()
magic, version, total = struct.unpack_from("<4sII", raw)
assert magic == b"glTF" and version == 2 and total == len(raw)
length, kind = struct.unpack_from("<II", raw, 12)
doc = json.loads(raw[20:20 + length])
binary = raw[28 + length:]


def accessor(index):
    """Read tightly packed or strided GLB accessor data using its actual component type."""
    acc = doc["accessors"][index]
    view = doc["bufferViews"][acc["bufferView"]]
    fmt = {5126: "f", 5125: "I", 5123: "H", 5121: "B"}[acc["componentType"]]
    count = {"VEC3": 3, "VEC2": 2, "SCALAR": 1}[acc["type"]]
    size = struct.calcsize("<" + fmt * count)
    start = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    return [struct.unpack_from("<" + fmt * count, binary,
                               start + i * view.get("byteStride", size))
            for i in range(acc["count"])]


assert not any(doc.get(key) for key in ("skins", "animations", "images", "textures", "cameras"))
assert len(doc["meshes"]) == len(meshes)
assert len(doc["materials"]) == 5
assert all(not m.get("doubleSided", False) for m in doc["materials"])
export_points, triangles, vertices, surfaces = [], 0, 0, 0
for mesh in doc["meshes"]:
    for primitive in mesh["primitives"]:
        surfaces += 1
        positions = [Vector(p) for p in accessor(primitive["attributes"]["POSITION"])]
        normals = [Vector(n) for n in accessor(primitive["attributes"]["NORMAL"])]
        indices = [v[0] for v in accessor(primitive["indices"])]
        assert all(abs(n.length - 1) < 1e-4 for n in normals)
        assert all(math.isfinite(v) for p in positions for v in p)
        for i in range(0, len(indices), 3):
            a, b, c = indices[i:i + 3]
            cross = (positions[b] - positions[a]).cross(positions[c] - positions[a])
            assert cross.length > 2e-10
            assert cross.dot(normals[a] + normals[b] + normals[c]) > 0
        export_points.extend(positions)
        triangles += len(indices) // 3
        vertices += len(positions)
assert triangles == report["triangles"]
actual_low = [min(p[i] for p in export_points) for i in range(3)]
actual_high = [max(p[i] for p in export_points) for i in range(3)]
assert all(abs(a - b) < 1e-5 for a, b in zip(
    actual_low + actual_high, report["godot_aabb"]["min"] + report["godot_aabb"]["max"]))
for name, location in markers.items():
    node = next(n for n in doc["nodes"] if n["name"] == name)
    assert all(abs(a - b) < 1e-5 for a, b in zip(node.get("translation", [0, 0, 0]), location))
assert {n["name"] for n in doc["nodes"]} == {o.name for o in collection.objects}
assert all("rotation" not in n and "scale" not in n for n in doc["nodes"])
reexport = Path(sys.argv[sys.argv.index("--") + 1])
assert reexport.read_bytes() == raw, "Fresh-process export differs"
report["glb"] = {"bytes": len(raw), "vertices": vertices, "triangles": triangles,
                 "surfaces": surfaces, "materials": doc["materials"],
                 "sha256": hashlib.sha256(raw).hexdigest(), "byte_identical_reexport": True,
                 "unit_normals": True, "degenerate_triangles": 0}
# Test actual unchanged shared fitting vertices in the shell's rear insertion voids.
fit_rows = []
for side, door_x, display_x, offset in (("0", -4.45, -7.35, 0),
                                      ("1", 1.95, -.95, 2), ("2", 8.35, 5.45, 4)):
    for kind, folder, filename, x, z, hole in (
        ("entrance", "city_shop_fittings_03", "city_shop_fittings_03_single", door_x, 0,
         openings[offset + 1]),
        ("door", "city_shop_fittings_06", "city_shop_fittings_06_single", door_x, 0,
         openings[offset + 1]),
        ("window", "city_shop_fittings_05", "city_shop_fittings_05", display_x, .48,
         openings[offset]),
    ):
        before = set(bpy.data.objects)
        fitting_path = ROOT / f"art/models/environment/{folder}/{filename}.glb"
        bpy.ops.import_scene.gltf(filepath=str(fitting_path))
        objects = set(bpy.data.objects) - before
        tested = 0
        for obj in objects:
            if obj.type != "MESH":
                continue
            for vertex in obj.data.vertices:
                point = obj.matrix_world @ vertex.co
                if point.y >= -1e-5:
                    continue
                point += Vector((x, 9, z))
                left, right, bottom, top = hole
                assert left < point.x < right and bottom <= point.z < top, (kind, point)
                assert point.y > 8.45, (kind, "rear insertion exceeds reserved void", point)
                tested += 1
        assert tested > 0
        fit_rows.append({"side": side, "fitting": kind, "rear_vertices_checked": tested,
                         "sha256": hashlib.sha256(fitting_path.read_bytes()).hexdigest()})
        for obj in objects:
            bpy.data.objects.remove(obj, do_unlink=True)
report["actual_fitting_rear_void_checks"] = fit_rows
reference = bpy.data.objects["authoring_1m_reference"]
assert (reference.dimensions - Vector((1, 1, 1))).length < 1e-6
assert reference.name not in {o.name for o in collection.objects}
report["excluded_metre_reference"] = True
# Count the actual fitted GLB instances recorded by Godot, without duplicating geometry.
if "model_instances" in report:
    totals = {"triangles": 0, "exported_vertices": 0, "meshes": 0, "surfaces": 0}
    for model in report["model_instances"]:
        payload = (ROOT / model["path"].removeprefix("res://")).read_bytes()
        json_length = struct.unpack_from("<I", payload, 12)[0]
        document = json.loads(payload[20:20 + json_length])
        totals["meshes"] += len(document["meshes"])
        for mesh in document["meshes"]:
            for primitive in mesh["primitives"]:
                totals["surfaces"] += 1
                totals["triangles"] += document["accessors"][primitive["indices"]]["count"] // 3
                totals["exported_vertices"] += document["accessors"][
                    primitive["attributes"]["POSITION"]]["count"]
    assert totals["meshes"] == report["mesh_instances"]
    assert totals["surfaces"] == report["material_surfaces"]
    report["fitted_geometry"] = totals
report["status"] = "PASS: source, raw GLB, interfaces and fresh-process reexport"
EVIDENCE.mkdir(parents=True, exist_ok=True)
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps({k: v for k, v in report.items() if k not in ("meshes", "glb")}, indent=2))
