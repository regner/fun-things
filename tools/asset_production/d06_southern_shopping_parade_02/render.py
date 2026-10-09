"""Render the validated saved-prefab composition; no asset geometry is authored here."""
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_southern_shopping_parade_02"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(SCRATCH / "validated_assembly.blend"))
scene = bpy.context.scene
camera = scene.camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1280, 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"
EVIDENCE.mkdir(parents=True, exist_ok=True)
selected = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
for name, location, target, scale in [
    ("hero", (-52, 65, 53), (0, 0, 2), 73),
    ("side", (-60, 8, 19), (0, 0, 2.5), 68),
    ("bay_detail", (-21, 24, 8), (-8.8, 24.5, 2.3), 10),
    ("overhead_47m_42deg", (-6, 0, 47), (0, 0, 0), 0),
]:
    if selected and name not in selected:
        continue
    camera.location = location
    if scale:
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = scale
    else:
        camera.rotation_euler = (0, 0, 0)
        camera.data.type = "PERSP"
        camera.data.sensor_fit = "VERTICAL"
        camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / (name + ".png"))
    bpy.ops.render.render(write_still=True)
