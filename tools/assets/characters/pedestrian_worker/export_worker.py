"""Re-export declared collections from the committed worker Blender source."""

import hashlib
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[4]
OUTPUTS = ["pedestrian_worker_a"]


def export_all(destination=None):
    """Validate collection scope and export source-linked GLBs with the pinned preset."""
    if bpy.app.version_string != "5.2.2 LTS":
        raise RuntimeError("Expected Blender 5.2.2 LTS")
    source = ROOT / "art/source/models/characters/pedestrian_worker/pedestrian_worker_a.blend"
    if Path(bpy.data.filepath).resolve() != source:
        raise RuntimeError("Worker source path mismatch")
    destination = Path(destination or ROOT / "art/models/characters/pedestrian_worker")
    destination.mkdir(parents=True, exist_ok=True)
    settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
    settings["export_animations"] = False
    settings["export_vertex_color"] = "NAME"
    settings["export_vertex_color_name"] = "worker_region"
    settings["export_all_vertex_colors"] = False
    rows = []
    for asset_id in OUTPUTS:
        collection = bpy.data.collections["export_" + asset_id]
        expected = {"WorkerMesh", "Rig"}
        if {object_.name for object_ in collection.all_objects} != expected:
            raise RuntimeError("Unexpected export members: " + asset_id)
        for object_ in collection.all_objects:
            if object_.type not in {"MESH", "ARMATURE"} or any(abs(v - 1) > .00001 for v in object_.scale):
                raise RuntimeError("Invalid export object: " + object_.name)
            if object_.matrix_world.determinant() <= 0:
                raise RuntimeError("Non-positive transform")
        target = destination / (asset_id + ".glb")
        settings["collection"] = collection.name
        settings["export_animations"] = True
        settings["export_vertex_color"] = "NAME"
        settings["filepath"] = str(target)
        bpy.ops.export_scene.gltf(**settings)
        rows.append({"collection": collection.name, "members": sorted(expected),
                     "output": str(target),
                     "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    print("WORKER_EXPORT", json.dumps(rows))
    return rows


if __name__ == "__main__":
    import sys
    destination = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else None
    export_all(destination)
