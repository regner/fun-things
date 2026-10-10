"""Construct the original closed service door and surround in pinned Blender; no external assets."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_service_furniture_03"
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
    """Use opaque, back-culled Principled materials shared by the service family language."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*rgb, 1)
    shader = result.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = roughness
    return result


enamel = material("service_enamel", (.095, .16, .175), .35, .48)
frame = material("service_frame", (.035, .070, .085), .45, .50)
recess = material("service_recess", (.012, .023, .027), .20, .58)
amber = material("service_warning_amber", (.75, .39, .095), .05, .52)


def box(name, location, dimensions, mat, bevel=.008):
    """Make a closed softly bevelled manufactured part and bake its weighted normals."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    modifier = obj.modifiers.new("Manufactured edge", "BEVEL")
    modifier.width = bevel
    modifier.segments = 3
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


# Metres; Blender +Y faces the rear route. Frame ground centre is the mounting datum.
# Separate sealed shells meet as manufactured parts; no boolean slivers or open backs.
for x in (-.62, .62):
    box("Surround jamb", (x, 0, 1.16), (.12, .24, 2.32), frame, .012)
box("Surround head", (0, 0, 2.38), (1.36, .24, .12), frame, .012)
box("Flush sill", (0, 0, .02), (1.12, .24, .04), frame, .006)
box("Closed perimeter shadow", (0, .012, 1.17), (1.13, .05, 2.30), recess, .005)
box("Closed steel leaf", (0, .038, 1.17), (1.10, .072, 2.26), enamel, .012)
# Broad pressed panel and kick plate: restrained service language, no shop glazing.
box("Pressed panel shadow", (0, .074, 1.40), (.96, .010, 1.56), recess, .008)
box("Broad inset panel", (0, .080, 1.40), (.92, .014, 1.52), enamel, .009)
box("Kick plate", (0, .080, .28), (.96, .014, .30), frame, .008)
for height in (.35, 1.17, 1.99):
    box("Quiet hinge", (-.535, .081, height), (.045, .04, .14), frame, .007)
# A simple sealed lever assembly, not an interaction socket or moving component.
box("Latch backplate", (.405, .085, 1.08), (.07, .018, .21), frame, .008)
box("Lever standoff", (.405, .127, 1.12), (.042, .084, .042), frame, .008)
box("Short return lever", (.335, .165, 1.12), (.18, .030, .045), frame, .011)
box("Quiet key impression", (.405, .096, 1.02), (.014, .006, .025), recess, .002)
# A tiny blank amber identification plate is dressing, never essential camera information.
box("Service identification plate", (0, .094, 1.94), (.19, .012, .075), amber, .008)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "CityServiceFurniture03_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityServiceFurniture03", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "city_service_furniture.03"
root["authorship"] = "Original Blender construction by commissioned specialist, 2026-10-10"
root["front_axis"] = "Blender +Y -> Godot -Z"
root["pivot"] = "Ground-centred surround (0,0,0); handle overhangs toward +Y"
root["state"] = "Static closed service entry; no interior, opening or interaction system"
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
print("CITY_SERVICE_FURNITURE_03_AUTHORED")
