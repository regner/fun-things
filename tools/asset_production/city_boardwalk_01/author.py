"""Author the original straight coastal deck; metres, +Y along route, +Z up."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_boardwalk_01"
WIDTH, LENGTH, DEPTH = 3.6, 6.0, .24
BOARD_COUNT, BOARD_GAP, BOARD_DEPTH = 20, .012, .08
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new("export_" + ASSET)
scene.collection.children.link(collection)
parts = []


def material(name, color, metallic=0, roughness=.68):
    """Use quiet opaque Principled colours without procedural texture dependencies."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


wood = material("boardwalk_timber_warm", (.235, .145, .085))
wood_light = material("boardwalk_timber_light", (.260, .166, .101))
wood_muted = material("boardwalk_timber_muted", (.215, .136, .085))
slate = material("boardwalk_underdeck_slate", (.048, .069, .078), .15, .58)


def box(name, position, dimensions, mat, bevel):
    """Construct a closed rounded component and bake weighted corner normals."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    for parent in list(obj.users_collection):
        parent.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    modifier = obj.modifiers.new("Soft timber arris", "BEVEL")
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


# The shallow core closes visual seams; exposed fascia, coast supports and rail are other IDs.
box("Recessed underdeck core", (0, 0, -(DEPTH + BOARD_DEPTH) / 2),
    (WIDTH - .08, LENGTH, DEPTH - BOARD_DEPTH), slate, .008)
pitch = LENGTH / BOARD_COUNT
palette = (wood, wood, wood_light, wood, wood_muted, wood, wood_light, wood)
for index in range(BOARD_COUNT):
    # Half-gap at each terminal preserves the same seam rhythm when repeated at 6 m centres.
    y = -LENGTH / 2 + (index + .5) * pitch
    box(f"Cross-deck timber {index:02d}", (0, y, -BOARD_DEPTH / 2),
        (WIDTH, pitch - BOARD_GAP, BOARD_DEPTH), palette[index % len(palette)], .004)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "CityBoardwalk01_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityBoardwalk01", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "city_boardwalk.01"
root["authorship"] = "Original Blender construction by commissioned production specialist"
root["datum"] = "Deck surface Z=0; underside Z=-.24; route ends Y=+/-3"
root["axes"] = "Blender +Y route maps to Godot -Z; +Z up maps to +Y"
source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
source.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print("SOURCE_SAVED", source)
