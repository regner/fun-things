"""Isolated read-only carrier previews: both lengths and both outside-facing UV orientations."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d09_freight_graphics_02"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
assert bpy.app.version_string == "5.2.2 LTS"


def aim(obj, target):
    """Aim cameras and lights along their local negative-Z axis."""
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z", "Y").to_euler()


def setup(variant, number):
    """Open accepted source without saving; replace only material slot three for evidence."""
    carrier = f"d09_storage_{number:02d}"
    source = ROOT / f"art/source/models/environment/{carrier}/{carrier}.blend"
    bpy.ops.wm.open_mainfile(filepath=str(source))
    scene = bpy.context.scene
    collection = bpy.data.collections["export_" + carrier]
    for obj in list(bpy.data.objects):
        if obj.name not in collection.all_objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    material = bpy.data.materials.new("container_id_preview")
    material.use_nodes = True
    material.use_backface_culling = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Roughness"].default_value = .62
    texture = material.node_tree.nodes.new("ShaderNodeTexImage")
    texture.image = bpy.data.images.load(str(
        ROOT / f"art/textures/environment/{NID}/container_id_{variant}_albedo.png"))
    texture.extension = "EXTEND"
    material.node_tree.links.new(texture.outputs["Color"], principled.inputs["Base Color"])
    bpy.data.objects[f"D09Storage{number:02d}_Mesh"].data.materials[3] = material
    world = bpy.data.worlds.new("Freight ID evidence world")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (.14, .18, .22, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = .8
    for name, location, energy, size in [
        ("key", (8, 5, 12), 1800, 8), ("fill", (-7, 4, 7), 1300, 7),
        ("rim", (2, -6, 9), 1400, 6),
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.size = energy, size
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = location
        aim(light, (0, 0, 1.3))
    camera_data = bpy.data.cameras.new("Container ID evidence camera")
    camera = bpy.data.objects.new("Container ID evidence camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.compression = 100
    scene.view_settings.view_transform = "AgX"
    scene.render.film_transparent = False
    return scene, camera, camera_data


def render(scene, camera, data, name, location, target, scale):
    """Capture an orthographic close/side evidence view without altering carrier transforms."""
    camera.location = location
    aim(camera, target)
    data.type, data.ortho_scale = "ORTHO", scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)


def main():
    """Capture long +X hero/detail/overhead and short -X side to expose either UV orientation."""
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    scene, camera, data = setup("long", 1)
    render(scene, camera, data, "hero", (14, 14, 11), (0, 0, 1.3), 14.0)
    render(scene, camera, data, "detail", (5.5, 4.65, 2.8), (1.23, 4.65, 1.96), 2.15)
    # Vertical-down, north-up camera. No tilted artwork or artificially raised/scaled carrier.
    camera.location, camera.rotation_euler = (0, 0, 47), (0, 0, 0)
    data.type, data.sensor_fit, data.angle = "PERSP", "VERTICAL", math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)
    scene, camera, data = setup("short", 2)
    render(scene, camera, data, "side", (-9, 0, 3.5), (0, 0, 1.3), 7.3)
    print("CONTAINER_PREVIEW_PASS: four 1280x720 renders; both source files never saved")


if __name__ == "__main__":
    main()
