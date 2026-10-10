"""Isolated Blender previews on unchanged hardware, without saving temporary assignments."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d08_repair_graphics_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / "art/source/models/environment/city_sign_supports_01/city_sign_supports_01.blend"


def aim(obj, target):
    """Point the camera or area light at the documented inspection target."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    """Render both finishes with original metre-scale mounting and calibrated overhead."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    collection = bpy.data.collections["export_city_sign_supports_01"]
    for obj in list(bpy.data.objects):
        if obj.name not in collection.all_objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    material = bpy.data.materials.new("service_warning_preview")
    material.use_nodes = True
    material.use_backface_culling = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Roughness"].default_value = 0.82
    texture = material.node_tree.nodes.new("ShaderNodeTexImage")
    texture.extension = "EXTEND"
    material.node_tree.links.new(texture.outputs["Color"], principled.inputs["Base Color"])
    bpy.data.objects["artwork_carrier"].data.materials[0] = material
    images = {variant: bpy.data.images.load(str(
        ROOT / f"art/textures/environment/{NID}/{variant}_albedo.png"))
        for variant in ("service_warning", "service_warning_patched")}
    world = bpy.data.worlds.new("Service warning inspection")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.14, 0.18, 0.22, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.8
    for name, location, energy, size in [
        ("key", (-3, 4, 6), 750, 5), ("fill", (4, 2, 2), 450, 4),
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.size, data.shape = energy, size, "DISK"
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = location
        aim(obj, (0, 0, 0))
    data = bpy.data.cameras.new("Evidence camera")
    camera = bpy.data.objects.new("Evidence camera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 95
    scene.render.dither_intensity = 0.0
    scene.view_settings.view_transform = "AgX"
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    for name, location, target, scale, variant in [
        ("hero", (-1.5, 5.8, 1.7), (0, 0, 0), 2.2, "service_warning"),
        ("side", (3, 3, 0.8), (0, 0.04, 0), 2.2, "service_warning_patched"),
        ("detail", (0.4, 2.5, 0.25), (0.15, 0.088, -0.10), 1.55, "service_warning_patched"),
    ]:
        texture.image = images[variant]
        camera.location = location
        aim(camera, target)
        data.type, data.ortho_scale = "ORTHO", scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    texture.image = images["service_warning"]
    bpy.data.objects["CitySignSupports01"].location = (0, 0, 1.6)
    camera.location, camera.rotation_euler = (0, 10, 47), (0, 0, 0)
    data.type, data.sensor_fit, data.angle = "PERSP", "VERTICAL", math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)
    print("WARNING_PREVIEWS_PASS: four 1280x720 images, source not saved")


if __name__ == "__main__":
    main()
