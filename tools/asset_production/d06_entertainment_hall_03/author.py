"""Build the original entry canopy; preceding family assets are read-only render context."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_entertainment_hall_03"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
WIDTH = 10.0
REAR = 8.85
FRONT = 11.8
FRONT_RADIUS = .8
CORNER_STEPS = 12
# Closed slab profiles: soft lower/upper shoulders, flat cyan top border, quiet top centre.
PROFILES = [(.08, 3.6), (0, 3.68), (0, 3.97), (.08, 4.05), (.50, 4.05)]


def material(name, color, metallic, roughness, emission=0.0):
    """Create an opaque back-culled export-compatible Principled material."""
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


def contour(inset):
    """Return a CCW plan with rounded front corners and a straight wall-contact edge."""
    half_width = WIDTH / 2 - inset
    radius = FRONT_RADIUS - inset
    points = [(half_width, REAR + inset)]
    for cx, start in ((WIDTH / 2 - FRONT_RADIUS, 0),
                      (-WIDTH / 2 + FRONT_RADIUS, 90)):
        for step in range(CORNER_STEPS + 1):
            angle = math.radians(start + 90 * step / CORNER_STEPS)
            points.append((cx + radius * math.cos(angle),
                           FRONT - FRONT_RADIUS + radius * math.sin(angle)))
    points.append((-half_width, REAR + inset))
    return points


def aim(obj, target):
    """Aim a studio camera/light at a fixed evidence target."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def light(name, position, energy, size):
    """Keep evidence lighting outside the export collection."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.size = energy, size
    data.shape = "DISK"
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (0, 0, 5))


def render(name, position, target, scale):
    """Render a reproducible orthographic evidence image."""
    camera.location = position
    aim(camera, target)
    data.type, data.ortho_scale = "ORTHO", scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)


assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
petrol = material("canopy_housing_petrol", (.035, .105, .125), .25, .43)
cyan = material("canopy_diffuser_cyan", (.015, .58, .68), 0, .38, .45)
vertices = [(x, y, height) for inset, height in PROFILES for x, y in contour(inset)]
count = len(contour(0))
faces = [tuple(reversed(range(count)))]
slots = [0]
for profile in range(len(PROFILES) - 1):
    for index in range(count):
        faces.append((profile * count + index, profile * count + (index + 1) % count,
                      (profile + 1) * count + (index + 1) % count,
                      (profile + 1) * count + index))
        # The back remains dark. Cyan is one connected U-shaped shoulder, not extra trim.
        slots.append(1 if profile >= 1 and index != count - 1 else 0)
faces.append(tuple(range((len(PROFILES) - 1) * count, len(PROFILES) * count)))
slots.append(0)
mesh = bpy.data.meshes.new("D06EntertainmentHall03_Mesh")
mesh.from_pydata(vertices, [], faces)
mesh.materials.append(petrol)
mesh.materials.append(cyan)
for face, slot in zip(mesh.polygons, slots):
    face.material_index = slot
    face.use_smooth = True
bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(mesh)
bm.free()
mesh.update()
obj = bpy.data.objects.new("D06EntertainmentHall03_Mesh", mesh)
collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
modifier = obj.modifiers.new("Weighted manufactured normals", "WEIGHTED_NORMAL")
modifier.keep_sharp = True
bpy.ops.object.modifier_apply(modifier=modifier.name)
obj.select_set(False)
root = bpy.data.objects.new("D06EntertainmentHall03", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "d06_entertainment_hall.03"
root["authorship"] = "Original Blender construction by commissioned production worker"
root["pivot"] = "Hall ground-centre; identity overlay on .01/.02"
root["wall_contact_godot_m"] = [0.0, 3.6, -9.0]
root["envelope_godot_m"] = "(-5,3.6,-11.8) to (5,4.05,-8.85); no ground contact"

scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.22, .27, .32, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .55
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
camera.location = (12, 18, 8)
aim(camera, (0, 10.3, 3.8))
data.type, data.ortho_scale = "ORTHO", 13
for directory in (SOURCE.parent, EVIDENCE, SCRATCH):
    directory.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(), "export.py", "exec"))
render("side", (12, 18, 8), (0, 10.3, 3.8), 13)
# The saved source/export contain ONLY this canopy; family append is render context only.
for suffix in ("01", "02"):
    family_id = f"d06_entertainment_hall_{suffix}"
    source = ROOT / f"art/source/models/environment/{family_id}/{family_id}.blend"
    with bpy.data.libraries.load(str(source), link=False) as (available, requested):
        requested.collections = [f"export_{family_id}"]
    for context in requested.collections:
        scene.collection.children.link(context)
render("hero", (32, 40, 29), (0, 0, 3.5), 38)
render("entry_detail", (12, 24, 9), (0, 9.7, 3.35), 13)
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
# Keep the unlit family comparison outside the lean four-image evidence set.
for name in ("canopy_diffuser_cyan", "ring_diffuser_magenta"):
    bpy.data.materials[name].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0
scene.render.filepath = str(SCRATCH / "unlit_overhead.png")
bpy.ops.render.render(write_still=True)
