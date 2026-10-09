"""Export only the explicit shell collection using the shared static glTF contract."""
import json
from pathlib import Path
import sys

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_small_shop_shells_02"
assert bpy.app.version_string == "5.2.2 LTS"
assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
output = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv else
          ROOT / f"art/models/environment/{ASSET}/{ASSET}.glb")
output.parent.mkdir(parents=True, exist_ok=True)
settings.update(filepath=str(output), collection="export_" + ASSET,
                export_animations=False, export_skins=False)
bpy.ops.export_scene.gltf(**settings)
print("EXPORTED", output)
