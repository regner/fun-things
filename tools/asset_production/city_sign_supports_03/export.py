"""Export only the noticeboard's declared collection using the shared pinned contract."""
import json
from pathlib import Path
import sys

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
NID = "city_sign_supports_03"
assert bpy.app.version_string == "5.2.2 LTS"
assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
assert {obj.name for obj in bpy.data.collections[f"export_{NID}"].objects} == {
    "CitySignSupports03", "CitySignSupports03_Hardware", "CitySignSupports03_ArtworkCarrier"
}
settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
settings.update(collection=f"export_{NID}", export_animations=False, export_skins=False)
output = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv
          else ROOT / f"art/models/environment/{NID}")
output.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(output / f"{NID}.glb"), **settings)
