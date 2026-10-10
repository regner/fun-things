"""Export the explicit saved swatch collection with a texture-free PBR fallback."""
from pathlib import Path
import json
import sys

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
NID = "city_water_look_01"
assert bpy.app.version_string == "5.2.2 LTS"
assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
output = (Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv
          else ROOT / f"art/models/environment/{NID}")
output.mkdir(parents=True, exist_ok=True)
settings = json.loads((ROOT / "tools/assets/blender/export_settings.json").read_text())
settings.update(collection=f"export_{NID}", export_animations=False, export_skins=False,
                filepath=str(output / f"{NID}.glb"))
material = bpy.data.materials["open_sea"]
# Preserve external texture ownership: Godot uses the saved .tres override. Never embed PNGs.
links = [(link.from_socket, link.to_socket) for link in material.node_tree.links
         if link.to_node.type == "BSDF_PRINCIPLED"]
for link in list(material.node_tree.links):
    if link.to_node.type == "BSDF_PRINCIPLED":
        material.node_tree.links.remove(link)
try:
    bpy.ops.export_scene.gltf(**settings)
finally:
    for source, target in links:
        material.node_tree.links.new(source, target)
print("WATER_EXPORT_PASS: shared export contract; external images remain outside GLB")
