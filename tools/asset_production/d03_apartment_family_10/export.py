"""Export each identity-transform roof cap from its own explicit collection."""
import json
import sys
from pathlib import Path

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_10"
assert bpy.app.version_string == "5.2.2 LTS", bpy.app.version_string
assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
settings.update(export_animations=False, export_skins=False)
outdir = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv
          else ROOT / f"art/models/environment/{NID}")
outdir.mkdir(parents=True, exist_ok=True)
for variant in ("straight", "end", "outside", "inside"):
    settings["collection"] = f"export_{NID}_{variant}"
    settings["filepath"] = str(outdir / f"{NID}_{variant}.glb")
    bpy.ops.export_scene.gltf(**settings)
