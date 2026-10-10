"""Render all three artworks on unchanged Blender fascia instances; never save a dependency."""
from pathlib import Path
import hashlib
import math

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_civic_graphics_04"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / "art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend"
assert bpy.app.version_string == "5.2.2 LTS"
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
collection = bpy.data.collections["export_city_shop_fittings_02"]
for obj in list(bpy.data.objects):
    if obj.name not in collection.all_objects:
        bpy.data.objects.remove(obj, do_unlink=True)
originals = list(collection.objects)
roots = []
for index, variant in enumerate(("tide_tea", "quay_pantry", "hem_repairs")):
    copies = {}
    for original in originals:
        copy = original.copy()
        if copy.type == "MESH":
            copy.data = original.data.copy()
        scene.collection.objects.link(copy)
        copies[original] = copy
    for original, copy in copies.items():
        copy.parent = copies.get(original.parent)
    root = copies[bpy.data.objects["city_shop_fittings_02"]]
    root.location.z = 1.05 - index * 1.05
    roots.append(root)
    material = bpy.data.materials.new(f"old_quay_{variant}_preview")
    material.use_nodes = True
    material.use_backface_culling = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Roughness"].default_value = 0.56
    texture = material.node_tree.nodes.new("ShaderNodeTexImage")
    texture.image = bpy.data.images.load(
        str(ROOT / f"art/textures/environment/{NID}/{variant}_albedo.png"))
    texture.extension = "EXTEND"
    material.node_tree.links.new(texture.outputs["Color"], principled.inputs["Base Color"])
    copies[bpy.data.objects["fascia_artwork_carrier"]].data.materials[0] = material
for obj in originals:
    bpy.data.objects.remove(obj, do_unlink=True)
world = bpy.data.worlds.new("Old Quay evidence world")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.14, 0.18, 0.22, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.8


def aim(obj, target):
    """Aim evidence camera/light with Blender's negative-Z viewing axis."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


for name, location, energy, size in [
    ("key", (-3, 4, 6), 750, 5), ("fill", (4, 2, 2), 450, 4)
]:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    aim(obj, (0, 0, 0))
camera_data = bpy.data.cameras.new("Evidence camera")
camera = bpy.data.objects.new("Evidence camera", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.compression = 95
scene.render.dither_intensity = 0
scene.view_settings.view_transform = "AgX"
scene.render.film_transparent = False
EVIDENCE.mkdir(parents=True, exist_ok=True)
for name, location, scale in [
    ("hero", (-1.0, 6.8, 1.3), 6.0),
    ("side", (3.0, 3.0, 0.8), 6.6),
    ("detail", (0, 6, 1.05), 3.7),
]:
    for root in roots[1:]:
        for child in root.children:
            child.hide_render = name == "detail"
    camera.location = location
    aim(camera, (0, 0.05, 1.05 if name == "detail" else 0))
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)
# Separate three hypothetical flat-wall bays, mounting pivot 3.8m, no implied world placement.
for index, root in enumerate(roots):
    for child in root.children:
        child.hide_render = False
    root.location = ((index - 1) * 4, 0, 3.8)
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
camera_data.type = "PERSP"
camera_data.sensor_fit = "VERTICAL"
camera_data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
assert source_hash == hashlib.sha256(SOURCE.read_bytes()).hexdigest()
print("CIVIC_PREVIEWS_PASS: no shared source or GLB writes")
