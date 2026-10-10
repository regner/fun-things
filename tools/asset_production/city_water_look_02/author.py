"""Construct the original planar material swatch in pinned Blender, in metres."""
from pathlib import Path
import os
import runpy

import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "city_water_look_02"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
assert bpy.app.version_string == "5.2.2 LTS", bpy.app.version_string
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
root = bpy.data.objects.new("CityWaterLook02", None)
collection.objects.link(root)
root["asset_id"] = "city_water_look.02"
root["purpose"] = "Static material-study swatch only; not water geometry or a walkable surface"
root["authorship"] = "Original Blender construction and analytic texture recipe by Codex"
root["datum"] = "Surface-centred at zero; +Z up, +Y north maps to Godot -Z"
mesh = bpy.data.meshes.new("CityWaterLook02_Swatch")
mesh.from_pydata([(-8, -8, 0), (8, -8, 0), (8, 8, 0), (-8, 8, 0)], [], [(0, 1, 2, 3)])
mesh.update()
uv = mesh.uv_layers.new(name="UVMap")
for loop, coordinate in zip(uv.data, [(0, 0), (1, 0), (1, 1), (0, 1)]):
    loop.uv = coordinate
obj = bpy.data.objects.new("CityWaterLook02_Mesh", mesh)
collection.objects.link(obj)
obj.parent = root
material = bpy.data.materials.new("quiet_basin")
material.use_nodes = True
material.use_backface_culling = True
principled = material.node_tree.nodes.get("Principled BSDF")
principled.inputs["Roughness"].default_value = 0.40
principled.inputs["Metallic"].default_value = 0.0
principled.inputs["IOR"].default_value = 1.333
# These linear values are only the portable untextured GLB fallback.
base = tuple(((value / 255 + 0.055) / 1.055) ** 2.4 for value in (23, 67, 81))
principled.inputs["Base Color"].default_value = (*base, 1)
material.diffuse_color = (*base, 1)
mesh.materials.append(material)
for suffix in ("albedo", "normal"):
    path = ROOT / f"art/textures/environment/{NID}/quiet_basin_{suffix}.png"
    image = bpy.data.images.load(str(path))
    image.colorspace_settings.name = "sRGB" if suffix == "albedo" else "Non-Color"
    image.filepath = "//" + os.path.relpath(path, SOURCE.parent).replace("\\", "/")
    texture = material.node_tree.nodes.new("ShaderNodeTexImage")
    texture.name = f"quiet_basin_{suffix}"
    texture.image = image
    texture.extension = "REPEAT"
    texture.interpolation = "Linear"
    if suffix == "albedo":
        material.node_tree.links.new(texture.outputs["Color"], principled.inputs["Base Color"])
    else:
        normal = material.node_tree.nodes.new("ShaderNodeNormalMap")
        normal.inputs["Strength"].default_value = 1.0
        material.node_tree.links.new(texture.outputs["Color"], normal.inputs["Color"])
        material.node_tree.links.new(normal.outputs["Normal"], principled.inputs["Normal"])
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
print("WATER_SOURCE_PASS: one original four-vertex surface swatch with authored UV0")
