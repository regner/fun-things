"""Author the original two-bay Old Quay frontage row shell; fittings stay linked separately."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_quay_frontages_02"
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


wall = material("quay_ochre_render", "C49A65")
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


def section(name, profile, x0, x1, mat, bevel=.015):
    """Extrude a closed YZ roof profile along the broader frontage."""
    count = len(profile)
    vertices = [(x, y, z) for x in (x0, x1) for y, z in profile]
    faces = [tuple(reversed(range(count))), tuple(range(count, count*2))]
    for i in range(count):
        j = (i+1) % count
        faces.append((i, j, j+count, i+count))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, name, mat, bevel)


# Two attached shop bays under one transverse pitched roof, not two scaled narrow houses.
body = section("Two_storey_row", [(-4, 0), (4, 0), (4, 6.85),
               (0, 9.11), (-4, 6.85)], -6.4, 6.4, wall, 0)
for bay in (-3.2, 3.2):
    for x, front, width, bottom, top in [
        (bay+1.95, 1, 1.42, -.1, 2.45), (bay-.95, 1, 3.04, .54, 2.42),
        (bay, 1, 4.68, 4.71, 6.19), (bay, -1, 4.68, 4.71, 6.19),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, front*3.775, (bottom+top)/2))
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
finish(body, "Two_storey_row", wall, .012)
for x in (-6.4, 6.4):
    box("Side_plinth", (x, 0, .22), (.03, 8, .39), base, .006)
box("Rear_plinth", (0, -4, .22), (12.8, .03, .39), base, .006)
for bay in (-3.2, 3.2):
    for x, width in [(-1.1, 4.2), (3.02, .36)]:
        box("Front_plinth", (bay+x, 4.015, .22), (width, .03, .39), base, .006)
# A quiet central pier articulates the attached plots without inventing a passage.
box("Shared_party_pier", (0, 4.025, 3.25), (.18, .05, 6.05), trim, .01)
box("Front_storey_course", (0, 4.055, 4.40), (12.8, .11, .18), accent, .018)
box("Rear_storey_course", (0, -4.035, 4.40), (12.8, .07, .14), trim, .012)
section("Warm_eave_and_rakes", [(-4.28, 6.55), (0, 9.0), (4.28, 6.55),
        (4.28, 6.65), (0, 9.1), (-4.28, 6.65)], -6.68, 6.68, trim, .012)
section("Quiet_transverse_slate_pitch", [(-4.28, 6.65), (0, 9.1), (4.28, 6.65),
        (4.28, 6.87), (0, 9.32), (-4.28, 6.87)], -6.68, 6.68, roof, .018)
box("Low_transverse_ridge_cap", (0, 0, 9.30), (13.38, .20, .20), roof, .035)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "D05QuayFrontages02_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D05QuayFrontages02", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "d05_quay_frontages.02"
root["provenance"] = "Original Blender construction; shared fittings are separate linked resources"
root["front_axis"] = "Blender +Y maps to Godot -Z"
root["footprint_m"] = "12.8 wide x 8 deep; ground-centred; provisional"
bpy.ops.mesh.primitive_cube_add(size=1, location=(15, 0, .5))
reference = bpy.context.object
reference.name = "authoring_1m_reference"
reference.hide_render = True
bpy.context.preferences.filepaths.save_version = 0
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
