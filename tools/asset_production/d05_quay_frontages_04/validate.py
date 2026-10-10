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
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d05_quay_frontages_04"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
collection = bpy.data.collections["export_" + ASSET]
assert bpy.data.objects["authoring_1m_reference"].dimensions == Vector((1, 1, 1))
EVIDENCE.mkdir(parents=True, exist_ok=True)
assert {o.name for o in collection.objects} == {"D05QuayFrontages04", "D05QuayFrontages04_Mesh"}
assert bpy.context.scene.unit_settings.system == "METRIC"
assert bpy.context.scene.unit_settings.scale_length == 1
for obj in collection.objects:
    assert obj.matrix_local == Matrix.Identity(4)
obj = bpy.data.objects["D05QuayFrontages04_Mesh"]
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
    [-4.68, -6.29, 0, 4.68, 6.28, 10.13]))
# Independent ray checks prove blind structural apertures rather than solid-wall mounting.
bvh = BVHTree.FromObject(obj, bpy.context.evaluated_depsgraph_get())
recess_probes = []
for start, direction, expected in [
    ((1.95, 8, 1), (0, -1, 0), (1.95, 5.35, 1)),
    ((-.95, 8, 1.5), (0, -1, 0), (-.95, 5.35, 1.5)),
    ((0, 8, 5.4), (0, -1, 0), (0, 5.35, 5.4)),
    ((0, -8, 5.4), (0, 1, 0), (0, -5.35, 5.4)),
    ((8, 2, 1.5), (-1, 0, 0), (3.75, 2, 1.5)),
    ((8, 2, 5.4), (-1, 0, 0), (3.75, 2, 5.4)),
    ((0, 8, 3), (0, -1, 0), (0, 6, 3)),
    ((8, 2, 3), (-1, 0, 0), (4.4, 2, 3)),
]:
    location, normal, index, distance = bvh.ray_cast(Vector(start), Vector(direction))
    assert location is not None and (location-Vector(expected)).length < .001
    recess_probes.append({"start_blender": start, "hit_blender": list(location)})

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
expected_materials = {"quay_ochre_render", "quay_slate_roof", "quay_warm_stone_trim",
                      "quay_petrol_plinth", "quay_amber_frontage"}
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
    [-4.68, 0, -6.28, 4.68, 10.13, 6.29]))
reexport = Path(sys.argv[sys.argv.index("--") + 1])
assert reexport.read_bytes() == raw, "Fresh-process export differs"
# Real reused display/leaf exports must fit the shell, not merely their nominal boxes.
shared_fit = []
mounts = [
    ("city_shop_fittings_06", "_single", (1.95, 6, 0), 0),
    ("city_shop_fittings_03", "_single", (1.95, 6, 0), 0),
    ("city_shop_fittings_05", "", (-.95, 6, .48), 0),
    ("city_shop_fittings_07", "", (0, 6, 4.65), 0),
    ("city_shop_fittings_07", "", (0, -6, 4.65), math.pi),
    ("city_shop_fittings_05", "", (4.4, 2, .48), -math.pi/2),
    ("city_shop_fittings_07", "", (4.4, 2, 4.65), -math.pi/2),
]
for dependency, suffix, offset, yaw in mounts:
    before = set(bpy.data.objects)
    dependency_path = ROOT / f"art/models/environment/{dependency}/{dependency}{suffix}.glb"
    bpy.ops.import_scene.gltf(filepath=str(dependency_path))
    imported = set(bpy.data.objects) - before
    for imported_obj in imported:
        if imported_obj.parent not in imported:
            imported_obj.matrix_world = (Matrix.Translation(Vector(offset))
                                         @ Matrix.Rotation(yaw, 4, "Z")
                                         @ imported_obj.matrix_world)
    bpy.context.view_layer.update()
    mesh_count = 0
    for imported_obj in imported:
        if imported_obj.type != "MESH":
            continue
        points_world = [imported_obj.matrix_world @ v.co for v in imported_obj.data.vertices]
        faces = [tuple(p.vertices) for p in imported_obj.data.polygons]
        fitting_bvh = BVHTree.FromPolygons(points_world, faces)
        overlaps = bvh.overlap(fitting_bvh)
        assert not overlaps, (dependency, imported_obj.name, len(overlaps))
        mesh_count += 1
    shared_fit.append({"dependency": dependency_path.relative_to(ROOT).as_posix(),
                       "sha256": hashlib.sha256(dependency_path.read_bytes()).hexdigest(),
                       "mount_blender": offset, "yaw_radians": yaw, "mesh_count": mesh_count,
                       "shell_surface_intersections": 0})

report = {
    "asset": "d05_quay_frontages.04", "blender": bpy.app.version_string,
    "build_hash": bpy.app.build_hash.decode(), "vertices": len(mesh.vertices),
    "triangles": triangles, "mesh_count": 1,
    "surfaces": len(metadata["meshes"][0]["primitives"]), "glb_vertices": vertices,
    "degenerate_faces": degenerate, "nonmanifold_edges": nonmanifold,
    "unit_normals": True, "consistent_winding": True, "applied_transforms": True,
    "source_aabb": {"min": low, "max": high},
    "godot_aabb": {"min": actual_low, "max": actual_high},
    "dimensions_godot_m": [9.36, 10.13, 12.57], "dimension_tolerance_m": .001,
    "pivot": [0, 0, 0], "datum": "ground-centred bounding wall footprint", "dimensions_status": "provisional",
    "fresh_reexport_byte_identical": True,
    "glb_sha256": hashlib.sha256(raw).hexdigest(), "glb_bytes": len(raw),
    "materials": metadata["materials"], "structural_recess_probes": recess_probes,
    "recess_depth_m": .65, "shared_fitting_fit": shared_fit,
    "status": "PASS source and export",
}
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps(report, indent=2))
