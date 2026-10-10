"""Render four isolated studio views; studio geometry never enters source or exports."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_shore_edges_04"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
EVIDENCE.mkdir(parents=True, exist_ok=True)
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.wm.open_mainfile(filepath=str(
    ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"))
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 40
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.compression = 95
# Output dither otherwise adds high-entropy noise across the empty studio background.
scene.render.dither_intensity = 0
scene.view_settings.view_transform = "AgX"
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.22, .28, .33, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .6


def aim(obj, target):
    """Aim studio camera and lights without changing the component axes."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


# Isolated exhibit floor; temporary roots align toes for three inspection views.
# No studio geometry or display transforms enter source or exports.
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.001))
ground = bpy.context.object
mat = bpy.data.materials.new("STUDIO_background")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (.12, .18, .20, 1)
mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = .8
ground.data.materials.append(mat)
for name, position, energy, size in (
    ("key", (2, 5, 10), 1700, 8), ("fill", (-6, -3, 6), 1300, 7),
    ("rim", (3, -6, 5), 900, 5),
):
    data = bpy.data.lights.new("STUDIO_" + name, "AREA")
    data.energy, data.shape, data.size = energy, "DISK", size
    obj = bpy.data.objects.new("STUDIO_" + name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (0, 0, 0))
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new("STUDIO_camera", data)
scene.collection.objects.link(camera)
scene.camera = camera
# Display only: align bottoms on the isolated floor for the first three views.
# Export roots stay identity; the overhead restores the actual common land datum.
roots = []
for column, family in enumerate(("wall", "quay", "rock")):
    for row, variant in enumerate(("corner", "end")):
        obj = bpy.data.objects["CityShoreEdges04_" + family + "_" + variant]
        obj.location = ((column - 1) * 4.5, 2.5 if row == 0 else -2.1,
                        {"wall": 0, "quay": 2.4, "rock": .6}[family])
        roots.append(obj)
for name, position, target, scale in (
    ("hero", (12, -18, 16), (-.3, .7, 1), 16.5),
    ("side", (6, -20, 9), (-.3, .7, .8), 16.0),
):
    camera.location = position
    aim(camera, target)
    data.type, data.ortho_scale = "ORTHO", scale
    scene.render.filepath = str(EVIDENCE / (name + ".png"))
    bpy.ops.render.render(write_still=True)
# Three terminal noses side by side expose the finish and untouched mating planes.
for obj in roots:
    obj.children[0].hide_render = obj.name.endswith("corner")
camera.location = (8, -12, 8)
aim(camera, (0, -2.1, 1.05))
data.ortho_scale = 12.5
scene.render.filepath = str(EVIDENCE / "detail.png")
bpy.ops.render.render(write_still=True)
for obj in roots:
    obj.children[0].hide_render = False
    obj.location.z = 0
# Overhead ground plane is below the deepest toe, never an authored land/water surface.
ground.location.z = -2.401
camera.location = (0, .5, 47)
camera.rotation_euler = (0, 0, 0)
data.type, data.sensor_fit = "PERSP", "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
print("FOUR_ISOLATED_VIEWS_RENDERED")
