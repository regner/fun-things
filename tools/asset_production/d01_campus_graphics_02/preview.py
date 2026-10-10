"""Render campus artwork on the unchanged Blender low panel; never save the source."""
import hashlib
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_campus_graphics_02"
SOURCE = ROOT / "art/source/models/environment/city_sign_supports_02/city_sign_supports_02.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
assert bpy.app.version_string == "5.2.2 LTS"
before = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
material = bpy.data.materials.new("entry_panel_preview")
material.use_nodes = True
material.use_backface_culling = True
principled = material.node_tree.nodes.get("Principled BSDF")
principled.inputs["Roughness"].default_value = 0.65
texture = material.node_tree.nodes.new("ShaderNodeTexImage")
texture.image = bpy.data.images.load(str(ROOT / f"art/textures/environment/{NID}/entry_panel_albedo.png"))
texture.extension = "EXTEND"
material.node_tree.links.new(texture.outputs["Color"], principled.inputs["Base Color"])
bpy.data.objects["CitySignSupports02_ArtworkCarrier"].data.materials[0] = material
camera = scene.camera
data = camera.data
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.image_settings.compression = 95
scene.render.image_settings.color_mode = "RGB"
scene.render.dither_intensity = 0
scene.cycles.samples = 32
scene.cycles.device = "CPU"


def aim(obj, target):
    """Aim an isolated studio camera at the documented point on the carrier."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


EVIDENCE.mkdir(parents=True, exist_ok=True)
for name, position, target, scale in (
    ("hero", (0.65, 5.5, 2.15), (0, 0, 0.675), 3.0),
    ("side", (4, -1.6, 2.1), (0, 0, 0.675), 3.2),
    ("detail", (0, 4, 1.075), (0, 0, 1.075), 1.7),
):
    camera.location = position
    aim(camera, target)
    data.type = "ORTHO"
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)
# The centred vertical face is edge-on: report that limitation rather than tilting it.
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == before
print("CAMPUS_PREVIEW_PASS: four isolated renders; reused source unchanged")
