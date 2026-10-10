"""Isolated Blender views of all route variants on unchanged linked-source hardware."""
import hashlib
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_campus_graphics_03"
SOURCE = ROOT / "art/source/models/environment/city_sign_supports_02/city_sign_supports_02.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"


def aim(camera, target):
    """Point the isolated camera at the documented studio target."""
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat("-Z", "Y").to_euler()


def main():
    """Render the three variants without saving or changing the accepted carrier source."""
    assert bpy.app.version_string == "5.2.2 LTS"
    before = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    collection = bpy.data.collections["export_city_sign_supports_02"]
    root = bpy.data.objects["CitySignSupports02"]
    originals = list(root.children)
    roots = []
    for variant, x in (("left", 2.0), ("ahead", 0), ("right", -2.0)):
        material = bpy.data.materials.new(f"route_{variant}_preview")
        material.use_nodes = True
        material.use_backface_culling = True
        principled = material.node_tree.nodes.get("Principled BSDF")
        principled.inputs["Roughness"].default_value = 0.65
        texture = material.node_tree.nodes.new("ShaderNodeTexImage")
        texture.image = bpy.data.images.load(str(
            ROOT / f"art/textures/environment/{NID}/route_{variant}_albedo.png"))
        texture.extension = "EXTEND"
        material.node_tree.links.new(texture.outputs["Color"], principled.inputs["Base Color"])
        instance = root.copy()
        collection.objects.link(instance)
        instance.location.x = x
        roots.append(instance)
        for original in originals:
            child = original.copy()
            child.data = original.data.copy()
            collection.objects.link(child)
            child.parent = instance
            if "ArtworkCarrier" in original.name:
                child.data.materials[0] = material
    for original in originals:
        original.hide_render = True
    camera, data = scene.camera, scene.camera.data
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.image_settings.compression = 95
    scene.render.image_settings.color_mode = "RGB"
    scene.render.dither_intensity = 0
    scene.cycles.samples = 32
    scene.cycles.device = "CPU"
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    for name, position, target, scale in (
        ("hero", (0.6, 8, 3.8), (0, 0, 0.675), 6.6),
        ("side", (4, -1.6, 2.1), (0, 0, 0.675), 3.2),
        ("detail", (0, 4, 1.075), (0, 0, 1.075), 1.7),
    ):
        for index, instance in enumerate(roots):
            for child in instance.children:
                child.hide_render = name != "hero" and index != 1
        camera.location = position
        aim(camera, target)
        data.type = "ORTHO"
        data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    for instance in roots:
        for child in instance.children:
            child.hide_render = False
    camera.location = (0, 0, 47)
    camera.rotation_euler = (0, 0, 0)
    data.type = "PERSP"
    data.sensor_fit = "VERTICAL"
    data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == before
    print("ROUTE_SET_PREVIEW_PASS: four renders, accepted source unchanged")


if __name__ == "__main__":
    main()
