"""Construct an original sealed drain-cover overlay in pinned Blender, without external assets."""
import math
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_service_furniture_02"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new("export_" + ASSET)
scene.collection.children.link(collection)
parts = []


def material(name, rgb, metal, roughness):
    """Match the cabinet and door's opaque, back-culled Principled service palette."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*rgb, 1)
    shader = result.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = roughness
    return result


frame = material("service_frame", (.035, .070, .085), .45, .50)
recess = material("service_recess", (.012, .023, .027), .20, .58)
enamel = material("service_enamel", (.095, .160, .175), .35, .48)


def finish(obj, name, mat, bevel):
    """Bake gentle bevels and weighted normals on closed manufactured shells."""
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    modifier = obj.modifiers.new("Manufactured edge", "BEVEL")
    modifier.width = bevel
    modifier.segments = 2
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    for face in obj.data.polygons:
        face.use_smooth = True
    modifier = obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    parts.append(obj)
    return obj


def box(name, location, dimensions, mat, bevel=.0008):
    """Create one sealed shallow cover part; no open slot or subterranean geometry."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    return finish(obj, name, mat, bevel)


def rounded_loop(width, depth, radius):
    """Return a counter-clockwise rounded-rectangle loop with matching corner samples."""
    points = []
    for cx, cy, start in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        for step in range(7):
            angle = math.radians(start + step * 15)
            points.append((cx * (width / 2 - radius) + radius * math.cos(angle),
                           cy * (depth / 2 - radius) + radius * math.sin(angle)))
    return points


# Shallow sealed overlay: root rests on the existing uncut road/yard surface.
# 8 mm relief is rendering separation, not a step, drain opening or walkable deck.
outer = rounded_loop(.80, .60, .035)
inner = rounded_loop(.67, .47, .024)
count = len(outer)
vertices = [(x, y, z) for z in (0, .008) for loop in (outer, inner) for x, y in loop]
faces = []
for i in range(count):
    j = (i + 1) % count
    faces.extend(((i, j, j + 2 * count, i + 2 * count),
                  (i + count, i + 3 * count, j + 3 * count, j + count),
                  (i + 2 * count, j + 2 * count, j + 3 * count, i + 3 * count),
                  (i, i + count, j + count, j)))
mesh_data = bpy.data.meshes.new("Rounded cast rim")
mesh_data.from_pydata(vertices, [], faces)
mesh_data.update()
obj = bpy.data.objects.new("Rounded cast rim", mesh_data)
collection.objects.link(obj)
finish(obj, "Rounded cast rim", frame, .0008)
# Dark backing is above the receiving surface; slots never expose a hole or z-fight it.
box("Sealed slot backing", (0, 0, .0015), (.70, .50, .003), recess, .0006)
# Six broad grate ribs and a transverse tie give a quiet two-bank slot rhythm.
for x in (-.275, -.165, -.055, .055, .165, .275):
    box("Broad grate rib", (x, 0, .005), (.052, .462, .006), enamel)
# Tie sits 0.5 mm below rib tops, avoiding coplanar overlap at manufactured junctions.
box("Transverse cast tie", (0, 0, .005), (.662, .048, .005), enamel)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "CityServiceFurniture02_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityServiceFurniture02", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "city_service_furniture.02"
root["authorship"] = "Original Blender construction by commissioned specialist, 2026-10-10"
root["front_axis"] = "Blender +Y -> Godot -Z; bilateral ground fixture"
root["pivot"] = "Ground-contact footprint centre (0,0,0); top relief 0.008 m"
root["state"] = "Static sealed drain-cover dressing; no opening, drainage or interaction system"
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
print("CITY_SERVICE_FURNITURE_02_AUTHORED")
