"""Render four isolated studio views; studio geometry never enters source or exports."""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_roof_details_04"
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


# A horizontal close-view studio floor exposes the complete inclined attachment underside.
# Only the gameplay view uses a matching roof slope; neither studio surface is exported.
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.45))
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
    ("hero", (5, -8, 5), (0, 0, .80), 6.0),
    ("side", (10, 0, 2.4), (0, 0, .80), 5.5),
    ("detail", (3, -5, 5), (0, 0, 1.51), 2.4),
):
    camera.location = position
    aim(camera, target)
    data.type, data.ortho_scale = "ORTHO", scale
    scene.render.filepath = str(EVIDENCE / (name + ".png"))
    bpy.ops.render.render(write_still=True)
# Roof-only placement height is illustrative; this is a studio slope, not a building.
bpy.data.objects["CityRoofDetails04"].location.z = 8
ground.location.z = 7.999
ground.rotation_euler.x = math.radians(30)
for obj in scene.objects:
    if obj.type == "LIGHT":
        obj.hide_render = True
sun = bpy.data.lights.new("STUDIO_context_sun", "SUN")
sun.energy, sun.angle = 2, .2
light = bpy.data.objects.new("STUDIO_context_sun", sun)
scene.collection.objects.link(light)
light.rotation_euler = (.45, -.55, -.3)
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type, data.sensor_fit = "PERSP", "VERTICAL"
data.angle = math.radians(42)
frame = data.view_frame(scene=scene)
vertical_fov = math.degrees(2 * math.atan(max(abs(v.y / v.z) for v in frame)))
assert abs(vertical_fov - 42) < .001
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
validation_path = EVIDENCE / "validation.json"
validation = json.loads(validation_path.read_text()) if validation_path.exists() else {}
validation["overhead_camera"] = {
    "projection": "perspective", "world_height_m": 47, "roof_height_m": 8,
    "vertical_fov_deg": vertical_fov, "rotation_blender_rad": [0, 0, 0],
    "resolution_px": [1280, 720], "engine_capture": False,
    "studio_slope_deg": 30, "component_translation_blender_m": [0, 0, 8],
    "no_building_or_world_placement_claim": True,
    "scope": "Temporary Blender comparison; not saved district placement",
}
validation_path.write_text(json.dumps(validation, indent=2) + "\n", newline="\n")
print("FOUR_ISOLATED_VIEWS_RENDERED")
