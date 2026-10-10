"""Author an original sealed pitched-roof chimney in pinned Blender; no external geometry."""
from pathlib import Path

import math

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_roof_details_04"
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


petrol = material("chimney_dark_petrol", "273F43", .28, .52)
folded = material("chimney_folded_metal", "314D50", .30, .55)
shadow = material("chimney_shadow", "172B30", .05, .78)


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
    """Build a sealed prism with independent top/bottom slopes; +Y is uphill."""
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
    return finish(obj, name, mat, .002)


# One reversible 30-degree interface: +Y uphill, root on the roof plane at its centre.
PITCH = math.tan(math.radians(30))
sloped_prism("Contained apron flashing", 1.30, 1.50,
             -.75 * PITCH, .75 * PITCH, -.75 * PITCH + .035, .75 * PITCH + .035, folded)
sloped_prism("Raised counterflashing boot", .96, 1.08,
             -.54 * PITCH + .02, .54 * PITCH + .02,
             -.54 * PITCH + .22, .54 * PITCH + .22, shadow)
sloped_prism("Quiet rendered stack", .76, .80,
             -.40 * PITCH + .035, .40 * PITCH + .035, 1.30, 1.30, petrol)
box("Overhanging coping", (0, 0, 1.32), (1.0, 1.04, .16), folded, .025)
bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.165, depth=.02,
                                   location=(0, 0, 1.406))
finish(bpy.context.object, "Recessed flue floor", shadow, .002)


def chimney_pot():
    """Revolve a closed annular section: actual bore, thick lip and no open mesh edges."""
    profile = [(1.39, .25), (1.46, .25), (1.82, .22), (1.84, .275),
               (1.96, .275), (1.96, .175), (1.84, .175), (1.46, .16), (1.39, .16)]
    segments = 24
    vertices = [(radius * math.cos(i * math.tau / segments),
                 radius * math.sin(i * math.tau / segments), height)
                for height, radius in profile for i in range(segments)]
    faces = []
    for ring in range(len(profile)):
        other = (ring + 1) % len(profile)
        for i in range(segments):
            j = (i + 1) % segments
            faces.append((ring * segments + i, ring * segments + j,
                          other * segments + j, other * segments + i))
    data = bpy.data.meshes.new("Hollow chimney pot")
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new("Hollow chimney pot", data)
    collection.objects.link(obj)
    finish(obj, "Tapered pot with rolled lip", petrol, .006)


chimney_pot()

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "CityRoofDetails04_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityRoofDetails04", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "city_roof_details.04"
root["authorship"] = "Original Blender construction by commissioned asset specialist"
root["front_axis"] = "Blender +Y -> Godot -Z; Blender +Z -> Godot +Y"
root["pivot"] = "30-degree roof plane centre; +Y uphill; base extends below origin"
root["state"] = "Static roof-only decoration above 2.5m; no smoke or rooftop access"
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
print("CITY_ROOF_DETAILS_04_AUTHORED")
