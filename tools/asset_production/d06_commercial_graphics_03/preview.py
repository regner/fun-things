"""Render two artwork wraps on unchanged drum copies; never save source changes."""
from pathlib import Path
import math

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_commercial_graphics_03"
VARIANTS = ("last_call", "small_prices")
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / "art/source/models/environment/d06_poster_drum_01/d06_poster_drum_01.blend"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
collection = bpy.data.collections["export_d06_poster_drum_01"]
for obj in list(bpy.data.objects):
    if obj.name not in collection.all_objects:
        bpy.data.objects.remove(obj, do_unlink=True)
original_root = bpy.data.objects["D06PosterDrum01"]
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
    carrier = next(obj for obj in meshes if obj.name.startswith("D06PosterDrum01_Body"))
    carrier.data = carrier.data.copy()
    material = bpy.data.materials.new(variant + "_preview")
    material.use_nodes = True
    material.use_backface_culling = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Roughness"].default_value = 0.7
    texture = material.node_tree.nodes.new("ShaderNodeTexImage")
    texture.image = bpy.data.images.load(str(
        ROOT / f"art/textures/environment/{NID}/{variant}_albedo.png"))
    texture.extension = "EXTEND"
    material.node_tree.links.new(texture.outputs["Color"], principled.inputs["Base Color"])
    carrier.data.materials[1] = material
    root.location = (0.7 - index * 1.4, 0, 0)
    roots.append(root)

world = bpy.data.worlds.new("Signal Row poster studio")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.14, 0.18, 0.22, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.8


def aim(obj, target):
    """Aim camera/light in source coordinates without altering model orientation."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


for name, location, energy, size in [
    ("key", (-3, 4, 6), 750, 5), ("fill", (4, 2, 2), 450, 4),
    ("rear_seam_fill", (0, -4, 3), 500, 5)
]:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    light = bpy.data.objects.new(name, data)
    scene.collection.objects.link(light)
    light.location = location
    aim(light, (0, 0, 0.7))

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
    ("hero", (0.5, 7, 3.0), (0, 0, 0.74), 3.3),
    ("side", (5, 5, 2.6), (0, 0, 0.74), 3.4),
    # Rear view: both U=0/1 seams run down each artwork centre, not hidden off-camera.
    ("detail", (0, -7, 1.7), (0, 0, 0.77), 3.0),
]:
    camera.location = location
    aim(camera, target)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)

# Grounded, unscaled drums, offset from the vertical camera to expose a little wrap.
for index, root in enumerate(roots):
    root.location = (1.0 - index * 2.0, 0, 0)
camera.location = (0, 10, 47)
camera.rotation_euler = (0, 0, 0)
camera_data.type = "PERSP"
camera_data.sensor_fit = "VERTICAL"
camera_data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
print("POSTER_WRAP_PREVIEWS_PASS: no source, model export or world placement writes")
