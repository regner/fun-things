"""Original level flared timber access with a flush slate promenade threshold."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_boardwalk_05"
LENGTH = 3.0
ENTRY_HALF_WIDTH = 1.8
EXIT_HALF_WIDTH = 2.4
BOARD_PITCH = .3
HALF_SEAM = .006
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
    """Match the sibling opaque Principled palette without texture dependencies."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


slate = material("boardwalk_underdeck_slate", (.048, .069, .078), .15, .58)
timbers = [material("boardwalk_timber_" + name, color, 0, .68) for name, color in (
    ("warm", (.235, .145, .085)), ("light", (.260, .166, .101)),
    ("muted", (.215, .136, .085)),
)]
threshold = material("boardwalk_access_threshold", (.090, .126, .137), .20, .50)


def half_width(y):
    """Widen the access symmetrically toward the promenade, without rotating its datum."""
    return ENTRY_HALF_WIDTH + (EXIT_HALF_WIDTH - ENTRY_HALF_WIDTH) * y / LENGTH


def prism(name, start, end, bottom, top, inset, mat, bevel):
    """Author a closed tapered strip, with optional baked soft arrises and weighted normals."""
    outline = [(-half_width(start) + inset, start), (half_width(start) - inset, start),
               (half_width(end) - inset, end), (-half_width(end) + inset, end)]
    vertices = [(x, y, z) for z in (bottom, top) for x, y in outline]
    faces = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if bevel:
        modifier = obj.modifiers.new("Quiet rounded arris", "BEVEL")
        modifier.width, modifier.segments = bevel, 2
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


# Core has the family 40 mm lateral recess; connector planes stay exact.
prism("Tapered structural backing", 0, LENGTH, -.24, -.08, .04, slate, 0)
for index in range(9):
    prism(f"Flared cross timber {index:02d}", index * BOARD_PITCH + HALF_SEAM,
          (index + 1) * BOARD_PITCH - HALF_SEAM, -.08, 0, 0,
          timbers[index % 3], .004)
# This narrow flush band is integral access hardware, not a paved sidewalk or raised curb.
prism("Flush promenade threshold", 2.706, LENGTH, -.08, 0, 0, threshold, .004)
bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "CityBoardwalk05_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityBoardwalk05", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "city_boardwalk.05"
root["authorship"] = "Original Blender construction by commissioned production specialist"
root["datum"] = "Entry walking surface at origin; promenade end Blender Y=3; level Z=0"
root["axes"] = "Blender +Y landward maps to Godot -Z; +Z maps to +Y"
source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
source.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print("SOURCE_SAVED", source)
