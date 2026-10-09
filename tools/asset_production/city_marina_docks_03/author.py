"""Construct the original shore gangway with matching marina deck and metal guards."""
from pathlib import Path

import math

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_marina_docks_03"
WIDTH, LENGTH = 2.0, 8.0
RAMP_ANGLE = math.atan(1 / 6)
RAMP_LENGTH = math.sqrt(37)
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


def box(name, position, dimensions, mat, bevel, slope=False, rail=False):
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
    if slope:
        # Shear the finished local mesh so the deck top is exactly y=.5..1.5 in Godot.
        for vertex in obj.data.vertices:
            vertex.co.z -= (vertex.co.y + obj.location.y) / 6
    if rail:
        # Rails and their two authored box colliders share this rigid slope rotation.
        obj.rotation_euler.x = -RAMP_ANGLE
        obj.location = (position[0],
                        math.cos(RAMP_ANGLE) * position[1] + math.sin(RAMP_ANGLE) * position[2],
                        -math.sin(RAMP_ANGLE) * position[1] + math.cos(RAMP_ANGLE) * position[2] + 1.5)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    modifier = obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    parts.append(obj)



# The six-metre slope joins two one-metre flat landing plates without changing the family datum.
for label, y, height in (("Pontoon", 3.5, .5), ("Shore", -3.5, 1.5)):
    box(label + " backing", (0, y, height - .11), (1.80, 1, .10), frame, .01)
    box(label + " hinge shoe", (0, y, height - .19), (1.54, .64, .12), flotation, .03)
    for index in range(3):
        box(label + " plank", (0, y - .45 + (index + .5) * .30, height - .04),
            (1.76, .292, .08), deck_alt if index == 1 else deck, .006)
    for x in (-.94, .94):
        box(label + " pale edge", (x, y, height - .07), (.12, 1, .18), edge, .012)
    for end in (-.475, .475):
        box(label + " flush threshold", (0, y + end, height - .04),
            (1.76, .05, .08), edge, .004)
box("Ramp backing", (0, 0, .89), (1.80, 6, .10), frame, .01, slope=True)
for x in (-.77, .77):
    box("Ramp stringer", (x, 0, .835), (.16, 6, .17), frame, .015, slope=True)
for index in range(18):
    y = -3 + (index + .5) / 3
    box("Ramp composite plank %02d" % index, (0, y, .96),
        (1.76, 1 / 3 - .008, .08), deck_alt if index % 4 == 1 else deck, .006, slope=True)
for x in (-.94, .94):
    box("Ramp pale edge", (x, 0, .93), (.12, 6, .18), edge, .012, slope=True)
    # Closed manufactured rails/posts, no ropes or sparse wire that shimmers overhead.
    for height in (-.45, 0, .453197):
        box("Guard longitudinal rail", (x, 0, height),
            (.10, RAMP_LENGTH, .08), edge, .018, rail=True)
    for distance in (-RAMP_LENGTH / 2 + .04, -1, 1, RAMP_LENGTH / 2 - .04):
        box("Guard upright", (x, distance, 0), (.08, .08, .866394), edge, .012, rail=True)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "CityMarinaDocks03_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityMarinaDocks03", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "city_marina_docks.03"
root["authorship"] = "Original Blender construction; commissioned production specialist"
root["datum"] = "Water Z=0; Godot pontoon end (0,.5,-4), shore end (0,1.5,4)"
source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
source.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print("SOURCE_SAVED", source)
