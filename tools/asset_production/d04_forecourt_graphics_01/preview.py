"""Isolated ground-artwork evidence; studio context is never saved or exported."""
import importlib.util
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_forecourt_graphics_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
spec = importlib.util.spec_from_file_location(
    "ground_studio", ROOT / "tools/asset_production/city_ground_finishes_01/preview.py")
studio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(studio)


def main():
    """Show the whole strip, edge datum, inset and exact 47m/42-degree overhead."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.wm.open_mainfile(filepath=str(
        ROOT / f"art/source/models/environment/{NID}/{NID}.blend"))
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.resolution_percentage = 100
    scene.render.dither_intensity = 0
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 95
    scene.view_settings.view_transform = "AgX"
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.22, .27, .32, 1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = .7
    # Read-only source-linked paving swatches give flat supporting context, not a new floor asset.
    with bpy.data.libraries.load(str(ROOT / (
            "art/source/models/environment/city_ground_finishes_01/city_ground_finishes_01.blend")),
            link=False) as (available, loaded):
        loaded.objects = ["CityGroundFinishes01_Mesh"]
    swatch = loaded.objects[0]
    for row in range(6):
        for col in range(8):
            obj = swatch.copy()
            obj.parent = None
            obj.location = (-14 + col * 4, -10 + row * 4, 0)
            scene.collection.objects.link(obj)
    light_data = bpy.data.lights.new("STUDIO_sun", "SUN")
    light_data.energy, light_data.angle = 2.0, math.radians(15)
    sun = bpy.data.objects.new("STUDIO_sun", light_data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(24), math.radians(-30), math.radians(-20))
    data = bpy.data.cameras.new("STUDIO_camera")
    camera = bpy.data.objects.new("STUDIO_camera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    for name, location, target, scale in [
        ("hero", (12, -21, 25), (0, 0, 0), 31),
        ("side", (0, -26, 10), (0, 0, 0), 29),
        ("detail", (11, -4, 7), (9.5, 0, 0), 6),
    ]:
        camera.location = location
        studio.aim(camera, target)
        data.type, data.ortho_scale = "ORTHO", scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    # Original committed references at true scale; neither is part of the delivery.
    for path, location in [
        ("art/models/characters/coral_courier/coral_courier.glb", (3, 0, 0)),
        ("art/models/vehicles/car_latch_a/car_latch_a.glb", (-5, -5, 0)),
    ]:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(ROOT / path))
        added = set(bpy.data.objects) - before
        for obj in added:
            if obj.parent not in added:
                obj.location += Vector(location)
    camera.location, camera.rotation_euler = (0, 0, 47), (0, 0, 0)
    data.type, data.sensor_fit, data.angle = "PERSP", "VERTICAL", math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
