"""Export the two cloth collections through the shared pinned glTF contract."""
import json
from pathlib import Path
import sys

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_laundry_frames_03"
assert bpy.app.version_string == "5.2.2 LTS", bpy.app.version_string
assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
settings.update(export_animations=False, export_skins=False)
bpy.context.window.scene = bpy.data.scenes["ClothSources"]
outdir = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv
          else ROOT / f"art/models/environment/{NID}")
outdir.mkdir(parents=True, exist_ok=True)
for variant in ("sheet", "towel"):
    settings["collection"] = f"export_{NID}_{variant}"
    settings["filepath"] = str(outdir / f"{NID}_{variant}.glb")
    bpy.ops.export_scene.gltf(**settings)
