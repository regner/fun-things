"""Render the shell with read-only shared GLBs at the exact saved prefab mounts."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_quay_frontages_04"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
bpy.ops.wm.open_mainfile(filepath=str(ROOT / f"art/source/models/environment/{NID}/{NID}.blend"))
scene = bpy.context.scene


def attach(asset, suffix, position, yaw=0):
    """Preview read-only shared GLBs at the saved facade mounts."""
    before = set(bpy.data.objects)
    filename = asset + suffix
    bpy.ops.import_scene.gltf(filepath=str(ROOT / f"art/models/environment/{asset}/{filename}.glb"))
    imported = set(bpy.data.objects) - before
    for obj in imported:
        if obj.parent not in imported:
            obj.rotation_mode = "XYZ"
            obj.rotation_euler.z = yaw
            obj.location = position


for asset, suffix, position, yaw in [
    ("city_shop_fittings_03", "_single", (1.95, 6, 0), 0),
    ("city_shop_fittings_06", "_single", (1.95, 6, 0), 0),
    ("city_shop_fittings_05", "", (-.95, 6, .48), 0),
    ("city_shop_fittings_01", "", (-.95, 6, 3), 0),
    ("city_shop_fittings_02", "", (-.95, 6, 3.8), 0),
    ("city_shop_fittings_07", "", (0, 6, 4.65), 0),
    ("city_shop_fittings_07", "", (0, -6, 4.65), math.pi),
    ("city_shop_fittings_05", "", (4.4, 2, .48), -math.pi/2),
    ("city_shop_fittings_01", "", (4.4, 2, 3), -math.pi/2),
    ("city_shop_fittings_02", "", (4.4, 2, 3.8), -math.pi/2),
    ("city_shop_fittings_07", "", (4.4, 2, 4.65), -math.pi/2),
]:
    attach(asset, suffix, position, yaw)


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
    aim(obj, (0, 0, 2))


world = scene.world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.22, .28, .36, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = .65
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.03))
ground = bpy.context.object
mat = bpy.data.materials.new("STUDIO_ground")
mat.diffuse_color = (.17, .20, .22, 1)
ground.data.materials.append(mat)
light("STUDIO_key", (4, 8, 18), 3200, 12)
light("STUDIO_rim", (-10, -8, 15), 3800, 10)
light("STUDIO_front_fill", (1, 12, 6), 1500, 8)
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
    ("hero", (22, 28, 19), (0, 0, 4.7), 30),
    ("side", (22, -26, 17), (0, 0, 4.7), 30),
    ("detail", (19, 23, 9), (1, 3.5, 3.5), 20),
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
