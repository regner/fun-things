"""Render three artwork variants on linked-source fascia copies; never save source changes."""
from pathlib import Path
import math

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_commercial_graphics_02"
VARIANTS = ("loose_change", "second_helping", "side_b")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / "art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
collection = bpy.data.collections["export_city_shop_fittings_02"]
for obj in list(bpy.data.objects):
    if obj.name not in collection.all_objects:
        bpy.data.objects.remove(obj, do_unlink=True)
original_root = bpy.data.objects["city_shop_fittings_02"]
original_meshes = list(original_root.children)
roots = []
for index, variant in enumerate(VARIANTS):
    if index == 0:
        root = original_root
        meshes = original_meshes
    else:
        root = original_root.copy()
        scene.collection.objects.link(root)
        root.name = variant
        meshes = []
        for original in original_meshes:
            obj = original.copy()
            obj.parent = root
            scene.collection.objects.link(obj)
            meshes.append(obj)
    # Material-slot changes stay confined to a transient mesh data copy in this process.
    carrier = next(obj for obj in meshes if obj.name.startswith("fascia_artwork_carrier"))
    carrier.data = carrier.data.copy()
    material = bpy.data.materials.new(variant + "_preview")
    material.use_nodes = True
    material.use_backface_culling = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Roughness"].default_value = 0.56
    texture = material.node_tree.nodes.new("ShaderNodeTexImage")
    texture.image = bpy.data.images.load(str(
        ROOT / f"art/textures/environment/{NID}/{variant}_albedo.png"))
    texture.extension = "EXTEND"
    material.node_tree.links.new(texture.outputs["Color"], principled.inputs["Base Color"])
    carrier.data.materials[0] = material
    root.location = (0, 0, 1.1 - index * 1.1)
    roots.append(root)

world = bpy.data.worlds.new("Signal Row fascia studio")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.14, 0.18, 0.22, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.8


def aim(obj, target):
    """Aim camera/light in source coordinates without altering model orientation."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


for name, location, energy, size in [
    ("key", (-3, 4, 6), 750, 5), ("fill", (4, 2, 2), 450, 4)
]:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    light = bpy.data.objects.new(name, data)
    scene.collection.objects.link(light)
    light.location = location
    aim(light, (0, 0, 0))

camera_data = bpy.data.cameras.new("Evidence camera")
camera = bpy.data.objects.new("Evidence camera", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = 1280
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"
scene.render.film_transparent = False
EVIDENCE.mkdir(parents=True, exist_ok=True)
for name, location, target, scale in [
    ("hero", (-0.6, 7, 1.3), (0, 0, 0), 5.1),
    ("side", (4, 6, 1.1), (0, 0.04, 0), 5.5),
    ("detail", (1.05, 3, -0.6), (0.95, 0.128, -1.1), 1.75),
]:
    camera.location = location
    aim(camera, target)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)

# Three equally high vertical storefront faces: left tag, middle bowl, right disc.
# Translation only, matching the hall's inherited 3.8m wall-centre mounting proposal.
for index, root in enumerate(roots):
    root.location = (4 - index * 4, 0, 3.8)
camera.location = (0, 10, 47)
camera.rotation_euler = (0, 0, 0)
camera_data.type = "PERSP"
camera_data.sensor_fit = "VERTICAL"
camera_data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
print("SHOP_FASCIA_PREVIEWS_PASS: no source, geometry export or world placement writes")
