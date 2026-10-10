"""Render original artwork on read-only shared Blender hardware; never save studio changes."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_neighbourhood_graphics_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / "art/source/models/environment/city_sign_supports_01/city_sign_supports_01.blend"))
assert bpy.app.version_string == "5.2.2 LTS"
scene = bpy.context.scene
root = bpy.data.objects["CitySignSupports01"]
root.location.z = 1.6
carrier = bpy.data.objects["artwork_carrier"]
art = carrier.data.materials[0].copy()
art.name = "STUDIO_watch_notice"
carrier.data.materials[0] = art
shader = art.node_tree.nodes.get("Principled BSDF")
shader.inputs["Base Color"].default_value = (1, 1, 1, 1)
shader.inputs["Roughness"].default_value = 0.8
shader.inputs["Metallic"].default_value = 0
texture = art.node_tree.nodes.new("ShaderNodeTexImage")
texture.image = bpy.data.images.load(str(
    ROOT / f"art/textures/environment/{NID}/watch_notice_albedo.png"))
texture.extension = "EXTEND"
art.node_tree.links.new(texture.outputs["Color"], shader.inputs["Base Color"])


def aim(obj, target):
    """Point isolated studio cameras/lights at an explicit metre-space target."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def light(name, location, power, size):
    """Add broad neutral studio fill; no production light nodes are authored."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.size = power, size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    aim(obj, (0, 0, 1.6))


scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.18, 0.22, 0.25, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.5
light("STUDIO_key", (-3, 4, 6), 650, 5)
light("STUDIO_fill", (4, 3, 3), 300, 4)
# Temporary neutral mounting wall/ground are evidence fixtures, never saved or exported.
mat = bpy.data.materials.new("STUDIO_wall")
mat.diffuse_color = (0.12, 0.18, 0.21, 1)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.15, 1.5))
wall = bpy.context.object
wall.name = "STUDIO_mounting_wall"
wall.dimensions = (4, 0.3, 3)
wall.data.materials.append(mat)
bpy.ops.mesh.primitive_plane_add(size=160)
ground = bpy.context.object
ground.name = "STUDIO_ground"
ground.data.materials.append(mat)
bpy.ops.object.camera_add()
camera = bpy.context.object
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.view_settings.view_transform = "AgX"
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.compression = 100
# Disable final display dithering to retain smooth, compact lossless evidence PNGs.
scene.render.dither_intensity = 0
for name, position, target, lens in [
    ("hero", (1.6, 3.5, 2.55), (0, 0.06, 1.6), 56),
    ("side", (2.8, 2.3, 2.0), (0, 0.05, 1.6), 55),
    ("detail", (0, 2.75, 1.6), (0, 0.088, 1.6), 52),
]:
    camera.location = position
    aim(camera, target)
    camera.data.lens = lens
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)
camera.location = (8, 9, 47)
camera.rotation_euler = (0, 0, 0)
camera.data.sensor_fit = "VERTICAL"
camera.data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
print("WATCH_PREVIEWS_PASS: 4 isolated 1280x720 renders; no source saves")
