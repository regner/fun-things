"""Render four isolated views; fitting imports are temporary read-only evidence composition."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_small_shop_shells_02"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1280, 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"
world = scene.world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.24, .30, .38, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = .55


def aim(obj, target):
    """Aim a studio camera or light without changing exported model orientation."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def light(name, position, energy, size):
    """Add a broad studio fill outside the export collection."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.shape, data.size = energy, "DISK", size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (0, 0, 2))


bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.015))
ground = bpy.context.object
mat = bpy.data.materials.new("STUDIO_ground")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (.13, .17, .20, 1)
mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = .8
ground.data.materials.append(mat)
light("STUDIO_key", (-6, 9, 18), 3600, 12)
light("STUDIO_rim", (3, -10, 14), 2800, 10)
light("STUDIO_front", (0, 12, 7), 900, 8)
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new("STUDIO_camera", data)
scene.collection.objects.link(camera)
scene.camera = camera


def render(name, position, target, scale):
    """Capture an orthographic inspection view at the specified physical scale."""
    camera.location = position
    aim(camera, target)
    data.type, data.ortho_scale = "ORTHO", scale
    scene.render.filepath = str(EVIDENCE / (name + ".png"))
    bpy.ops.render.render(write_still=True)


# Side/rear shell-only view makes the standalone wall and continuous coping visible.
render("side", (16, -12, 10), (0, 0, 2.2), 19)
# Instance unchanged fitting exports only in this unsaved render scene.
for side in ("left", "right"):
    for kind, folder, filename in (
        ("entrance_single", "city_shop_fittings_03", "city_shop_fittings_03_single"),
        ("door_single", "city_shop_fittings_06", "city_shop_fittings_06_single"),
        ("display_window", "city_shop_fittings_05", "city_shop_fittings_05"),
        ("canopy", "city_shop_fittings_01", "city_shop_fittings_01"),
        ("fascia", "city_shop_fittings_02", "city_shop_fittings_02"),
    ):
        before = set(bpy.data.objects)
        path = ROOT / f"art/models/environment/{folder}/{filename}.glb"
        bpy.ops.import_scene.gltf(filepath=str(path))
        mount = bpy.data.objects[f"mount_{side}_{kind}"].location
        for obj in set(bpy.data.objects) - before:
            if obj.parent is None:
                obj.location += mount
render("hero", (16, 20, 15), (0, 0, 2.2), 20)
render("detail", (1, 17, 7), (-3.2, 4.4, 2.25), 8.8)
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type, data.sensor_fit = "PERSP", "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
print("FOUR_VIEWS_RENDERED: side bare; hero/detail/overhead fitted; no source saved")
