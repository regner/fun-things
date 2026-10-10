"""Construct the original corner connector and modular edge bumper; all dimensions are metres, Blender Z is up."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_marina_docks_04"
WIDTH, LENGTH = 3.0, 3.0
DECK_TOP, EDGE_TOP, FLOAT_BOTTOM = .50, .52, -.30
BOARD_COUNT = 8
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
rubber = material("dock_bumper_petrol_rubber", (.018, .045, .051), 0, .80)
frame = material("dock_frame_metal", (.055, .075, .079), .55, .44)


def box(name, position, dimensions, mat, bevel):
    """Make a closed softly bevelled component with baked transforms and normals."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.dimensions = dimensions
    finish(obj, name, mat, bevel)


def finish(obj, name, mat, bevel):
    """Bake closed manufactured geometry with consistent normals."""
    obj.name = name
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


# A broad sealed float supports the corner; no buoyancy simulation.
box("Sealed flotation body", (0, 0, (FLOAT_BOTTOM + .25) / 2),
    (WIDTH - .30, LENGTH - .28, .55), flotation, .12)
for x in (-.9, .9):
    box("Longitudinal bearer", (x, 0, .31), (.15, LENGTH - .20, .22), frame, .018)
for y in (-1.1, 0, 1.1):
    box("Transverse underdeck bearer", (0, y, .35), (WIDTH - .12, .12, .14), frame, .015)
# Backing closes narrow board joints; collision is an independent continuous slab.
box("Deck backing", (0, 0, .39), (WIDTH - .20, LENGTH - .16, .06), frame, .012)
pitch = (LENGTH - .20) / BOARD_COUNT
for index in range(BOARD_COUNT):
    y = -(LENGTH - .20) / 2 + pitch * (index + .5)
    box("Composite plank %02d" % index, (0, y, DECK_TOP - .04),
        (WIDTH - .24, pitch - .008, .08), deck_alt if index % 4 == 1 else deck, .008)
# Same restrained .01 perimeter; open joining edges retain only the visual pale lip.
for x in (-(WIDTH - .12) / 2, (WIDTH - .12) / 2):
    box("Pale longitudinal edge", (x, 0, EDGE_TOP - .09), (.12, LENGTH, .18), edge, .018)
for y in (-(LENGTH - .10) / 2, (LENGTH - .10) / 2):
    box("Pale end join strip", (0, y, EDGE_TOP - .09), (WIDTH - .24, .10, .18), edge, .012)

# A single closed L extrusion avoids overlapped/coplanar bumper corners.
outline = [(-1.62, -1.62), (1.48, -1.62), (1.48, -1.48),
           (-1.48, -1.48), (-1.48, 1.48), (-1.62, 1.48)]
vertices = [(x, y, z) for z in (.20, .46) for x, y in outline]
count = len(outline)
faces = [tuple(reversed(range(count))), tuple(range(count, 2 * count))]
faces += [(i, (i + 1) % count, (i + 1) % count + count, i + count)
          for i in range(count)]
data = bpy.data.meshes.new("Continuous corner rubber")
data.from_pydata(vertices, [], faces)
data.update()
obj = bpy.data.objects.new("Continuous corner rubber", data)
collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
finish(obj, obj.name, rubber, .045)


def assemble(root_name, datum):
    """Join this export's closed islands under an identity water-datum root."""
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = root_name + "_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new(root_name, None)
    collection.objects.link(root)
    mesh.parent = root
    root["asset_id"] = "city_marina_docks.04"
    root["authorship"] = "Original Blender construction; commissioned production specialist"
    root["datum"] = datum


assemble("CityMarinaDocks04", "Water Z=0, deck .50; joins Godot -Z/+X at 1.5m")
# Independent mounting pivot: centred along edge, at water level; Godot +Z faces water.
collection = bpy.data.collections.new("export_" + ASSET + "_bumper")
scene.collection.children.link(collection)
parts = []
box("Modular rounded rubber edge", (0, -.05, .33), (1.5, .14, .26), rubber, .045)
assemble("CityMarinaDocks04Bumper", "Water Z=0; edge anchor Y=0; Godot +Z faces water")
source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
source.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print("SOURCE_SAVED", source)
