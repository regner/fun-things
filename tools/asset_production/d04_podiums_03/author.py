"""Original Glassward short service wing; isolated Blender 5.2.2 LTS only."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_podiums_03"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
ROOF_DATUM = 6.0
HEIGHT = 6.9
WIDTH = 20.0
DEPTH = 10.0
ENTRY_CENTRE_X = 5.0
ENTRY_WIDTH = 4.0
ENTRY_DEPTH = 1.6


def material(name, color, metallic=0.0, roughness=0.5, emission=0.0):
    """Use opaque flat Principled colors, with no texture or illumination dependency."""
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


def box(name, position, size, mat, bevel=0.03):
    """Build a closed architectural part with applied bevel and weighted normals."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new("Architectural soft edge", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=0.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    for face in obj.data.polygons:
        face.use_smooth = True
    modifier = obj.modifiers.new("Weighted architectural normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    parts.append(obj)
    return obj


def join_section(name):
    """Join original architectural parts at the ground pivot."""
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = name
    obj.data.name = name + "_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    obj.parent = root
    parts.clear()
    return obj


def structure():
    """An asymmetric three-part footprint keeps the recessed service entrance open."""
    box("Rear service mass", (0, -.8, 3), (19.9, 8.3, 6), slate, .035)
    box("Rear stone footing", (0, -.8, .15), (WIDTH, 8.4, .3), stone, .02)
    for x, width in ((-3.5, 13), (8.5, 3)):
        box("Front service mass", (x, 4.15, 3), (width - .1, 1.6, 6), slate, .035)
        box("Front stone footing", (x, 4.2, .15), (width, ENTRY_DEPTH, .3), stone, .02)
        box("Front roof fascia", (x, 4.93, 5.8), (width, .1, .4), frame, .015)
    for x in (2.85, 7.15):
        box("Deep stone entry reveal", (x, 4.2, 3.1), (.3, 1.6, 5.6), stone, .025)
    for sign in (-1, 1):
        box("Side roof fascia", (sign * 9.93, 0, 5.8), (.1, 9.8, .4), frame, .015)
    box("Rear roof fascia", (0, -4.93, 5.8), (WIDTH, .1, .4), frame, .015)


def windows():
    """High grouped glazing and a broad closed shutter distinguish this service wing."""
    for x in (-7.3, -2.7):
        box("Front clerestory", (x, 4.98, 4.85), (3.9, .035, 1.05), glass, .008)
    for x in (-7.2, -2.4, 2.4, 7.2):
        box("Rear clerestory", (x, -4.98, 4.5), (4.0, .035, 1.4), glass, .008)
    for y in (-2.45, 2.45):
        box("West clerestory", (-9.98, y, 4.5), (.035, 3.85, 1.4),
            highlight if y == 2.45 else glass, .008)
    box("Closed service shutter backing", (-4.8, 4.958, 2.05), (6.6, .012, 3.5), frame, .008)
    box("Closed service shutter", (-4.8, 4.978, 2.02), (6.2, .025, 3.2), slate, .006)
    # Few broad seams, not noisy fine corrugation. This shutter is a static facade detail.
    for z in (.9, 1.7, 2.5, 3.3):
        box("Shutter broad seam", (-4.8, 4.994, z), (6.12, .008, .045), frame, .002)
    for x in (-8.02, -1.58):
        box("Shutter stone jamb", (x, 4.985, 2.05), (.22, .03, 3.55), stone, .006)
    box("East ventilation recess", (9.98, 0, 2.85), (.035, 5.8, 2.5), frame, .008)
    for z in (1.95, 2.55, 3.15, 3.75):
        box("Broad ventilation blade", (9.99, 0, z), (.02, 5.5, .3), slate, .015)


def entrance_and_roof():
    """A roof notch and inset canopy mark the service door without adding roof equipment."""
    box("Recessed entry backing", (5, 3.39, 2.8), (4, .02, 5), frame, .005)
    for x in (4.25, 5.75):
        box("Closed service door leaf", (x, 3.408, 1.65), (1.4, .025, 3.1), glass, .006)
    box("Door central mullion", (5, 3.422, 1.65), (.12, .02, 3.1), stone, .004)
    for x in (4.82, 5.18):
        box("Door pull", (x, 3.48, 1.5), (.04, .10, .7), stone, .01)
    box("Inset canopy", (5, 4.175, 3.78), (4, 1.55, .36), frame, .03)
    box("Pale canopy soffit", (5, 4.15, 3.57), (3.65, 1.35, .06), stone, .012)
    box("Small magenta lintel", (5, 4.96, 3.79), (2.4, .035, .25), magenta, .006)
    # Raised roof caps avoid coplanar surfaces while keeping the six-metre family datum.
    box("Quiet rear roof", (0, -.65, 6.015), (19.4, 8.1, .05), indigo, 0)
    box("Quiet long front roof", (-3.5, 4.05, 6.015), (12.4, 1.3, .05), indigo, 0)
    box("Quiet short front roof", (8.5, 4.05, 6.015), (2.4, 1.3, .05), indigo, 0)
    for x, width in ((-3.5, 13), (8.5, 3)):
        box("Front parapet", (x, 4.8, 6.45), (width, .4, .9), slate, .025)
    for sign in (-1, 1):
        box("Side parapet", (sign * 9.8, 0, 6.45), (.4, 9.2, .9), slate, .025)
    box("Rear parapet", (0, -4.8, 6.45), (20, .4, .9), slate, .025)
    for x in (2.8, 7.2):
        box("Notch parapet return", (x, 4.0, 6.45), (.4, 1.2, .9), slate, .025)
    box("Notch parapet back", (5, 3.2, 6.45), (4.8, .4, .9), slate, .025)



def aim(obj, target):
    """Aim studio objects without changing the model orientation."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def light(name, position, energy, size):
    """Studio lighting is never a runtime fixture or an export member."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (0, 0, 6))


assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
root = bpy.data.objects.new("D04Podiums03", None)
collection.objects.link(root)
root["asset_id"] = "d04_podiums.03"
root["authorship"] = "Original Blender construction by commissioned asset worker"
root["front_axis"] = "Blender +Y maps to Godot -Z; Z up maps to Y up"
root["ground_pivot"] = "Centre of nominal 20 x 10 m footprint, ground Y=0 in Godot"
root["roof_datum_m"] = ROOF_DATUM
root["entry_recess_width_depth_m"] = [ENTRY_WIDTH, ENTRY_DEPTH]
root["entry_centre_x_m"] = ENTRY_CENTRE_X
parts = []
slate = material("glassward_office_slate", (.18, .25, .32), .05, .58)
frame = material("glassward_frame", (.12, .18, .28), .32, .42)
glass = material("glassward_glazing_opaque", (.055, .145, .24), .42, .3)
highlight = material("glassward_glazing_highlight", (.09, .22, .32), .38, .3)
indigo = material("glassward_indigo", (.033, .052, .15), .22, .46)
magenta = material("glassward_accent_magenta", (.62, .035, .25), .1, .4, .12)
stone = material("glassward_lobby_stone", (.32, .39, .46), .0, .6)
structure()
windows()
entrance_and_roof()
join_section("D04Podiums03_Mesh")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.22, .27, .34, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .55
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.035))
bpy.context.object.name = "STUDIO_ground"
bpy.context.object.data.materials.append(material("STUDIO_slate", (.18, .23, .27)))
light("STUDIO_key", (24, 28, 36), 19000, 24)
light("STUDIO_rim", (-20, -18, 28), 22000, 20)
light("STUDIO_fill", (8, 30, 12), 8500, 18)
data = bpy.data.cameras.new("STUDIO_camera")
data.clip_end = 500
camera = bpy.data.objects.new("STUDIO_camera", data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_percentage = 100
scene.render.resolution_x = 1152
scene.render.resolution_y = 648
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.compression = 95
scene.view_settings.view_transform = "AgX"
camera.location = (28, 35, 24)
aim(camera, (0, 0, 3))
data.type = "ORTHO"
data.ortho_scale = 38
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(), "export.py", "exec"))
for name, position, target, scale in [
    ("hero", (28, 35, 24), (0, 0, 3), 38),
    ("side", (30, 0, 3.3), (0, 0, 3.3), 23),
    ("entry_detail", (12, 21, 8), (5, 4.2, 3), 12),
]:
    camera.location = position
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
