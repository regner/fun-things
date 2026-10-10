"""Build the original closed municipal bin with the pinned Blender CLI."""
import math
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_waste_01"
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


# Muted family swatches: public furniture, not a pickup or an actor-colored beacon.
body = material("waste_body_petrol", (.035, .085, .090), .25, .49)
lid = material("waste_lid_sage", (.100, .165, .155), .25, .47)
recess = material("waste_recess_charcoal", (.016, .025, .029), .15, .60)
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


box("Recessed stationary plinth", (0, 0, .045), (.54, .44, .09), recess, .022)
box("Rounded municipal body", (0, 0, .455), (.60, .50, .79), body, .048)
box("Lid shadow seam", (0, 0, .822), (.622, .522, .044), recess, .028)
# A broad shallow barrel crown distinguishes the public bin from flat wheelie lids.
# The front face is closed; the inset below is a shut disposal flap, not an open cavity.
profile = [(-.33, .84), (.33, .84), (.33, .94)]
for index in range(17):
    angle = index * math.pi / 16
    profile.append((.33 * math.cos(angle), .94 + .11 * math.sin(angle)))
profile.append((-.33, .94))
# Remove adjacent duplicate shoulder points before face construction.
profile = [point for index, point in enumerate(profile)
           if index == 0 or point != profile[index - 1]]
count = len(profile)
vertices = [(x, y, z) for y in (-.29, .29) for x, z in profile]
faces = [tuple(reversed(range(count))), tuple(range(count, 2 * count))]
for index in range(count):
    following = (index + 1) % count
    faces.append((index, following, count + following, count + index))
mesh = bpy.data.meshes.new("Barrel crown topology")
mesh.from_pydata(vertices, [], faces)
mesh.update()
obj = bpy.data.objects.new("Barrel crown", mesh)
collection.objects.link(obj)
finish(obj, "Fixed barrel crown", lid, .014)
box("Closed chute surround", (0, .289, .901), (.44, .012, .105), recess, .018)
box("Shut push flap", (0, .297, .906), (.398, .012, .074), metal, .012)
# A flush broad door seam and one latch are enough at close inspection; no micro-grime.
box("Service door shadow", (0, .248, .443), (.45, .014, .566), recess, .034)
box("Closed service door", (0, .257, .443), (.434, .014, .550), body, .030)
box("Flush service latch", (.162, .266, .525), (.027, .009, .055), metal, .007)
bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "CityWaste01_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityWaste01", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "city_waste.01"
root["authorship"] = "Original Blender construction; commissioned implementation specialist"
root["front_axis"] = "Blender +Y maps to Godot -Z; shut flap faces front"
root["state"] = "Closed static; no collection, loot, destruction or moving parts"
root["ground_datum"] = "Ground-centered footprint; lowest plinth vertices Z=0"
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
print("CITY_WASTE_01_AUTHORED")
