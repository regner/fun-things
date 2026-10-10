"""Export only the saved Sable wreck collection using the shared static glTF contract."""
import json
from pathlib import Path
import sys

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
ASSET = "vehicle_wrecks_01"
assert bpy.app.version_string == "5.2.2 LTS"
assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
output = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv
          else ROOT / f"art/models/vehicles/{ASSET}")
output.mkdir(parents=True, exist_ok=True)
settings.update(collection="export_" + ASSET, export_animations=False, export_skins=False,
                filepath=str(output / (ASSET + ".glb")))
bpy.ops.export_scene.gltf(**settings)
