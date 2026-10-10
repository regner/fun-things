"""Render the civic face on its existing low panel; never save shared dependencies."""
from pathlib import Path
import hashlib
import math

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_civic_graphics_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / "art/source/models/environment/city_sign_supports_02/city_sign_supports_02.blend"
assert bpy.app.version_string == "5.2.2 LTS"
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
collection = bpy.data.collections["export_city_sign_supports_02"]
for obj in list(bpy.data.objects):
    if obj.name not in collection.all_objects:
        bpy.data.objects.remove(obj, do_unlink=True)

material = bpy.data.materials.new("old_quay_civic_preview")
material.use_nodes = True
material.use_backface_culling = True
principled = material.node_tree.nodes.get("Principled BSDF")
principled.inputs["Roughness"].default_value = 0.56
image = bpy.data.images.load(str(ROOT / f"art/textures/environment/{NID}/direction_panel_albedo.png"))
texture = material.node_tree.nodes.new("ShaderNodeTexImage")
texture.image = image
texture.extension = "EXTEND"
material.node_tree.links.new(texture.outputs["Color"], principled.inputs["Base Color"])
bpy.data.objects["CitySignSupports02_ArtworkCarrier"].data.materials[0] = material
world = bpy.data.worlds.new("Old Quay evidence world")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.14, 0.18, 0.22, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.8


def aim(obj, target):
    """Aim camera/light using Blender's negative-Z viewing direction."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


lights = []
for name, location, energy, size in [
    ("key", (-3, 4, 6), 750, 5), ("fill", (4, 2, 2), 450, 4)
]:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    aim(obj, (0, 0, 1))
    lights.append(obj)

camera_data = bpy.data.cameras.new("Evidence camera")
camera = bpy.data.objects.new("Evidence camera", camera_data)
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
scene.render.dither_intensity = 0
scene.view_settings.view_transform = "AgX"
scene.render.film_transparent = False
EVIDENCE.mkdir(parents=True, exist_ok=True)
for name, location, target, scale in [
    ("hero", (-1.7, 6.5, 2.6), (0, 0, 0.69), 3.2),
    ("side", (3.8, 2.8, 2.0), (0, 0, 0.69), 3.4),
    ("detail", (0, 4.5, 1.2), (0, 0.071, 1.075), 1.9),
]:
    camera.location = location
    aim(camera, target)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)

# Exact vertical-down perspective, not an enlarged graphic or tilted-camera substitute.
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
camera_data.type = "PERSP"
camera_data.sensor_fit = "VERTICAL"
camera_data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
assert source_hash == hashlib.sha256(SOURCE.read_bytes()).hexdigest()
print("CIVIC_PREVIEWS_PASS: no shared source or GLB writes")
