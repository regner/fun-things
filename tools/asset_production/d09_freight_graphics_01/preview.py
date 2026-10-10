"""Render freight art on the unchanged Blender fascia in an isolated, never-saved session."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d09_freight_graphics_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / "art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
collection = bpy.data.collections["export_city_shop_fittings_02"]
for obj in list(bpy.data.objects):
    if obj.name not in collection.all_objects:
        bpy.data.objects.remove(obj, do_unlink=True)

material = bpy.data.materials.new("warehouse_fascia_preview")
material.use_nodes = True
material.use_backface_culling = True
principled = material.node_tree.nodes.get("Principled BSDF")
principled.inputs["Roughness"].default_value = .62
image = bpy.data.images.load(str(ROOT / f"art/textures/environment/{NID}/warehouse_fascia_albedo.png"))
texture = material.node_tree.nodes.new("ShaderNodeTexImage")
texture.image = image
texture.extension = "EXTEND"
material.node_tree.links.new(texture.outputs["Color"], principled.inputs["Base Color"])
bpy.data.objects["fascia_artwork_carrier"].data.materials[0] = material
world = bpy.data.worlds.new("Freight evidence world")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.14, .18, .22, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = .8


def aim(obj, target):
    """Aim cameras and lights along their negative-Z viewing axis."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


for name, location, energy, size in [("key", (-3, 4, 6), 750, 5), ("fill", (4, 2, 2), 450, 4)]:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    light = bpy.data.objects.new(name, data)
    scene.collection.objects.link(light)
    light.location = location
    aim(light, (0, 0, 0))

camera_data = bpy.data.cameras.new("Freight evidence camera")
camera = bpy.data.objects.new("Freight evidence camera", camera_data)
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
scene.render.image_settings.compression = 100
scene.view_settings.view_transform = "AgX"
scene.render.film_transparent = False
EVIDENCE.mkdir(parents=True, exist_ok=True)
for name, location, target, scale in [
    ("hero", (-1.2, 6, 1.7), (0, 0, 0), 3.9),
    ("side", (3, 3, .8), (0, .04, 0), 3.8),
    ("detail", (.90, 3, .45), (.90, .128, 0), 1.55),
]:
    camera.location = location
    aim(camera, target)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)

# Translation only: normal wall-centre mounting at 3.8 m, no enlarged or tilted art.
bpy.data.objects["city_shop_fittings_02"].location = (0, 0, 3.8)
camera.location = (0, 10, 47)
camera.rotation_euler = (0, 0, 0)
camera_data.type = "PERSP"
camera_data.sensor_fit = "VERTICAL"
camera_data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
print("FREIGHT_PREVIEW_PASS: four 1280x720 renders; shared source never saved")
