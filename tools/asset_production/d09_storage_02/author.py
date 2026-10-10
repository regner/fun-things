"""Author a short dock container using the original storage-family Blender recipe."""
import math
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[3]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools/asset_production/d09_storage_01"))
import author as family

ASSET = "d09_storage_02"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
LENGTH_M = 6.0


def main():
    """Rebuild at half length without scaling the family cross-section or hardware."""
    assert bpy.app.version_string == "5.2.2 LTS"
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system, scene.unit_settings.scale_length = "METRIC", 1
    family.ASSET = ASSET
    family.PARTS.clear()
    collection = bpy.data.collections.new("export_" + ASSET)
    scene.collection.children.link(collection)
    family.build_container(length=LENGTH_M)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in family.PARTS:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = family.PARTS[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = "D09Storage02_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new("D09Storage02", None)
    collection.objects.link(root)
    mesh.parent = root
    root["asset_id"] = "d09_storage.02"
    root["authorship"] = "Original Blender construction using d09_storage_01 family recipe"
    root["axes"] = "Ground-centred; closed doors Blender +Y / Godot -Z"
    root["state"] = "Static intact exterior only; no opening doors, freight or stack simulation"
    root["length_m"] = LENGTH_M
    camera = family.studio(scene)
    camera.location = (10, 11, 8)
    family.aim(camera, (0, 0, 1.2))
    camera.data.ortho_scale = 10
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    script = Path(__file__).with_name("export.py")
    exec(compile(script.read_text(), str(script), "exec"), {"__file__": str(script)})
    for name, location, target, scale in [
        ("hero", (10, 11, 8), (0, 0, 1.2), 10),
        ("side", (15, 0, 4.5), (0, 0, 1.3), 8.5),
        ("detail", (5, 10, 4), (0, 2.6, 1.35), 5.6),
    ]:
        camera.location = location
        family.aim(camera, target)
        camera.data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location, camera.rotation_euler = (0, 0, 47), (0, 0, 0)
    camera.data.type, camera.data.sensor_fit = "PERSP", "VERTICAL"
    camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
