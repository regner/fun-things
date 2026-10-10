"""Original Glassward setback podium; isolated Blender 5.2.2 LTS only."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_podiums_02"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
LOBBY_HEIGHT = 6.0
FLOOR_PITCH = 3.6
FLOOR_COUNT = 1
CROWN_DATUM = LOBBY_HEIGHT + FLOOR_PITCH * FLOOR_COUNT
HEIGHT = 10.5


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
    """Two stacked masses leave broad roof setbacks rather than a lot-wide platform."""
    box("Slate lobby mass", (0, 0, 2.97), (29.9, 17.9, 5.94), slate, .04)
    box("Stone ground footing", (0, 0, .15), (30, 18, .3), stone, .025)
    box("Lobby roof fascia", (0, 0, 5.76), (30, 18, .4), frame, .025)
    box("Upper setback mass", (0, -2, 7.8), (21.9, 11.9, 3.6), slate, .04)
    # Exposed roofs are inaccessible building caps, not terraces or raised forecourts.
    box("Broad quiet lower roof", (0, 0, 5.96), (29.6, 17.6, .08), indigo, .015)
    box("Upper roof fascia", (0, -2, 9.42), (22, 12, .36), frame, .025)
    box("Quiet upper roof", (0, -2, 9.58), (21.4, 11.4, .08), indigo, .01)
    for sign in (-1, 1):
        box("Upper side parapet", (sign * 10.8, -2, 10.05),
            (.4, 11.2, .9), slate, .025)
    for y in (-7.8, 3.8):
        box("Upper end parapet", (0, y, 10.05), (22, .4, .9), slate, .025)


def windows():
    """Large opaque glazing groups follow the sibling's quiet floor rhythm."""
    for sign in (-1, 1):
        for x in (6.1, 11.85):
            box("Lobby front glazing", (sign * x, 8.98, 2.95),
                (4.85, .035, 4.45), glass, .008)
        for y in (-5.8, 0, 5.8):
            box("Lobby side glazing", (sign * 14.98, y, 2.95),
                (.035, 4.9, 4.45), glass, .008)
        for y in (-8.65, -2.9, 2.9, 8.65):
            box("Lobby side pier", (sign * 14.97, y, 2.9),
                (.06, .3, 5.2), stone, .012)
        for y in (-5.8, -2, 1.8):
            box("Upper side glazing", (sign * 10.98, y, 7.8),
                (.035, 3.15, 2.55), glass, .008)
    for x in (-11.25, -3.75, 3.75, 11.25):
        box("Lobby rear glazing", (x, -8.98, 2.95),
            (6.5, .035, 4.45), glass, .008)
    for x in (-8.25, -2.75, 2.75, 8.25):
        mat = highlight if x == 2.75 else glass
        box("Upper front glazing", (x, 3.98, 7.8), (4.65, .035, 2.55), mat, .008)
        box("Upper rear glazing", (x, -7.98, 7.8), (4.65, .035, 2.55), glass, .008)
    for x in (-14.65, -9, -3.25, 3.25, 9, 14.65):
        box("Lobby front stone pier", (x, 8.97, 2.9), (.3, .06, 5.2), stone, .012)


def entrance_and_roof():
    """A deep overhead portal shelters a closed facade entry; ground stays open."""
    box("Entry backing", (0, 8.98, 2.6), (6, .03, 5), frame, .006)
    for x in (-1.1, 1.1):
        box("Closed lobby leaf", (x, 9.008, 1.7), (2.05, .025, 3.25), glass, .006)
    box("Door centre mullion", (0, 9.025, 1.7), (.14, .02, 3.25), stone, .004)
    for x in (-.2, .2):
        box("Door vertical pull", (x, 9.08, 1.55), (.045, .10, .75), stone, .01)
    box("Deep entry canopy", (0, 9.975, 3.95), (6.6, 2.05, .4), frame, .035)
    box("Canopy pale soffit", (0, 9.95, 3.72), (6.25, 1.95, .06), stone, .012)
    # Above-head cheeks create portal depth without placing piers in the entry walk strip.
    for sign in (-1, 1):
        box("Overhead portal return", (sign * 3.18, 9.95, 3.25),
            (.24, 1.95, .9), slate, .02)
    box("Single magenta lintel", (0, 10.985, 3.95), (3.6, .03, .23), magenta, .006)


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
root = bpy.data.objects.new("D04Podiums02", None)
collection.objects.link(root)
root["asset_id"] = "d04_podiums.02"
root["authorship"] = "Original Blender construction by commissioned asset worker"
root["front_axis"] = "Blender +Y maps to Godot -Z; Z up maps to Y up"
root["ground_pivot"] = "Centre of nominal 30 x 18 m footprint, ground Y=0 in Godot"
root["floor_pitch_m"] = FLOOR_PITCH
root["upper_setback_front_sides_back_m"] = [5.0, 4.0, 1.0]
root["entry_canopy_depth_m"] = 2.0
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
join_section("D04Podiums02_Mesh")
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
camera.location = (36, 44, 32)
aim(camera, (0, 0, 6))
data.type = "ORTHO"
data.ortho_scale = 56
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(), "export.py", "exec"))
for name, position, target, scale in [
    ("hero", (36, 44, 32), (0, 0, 4.8), 56),
    ("side", (42, 0, 5.2), (0, 0, 5.2), 38),
    ("entry_detail", (11, 26, 9), (0, 9.5, 3.2), 17),
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
