"""Render the shell with read-only shared GLBs at the exact saved prefab mounts."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_quay_frontages_02"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
bpy.ops.wm.open_mainfile(filepath=str(ROOT / f"art/source/models/environment/{NID}/{NID}.blend"))
scene = bpy.context.scene


def attach(asset, suffix, position):
    """Preview existing accepted hardware without authoring duplicate mesh outputs."""
    before = set(bpy.data.objects)
    filename = asset + suffix
    bpy.ops.import_scene.gltf(filepath=str(ROOT / f"art/models/environment/{asset}/{filename}.glb"))
    imported = set(bpy.data.objects) - before
    for obj in imported:
        if obj.parent not in imported:
            obj.location += Vector(position)


for bay in (-3.2, 3.2):
    attach("city_shop_fittings_05", "", (bay-.95, 4, .48))
    attach("city_shop_fittings_01", "", (bay-.95, 4, 3))
    attach("city_shop_fittings_02", "", (bay-.95, 4, 3.8))
    attach("city_shop_fittings_03", "_single", (bay+1.95, 4, 0))
    attach("city_shop_fittings_06", "_single", (bay+1.95, 4, 0))
    attach("city_shop_fittings_07", "", (bay, 4, 4.65))
    before = set(bpy.data.objects)
    attach("city_shop_fittings_07", "", (0, 0, 0))
    imported = set(bpy.data.objects) - before
    for obj in imported:
        if obj.parent not in imported:
            obj.rotation_mode = "XYZ"
            obj.rotation_euler.z = math.pi
            obj.location = (bay, -4, 4.65)


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
    ("hero", (20, 28, 19), (0, .1, 4.2), 29),
    ("side", (-24, -25, 16), (0, -.1, 4.2), 29),
    ("detail", (1, 23, 8), (0, 4, 3.35), 17),
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
