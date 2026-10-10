"""Author an original sealed roof-access housing in pinned Blender; no external geometry."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_roof_details_03"
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


petrol = material("roof_access_dark_petrol", "273F43", .28, .52)
folded = material("roof_access_folded_metal", "314D50", .30, .55)
shadow = material("roof_access_shadow", "172B30", .05, .78)


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
    """Construct a sealed shallow shed profile; front is Blender +Y, Godot -Z."""
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
    return finish(obj, name, mat, .018)


# A contained level-roof interface, consistent with roof fittings .01/.02.
box("Continuous roof flashing", (0, 0, .02), (3.20, 3.80, .04), folded, .008)
box("Raised sealed curb", (0, 0, .13), (3.04, 3.64, .22), shadow, .022)
sloped_prism("Sealed access housing", 2.90, 3.50, .18, .18, 2.59, 2.72, petrol)
# Broad shallow fall to rear: the cap silhouette, not tiny equipment, defines the roof.
sloped_prism("Folded drip cap", 3.12, 3.72, 2.56, 2.70, 2.71, 2.85, folded)
# Closed service face is integral decoration, with no opening, hinge pivot or interior.
box("Door perimeter shadow", (0, 1.759, 1.30), (1.24, .036, 2.20), shadow, .012)
box("Fixed access leaf", (0, 1.785, 1.30), (1.10, .040, 2.08), petrol, .018)
box("Quiet kick plate", (0, 1.809, .44), (1.00, .018, .27), folded, .009)
box("Door head drip", (0, 1.813, 2.44), (1.36, .12, .065), folded, .016)
box("Latch backplate", (.39, 1.814, 1.25), (.10, .025, .25), shadow, .009)
box("Static pull", (.39, 1.844, 1.25), (.038, .040, .18), folded, .010)
# A single sparse side intake breaks the service mass without a noisy grille.
box("Side intake shadow", (1.455, -.67, 1.93), (.035, .94, .47), shadow, .014)
for height in (1.79, 1.94, 2.09):
    box("Broad intake blade", (1.482, -.67, height), (.055, .86, .075), petrol, .014)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "CityRoofDetails03_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityRoofDetails03", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "city_roof_details.03"
root["authorship"] = "Original Blender construction by commissioned asset specialist"
root["front_axis"] = "Blender +Y -> Godot -Z; Blender +Z -> Godot +Y"
root["pivot"] = "Level roof-contact flashing centre at (0,0,0)"
root["state"] = "Static closed housing; no interior, rooftop access or moving parts"
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
print("CITY_ROOF_DETAILS_03_AUTHORED")
