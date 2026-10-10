"""Author the original compact hipped-roof Old Quay house shell; fittings stay linked separately."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_quay_frontages_03"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new("export_" + NID)
scene.collection.children.link(collection)
parts = []


def material(name, swatch, metal=0, rough=.62):
    """Convert original sRGB swatches to opaque Principled materials."""
    values = [int(swatch[i:i+2], 16)/255 for i in (0, 2, 4)]
    rgb = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in values]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = rough
    mat.diffuse_color = (*rgb, 1)
    return mat


wall = material("quay_muted_plum_render", "927380")
roof = material("quay_slate_roof", "394D62", .12, .52)
trim = material("quay_warm_stone_trim", "C8C2AD", .05, .57)
base = material("quay_petrol_plinth", "405B68", .05, .64)
accent = material("quay_amber_frontage", "DDA653", .05, .5)


def finish(obj, name, mat, bevel=.015):
    """Apply transforms, soft bevels and stable normals to a closed authored solid."""
    obj.name = name
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if bevel:
        mod = obj.modifiers.new("Soft architectural edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    mod = obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.select_set(False)
    parts.append(obj)
    return obj


def box(name, location, dimensions, mat, bevel=.015):
    """Create a measured Blender solid, never a runtime render primitive."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    return finish(obj, name, mat, bevel)


def hip_roof():
    """Build four uninterrupted roof slopes over one closed near-square hip volume."""
    a, b, ridge = 3.88, 4.08, .90
    corners = [(-a, -b), (a, -b), (a, b), (-a, b)]
    vertices = [(x, y, z) for z in (6.65, 6.87) for x, y in corners]
    vertices += [(0, -ridge, 8.95), (0, ridge, 8.95)]
    faces = [(3, 2, 1, 0), (4, 5, 8), (5, 6, 9, 8), (6, 7, 9), (7, 4, 8, 9)]
    faces += [(i, (i+1) % 4, (i+1) % 4 + 4, i+4) for i in range(4)]
    mesh = bpy.data.meshes.new("Four_slope_hip")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("Four_slope_hip", mesh)
    collection.objects.link(obj)
    return finish(obj, "Four_slope_hip", roof, .018)


# Compact residential infill: no retail canopy/fascia and no invented rooftop fittings.
body = box("Compact_house_body", (0, 0, 3.425), (7.2, 7.6, 6.85), wall, 0)
for x, front, width, bottom, top in [
    (2.45, 1, 1.42, -.1, 2.45), (-1, 1, 4.68, .96, 2.44),
    (0, 1, 4.68, 4.71, 6.19), (0, -1, 4.68, 4.71, 6.19),
    (0, -1, 4.68, .96, 2.44),
]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, front*3.575, (bottom+top)/2))
    cutter = bpy.context.object
    cutter.dimensions = (width, .85, top-bottom)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.context.view_layer.objects.active = body
    mod = body.modifiers.new("Shared fitting blind recess", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
parts.remove(body)
body.data.materials.clear()
finish(body, "Compact_house_body", wall, .012)
for x in (-3.6, 3.6):
    box("Side_plinth", (x, 0, .22), (.03, 7.6, .39), base, .006)
box("Rear_plinth", (0, -3.8, .22), (7.2, .03, .39), base, .006)
for x, width in [(-1.025, 5.15), (3.475, .25)]:
    box("Front_plinth", (x, 3.815, .22), (width, .03, .39), base, .006)
box("Front_storey_course", (0, 3.855, 4.40), (7.2, .11, .18), accent, .018)
box("Rear_storey_course", (0, -3.835, 4.40), (7.2, .07, .14), trim, .012)
box("Continuous_warm_eave", (0, 0, 6.60), (7.76, 8.16, .10), trim, .012)
hip_roof()
box("Short_hip_ridge_cap", (0, 0, 8.94), (.20, 1.84, .18), roof, .025)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "D05QuayFrontages03_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D05QuayFrontages03", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "d05_quay_frontages.03"
root["provenance"] = "Original Blender construction; shared fittings are separate linked resources"
root["front_axis"] = "Blender +Y maps to Godot -Z"
root["footprint_m"] = "7.2 wide x 7.6 deep; ground-centred; provisional"
bpy.ops.mesh.primitive_cube_add(size=1, location=(10, 0, .5))
reference = bpy.context.object
reference.name = "authoring_1m_reference"
reference.hide_render = True
bpy.context.preferences.filepaths.save_version = 0
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
