"""Export only the saved corner seat collection using the shared pinned contract."""
import json
from pathlib import Path
import sys

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_seating_03"
assert bpy.app.version_string == "5.2.2 LTS"
assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
outdir = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv else
          ROOT / f"art/models/environment/{ASSET}")
outdir.mkdir(parents=True, exist_ok=True)
settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
settings.update(collection="export_" + ASSET, export_animations=False, export_skins=False,
                filepath=str(outdir / (ASSET + ".glb")))
bpy.ops.export_scene.gltf(**settings)
print("EXPORT_PASS", settings["filepath"])
