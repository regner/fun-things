"""Render four isolated studio views; studio geometry never enters source or exports."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_shore_edges_02"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
EVIDENCE.mkdir(parents=True, exist_ok=True)
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.compression = 95
scene.view_settings.view_transform = "AgX"
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.22, .28, .33, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .6


def aim(obj, target):
    """Aim studio camera and lights without changing the component axes."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


# Isolated display floor is below the toe, NOT the land or water datum.
# No studio geometry enters the source or exports; the actual land datum is cap-top Z=0.
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -2.401))
ground = bpy.context.object
mat = bpy.data.materials.new("STUDIO_background")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (.12, .18, .20, 1)
mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = .8
ground.data.materials.append(mat)
for name, position, energy, size in (
    ("key", (2, 5, 10), 1700, 8), ("fill", (-6, -3, 6), 1300, 7),
    ("rim", (3, -6, 5), 900, 5),
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
    ("hero", (5, 7, 3.2), (0, 0, -1.15), 7.4),
    ("side", (0, 8, -1.2), (0, 0, -1.2), 5.3),
    ("detail", (1.8, 3, 2.2), (0, .25, -.15), 2.2),
):
    camera.location = position
    aim(camera, target)
    data.type, data.ortho_scale = "ORTHO", scale
    scene.render.filepath = str(EVIDENCE / (name + ".png"))
    bpy.ops.render.render(write_still=True)
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type, data.sensor_fit = "PERSP", "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
print("FOUR_ISOLATED_VIEWS_RENDERED")
