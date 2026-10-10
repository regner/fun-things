"""Export the declared swatch with an external-material slot, never embedded textures."""
import json
import sys
from pathlib import Path

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
NID = "city_ground_finishes_05"


def export_swatch(directory):
    """Apply shared export settings; temporarily disconnect the externally remapped albedo."""
    assert bpy.app.version_string == "5.2.2 LTS"
    assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
    settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
    settings.update(collection="export_" + NID, export_animations=False, export_skins=False)
    directory.mkdir(parents=True, exist_ok=True)
    settings["filepath"] = str(directory / f"{NID}.glb")
    material = bpy.data.materials["quiet_garden_soil"]
    tree = material.node_tree
    base = tree.nodes["Principled BSDF"].inputs["Base Color"]
    texture_output = tree.nodes["CommittedAlbedo"].outputs["Color"]
    for link in list(base.links):
        tree.links.remove(link)
    try:
        bpy.ops.export_scene.gltf(**settings)
    finally:
        tree.links.new(texture_output, base)


if __name__ == "__main__":
    output = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv else
              ROOT / f"art/models/environment/{NID}")
    export_swatch(output)
