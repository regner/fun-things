"""Render artwork on the original read-only Blender support; never save/export a copy."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "city_parking_furniture_04"
HARDWARE = "city_traffic_fixtures_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"


def aim(camera, target):
    """Aim an isolated studio camera without altering the shared model transforms."""
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def main():
    """Reuse the hardware studio lighting and ground for four calibrated lean views."""
    assert bpy.app.version_string == "5.2.2 LTS"
    source = ROOT / f"art/source/models/environment/{HARDWARE}/{HARDWARE}.blend"
    bpy.ops.wm.open_mainfile(filepath=str(source))
    material = bpy.data.materials.new("bus_stop_preview")
    material.use_nodes = True
    material.use_backface_culling = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Roughness"].default_value = .52
    texture = material.node_tree.nodes.new("ShaderNodeTexImage")
    texture.image = bpy.data.images.load(
        str(ROOT / f"art/textures/environment/{NID}/bus_stop_albedo.png"))
    texture.extension = "EXTEND"
    # The shared source carries UVMap but does not mark an active render UV layer.
    # Bind the declared map explicitly; do not mutate or save the hardware source.
    uv = material.node_tree.nodes.new("ShaderNodeUVMap")
    uv.uv_map = "UVMap"
    material.node_tree.links.new(uv.outputs["UV"], texture.inputs["Vector"])
    material.node_tree.links.new(texture.outputs["Color"], principled.inputs["Base Color"])
    mesh = bpy.data.objects["CityTrafficFixtures03_Mesh"]
    assert mesh.data.materials[2].name == "road_sign_face"
    mesh.data.materials[2] = material
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.compression = 100
    scene.render.image_settings.color_mode = "RGB"
    scene.cycles.samples = 32
    scene.cycles.device = "CPU"
    camera = scene.camera
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    for name, position, target, scale in [
        ("hero", (5, 10, 5.5), (0, 0, 1.65), 6.5),
        ("side", (10, -3, 3.8), (0, 0, 1.65), 6.5),
        ("detail", (0, 5, 3.3), (0, .135, 2.9), 1.5),
    ]:
        camera.location = position
        aim(camera, target)
        camera.data.type, camera.data.ortho_scale = "ORTHO", scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location, camera.rotation_euler = (0, 0, 47), (0, 0, 0)
    camera.data.type, camera.data.sensor_fit = "PERSP", "VERTICAL"
    camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)
    print("BUS_STOP_PREVIEW_PASS: no source or GLB writes")


if __name__ == "__main__":
    main()
