"""Build the original closed domestic wheelie bin with the pinned Blender CLI."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_waste_02"
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


def material(name, color, metallic, roughness):
    """Create opaque, back-culled Principled surfaces without external dependencies."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


# The public-bin sibling owns the palette reference; this domestic shell is matte plastic.
body = material("waste_body_petrol", (.035, .085, .090), 0, .58)
lid = material("waste_lid_sage", (.100, .165, .155), 0, .54)
recess = material("waste_recess_charcoal", (.016, .025, .029), 0, .72)
metal = material("waste_hardware_slate", (.170, .215, .225), .50, .42)


def finish(obj, name, mat, bevel):
    """Apply soft manufactured edges and preserve closed, consistently wound subparts."""
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Manufactured edge radius", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    bmesh.ops.remove_doubles(mesh, verts=list(mesh.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(mesh, edges=list(mesh.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(mesh, faces=list(mesh.faces))
    mesh.to_mesh(obj.data)
    mesh.free()
    obj.data.update()
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    modifier = obj.modifiers.new("Weighted manufactured normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    parts.append(obj)
    return obj


def box(name, position, dimensions, mat, bevel):
    """Author one editable solid with literal metre dimensions."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.dimensions = dimensions
    return finish(obj, name, mat, bevel)


# Tapered closed molding, wider at the rim than at the ground-contact toe.
vertices = [(x * width / 2, y * depth / 2, z)
            for z, width, depth in ((0, .44, .43), (1.005, .56, .56))
            for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
faces = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4),
         (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
mesh = bpy.data.meshes.new("Tapered domestic molding")
mesh.from_pydata(vertices, [], faces)
mesh.update()
obj = bpy.data.objects.new("Tapered body", mesh)
collection.objects.link(obj)
finish(obj, "Tapered closed body", body, .032)
box("Closed lid shadow seam", (0, .01, 1.008), (.578, .61, .030), recess, .020)
box("Broad flat hinged lid", (0, .01, 1.045), (.60, .64, .070), lid, .028)
# Broad molded stiffening ribs, not a high-contrast recycling icon or text.
for x in (-.17, .17):
    box("Lid stiffening rib", (x, .015, 1.081), (.032, .41, .038), lid, .014)
box("Front lifting lip", (0, .316, 1.032), (.22, .028, .046), lid, .012)
# Rear handle has a genuine open finger gap, visible in side and detail views.
for x in (-.22, .22):
    box("Rear handle support", (x, -.320, 1.032), (.052, .170, .060), body, .014)
box("Rear carry bar", (0, -.380, 1.050), (.49, .060, .060), body, .020)
# Two stationary, closed wheel solids; their axes run along Blender X.
for x in (-.275, .275):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.11, depth=.07,
                                      location=(x, -.22, .11), rotation=(0, 1.57079632679, 0))
    finish(bpy.context.object, "Rear rubber wheel", recess, .008)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=.048, depth=.008,
                                      location=(x + (.036 if x > 0 else -.036), -.22, .11),
                                      rotation=(0, 1.57079632679, 0))
    finish(bpy.context.object, "Inset axle hub", metal, .003)
bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "CityWaste02_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityWaste02", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "city_waste.02"
root["authorship"] = "Original Blender construction; commissioned implementation specialist"
root["front_axis"] = "Blender +Y maps to Godot -Z; lifting lip faces front"
root["state"] = "Closed static; no collection, loot, destruction or moving parts"
root["ground_datum"] = "Ground-centered footprint; toe and rear wheels contact Z=0; rear handle overhang recorded"
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
print("CITY_WASTE_02_AUTHORED")
