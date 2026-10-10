"""Isolated support views and unchanged sibling-deck context; no studio geometry is exported."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_boardwalk_04"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
EVIDENCE.mkdir(parents=True, exist_ok=True)
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
scene = bpy.context.scene
original = bpy.data.objects["CityBoardwalk04_Mesh"]
bpy.data.collections["export_" + ASSET].hide_render = True
context = []


def support(position, group):
    """Instance the authored mesh for transient studio-only assembly context."""
    obj = bpy.data.objects.new("STUDIO_support", original.data)
    scene.collection.objects.link(obj)
    obj.location = position
    group.append(obj)
    return obj


def sibling(asset, position, angle=0):
    """Read a sibling collection without modifying its source, material or export."""
    path = ROOT / f"art/source/models/environment/{asset}/{asset}.blend"
    with bpy.data.libraries.load(str(path), link=False) as (_available, selected):
        selected.collections = ["export_" + asset]
    collection = selected.collections[0]
    scene.collection.children.link(collection)
    for obj in collection.objects:
        if obj.parent is None:
            obj.location, obj.rotation_euler.z = position, angle
        context.append(obj)


bare = support((-3, 0, 0), [])
sibling("city_boardwalk_01", (3, 2, 2.24))
sibling("city_boardwalk_03", (4.8, 2, 2.24))
sibling("city_boardwalk_03", (1.2, 2, 2.24), math.pi)
support((3, .5, 0), context)
support((3, 3.5, 0), context)
scene.render.engine = "CYCLES"
scene.cycles.device, scene.cycles.samples = "CPU", 96
scene.cycles.use_denoising = True
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.compression = 95
scene.view_settings.view_transform = "AgX"
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.22, .28, .33, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .6


def aim(obj, target):
    """Point studio equipment without changing any saved asset transforms."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.025))
ground = bpy.context.object
ground.name = "STUDIO_ground_not_exported"
mat = bpy.data.materials.new("STUDIO_background")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (.12, .18, .20, 1)
mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = .8
ground.data.materials.append(mat)
for name, position, energy, size in (
    ("key", (2, -6, 10), 1800, 8), ("fill", (-6, -3, 6), 1300, 7),
    ("rim", (5, 7, 8), 1800, 6),
):
    data = bpy.data.lights.new("STUDIO_" + name, "AREA")
    data.energy, data.shape, data.size = energy, "DISK", size
    obj = bpy.data.objects.new("STUDIO_" + name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (0, 1, 1))
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new("STUDIO_camera", data)
scene.collection.objects.link(camera)
scene.camera = camera
for name, position, target, scale in (
    ("hero", (11, -17, 11), (.3, 1.2, 1), 14),
    ("side", (0, -12, 1.0), (0, 0, 1), 4.6),
    ("detail", (4, -6, 3.8), (1.15, 0, 1.56), 2.1),
):
    for obj in context:
        obj.hide_render = name != "hero"
    bare.location.x = -3 if name == "hero" else 0
    scene.render.resolution_x, scene.render.resolution_y = {
        "hero": (1152, 648), "side": (1280, 720), "detail": (1024, 576),
    }[name]
    camera.location = position
    aim(camera, target)
    data.type, data.ortho_scale = "ORTHO", scale
    scene.render.filepath = str(EVIDENCE / (name + ".png"))
    bpy.ops.render.render(write_still=True)
for obj in context:
    obj.hide_render = False
bare.location.x = -3
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
camera.location, camera.rotation_euler = (0, 1.5, 47), (0, 0, 0)
data.type, data.sensor_fit = "PERSP", "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
print("FOUR_ISOLATED_SUPPORT_VIEWS_RENDERED")
