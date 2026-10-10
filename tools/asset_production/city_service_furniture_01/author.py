"""Construct the original closed utility cabinet in pinned Blender; no external assets."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_service_furniture_01"
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


# Metres; front is Blender +Y. The broad cap determines the symmetrical plan bounds.
box("Raised plinth", (0, 0, .06), (1.12, .50, .12), frame, .015)
box("Closed steel housing", (0, 0, .775), (1.14, .49, 1.31), frame, .022)
box("Cap shadow seam", (0, 0, 1.4225), (1.16, .51, .025), recess, .006)
box("Weather cap", (0, 0, 1.4625), (1.20, .55, .075), enamel, .018)
box("Door perimeter recess", (0, .242, .775), (1.08, .022, 1.21), recess, .01)
box("Broad inset closed door", (0, .253, .775), (1.03, .022, 1.16), enamel, .010)
# A single broad side inset, not a grid of screws or textures.
for side in (-1, 1):
    box("Side inset", (side * .568, -.01, .79), (.014, .36, 1.12), enamel, .006)
for height in (.38, 1.17):
    box("Flush hinge", (-.493, .256, height), (.037, .024, .10), frame, .005)
box("Latch recess", (.415, .263, .81), (.065, .012, .145), recess, .005)
box("Flush latch", (.415, .270, .81), (.023, .008, .085), frame, .003)
# Three broad dark vent impressions are visual only; the enclosure stays sealed.
for height in (.34, .405, .47):
    box("Vent impression", (-.06, .265, height), (.49, .008, .027), recess, .003)
# Small generic warning plate; original geometric mark, no brand/copy dependency.
box("Warning plate", (.33, .266, 1.17), (.09, .008, .10), amber, .006)
box("Warning stem", (.33, .271, 1.183), (.012, .002, .037), recess, .0005)
box("Warning dot", (.33, .271, 1.151), (.012, .002, .011), recess, .0005)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "CityServiceFurniture01_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityServiceFurniture01", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "city_service_furniture.01"
root["authorship"] = "Original Blender construction by commissioned specialist, 2026-10-10"
root["front_axis"] = "Blender +Y -> Godot -Z"
root["pivot"] = "Ground-centred footprint (0,0,0)"
root["state"] = "Static closed cabinet; no electrical or interaction system"
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
print("CITY_SERVICE_FURNITURE_01_AUTHORED")
