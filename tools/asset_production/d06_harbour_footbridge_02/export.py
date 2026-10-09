"""Export only the named span collection using the shared glTF contract."""
import json
import sys
from pathlib import Path

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_harbour_footbridge_02"
assert bpy.app.version_string == "5.2.2 LTS", bpy.app.version_string
assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
settings.update(collection=f"export_{NID}", export_animations=False, export_skins=False)
out = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv
       else ROOT / f"art/models/environment/{NID}")
out.mkdir(parents=True, exist_ok=True)
settings["filepath"] = str(out / f"{NID}.glb")
bpy.ops.export_scene.gltf(**settings)
