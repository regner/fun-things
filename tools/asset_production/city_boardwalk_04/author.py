"""Original twin-post coastal bent, with a ground pivot and two-metre bearing datum."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_boardwalk_04"
POST_CENTRES = (-1.38, 1.38)
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
    """Match the sibling slate palette with opaque Principled materials."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


slate = material("boardwalk_support_slate", (.048, .069, .078), .15, .58)
shoes = material("boardwalk_support_shoes", (.090, .126, .137), .20, .50)


def box(name, position, dimensions, mat, bevel):
    """Bake a closed softly rounded manufactured member and its corner normals."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.name, obj.dimensions = name, dimensions
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    for parent in list(obj.users_collection):
        parent.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    modifier = obj.modifiers.new("Quiet manufactured arris", "BEVEL")
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


# Crosshead bears against the sibling underside, not the walking surface.
box("Continuous crosshead", (0, 0, 1.84), (3.36, .48, .32), slate, .012)
for index, x in enumerate(POST_CENTRES):
    box(f"Post {index}", (x, 0, .89), (.34, .38, 1.62), slate, .012)
    box(f"Ground shoe {index}", (x, 0, .06), (.50, .56, .12), shoes, .014)
    box(f"Upper collar {index}", (x, 0, 1.61), (.44, .48, .14), shoes, .010)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "CityBoardwalk04_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityBoardwalk04", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "city_boardwalk.04"
root["authorship"] = "Original Blender construction by commissioned production specialist"
root["datum"] = "Ground Z=0; crosshead bearing Z=2; deck surface placed Z=2.24"
root["axes"] = "Blender +Y route maps to Godot -Z; crosshead spans X"
source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
source.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print("SOURCE_SAVED", source)
