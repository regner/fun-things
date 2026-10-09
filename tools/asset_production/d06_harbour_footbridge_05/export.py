"""Export the three named access collections through the existing shared glTF contract."""
import json
import sys
from pathlib import Path

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_harbour_footbridge_05"
assert bpy.app.version_string == "5.2.2 LTS"
assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
settings.update(export_animations=False, export_skins=False)
out = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv
       else ROOT / f"art/models/environment/{NID}")
out.mkdir(parents=True, exist_ok=True)
for variant in ("main", "south", "quay"):
    settings.update(collection=f"export_{NID}_{variant}",
                    filepath=str(out / f"{NID}_{variant}.glb"))
    bpy.ops.export_scene.gltf(**settings)
