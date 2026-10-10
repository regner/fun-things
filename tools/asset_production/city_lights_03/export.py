"""Export warm/cool yard poles from the saved named collection using the shared contract."""
import json
import sys
from pathlib import Path

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_lights_03"
assert bpy.app.version_string == "5.2.2 LTS", bpy.app.version_string
assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
settings.update(collection=f"export_{ASSET}", export_animations=False, export_skins=False)
outdir = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv
          else ROOT / f"art/models/environment/{ASSET}")
outdir.mkdir(parents=True, exist_ok=True)
obj = bpy.data.objects["CityLights03_Mesh"]
slot = next(slot for slot in obj.material_slots if slot.material.name == "lens_warm")
try:
    for variant in ("warm", "cool"):
        slot.material = bpy.data.materials[f"lens_{variant}"]
        settings["filepath"] = str(outdir / f"{ASSET}_{variant}.glb")
        bpy.ops.export_scene.gltf(**settings)
finally:
    slot.material = bpy.data.materials["lens_warm"]
