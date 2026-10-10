"""Render saved group placements using the unchanged Blender trolley source and family studio."""
import math
from pathlib import Path
import sys

import bpy

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))
import assembly


def main():
    """Produce four isolated review views without saving a duplicate model or export."""
    assert bpy.app.version_string == "5.2.2 LTS"
    assembly.EVIDENCE.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(assembly.SOURCE))
    scene = bpy.context.scene
    studio = assembly.load_tool("shelter_author",
        "tools/asset_production/d07_trolley_shelter_01/author.py")
    original = bpy.data.objects["D07TrolleyShelter02_Mesh"]
    for name, (x, y, z) in assembly.placements():
        instance = original.copy()
        instance.data = original.data
        instance.name = "REFERENCE_" + name
        scene.collection.objects.link(instance)
        instance.parent = None
        instance.location = (x, -z, y)
    bpy.data.objects.remove(original, do_unlink=True)
    camera = scene.camera
    for name, position, target, scale in [
        ("hero", (3.0, 4.0, 2.6), (0, 0, .50), 3.8),
        ("side", (4, 0, 1.6), (0, 0, .52), 3.6),
        ("detail", (1.6, -2.6, 2.1), (0, -.22, .71), 2.5),
    ]:
        camera.location = position
        studio.aim(camera, target)
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = scale
        scene.render.filepath = str(assembly.EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location = (0, 0, 47)
    camera.rotation_euler = (0, 0, 0)
    camera.data.type = "PERSP"
    camera.data.sensor_fit = "VERTICAL"
    camera.data.angle = math.radians(42)
    scene.render.filepath = str(assembly.EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
