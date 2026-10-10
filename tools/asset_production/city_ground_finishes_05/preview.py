"""Render isolated evidence; the repetition/character/car comparison is not world placement."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "city_ground_finishes_05"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"


def aim(obj, target):
    """Aim Blender's -Z camera/light axis with +Y image up."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    """Save four <=1280x720 views with an exact 47 m, vertical 42-degree camera."""
    bpy.ops.wm.open_mainfile(filepath=str(
        ROOT / f"art/source/models/environment/{NID}/{NID}.blend"))
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.resolution_percentage = 100
    scene.render.dither_intensity = 0.0
    scene.render.resolution_x = 960
    scene.render.resolution_y = 640
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 100
    scene.view_settings.view_transform = "AgX"
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.15, 0.19, 0.23, 1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.65
    light_data = bpy.data.lights.new("STUDIO_sun", "SUN")
    light_data.energy = 2.0
    light_data.angle = math.radians(15)
    light = bpy.data.objects.new("STUDIO_sun", light_data)
    scene.collection.objects.link(light)
    light.rotation_euler = (math.radians(24), math.radians(-30), math.radians(-20))
    camera_data = bpy.data.cameras.new("STUDIO_camera")
    camera = bpy.data.objects.new("STUDIO_camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    for name, location, target, scale in [
        ("hero", (6, -7, 7), (0, 0, -0.02), 6.3),
        ("side", (0, -7, 1.8), (0, 0, -0.02), 5.6),
        ("soil_detail", (1.9, -2.1, 3.2), (0, 0, 0), 2.6),
    ]:
        camera.location = location
        aim(camera, target)
        camera_data.type = "ORTHO"
        camera_data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    # Linked repetitions of the SAME Blender swatch, not a new garden geometry deliverable.
    swatch = bpy.data.objects["CityGroundFinishes05_Mesh"]
    swatch.hide_render = True
    for row in range(6):
        for column in range(8):
            obj = swatch.copy()
            obj.data = swatch.data
            obj.hide_render = False
            obj.parent = None
            obj.location = (-14 + column * 4, -10 + row * 4, 0)
            scene.collection.objects.link(obj)
    # Accepted source-backed assets are read-only studio references, never re-exported/saved here.
    for path, location in [
        ("art/models/characters/coral_courier/coral_courier.glb", (3, 0, 0)),
        ("art/models/vehicles/car_latch_a/car_latch_a.glb", (-4, 0, 0)),
    ]:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(ROOT / path))
        added = set(bpy.data.objects) - before
        for obj in added:
            if obj.parent not in added:
                obj.location += Vector(location)
    camera.location = (0, 0, 47)
    camera.rotation_euler = (0, 0, 0)
    camera_data.type = "PERSP"
    camera_data.sensor_fit = "VERTICAL"
    camera_data.angle = math.radians(42)
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
