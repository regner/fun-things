"""Render unchanged Blender collections at placements measured from the saved Godot assembly."""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_02"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
assert bpy.app.version_string == "5.2.2 LTS"
receipt = json.loads((SCRATCH / "prefab-check.json").read_text())
assert receipt["ok"] and receipt["roundtrip"]["byte_stable"]
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collections = {}
for index, item in enumerate(receipt["models"]):
    glb = Path(item["path"].removeprefix("res://"))
    sibling = glb.parent.name
    if glb.stem not in collections:
        source = ROOT / f"art/source/models/environment/{sibling}/{sibling}.blend"
        with bpy.data.libraries.load(str(source), link=True) as (_, loaded):
            loaded.collections = ["export_" + glb.stem]
        collections[glb.stem] = loaded.collections[0]
    obj = bpy.data.objects.new(f"REFERENCE_{index:02d}_{glb.stem}", None)
    scene.collection.objects.link(obj)
    obj.instance_type = "COLLECTION"
    obj.instance_collection = collections[glb.stem]
    x, y, z = item["position"]
    obj.location = (x, -z, y)
    obj.rotation_euler.z = math.radians(item["yaw_degrees"])


def aim(obj, target):
    """Aim evidence cameras/lights without altering the saved assembly or sibling sources."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.24, .29, .37, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .65
# Studio backdrop only; not authored asset geometry and never saved/exported.
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.025))
mat = bpy.data.materials.new("STUDIO_teal_slate")
mat.diffuse_color = (.11, .17, .18, 1)
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = mat.diffuse_color
mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = .8
bpy.context.object.data.materials.append(mat)
for name, position, energy, size in [("key", (5, 20, 35), 16000, 22),
                                      ("fill", (30, -15, 25), 13000, 20),
                                      ("rim", (-15, -20, 30), 14000, 20)]:
    data = bpy.data.lights.new("STUDIO_" + name, "AREA")
    data.energy, data.size = energy, size
    obj = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (15, -5, 3))
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new(data.name, data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.compression = 100
scene.render.image_settings.color_mode = "RGB"
scene.render.dither_intensity = 0
scene.view_settings.view_transform = "AgX"
views = []
for name, location, target, scale in [
    ("hero", (52, -48, 39), (15, -4, 3.8), 64),
    ("side", (-34, 38, 31), (15, -4, 3.8), 65),
    ("assembly_detail", (30, -27, 18), (20, -7, 4), 35),
]:
    scene.render.resolution_x, scene.render.resolution_y = (
        (1024, 576) if name == "assembly_detail" else (1280, 720))
    data.type, data.ortho_scale = "ORTHO", scale
    camera.location = location
    aim(camera, target)
    scene.render.filepath = str(EVIDENCE / (name + ".png"))
    bpy.ops.render.render(write_still=True)
    views.append({"name": name, "blender_position": location, "target": target,
                  "orthographic_scale": scale})
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
camera.location = (15, -6.08, 47)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
views.append({"name": "overhead_47m_42deg", "blender_position": list(camera.location),
              "vertical_fov_degrees": 42, "north_up": True})
(SCRATCH / "renders.json").write_text(json.dumps({"blender": bpy.app.version_string,
    "resolution": [1280, 720], "detail_resolution": [1024, 576],
    "samples": 32, "png_compression": 100, "color_mode": "RGB", "views": views,
    "source": "Actual saved-scene model transforms from prefab-check.json; linked Blender collections"},
    indent=2) + "\n")
