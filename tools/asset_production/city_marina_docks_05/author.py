"""Author an original small twin-horn dock cleat in metres, with a deck-contact pivot."""
import math
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_marina_docks_05"
BASE_LENGTH, BASE_WIDTH, BASE_HEIGHT = .32, .16, .028
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
    """Keep the marina's quiet opaque metal family without texture dependencies."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


frame = material("dock_frame_metal", (.055, .075, .079), .55, .44)
satin = material("dock_cleat_satin_metal", (.32, .37, .36), .65, .36)


def finish(obj, name, mat, bevel=0):
    """Bake roundovers, clean closed topology and preserve broad smooth highlights."""
    obj.name = name
    for parent in list(obj.users_collection):
        parent.objects.unlink(obj)
    collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new("Manufactured roundover", "BEVEL")
        modifier.width, modifier.segments = bevel, 3
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    modifier = obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    parts.append(obj)


def box(name, location, dimensions, mat, bevel):
    """Create a closed base plate with a deck-contact lower face."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    finish(obj, name, mat, bevel)


def swept_horn():
    """Make one continuous tapered crossbar with rounded, gently lifted horn ends."""
    # X, centre Z, transverse radius, vertical radius. Ends are capped, not zero-area tips.
    rings = [(-.24, .139, .008, .008), (-.232, .139, .013, .011),
             (-.18, .128, .023, .017), (-.11, .115, .034, .024),
             (-.06, .113, .038, .027), (.06, .113, .038, .027),
             (.11, .115, .034, .024), (.18, .128, .023, .017),
             (.232, .139, .013, .011), (.24, .139, .008, .008)]
    count = 16
    vertices = [(x, ry * math.cos(i * math.tau / count),
                 z + rz * math.sin(i * math.tau / count))
                for x, z, ry, rz in rings for i in range(count)]
    faces = [tuple(reversed(range(count)))]
    for ring in range(len(rings) - 1):
        for i in range(count):
            a, b = ring * count + i, ring * count + (i + 1) % count
            faces.append((a, b, b + count, a + count))
    faces.append(tuple(range((len(rings) - 1) * count, len(rings) * count)))
    mesh = bpy.data.meshes.new("Continuous twin horn")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("Continuous twin horn", mesh)
    collection.objects.link(obj)
    finish(obj, obj.name, satin)


box("Deck mounting plate", (0, 0, BASE_HEIGHT / 2),
    (BASE_LENGTH, BASE_WIDTH, BASE_HEIGHT), frame, .012)
# Two tapered legs leave a genuine open throat; no fake black face or rope geometry.
for x in (-.073, .073):
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=.032, radius2=.024,
                                   depth=.083, location=(x, 0, .0645))
    finish(bpy.context.object, "Cast support leg", satin, .006)
swept_horn()
for x in (-.115, .115):
    for y in (-.050, .050):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=.012, depth=.009,
                                           location=(x, y, .0305))
        finish(bpy.context.object, "Restrained hex fastener", satin, .0015)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "CityMarinaDocks05_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityMarinaDocks05", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "city_marina_docks.05"
root["authorship"] = "Original Blender construction; commissioned production specialist"
root["datum"] = "Deck-contact base Z=0; mount at Godot Y=.50 on marina composite, not pale lip"
root["axes"] = "Horn long axis X; Blender +Z maps to Godot +Y, +Y maps to -Z"
source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
source.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print("SOURCE_SAVED", source)
