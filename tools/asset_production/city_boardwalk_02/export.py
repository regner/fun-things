"""Export each named bend collection with the shared pinned static GLB settings."""
import json
from pathlib import Path
import sys

import bpy
import io_scene_gltf2

sys.path.insert(0, str(Path(__file__).parent))
from design import ASSET, VARIANTS

ROOT = Path(__file__).resolve().parents[3]
assert bpy.app.version_string == "5.2.2 LTS"
assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
output = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv else
          ROOT / f"art/models/environment/{ASSET}")
output.mkdir(parents=True, exist_ok=True)
settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
settings.update(export_animations=False, export_skins=False)
for suffix, _angle, _count in VARIANTS:
    name = ASSET + suffix
    settings.update(filepath=str(output / (name + ".glb")), collection="export_" + name)
    bpy.ops.export_scene.gltf(**settings)
    print("EXPORTED", name)
