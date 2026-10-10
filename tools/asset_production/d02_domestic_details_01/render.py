"""Render four isolated Blender views; studio geometry is never exported or saved."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_domestic_details_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
bpy.ops.wm.open_mainfile(filepath=str(ROOT / f"art/source/models/environment/{NID}/{NID}.blend"))
scene = bpy.context.scene


def aim(obj, target):
    """Keep studio framing explicit and separate from the vertical gameplay camera."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def light(name, position, power, size):
    """Provide broad neutral studio fill without adding runtime light nodes."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (0, 0, .4))


world = scene.world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.22, .28, .36, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = .65
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.03))
ground = bpy.context.object
mat = bpy.data.materials.new("STUDIO_ground")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (.13, .17, .20, 1)
mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = .8
ground.data.materials.append(mat)
light("STUDIO_key", (2, 4, 6), 40, 5)
light("STUDIO_rim", (-3, -4, 5), 55, 4)
light("STUDIO_front_fill", (1, 5, 2), 15, 3)
sun_data = bpy.data.lights.new("STUDIO_sun", "SUN")
sun_data.energy = 1.5
sun_data.angle = math.radians(12)
sun = bpy.data.objects.new("STUDIO_sun", sun_data)
scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(25), math.radians(-20), math.radians(-25))
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new("STUDIO_camera", data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.compression = 95
scene.view_settings.view_transform = "AgX"
for name, location, target, scale in [
    ("hero", (4, 6, 3.7), (0, 0, .47), 4.6),
    ("side", (0, 7, .47), (0, 0, .47), 4.2),
    ("detail", (2.8, 3, 2.3), (.85, 0, .73), 1.8),
]:
    camera.location = location
    aim(camera, target)
    data.type = "ORTHO"
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
