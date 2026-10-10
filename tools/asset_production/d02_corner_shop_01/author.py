"""Build the original Crescents wedge shell; shared frontage hardware is not copied."""
import math
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_corner_shop_01"
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
warm = material("shop_entry_amber", "FFC05A", .05, .45)


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


# Plan: broad street frontage and narrow rear; neither roads nor garden terrain are authored.
# A single closed wall solid avoids coplanar seams. Blind recesses stop 650 mm behind
# the facade, beyond the shared door's 540 mm and window's 200 mm required voids.
body = prism("Wedge_walls", [(-2.4, -5), (2.4, -5), (6.4, 4), (-6.4, 4)],
             0, 6.55, wall, 0)
for x, width, bottom, top in [(0, 1.42, -.1, 2.45),
                              (-3.6, 3.04, .54, 2.42), (3.6, 3.04, .54, 2.42)]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 3.775, (bottom+top)/2))
    cutter = bpy.context.object
    cutter.dimensions = (width, .85, top-bottom)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.context.view_layer.objects.active = body
    cut = body.modifiers.new("Shared fitting recess", "BOOLEAN")
    cut.operation = "DIFFERENCE"
    cut.solver = "EXACT"
    cut.object = cutter
    bpy.ops.object.modifier_apply(modifier=cut.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
parts.remove(body)
body.data.materials.clear()
finish(body, "Wedge_walls", wall, .015)
# Quiet ground skirt follows side/rear walls, never crossing the shared display/door openings.
for sign in (-1, 1):
    points = [(sign*2.44, -5), (sign*6.44, 4), (sign*6.395, 4), (sign*2.395, -5)]
    prism("Diagonal_base", points, .025, .38, plinth, .008)
box("Rear_base", -2.4, 2.4, -5.015, -4.93, .025, .38, plinth, .008)
# Single broad blue transom; shared sign/canopies remain separate linked assets.
box("Blue_front_band", -6.28, 6.28, 4.012, 4.09, 4.28, 4.52, blue, .018)
# Upper-storey windows belong to this shell, rather than a second reusable hardware asset.
for x in (-3.6, 0, 3.6):
    box("Upper_frame", x-1.28, x+1.28, 4.012, 4.085, 4.85, 6.2, trim, .035)
    box("Upper_dark_pair", x-1.17, x+1.17, 4.085, 4.105, 4.96, 6.09, glass, .018)
    box("Upper_mullion", x-.035, x+.035, 4.105, 4.13, 4.96, 6.09, trim, .006)
    box("Upper_sill", x-1.34, x+1.34, 4.00, 4.22, 4.80, 4.90, trim, .02)
# Warm jamb accents flank, but do not duplicate, the accepted recessed surround.
for x in (-.91, .91):
    box("Warm_entry_jamb", x-.07, x+.07, 4.015, 4.065, .4, 2.35, warm, .015)
# Broad convex curved front eave: y=4.25 at ends and 4.65 at centre.
arc = [(6.65*math.cos(t), 4.25+.4*math.sin(t))
       for t in [math.pi*i/24 for i in range(25)]]
outline = [(-2.65, -5.25), (2.65, -5.25)] + arc
prism("Curved_ivory_eave", outline, 6.55, 6.72, trim, .025)
prism("Quiet_blue_roof", outline, 6.72, 7.04, roof, .045)
# A raised curved cobalt lip makes the road-facing gesture readable from overhead.
outer = [(x, y) for x, y in arc]
inner = [(x*.978, y-.20) for x, y in reversed(arc)]
prism("Curved_blue_roof_lip", outer+inner, 7.035, 7.18, blue, .015)
# Sparse back ridge cap, intentionally lower than the broad street-side arc.
box("Rear_roof_seam", -1.9, 1.9, -4.4, -4.25, 7.035, 7.10, roof, .02)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "D02CornerShop01_Mesh"
# Centre the bounding wall footprint on the ground pivot; roof overhang stays asymmetric.
for vertex in mesh.data.vertices:
    vertex.co.y += .5
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D02CornerShop01", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "d02_corner_shop.01"
root["provenance"] = "Original Blender construction; no external geometry or imagery"
root["footprint_blender_xy"] = "(-2.4,-4.5), (2.4,-4.5), (6.4,4.5), (-6.4,4.5)"
root["rear_annex_interface"] = "Rear wall y=-4.5; centre x=0; no interior passage"
# Metre fixture is saved but excluded from export.
bpy.ops.mesh.primitive_cube_add(size=1, location=(15, 0, .5))
reference = bpy.context.object
reference.name = "authoring_1m_reference"
reference.hide_render = True
bpy.context.preferences.filepaths.save_version = 0
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
