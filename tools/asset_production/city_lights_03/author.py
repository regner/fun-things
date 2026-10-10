"""Construct the original twin-head yard pole with the accepted light-family finish."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_lights_03"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
POLE_TOP_M = 8.05
HEAD_CENTRES_X_M = (-1.0, 1.0)


def material(name, rgb, metal=0.0, rough=0.45, emission=0.0):
    """Use the sibling light's opaque Principled palette, without texture dependencies."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    for key, value in {"Base Color": (*rgb, 1), "Metallic": metal, "Roughness": rough,
                       "Emission Color": (*rgb, 1), "Emission Strength": emission}.items():
        shader.inputs[key].default_value = value
    mat.diffuse_color = (*rgb, 1)
    return mat


def finish(obj, name, mat, bevel=0.0):
    """Apply static transforms/bevels and clean welded, outward-facing closed components."""
    obj.name = name
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Soft manufactured edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    bmesh.ops.remove_doubles(mesh, verts=list(mesh.verts), dist=0.000001)
    bmesh.ops.dissolve_degenerate(mesh, edges=list(mesh.edges), dist=0.000001)
    bmesh.ops.recalc_face_normals(mesh, faces=list(mesh.faces))
    mesh.to_mesh(obj.data)
    mesh.free()
    obj.data.update()
    for face in obj.data.polygons:
        face.use_smooth = True
    modifier = obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    parts.append(obj)
    return obj


def box(name, location, dimensions, mat, bevel):
    """Create an editable rounded casting, not a Godot-generated render primitive."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    return finish(obj, name, mat, bevel)


def lathe(name, rings, mat):
    """Build a capped twenty-sided pole profile in metres."""
    count = 20
    vertices = [(r * math.cos(i * math.tau / count), r * math.sin(i * math.tau / count), z)
                for z, r in rings for i in range(count)]
    faces = [tuple(reversed(range(count)))]
    for ring in range(len(rings) - 1):
        for i in range(count):
            a, b = ring * count + i, ring * count + (i + 1) % count
            faces.append((a, b, b + count, a + count))
    faces.append(tuple(range((len(rings) - 1) * count, len(rings) * count)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, name, mat, 0.008)


def aim(obj, target):
    """Orient studio lights and cameras without affecting exported geometry."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def light(name, location, power, size):
    """Create an isolated broad studio softbox, excluded from export."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.shape, data.size = power, "DISK", size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    aim(obj, (0, 0, 4))


assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f"export_{ASSET}")
scene.collection.children.link(collection)
parts = []
petrol = material("pole_petrol", (0.025, 0.075, 0.09), 0.45, 0.46)
trim = material("fixture_rim", (0.07, 0.13, 0.15), 0.50, 0.42)
recess = material("service_recess", (0.012, 0.025, 0.03), 0.25, 0.50)
warm = material("lens_warm", (0.95, 0.69, 0.32), 0.0, 0.32, 0.45)
cool = material("lens_cool", (0.46, 0.78, 0.92), 0.0, 0.32, 0.45)
cool.use_fake_user = True

# A wider cast shoe and quiet tapered mast distinguish yard scale without busy bracing.
lathe("Cast ground shoe", [(0, .28), (.06, .28), (.10, .25), (.36, .22), (.42, .18)], petrol)
lathe("Foot collar", [(.34, .225), (.40, .225)], trim)
lathe("Tapered yard mast", [(.12, .17), (.50, .17), (.67, .135), (POLE_TOP_M, .09)], petrol)
box("Service hatch recess", (0, .158, .79), (.135, .035, .34), recess, .022)
box("Service hatch cover", (0, .179, .79), (.105, .018, .296), petrol, .019)
# Short horizontal crosshead and two forward arms give the twin lamps a connected T silhouette.
box("Crosshead", (0, -.035, 8.025), (2.15, .22, .22), petrol, .055)
for x in HEAD_CENTRES_X_M:
    side = "Left" if x < 0 else "Right"
    # Rear-entry support stops before the lens face instead of occluding its lit area.
    box(f"{side} arm", (x, -.12, 8.07), (.18, .30, .18), petrol, .045)
    box(f"{side} lower housing", (x, .46, 8.20), (.90, 1.40, .18), trim, .085)
    box(f"{side} canopy", (x, .44, 8.31), (.84, 1.31, .18), petrol, .08)
    box(f"{side} gasket", (x, .54, 8.113), (.76, 1.11, .034), recess, .07)
    box(f"{side} lens", (x, .54, 8.096), (.66, 1.00, .034), warm, .065)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "CityLights03_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityLights03", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "city_lights.03"
root["front_axis"] = "Blender +Y maps to Godot -Z; +Z maps to +Y"
root["ground_pivot"] = "Mast foot centre (0,0,0); no placement correction"
root["authorship"] = "Original Blender construction by commissioned Codex specialist, 2026-10-10"

# Studio is deliberately separate from the named export collection.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.19, .24, .29, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .5
bpy.ops.mesh.primitive_plane_add(size=200)
ground = bpy.context.object
ground.name = "STUDIO_ground"
ground.location.z = -.015
ground.data.materials.append(material("STUDIO_slate", (.15, .19, .22), 0, .65))
light("STUDIO_key", (5, 5, 12), 2300, 8)
light("STUDIO_rim", (-5, -4, 9), 2600, 6)
light("STUDIO_fill", (1, 6, 4), 700, 5)
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new("STUDIO_camera", data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_percentage = 100
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.compression = 95
scene.view_settings.view_transform = "AgX"
data.type = "ORTHO"
data.ortho_scale = 17.0
camera.location = (11, 16, 10)
aim(camera, (0, .15, 4.1))
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
for name, location, target, scale in [
    ("hero", (11, 16, 10), (0, .15, 4.1), 17.0),
    ("side", (12, 0, 5.2), (0, .38, 4.1), 17.0),
    ("detail", (4, 6, 5.8), (0, .45, 8.15), 5.8),
]:
    camera.location = location
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
