"""Render linked GLBs at full transforms read back from the saved fitted Godot scene."""
import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs/assets/production/d06_shopfront_blocks_03-evidence"
report = json.loads((EVIDENCE / "validation.json").read_text())
scene_file = ROOT / "scenes/prefabs/environment/d06_shopfront_blocks_03_fitted.tscn"
assert hashlib.sha256(scene_file.read_bytes()).hexdigest() == report["scenes"]["res://scenes/prefabs/environment/d06_shopfront_blocks_03_fitted.tscn"]["sha256"]
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
for model in report["model_instances"]:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(ROOT / model["path"].removeprefix("res://")))
    x, y, z = model["position"]
    for obj in set(bpy.data.objects) - before:
        if obj.parent is None:
            obj.matrix_world = (Matrix.Translation(Vector((x, -z, y)))
                                @ Matrix.Rotation(math.radians(model["yaw_degrees"]), 4, "Z")
                                @ obj.matrix_world)

# Studio ground exists only in this unsaved evidence session, never in the asset scene/export.
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.015))
material = bpy.data.materials.new("STUDIO_only_slate")
material.use_nodes = True
material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (.13, .17, .20, 1)
material.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = .8
bpy.context.object.data.materials.append(material)
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.24, .30, .38, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .55


def aim(obj, target):
    """Aim evidence lighting/cameras without modifying any linked model geometry."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


for name, loc, power, size in (
        ("key", (-12, 16, 25), 10000, 22),
        ("rim", (8, -14, 18), 6500, 18),
        ("front", (0, 18, 9), 3000, 16)):
    data = bpy.data.lights.new("STUDIO_" + name, "AREA")
    data.energy, data.shape, data.size = power, "DISK", size
    obj = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(obj)
    obj.location = loc
    aim(obj, (0, 0, 2))
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new(data.name, data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.compression = 95
scene.render.dither_intensity = 0
scene.view_settings.view_transform = "AgX"


def render(name, position, target, scale):
    """Capture a shell inspection or chamfer detail; no scene is saved from Blender."""
    camera.location = position
    aim(camera, target)
    data.type, data.ortho_scale = "ORTHO", scale
    scene.render.filepath = str(EVIDENCE / (name + ".png"))
    bpy.ops.render.render(write_still=True)


render("hero", (26, 33, 25), (0, 0, 1.8), 32)
render("side", (-25, -30, 24), (0, 0, 1.8), 32)
render("detail", (21, 24, 13), (5.2, 3.7, 2.2), 15)
camera.location, camera.rotation_euler = (0, 0, 47), (0, 0, 0)
data.type, data.sensor_fit = "PERSP", "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
report["renders"] = {"engine": "Blender Cycles CPU", "samples": 24, "view_transform": "AgX",
                     "dimensions": [1280, 720], "png_compression": 95, "dither_intensity": 0,
                     "overhead": {"height_m": 47, "vertical_fov_degrees": 42,
                                  "north_up": True, "vertical_down": True},
                     "placement_source": "model_instances measured from saved Godot scene",
                     "scope": "isolated evidence, not a Godot gameplay capture"}
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print("FOUR_CHAMFERED_CORNER_RENDERS_PASS")
