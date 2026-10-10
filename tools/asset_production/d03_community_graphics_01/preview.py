"""Render face-only artwork on the unchanged Blender noticeboard; never save its source."""
import hashlib
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_community_graphics_01"
SOURCE = ROOT / "art/source/models/environment/city_sign_supports_03/city_sign_supports_03.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"


def main():
    """Reuse the saved board studio and inspect artwork, profile and calibrated overhead."""
    assert bpy.app.version_string == "5.2.2 LTS"
    before = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    material = bpy.data.materials.new("community_board_preview")
    material.use_nodes = True
    material.use_backface_culling = True
    p = material.node_tree.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = .84
    texture = material.node_tree.nodes.new("ShaderNodeTexImage")
    texture.image = bpy.data.images.load(str(
        ROOT / f"art/textures/environment/{NID}/community_board_albedo.png"))
    texture.extension = "EXTEND"
    material.node_tree.links.new(texture.outputs["Color"], p.inputs["Base Color"])
    bpy.data.objects["CitySignSupports03_ArtworkCarrier"].data.materials[0] = material
    camera = scene.camera
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.image_settings.compression = 95
    scene.render.dither_intensity = 0
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    for name, position, target, scale in [
        ("hero", (2.2,4.5,2.65), (0,0,1.05), 4.4),
        ("side", (4,1.8,2.4), (0,0,1.05), 5.0),
        ("detail", (0,4,1.55), (0,.071,1.42), 1.87),
    ]:
        camera.location = position
        camera.rotation_euler = (Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
        camera.data.type, camera.data.ortho_scale = "ORTHO", scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location, camera.rotation_euler = (0,0,47), (0,0,0)
    camera.data.type, camera.data.sensor_fit = "PERSP", "VERTICAL"
    camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)
    assert before == hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    print("COMMUNITY_PREVIEW_PASS: four source-studio renders; carrier source never saved")


if __name__ == "__main__":
    main()
