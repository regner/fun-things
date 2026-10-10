"""Author the original short low plaza seat; all dimensions are provisional metres."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_seating_02"
WIDTH, DEPTH, HEIGHT = 1.50, .72, .46
SEAT_HEIGHT, SEAT_THICKNESS = .46, .09
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new("export_" + ASSET)
scene.collection.children.link(collection)
parts = []


def material(name, color, metallic, roughness):
    """Define the seating family's quiet opaque ivory, slate and petrol finishes."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


ivory = material("seating_ivory", (.82, .80, .67), 0, .48)
slate = material("seating_slate", (.23, .30, .34), .15, .48)
petrol = material("seating_petrol_trim", (.045, .10, .115), .35, .40)


def box(name, location, dimensions, mat, bevel):
    """Bake a closed rounded component and stable broad-face weighted normals."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    for parent in list(obj.users_collection):
        parent.objects.unlink(obj)
    collection.objects.link(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.materials.append(mat)
    modifier = obj.modifiers.new("Soft civic roundover", "BEVEL")
    modifier.width, modifier.segments = bevel, 3
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    modifier = obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    parts.append(obj)


# Backless and short: broad seat over a single recessed slate plinth, not a bench variant.
box("Continuous ivory seat", (0, 0, SEAT_HEIGHT - SEAT_THICKNESS / 2),
    (WIDTH, DEPTH, SEAT_THICKNESS), ivory, .035)
box("Recessed petrol seat rim", (0, 0, .3525), (1.42, .64, .045), petrol, .018)
box("Slate ground plinth", (0, 0, .17), (1.26, .50, .34), slate, .045)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "CitySeating02_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CitySeating02", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "city_seating.02"
root["authorship"] = "Original Blender construction; commissioned production specialist"
root["datum"] = "Ground-centred footprint at Z=0; seat top .46 m"
root["axes"] = "Front Blender +Y maps to Godot -Z; up +Z maps to +Y"
source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
source.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print("SOURCE_SAVED", source)
