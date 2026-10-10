"""Export only the eight named fascia collections using the shared static GLB contract."""
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
outdir = Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv else (
    ROOT / f"art/models/environment/{ASSET}")
outdir.mkdir(parents=True, exist_ok=True)
settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
settings.update(export_animations=False, export_skins=False)
for suffix, *_unused in VARIANTS:
    name = ASSET + suffix
    settings.update(collection="export_" + name, filepath=str(outdir / (name + ".glb")))
    bpy.ops.export_scene.gltf(**settings)
print("EIGHT_FASCIA_EXPORTS_PASS")
