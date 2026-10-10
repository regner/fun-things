"""Isolated access views with unchanged straight-deck context; never save studio geometry."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_boardwalk_05"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
EVIDENCE.mkdir(parents=True, exist_ok=True)
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
scene = bpy.context.scene
# The accepted sibling is read-only context, not copied into this asset's source/export.
path = ROOT / "art/source/models/environment/city_boardwalk_01/city_boardwalk_01.blend"
with bpy.data.libraries.load(str(path), link=False) as (_available, selected):
    selected.collections = ["export_city_boardwalk_01"]
context = selected.collections[0]
scene.collection.children.link(context)
for obj in context.objects:
    if obj.parent is None:
        obj.location = (0, -3, 0)
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
    """Point temporary studio equipment without changing any saved asset transforms."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.265))
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
    aim(obj, (0, 0, 0))
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new("STUDIO_camera", data)
scene.collection.objects.link(camera)
scene.camera = camera
for name, position, target, scale in (
    ("hero", (10, 12, 13), (0, -1.5, 0), 13),
    ("side", (9, 0, 1.9), (0, 1.5, -.05), 5.7),
    ("detail", (4, 6, 3.8), (1.1, 2.65, -.04), 2.8),
):
    context.hide_render = name != "hero"
    scene.render.resolution_x, scene.render.resolution_y = {
        "hero": (1152, 648), "side": (1280, 720), "detail": (1024, 576),
    }[name]
    camera.location = position
    aim(camera, target)
    data.type, data.ortho_scale = "ORTHO", scale
    scene.render.filepath = str(EVIDENCE / (name + ".png"))
    bpy.ops.render.render(write_still=True)
context.hide_render = False
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
camera.location, camera.rotation_euler = (0, -1.5, 47), (0, 0, 0)
data.type, data.sensor_fit = "PERSP", "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
print("FOUR_ISOLATED_ACCESS_VIEWS_RENDERED")
