"""Audit reused sources and the actual saved parade interface; never write dependencies."""
import hashlib
import json
from pathlib import Path
import struct

import bmesh
import bpy
from mathutils import Matrix
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_southern_shopping_parade_02"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
SHELL = "d06_southern_shopping_parade_01"
# These are read-only mappings, not new sources or exports for the interface reference.
INPUTS = {
    SHELL: (SHELL, f"export_{SHELL}"),
    "city_shop_fittings_01": ("city_shop_fittings_01", "export_city_shop_fittings_01"),
    "city_shop_fittings_02": ("city_shop_fittings_02", "export_city_shop_fittings_02"),
    "city_shop_fittings_03_single": ("city_shop_fittings_03", "variant_single"),
    "city_shop_fittings_05": ("city_shop_fittings_05", "export_city_shop_fittings_05"),
    "city_shop_fittings_06_single": ("city_shop_fittings_06", "variant_single"),
}
CONVERSION = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
assert bpy.app.version_string == "5.2.2 LTS"
assert bpy.app.build_hash.decode() == "d13f752e3b9c"
engine = json.loads((SCRATCH / "prefab.json").read_text())
assert engine["ok"] and len(engine["model_instances"]) == 31
report = {"blender": bpy.app.version_string, "build_hash": bpy.app.build_hash.decode(),
          "reused_assets": {}, "inputs": [], "new_render_geometry": 0,
          "new_source_or_glb_reexport": "Not applicable: reference composes existing prefabs only"}


def fingerprint(path):
    """Record immutable input provenance and verify no source/import/prefab was modified."""
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


for asset, (family, collection_name) in INPUTS.items():
    source = ROOT / f"art/source/models/environment/{family}/{family}.blend"
    glb = ROOT / f"art/models/environment/{family}/{asset}.glb"
    prefab = ROOT / f"scenes/prefabs/environment/{asset}.tscn"
    report["inputs"].extend(fingerprint(path) for path in
                            (source, glb, glb.with_suffix(".glb.import"), prefab))
    bpy.ops.wm.open_mainfile(filepath=str(source))
    assert bpy.context.scene.unit_settings.scale_length == 1
    collection = bpy.data.collections[collection_name]
    meshes = [obj for obj in collection.all_objects if obj.type == "MESH"]
    stats = {"source_vertices": 0, "triangles": 0, "source_meshes": len(meshes),
             "nonmanifold_edges": 0, "degenerate_faces": 0, "max_normal_length_error": 0}
    for obj in meshes:
        assert not obj.modifiers
        assert tuple(obj.scale) == (1, 1, 1)
        mesh = obj.data
        mesh.calc_loop_triangles()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        stats["source_vertices"] += len(mesh.vertices)
        stats["triangles"] += len(mesh.loop_triangles)
        stats["nonmanifold_edges"] += sum(not edge.is_manifold for edge in bm.edges)
        stats["degenerate_faces"] += sum(face.calc_area() <= 1e-10 for face in bm.faces)
        stats["max_normal_length_error"] = max(stats["max_normal_length_error"],
            max(abs(normal.vector.length - 1) for normal in mesh.corner_normals))
        bm.free()
    assert stats["nonmanifold_edges"] == stats["degenerate_faces"] == 0
    assert stats["max_normal_length_error"] < .0001
    raw = glb.read_bytes()
    assert struct.unpack_from("<III", raw) == (0x46546C67, 2, len(raw))
    size = struct.unpack_from("<I", raw, 12)[0]
    doc = json.loads(raw[20:20 + size])
    primitives = [p for mesh in doc["meshes"] for p in mesh["primitives"]]
    stats["export_vertices"] = sum(doc["accessors"][p["attributes"]["POSITION"]]["count"]
                                    for p in primitives)
    stats["export_surfaces"] = len(primitives)
    assert stats["triangles"] == sum(doc["accessors"][p["indices"]]["count"] // 3
                                     for p in primitives)
    assert not doc.get("images") and not doc.get("animations")
    report["reused_assets"][asset] = stats

# Reuse the existing shell's isolated studio rather than inventing reference geometry.
bpy.ops.wm.open_mainfile(filepath=str(ROOT /
    f"art/source/models/environment/{SHELL}/{SHELL}.blend"))
for obj in list(bpy.data.collections[f"export_{SHELL}"].all_objects):
    bpy.data.objects.remove(obj, do_unlink=True)
instances = {}
for row in engine["model_instances"]:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(ROOT / row["model"].removeprefix("res://")))
    imported = set(bpy.data.objects) - before
    transform = CONVERSION @ Matrix(row["matrix_godot"]) @ CONVERSION.inverted()
    for obj in imported:
        if obj.parent is None:
            obj.matrix_world = transform @ obj.matrix_world
    bpy.context.view_layer.update()
    instances[row["path"]] = [obj for obj in imported if obj.type == "MESH"]


