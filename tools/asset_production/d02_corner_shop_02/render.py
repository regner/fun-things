"""Render annex details and a read-only sibling attachment comparison."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_corner_shop_02"
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
    ("hero", (9, -12, 8), (0, 0, 1.65), 11.5),
    ("detail", (2.7, -8, 4), (0, -1.8, 2.45), 5.8),
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

# Existing shop geometry stays read-only and is never saved into the annex source/export.
# Annex root remains at zero here; shop root moves +6.3 Blender Y for the same mating.
attach("d02_corner_shop_01", "", (0, 6.3, 0))
for x in (-3.6, 3.6):
    attach("city_shop_fittings_05", "", (x, 10.8, .48))
for x in (-3.6, 0, 3.6):
    attach("city_shop_fittings_01", "", (x, 10.8, 3))
attach("city_shop_fittings_02", "", (0, 10.8, 3.8))
attach("city_shop_fittings_03", "_single", (0, 10.8, 0))
attach("city_shop_fittings_06", "_single", (0, 10.8, 0))
camera.location = (18, -19, 14)
aim(camera, (0, 4.3, 3.1))
data.type = "ORTHO"
data.ortho_scale = 21
scene.render.filepath = str(EVIDENCE / "side.png")
bpy.ops.render.render(write_still=True)
