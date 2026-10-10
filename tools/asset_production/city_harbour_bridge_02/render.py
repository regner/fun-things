"""Four Blender views with read-only sibling deck context; no studio geometry is exported."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "city_harbour_bridge_02"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"


def aim(obj, target):
    """Aim studio camera/lights; exported geometry remains untouched."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    """Render the matched pair, inner marker detail and a true 47 m vertical camera crop."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.wm.open_mainfile(filepath=str(
        ROOT / f"art/source/models/environment/{NID}/{NID}.blend"))
    # Append the unchanged accepted sibling as context only; never save/export this scene.
    deck_source = ROOT / "art/source/models/environment/city_harbour_bridge_01/city_harbour_bridge_01.blend"
    with bpy.data.libraries.load(str(deck_source), link=False) as (source, target):
        target.collections = ["export_city_harbour_bridge_01"]
    for collection in target.collections:
        bpy.context.scene.collection.children.link(collection)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.22, 0.29, 0.35, 1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    # A flat matte studio water datum illustrates the preserved open space, not wave gameplay.
    bpy.ops.mesh.primitive_plane_add(size=10000, location=(0, 0, -2.1))
    plane = bpy.context.object
    plane.name = "STUDIO_water_datum_not_exported"
    mat = bpy.data.materials.new("STUDIO_water")
    mat.diffuse_color = (0.035, 0.16, 0.18, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = mat.diffuse_color
    shader.inputs["Roughness"].default_value = 0.8
    plane.data.materials.append(mat)
    for name, location, energy, size in (
        ("key", (5, -45, 60), 130000, 55),
        ("fill", (-30, 30, 40), 100000, 45),
        ("soffit_fill", (0, -45, 5), 18000, 35),
    ):
        data = bpy.data.lights.new("STUDIO_" + name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        obj = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(obj)
        obj.location = location
        aim(obj, (0, 0, -0.5))
    data = bpy.data.cameras.new("STUDIO_camera")
    camera = bpy.data.objects.new(data.name, data)
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
    scene.render.image_settings.compression = 100
    scene.view_settings.view_transform = "AgX"
    for name, location, target, scale in (
        ("hero", (65, -105, 55), (0, 0, 0), 111),
        ("side", (0, -110, 2), (0, 0, 0.15), 100),
        ("detail", (5, -2, 4.5), (0, -8.325, 0.5), 11),
    ):
        camera.location = location
        aim(camera, target)
        data.type = "ORTHO"
        data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / (name + ".png"))
        bpy.ops.render.render(write_still=True)
    camera.location = (0, 0, 47)
    camera.rotation_euler = (0, 0, 0)
    data.type = "PERSP"
    data.sensor_fit = "VERTICAL"
    data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
