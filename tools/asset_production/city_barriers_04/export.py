"""Fresh-export existing terminal dependencies to scratch; never duplicate production carriers."""
import json
from pathlib import Path

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
KIT = "city_quay_furniture_02"
SCRATCH = Path("C:/tmp/ft/assets/city_barriers_04/reexport")
COMPONENTS = ("end", "post_landward")


def main():
    """Open the unchanged kit source and export only this reference's two shared components."""
    assert bpy.app.version_string == "5.2.2 LTS"
    assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
    bpy.ops.wm.open_mainfile(filepath=str(
        ROOT / f"art/source/models/environment/{KIT}/{KIT}.blend"))
    settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
    settings.update(export_animations=False, export_skins=False)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    for component in COMPONENTS:
        bpy.ops.export_scene.gltf(**dict(
            settings, collection=f"export_{KIT}_{component}",
            filepath=str(SCRATCH / f"{KIT}_{component}.glb")))


if __name__ == "__main__":
    main()