def triangles_world(objects):
    """Read actual world-space triangle coordinates for intersection classification."""
    vertices, triangles = [], []
    for obj in objects:
        obj.data.calc_loop_triangles()
        start = len(vertices)
        vertices.extend(obj.matrix_world @ vert.co for vert in obj.data.vertices)
        triangles.extend(tuple(start + i for i in face.vertices)
                         for face in obj.data.loop_triangles)
    return vertices, triangles


def tree(objects):
    """Build a world-space BVH from actual imported geometry, not declared boxes."""
    vertices, triangles = triangles_world(objects)
    return BVHTree.FromPolygons(vertices, triangles, all_triangles=True, epsilon=0)


shell_objects = next(objects for path, objects in instances.items() if path.endswith("/Shell"))
shell_tree = tree(shell_objects)
intersections, wall_contacts = [], []
shell_vertices, shell_triangles = triangles_world(shell_objects)
# Only flat facade contacts with entirely exterior canopy/fascia triangles are allowed.
# This does not suppress crossing/penetration or intersections with shell trim/backers.
for path, objects in instances.items():
    if path.endswith("/Shell"):
        continue
    overlaps = shell_tree.overlap(tree(objects))
    vertices, triangles = triangles_world(objects)
    contacts = 0
    for shell_index, fitting_index in overlaps:
        shell_points = [shell_vertices[i] for i in shell_triangles[shell_index]]
        fitting_points = [vertices[i] for i in triangles[fitting_index]]
        is_contact = (path.endswith(("/Canopy", "/Fascia"))
                      and all(abs(point.x + 9) < .00001 for point in shell_points)
                      and all(point.x <= -9 + .00001 for point in fitting_points)
                      and any(abs(point.x + 9) < .00001 for point in fitting_points))
        if is_contact:
            contacts += 1
        else:
            intersections.append({"path": path, "shell_triangle": shell_index,
                                  "fitting_triangle": fitting_index})
    if contacts:
        wall_contacts.append({"path": path, "contact_triangle_pairs": contacts})
report["intentional_flush_wall_contacts"] = wall_contacts
report["shell_fitting_surface_intersections"] = intersections
print("SHELL_FITTING_INTERSECTIONS", json.dumps(intersections), flush=True)
assert not intersections, intersections

# Independent literal aperture constraints apply to the actual inserted world vertices.
inserted_vertices = 0
for path, objects in instances.items():
    if not path.endswith(("/Entrance", "/Window", "/Door")):
        continue
    bay_number = int(path.split("WestBay")[-1].split("/")[0])
    centre = (25, 15, 5, -5, -15, -25)[bay_number - 1]
    for obj in objects:
        for vertex in obj.data.vertices:
            point = obj.matrix_world @ vertex.co
            if point.x <= -8.999:
                continue
            u, h = point.y - centre, point.z
            if path.endswith("/Window"):
                assert -2.47 - .0001 <= u <= .57 + .0001 and .54 - .0001 <= h <= 2.42 + .0001
            else:
                assert 1.24 - .0001 <= u <= 2.66 + .0001 and -.0001 <= h <= 2.45 + .0001
            assert point.x < -8.46 + .0001, "Insertion must not reach shell recess backing"
            inserted_vertices += 1
report["actual_inserted_vertices_in_apertures"] = inserted_vertices
# Cross-fitting checks exclude internal manufactured joins within the same supplied fitting.
checked_pairs = 0
for number in range(1, 7):
    selected = [(path, objs) for path, objs in instances.items() if f"/WestBay{number:02}/" in path]
    for index, (left_path, left) in enumerate(selected):
        for right_path, right in selected[index + 1:]:
            assert not tree(left).overlap(tree(right)), (left_path, right_path)
            checked_pairs += 1
report["cross_fitting_pairs_without_surface_intersection"] = checked_pairs
normal_error = 0
for objects in instances.values():
    for obj in objects:
        normal_error = max(normal_error,
            max(abs(normal.vector.length - 1) for normal in obj.data.corner_normals))
        for triangle in obj.data.loop_triangles:
            a, b, c = (obj.data.vertices[i].co for i in triangle.vertices)
            assert (b - a).cross(c - a).length > 1e-10
assert normal_error < .0001
report["imported_glb_max_normal_length_error"] = normal_error
report["imported_glb_degenerate_triangles"] = 0
all_points = [obj.matrix_world @ vert.co for objects in instances.values()
              for obj in objects for vert in obj.data.vertices]
low = [min(point[i] for point in all_points) for i in range(3)]
high = [max(point[i] for point in all_points) for i in range(3)]
report["assembled_godot_bounds"] = {"min": [low[0], low[2], -high[1]],
                                      "max": [high[0], high[2], -low[1]]}
report["assembled_totals"] = {
    key: sum(row[key] * (1 if asset == SHELL else 6)
             for asset, row in report["reused_assets"].items())
    for key in ("triangles", "source_vertices", "export_vertices", "source_meshes", "export_surfaces")}
for entry in report["inputs"]:
    assert fingerprint(ROOT / entry["path"]) == entry
report["dependencies_unchanged"] = True
report["ok"] = True
(SCRATCH / "geometry.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SCRATCH / "validated_assembly.blend"))
print("PASS", json.dumps(report["assembled_totals"]), flush=True)
