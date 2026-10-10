"""Build a low rear annex matching the Crescents shop palette and attachment datum."""
import math
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_corner_shop_02"
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


def material(name, hex_color, metal=0, rough=.6):
    """Use opaque calibrated sRGB swatches without texture dependencies."""
    values = [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]
    rgb = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = rough
    mat.diffuse_color = (*rgb, 1)
    return mat


wall = material("shop_warm_stucco", "B9B7A4")
plinth = material("shop_petrol_plinth", "405B68")
blue = material("shop_cobalt_accent", "235FCC", .15, .42)
roof = material("shop_slate_blue_roof", "344D6C", .18, .5)
trim = material("shop_ivory_trim", "D6CFB7", .12, .48)
glass = material("shop_upper_opaque_glazing", "254957", .22, .28)


def finish(obj, name, mat, bevel=.015):
    """Bake soft edges into closed solids while retaining applied mesh transforms."""
    obj.name = name
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if bevel:
        mod = obj.modifiers.new("Broad softened edges", "BEVEL")
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
    normal = obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    normal.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=normal.name)
    obj.select_set(False)
    parts.append(obj)
    return obj


def prism(name, polygon, bottom, top, mat, bevel=.015):
    """Extrude a plan polygon into a closed editable architectural solid."""
    count = len(polygon)
    vertices = [(x, y, z) for z in (bottom, top) for x, y in polygon]
    faces = [tuple(reversed(range(count))), tuple(range(count, 2*count))]
    for i in range(count):
        j = (i + 1) % count
        faces.append((i, j, j+count, i+count))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, name, mat, bevel)


def box(name, x0, x1, y0, y1, z0, z1, mat, bevel=.015):
    """Create a dimensioned structural span without a runtime mesh primitive."""
    return prism(name, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, mat, bevel)


# +Y is the hidden attachment face. The annex is not a second shopfront: no duplicated
# door, sign, canopy or display hardware. High windows are integral shell detailing.
body = box("Annex_walls", -2.2, 2.2, -1.8, 1.8, 0, 2.85, wall, 0)
for vertex in body.data.vertices:
    if vertex.co.z > 2:
        vertex.co.z = 2.80 + (vertex.co.y + 2.0) * (.3 / 3.8)
parts.remove(body)
body.data.materials.clear()
finish(body, "Annex_walls", wall, .012)
for sign in (-1, 1):
    x = sign * 2.2
    box("Side_base", x-.018, x+.018, -1.8, 1.8, .025, .38, plinth, .008)
box("Rear_base", -2.2, 2.2, -1.825, -1.795, .025, .38, plinth, .008)
# Two quiet high windows on the outer rear, rather than a false accessible entrance.
for x in (-1.03, 1.03):
    box("High_window_frame", x-.83, x+.83, -1.86, -1.799, 1.98, 2.62, trim, .025)
    box("High_opaque_pane", x-.745, x+.745, -1.881, -1.858, 2.065, 2.535, glass, .012)
    box("High_window_sill", x-.88, x+.88, -1.94, -1.79, 1.93, 2.015, trim, .015)
# Low mono-pitch roof slopes away from the main building. Its front ends exactly at
# the attachment plane: no overlap into sibling geometry; overhead eaves elsewhere.
def sloped_box(name, x0, x1, y0, y1, bottom, thickness, mat, bevel=.015):
    """Shear a closed roof strip along its depth while preserving level attachment."""
    obj = box(name, x0, x1, y0, y1, bottom, bottom+thickness, mat, 0)
    for vertex in obj.data.vertices:
        vertex.co.z += (vertex.co.y + 2.0) * (.3 / 3.8)
    parts.remove(obj)
    obj.data.materials.clear()
    return finish(obj, name, mat, bevel)


sloped_box("Ivory_eave", -2.35, 2.35, -2.0, 1.8, 2.80, .10, trim, .02)
sloped_box("Slate_mono_pitch_roof", -2.35, 2.35, -2.0, 1.8, 2.90, .12, roof, .025)
# Broad seams establish a smaller utility roof rhythm without rooftop clutter.
for x in (-1.15, 0, 1.15):
    sloped_box("Roof_standing_seam", x-.025, x+.025, -1.86, 1.7, 3.015, .04, roof, .009)
box("Cobalt_rear_drip_edge", -2.35, 2.35, -2.015, -1.98, 2.86, 3.025, blue, .008)
box("Attachment_flashing", -2.2, 2.2, 1.72, 1.8, 3.285, 3.39, roof, .01)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "D02CornerShop02_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D02CornerShop02", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "d02_corner_shop.02"
root["provenance"] = "Original Blender construction; no external geometry or imagery"
root["attachment"] = "Local Godot Z=-1.8 meets shop Z=4.5 at root translation (0,0,6.3)"
root["front_axis"] = "Blender +Y maps to Godot -Z; hidden attachment face"
bpy.ops.mesh.primitive_cube_add(size=1, location=(8, 0, .5))
reference = bpy.context.object
reference.name = "authoring_1m_reference"
reference.hide_render = True
bpy.context.preferences.filepaths.save_version = 0
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
