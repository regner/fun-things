"""Export only the six declared reusable rail components with the shared glTF settings."""
import json
from pathlib import Path
import sys

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_quay_furniture_02"
COMPONENTS = ("straight", "corner", "end", "post_quay", "post_deck", "post_landward")
assert bpy.app.version_string == "5.2.2 LTS", bpy.app.version_string
assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
settings.update(export_animations=False, export_skins=False)
out = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv
       else ROOT / f"art/models/environment/{ASSET}")
out.mkdir(parents=True, exist_ok=True)
for component in COMPONENTS:
    settings["collection"] = f"export_{ASSET}_{component}"
    settings["filepath"] = str(out / f"{ASSET}_{component}.glb")
    bpy.ops.export_scene.gltf(**settings)
