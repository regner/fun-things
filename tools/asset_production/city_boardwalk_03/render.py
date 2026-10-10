"""Four isolated Blender views of the trim fitted to unchanged source-linked sibling decks."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_boardwalk_03"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
EVIDENCE.mkdir(parents=True, exist_ok=True)
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
scene = bpy.context.scene
for collection in list(bpy.data.collections):
    if collection.name.startswith("export_"):
        collection.hide_render = True
bends, straight = [], []


def trim(suffix, position, angle, group):
    """Duplicate source mesh references for transient studio placement, never save or export them."""
    source = bpy.data.objects["CityBoardwalk03" + suffix + "_Mesh"]
    obj = bpy.data.objects.new("STUDIO_" + suffix, source.data)
    scene.collection.objects.link(obj)
    obj.location, obj.rotation_euler.z = position, angle
    group.append(obj)


def deck(asset, suffix, position, group):
    """Load unchanged sibling Blender collections for fit context; never write sibling paths."""
    path = ROOT / f"art/source/models/environment/{asset}/{asset}.blend"
    with bpy.data.libraries.load(str(path), link=False) as (_available, selected):
        selected.collections = ["export_" + asset + suffix]
    collection = selected.collections[0]
    scene.collection.children.link(collection)
    for obj in collection.objects:
        if obj.parent is None:
            obj.location = position
        group.append(obj)


for suffix, degrees, offset in (("", "90", 0), ("_45", "45", -6), ("_22p5", "22p5", -11)):
    deck("city_boardwalk_02", suffix, (offset, 0, 0), bends)
    for edge in ("outer", "inner"):
        trim("_" + edge + "_" + degrees, (offset, 0, 0), 0, bends)
deck("city_boardwalk_01", "", (10, 3, 0), straight)
trim("", (11.8, 3, 0), 0, straight)
trim("", (8.2, 3, 0), math.pi, straight)
trim("_terminal", (10, 6, 0), math.pi / 2, straight)
scene.render.engine = "CYCLES"
scene.cycles.device, scene.cycles.samples = "CPU", 96
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.compression = 95
scene.view_settings.view_transform = "AgX"
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.22, .28, .33, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .6


def aim(obj, target):
    """Orient studio equipment without changing the saved asset coordinates."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.32))
ground = bpy.context.object
ground.name = "STUDIO_ground_not_exported"
mat = bpy.data.materials.new("STUDIO_background")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (.12, .18, .20, 1)
mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = .8
ground.data.materials.append(mat)
for name, position, energy, size in (
    ("key", (8, 5, 12), 2200, 9), ("fill", (-6, -3, 7), 1500, 8),
    ("rim", (9, 9, 5), 1000, 6),
):
    data = bpy.data.lights.new("STUDIO_" + name, "AREA")
    data.energy, data.shape, data.size = energy, "DISK", size
    obj = bpy.data.objects.new("STUDIO_" + name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (2, 3, 0))
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new("STUDIO_camera", data)
scene.collection.objects.link(camera)
scene.camera = camera
for name, position, target, scale in (
    ("hero", (18, -22, 25), (.3, 3.5, -.1), 31),
    ("side", (18, 9, 2.2), (10, 3, -.1), 8.5),
    ("detail", (15, 10, 2.8), (11.4, 5.5, -.10), 3.2),
):
    for obj in bends:
        obj.hide_render = name != "hero"
    scene.render.resolution_x, scene.render.resolution_y = {
        "hero": (1152, 648), "side": (1280, 720), "detail": (1024, 576),
    }[name]
    camera.location = position
    aim(camera, target)
    data.type, data.ortho_scale = "ORTHO", scale
    scene.render.filepath = str(EVIDENCE / (name + ".png"))
    bpy.ops.render.render(write_still=True)
for obj in bends:
    obj.hide_render = False
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
camera.location, camera.rotation_euler = (0, 3.5, 47), (0, 0, 0)
data.type, data.sensor_fit = "PERSP", "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
print("FOUR_ISOLATED_MATING_VIEWS_RENDERED")
