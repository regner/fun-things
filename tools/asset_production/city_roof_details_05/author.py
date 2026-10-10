"""Author an original sealed gabled dormer in pinned Blender; no external geometry."""
from pathlib import Path

import math

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_roof_details_05"
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


def material(name, hex_rgb, metal, roughness):
    """Match the existing roof fittings' sRGB swatches in opaque linear Principled materials."""
    srgb = [int(hex_rgb[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    rgb = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in srgb]
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*rgb, 1)
    shader = result.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = roughness
    return result


petrol = material("dormer_dark_petrol", "273F43", .28, .52)
folded = material("dormer_folded_metal", "314D50", .30, .55)
shadow = material("dormer_shadow", "172B30", .05, .78)
# Glazing and a restrained bead match the accepted upper-facade window language.
glass = material("dormer_opaque_tint", "345D64", .18, .28)
bead = material("dormer_warm_bead", "C8C2AD", .22, .48)


def finish(obj, name, mat, bevel):
    """Bake restrained edge rounds and weighted normals on each closed manufactured solid."""
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    obj.data.materials.append(mat)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    modifier = obj.modifiers.new("Soft folded edge", "BEVEL")
    modifier.width = min(bevel, min(obj.dimensions) * .35)
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


def box(name, location, dimensions, mat, bevel=.012):
    """Build a closed rectangular component with applied scale."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    return finish(obj, name, mat, bevel)


def sloped_prism(name, width, depth, bottom_rear, bottom_front, top_rear, top_front, mat):
    """Build a sealed prism with independent top/bottom slopes; +Y is the downhill window front."""
    vertices = [(-width / 2, -depth / 2, bottom_rear),
                (width / 2, -depth / 2, bottom_rear),
                (width / 2, depth / 2, bottom_front),
                (-width / 2, depth / 2, bottom_front),
                (-width / 2, -depth / 2, top_rear),
                (width / 2, -depth / 2, top_rear),
                (width / 2, depth / 2, top_front),
                (-width / 2, depth / 2, top_front)]
    faces = [(3, 2, 1, 0), (0, 1, 5, 4), (1, 2, 6, 5),
             (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, name, mat, .001)


def gabled_prism(name, width, depth, bottom_rear, bottom_front, eave, peak, mat):
    """Extrude a five-sided house section with a roof-contact underside and sealed gables."""
    vertices = []
    for y, bottom in ((-depth / 2, bottom_rear), (depth / 2, bottom_front)):
        vertices.extend([(-width / 2, y, bottom), (width / 2, y, bottom),
                         (width / 2, y, eave), (0, y, peak), (-width / 2, y, eave)])
    faces = [tuple(reversed(range(5))), tuple(range(5, 10))]
    for i in range(5):
        j = (i + 1) % 5
        faces.append((i, j, j + 5, i + 5))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, name, mat, .001)


def frame_ring(name, width, height, border, y_back, y_front, mat, bevel):
    """Make one continuous closed rectangular ring rather than overlapping corner bars."""
    vertices = []
    for y in (y_back, y_front):
        for w, h in ((width, height), (width - 2 * border, height - 2 * border)):
            vertices.extend([(-w / 2, y, .30 - h / 2), (w / 2, y, .30 - h / 2),
                             (w / 2, y, .30 + h / 2), (-w / 2, y, .30 + h / 2)])
    faces = []
    for i in range(4):
        j = (i + 1) % 4
        faces.extend([(i, j, j + 8, i + 8), (i + 4, i + 12, j + 12, j + 4),
                      (i, i + 4, j + 4, j), (i + 8, j + 8, j + 12, i + 12)])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, name, mat, bevel)


# One fixed 30-degree interface: +Y downhill/front, origin at roof plane centre.
# Chimney .04 uses +Y uphill, so it needs 180-degree relative yaw on this same roof face.
PITCH = math.tan(math.radians(30))
sloped_prism("Contained apron flashing", 2.80, 3.00,
             1.5 * PITCH, -1.5 * PITCH, 1.5 * PITCH + .035, -1.5 * PITCH + .035, folded)
sloped_prism("Raised perimeter boot", 2.40, 2.60,
             1.30 * PITCH + .02, -1.30 * PITCH + .02,
             1.30 * PITCH + .16, -1.30 * PITCH + .16, shadow)
gabled_prism("Sealed dormer cheeks and gables", 2.20, 2.24,
             1.12 * PITCH + .04, -1.12 * PITCH + .04, 1.18, 1.84, petrol)
# Two closed inclined cap leaves meet under the ridge; no thin open render planes.
for side in (-1, 1):
    obj = sloped_prism("Folded gable cap", 2.56, 1.25,
                       1.075, 1.825, 1.175, 1.925, folded)
    # Local Y across the leaf maps to +/- X; slope rises toward the central ridge.
    obj.rotation_euler.z = side * math.pi / 2
    obj.location.x = side * .625
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)
# A shallow sealed window face overlays the solid gable: no interior or roof opening.
box("Dark window recess", (0, 1.145, .30), (1.96, .07, 1.40), shadow, .015)
frame_ring("Broad folded window frame", 2.00, 1.44, .085, 1.15, 1.245, folded, .012)
frame_ring("Narrow warm glazing bead", 1.85, 1.29, .026, 1.185, 1.252, bead, .006)
# One meeting stile only; large panes, no transoms or fine facade grid.
for side in (-1, 1):
    box("Opaque fixed pane", (side * .463, 1.188, .30), (.88, .045, 1.22), glass, .008)
box("Central meeting stile", (0, 1.223, .30), (.07, .062, 1.28), folded, .008)
box("Contained drip sill", (0, 1.23, -.455), (2.10, .20, .09), folded, .012)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "CityRoofDetails05_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityRoofDetails05", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "city_roof_details.05"
root["authorship"] = "Original Blender construction by commissioned asset specialist"
root["front_axis"] = "Blender +Y -> Godot -Z; Blender +Z -> Godot +Y"
root["pivot"] = "30-degree roof plane centre; +Y front/downhill; base extends below origin"
root["state"] = "Static roof-only decoration above 2.5m; sealed window, no rooftop access"
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
print("CITY_ROOF_DETAILS_05_AUTHORED")
