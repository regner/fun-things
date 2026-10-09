"""Export only the declared static drum collection with the shared export contract."""
import json
from pathlib import Path
import sys

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_poster_drum_01"
assert bpy.app.version_string == "5.2.2 LTS", bpy.app.version_string
assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
settings.update(collection=f"export_{NID}", export_animations=False, export_skins=False)
output = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv
          else ROOT / f"art/models/environment/{NID}")
output.mkdir(parents=True, exist_ok=True)
settings["filepath"] = str(output / f"{NID}.glb")
bpy.ops.export_scene.gltf(**settings)
