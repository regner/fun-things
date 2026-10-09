"""Construct the original main pontoon; all dimensions are metres, Blender Z is up."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_marina_docks_01"
WIDTH, LENGTH = 3.0, 8.0
DECK_TOP, EDGE_TOP, FLOAT_BOTTOM = .50, .52, -.30
BOARD_COUNT = 20
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new("export_" + ASSET)
scene.collection.children.link(collection)
parts = []


def material(name, color, metallic=0, roughness=.6):
    """Use opaque original palette materials without procedural or embedded textures."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


deck = material("dock_deck_dark_composite", (.075, .090, .085))
deck_alt = material("dock_deck_soft_variation", (.082, .098, .092))
edge = material("dock_edge_warm_pale", (.57, .59, .51), .12, .48)
flotation = material("dock_float_petrol", (.018, .045, .051), 0, .54)
frame = material("dock_frame_metal", (.055, .075, .079), .55, .44)


def box(name, position, dimensions, mat, bevel):
    """Make a closed softly bevelled component with baked transforms and normals."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    for parent in list(obj.users_collection):
        parent.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    modifier = obj.modifiers.new("Manufactured roundover", "BEVEL")
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


# Twin sealed floats sit below the water datum; no buoyancy or mooring simulation.
for x in (-.92, .92):
    box("Sealed flotation body", (x, 0, -.025), (.78, 7.72, .55), flotation, .12)
    box("Longitudinal bearer", (x, 0, .31), (.15, 7.80, .22), frame, .018)
for y in (-3.5, -1.75, 0, 1.75, 3.5):
    box("Transverse underdeck bearer", (0, y, .35), (2.88, .12, .14), frame, .015)
# Dark backing closes the board gaps visually; independent deck slab collision is continuous.
box("Deck backing", (0, 0, .39), (2.80, 7.84, .06), frame, .012)
pitch = 7.8 / BOARD_COUNT
for index in range(BOARD_COUNT):
    y = -3.9 + pitch * (index + .5)
    box("Composite plank %02d" % index, (0, y, .46),
        (2.76, pitch - .008, .08), deck_alt if index % 4 == 1 else deck, .008)
# Flush rectangular end interfaces: no protruding fasteners, cleats or bumper kit duplication.
for x in (-1.44, 1.44):
    box("Pale longitudinal edge", (x, 0, .43), (.12, LENGTH, .18), edge, .018)
for y in (-3.95, 3.95):
    box("Pale end join strip", (0, y, .43), (2.76, .10, .18), edge, .012)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "CityMarinaDocks01_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityMarinaDocks01", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "city_marina_docks.01"
root["authorship"] = "Original Blender construction; commissioned production specialist"
root["datum"] = "Waterline Z=0; deck Z=.50; end joins Y=+/-4; Blender +Y maps to Godot -Z"
source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
source.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print("SOURCE_SAVED", source)
