"""Export only the named tyre-rack collection with the shared glTF contract."""
import json
from pathlib import Path
import sys

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d08_repair_furniture_02"
assert bpy.app.version_string == "5.2.2 LTS"
assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
settings.update(collection="export_" + ASSET, export_animations=False, export_skins=False)
out = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv
       else ROOT / f"art/models/environment/{ASSET}")
out.mkdir(parents=True, exist_ok=True)
settings["filepath"] = str(out / (ASSET + ".glb"))
bpy.ops.export_scene.gltf(**settings)
print("D08_REPAIR_FURNITURE_02_EXPORTED", settings["filepath"])
