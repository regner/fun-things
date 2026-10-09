"""Author the original broad roof-ring trim; source contains no copied hall geometry."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_entertainment_hall_02"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
CORNER_STEPS = 16
MOUNT_RADIUS = 5.85
# Cross-section proceeds around the entire solid; slot belongs to the following edge.
# One continuous diffuser wraps from the outer face onto the broad top shoulder.
SECTION = [
    (-.10, 6.83, 0), (-.02, 6.75, 0), (.95, 6.75, 0),
    (1.055, 6.795, 0), (1.10, 6.90, 0), (1.10, 7.04, 1),
    (1.10, 7.43, 1), (1.08, 7.515, 1), (1.025, 7.585, 1),
    (.95, 7.635, 1), (.87, 7.65, 1), (.10, 7.65, 0),
    (-.02, 7.65, 0), (-.08, 7.62, 0), (-.10, 7.55, 0),
]


def material(name, color, metallic, roughness, emission=0.0):
    """Make opaque back-culled Principled material, with modest optional emission."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*color, 1)
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Emission Color"].default_value = (*color, 1)
    shader.inputs["Emission Strength"].default_value = emission
    return result


def contour(offset):
    """Match .01's corner centres and 16-segment quarter arcs without rescaling."""
    points = []
    for cx, cy, start in ((7, 3, 0), (-7, 3, 90), (-7, -3, 180), (7, -3, 270)):
        for step in range(CORNER_STEPS + 1):
            angle = math.radians(start + 90 * step / CORNER_STEPS)
            points.append((cx + (MOUNT_RADIUS + offset) * math.cos(angle),
                           cy + (MOUNT_RADIUS + offset) * math.sin(angle)))
    return points


def aim(obj, target):
    """Aim a studio camera or area light, never an exported node."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def light(name, position, energy, size):
    """Keep evidence lighting outside the named export collection."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.size = energy, size
    data.shape = "DISK"
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (0, 0, 5))


def render(name, position, target, scale, directory=EVIDENCE):
    """Render an orthographic evidence view with the fixed studio settings."""
    camera.location = position
    aim(camera, target)
    data.type = "ORTHO"
    data.ortho_scale = scale
    scene.render.filepath = str(directory / f"{name}.png")
    bpy.ops.render.render(write_still=True)


assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
petrol = material("ring_housing_petrol", (.035, .105, .125), .25, .43)
magenta = material("ring_diffuser_magenta", (.64, .018, .23), .0, .38, .45)
vertices = [(x, y, height) for offset, height, slot in SECTION for x, y in contour(offset)]
count = len(contour(0))
faces, slots = [], []
for section, (_, _, slot) in enumerate(SECTION):
    for index in range(count):
        next_section = (section + 1) % len(SECTION)
        faces.append((section * count + index, section * count + (index + 1) % count,
                      next_section * count + (index + 1) % count, next_section * count + index))
        slots.append(slot)
mesh = bpy.data.meshes.new("D06EntertainmentHall02_Mesh")
mesh.from_pydata(vertices, [], faces)
mesh.materials.append(petrol)
mesh.materials.append(magenta)
for face, slot in zip(mesh.polygons, slots):
    face.material_index = slot
    face.use_smooth = True
bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(mesh)
bm.free()
mesh.update()
obj = bpy.data.objects.new("D06EntertainmentHall02_Mesh", mesh)
collection.objects.link(obj)
root = bpy.data.objects.new("D06EntertainmentHall02", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "d06_entertainment_hall.02"
root["authorship"] = "Original Blender construction by commissioned production worker"
root["mount_datum_godot_y_m"] = 7.2
root["pivot"] = "Hall ground-centre, not ring underside; identity overlay on .01"
root["section"] = "Wall offset -0.10 to +1.10 m; height 6.75 to 7.65 m"

scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.22, .27, .32, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .55
# A studio plane is an evidence backdrop only, not part of the game-ready mesh.
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.025))
bpy.context.object.name = "STUDIO_ground"
bpy.context.object.data.materials.append(material("STUDIO_slate", (.14, .18, .21), 0, .5))
light("STUDIO_key", (12, 20, 32), 18000, 22)
light("STUDIO_rim", (-20, -10, 25), 21000, 18)
light("STUDIO_fill", (-4, 22, 12), 6000, 14)
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new("STUDIO_camera", data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_percentage = 100
scene.render.resolution_x, scene.render.resolution_y = 1280, 800
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"
camera.location = (32, 40, 29)
aim(camera, (0, 0, 4))
data.type, data.ortho_scale = "ORTHO", 38
for directory in (SOURCE.parent, EVIDENCE, SCRATCH):
    directory.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(), "export.py", "exec"))
# Isolated component view proves the hollow centre and non-ground-contact origin.
render("side", (32, 36, 21), (0, 0, 7.2), 35)
# Read-only existing source context is appended AFTER save/export, never redistributed.
hall_path = ROOT / "art/source/models/environment/d06_entertainment_hall_01/d06_entertainment_hall_01.blend"
with bpy.data.libraries.load(str(hall_path), link=False) as (available, requested):
    requested.collections = ["export_d06_entertainment_hall_01"]
for hall in requested.collections:
    scene.collection.children.link(hall)
render("hero", (32, 40, 29), (0, 0, 3.5), 38)
render("ring_detail", (26, 25, 19), (10.8, 7.0, 7.2), 9)
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
# Additional unlit check is scratch-only; four final renders remain the lean evidence set.
magenta.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0
scene.render.filepath = str(SCRATCH / "unlit_overhead.png")
bpy.ops.render.render(write_still=True)
