"""Re-export the open committed S13 humanoid source to a requested GLB path."""
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[2]
COLLECTION_NAME = "export_s13_humanoid"
EXPECTED_OBJECTS = {"Rig", "Skin"}
EXPECTED_ACTIONS = {"idle", "walk", "run", "death"}
EXPECTED_BONES = {"root", "spine", "head", "arm_l", "arm_r", "leg_l", "leg_r"}


def main():
    """Validate source structure and export it with the project's pinned glTF settings."""
    if bpy.app.version_string != "5.2.2 LTS":
        raise RuntimeError(f"expected Blender 5.2.2 LTS, got {bpy.app.version_string}")
    if Path(bpy.data.filepath).name != "s13_humanoid.blend":
        raise RuntimeError("unexpected source file")
    if "--" not in sys.argv:
        raise RuntimeError("output path required after --")
    output = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    collection = bpy.data.collections[COLLECTION_NAME]
    if {item.name for item in collection.all_objects} != EXPECTED_OBJECTS:
        raise RuntimeError("unexpected export collection membership")
    if set(bpy.data.actions.keys()) != EXPECTED_ACTIONS:
        raise RuntimeError("unexpected animation actions")
    rig = bpy.data.objects["Rig"]
    if {bone.name for bone in rig.data.bones} != EXPECTED_BONES:
        raise RuntimeError("unexpected rig bones")
    mesh = bpy.data.objects["Skin"]
    triangle_count = sum(len(polygon.vertices) - 2 for polygon in mesh.data.polygons)
    if triangle_count >= 1500:
        raise RuntimeError(f"triangle budget exceeded: {triangle_count}")
    for item in collection.all_objects:
        if any(abs(value - 1.0) > 0.0001 for value in item.scale):
            raise RuntimeError(f"non-unit object scale: {item.name}")
        if item.matrix_world.determinant() <= 0:
            raise RuntimeError(f"non-positive transform: {item.name}")
    settings = json.loads((ROOT / "tools/s01/export_settings.json").read_text())
    settings["collection"] = COLLECTION_NAME
    settings["export_animations"] = True
    settings["filepath"] = str(output)
    bpy.ops.export_scene.gltf(**settings)
    print("S13_EXPORT", output, "triangles", triangle_count)


if __name__ == "__main__":
    main()
