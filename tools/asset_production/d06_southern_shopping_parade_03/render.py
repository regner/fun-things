"""Render actual saved-reference GLB placements in an isolated Blender studio."""
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_southern_shopping_parade_03"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
assert bpy.app.version_string == "5.2.2 LTS"
receipt = json.loads((SCRATCH / "prefab.json").read_text())
assert receipt["ok"]
bpy.ops.wm.open_mainfile(filepath=str(ROOT / f"art/source/models/environment/{NID}/{NID}.blend"))
# Keep only the authored studio. Geometry comes from the real imported GLBs and
# transforms recorded by Godot, so render composition is never a second placement writer.
for obj in list(bpy.data.collections[f"export_{NID}"].objects):
    bpy.data.objects.remove(obj, do_unlink=True)
conversion = Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))
for row in receipt["model_instances"]:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(ROOT / row["model"].removeprefix("res://")))
    transform = conversion @ Matrix(row["matrix_godot"]) @ conversion.inverted()
    for obj in set(bpy.data.objects) - before:
        if obj.parent is None:
            obj.matrix_world = transform @ obj.matrix_world
bpy.context.view_layer.update()
scene = bpy.context.scene
for obj in scene.objects:
    if obj.type == "LIGHT":
        obj.location.y += 25
        obj.rotation_euler = (Vector((0,20,2))-obj.location).to_track_quat('-Z','Y').to_euler()
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
    ("hero", (-22,57,20), (0,25,2.6), 27),
    ("side", (-52,65,53), (0,0,2), 73),
    ("relief_detail", (-12,44,7), (-5.8,30,2.5), 8),
    ("overhead_47m_42deg", (0,38,47), (0,0,0), 0),
]:
    if selected and name not in selected:
        continue
    camera.location = location
    if scale:
        camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        camera.data.type, camera.data.ortho_scale = "ORTHO", scale
    else:
        camera.rotation_euler = (0,0,0)
        camera.data.type = "PERSP"
        camera.data.sensor_fit = "VERTICAL"
        camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / (name + ".png"))
    bpy.ops.render.render(write_still=True)
