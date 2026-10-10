"""Render the saved landward assembly using unchanged Blender source meshes; save no new source."""
import math
import runpy
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[3]
KIT = "city_quay_furniture_02"
EVIDENCE = ROOT / "docs/assets/production/city_barriers_02-evidence"


def main():
    """Reuse the kit's source and studio for four views of its existing landward straight prefab."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.wm.open_mainfile(filepath=str(
        ROOT / f"art/source/models/environment/{KIT}/{KIT}.blend"))
    helpers = runpy.run_path(str(ROOT / f"tools/asset_production/{KIT}/author.py"))
    scene = bpy.context.scene
    # The source studio contains a mixed kit display; show only the actual reference members.
    for obj in scene.objects:
        if obj.name.startswith("STUDIO_") and obj.type == "MESH" and obj.name != "STUDIO_ground":
            obj.hide_render = True
    helpers["preview"]("straight", (0, 0, 0))
    helpers["preview"]("post_landward", (-1.5, 0, 0))
    helpers["preview"]("post_landward", (1.5, 0, 0))
    camera = scene.camera
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.image_settings.compression = 100
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    for name, location, target, scale in [
        ("hero", (5, -8, 4), (0, 0, .5), 4.7),
        ("side", (0, -10, 2), (0, 0, .53), 4.3),
        ("detail", (2.7, -2, 1.3), (1.5, 0, .34), 1.45),
    ]:
        camera.location = location
        helpers["aim"](camera, target)
        camera.data.type, camera.data.ortho_scale = "ORTHO", scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location, camera.rotation_euler = (0, 0, 47), (0, 0, 0)
    camera.data.type, camera.data.sensor_fit = "PERSP", "VERTICAL"
    camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
