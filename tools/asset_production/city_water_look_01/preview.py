"""Render isolated Blender evidence, including an unchanged 3x3 swatch seam field."""
from pathlib import Path
import math

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "city_water_look_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(ROOT / f"art/source/models/environment/{NID}/{NID}.blend"))
scene = bpy.context.scene
world = bpy.data.worlds.new("STUDIO_blue_hour")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.085, 0.13, 0.18, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.7


def aim(obj, target):
    """Point negative-Z camera/light axes at the swatch centre."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


for name, location, power, size, colour in [
    ("cool_fill", (-3, 4, 14), 2800, 12, (0.69, 0.84, 1.0)),
    ("warm_key", (8, 9, 11), 1800, 8, (1.0, 0.79, 0.55)),
]:
    data = bpy.data.lights.new(f"STUDIO_{name}", "AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    data.color = colour
    light = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(light)
    light.location = location
    aim(light, (0, 0, 0))
camera_data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new("STUDIO_camera", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.compression = 95
scene.render.dither_intensity = 0.0
scene.view_settings.view_transform = "AgX"
EVIDENCE.mkdir(parents=True, exist_ok=True)
for name, position, target, scale in [
    ("hero", (18, -23, 24), (0, 0, 0), 27),
    ("side", (0, -24, 11), (0, 0, 0), 26),
    ("detail", (2, -5, 12), (0, 1, 0), 9),
]:
    camera.location = position
    aim(camera, target)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)
# Translation-only copies test repeat seams, not a proposed water-system mesh or placement.
original = bpy.data.objects["CityWaterLook01_Mesh"]
for x in (-16, 0, 16):
    for y in (-16, 0, 16):
        if x == 0 and y == 0:
            continue
        copy = original.copy()
        copy.name = f"STUDIO_repeat_{x}_{y}"
        copy.parent = None
        copy.location = (x, y, 0)
        scene.collection.objects.link(copy)
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
camera_data.type = "PERSP"
camera_data.sensor_fit = "VERTICAL"
camera_data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
print("WATER_PREVIEW_PASS: four isolated 1280x720 renders; source untouched")
