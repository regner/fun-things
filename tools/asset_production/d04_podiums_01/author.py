"""Original Glassward low office; isolated Blender 5.2.2 LTS only."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_podiums_01"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
LOBBY_HEIGHT = 6.0
FLOOR_PITCH = 3.6
FLOOR_COUNT = 2
CROWN_DATUM = LOBBY_HEIGHT + FLOOR_PITCH * FLOOR_COUNT
HEIGHT = 14.1


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
    """Three masses retain a true full-height entry notch without an interior."""
    box("Rear office mass", (0, -.75, 6.6), (25.9, 14.4, 13.2), slate, .035)
    for sign in (-1, 1):
        box("Front office wing", (sign * 7.75, 7.2, 6.6), (10.4, 1.5, 13.2), slate, .035)
        box("Front stone footing", (sign * 7.75, 7.25, .15), (10.5, 1.5, .3), stone, .02)
        box("Entry reveal pier", (sign * 2.65, 7.25, 6.75), (.3, 1.5, 12.9), stone, .025)
    box("Rear stone footing", (0, -.75, .15), (26, 14.5, .3), stone, .02)
    for height in (6, 9.6):
        for sign in (-1, 1):
            box("Front broad spandrel", (sign * 7.8, 7.945, height),
                (10.2, .08, .45), frame, .018)
            box("Side broad spandrel", (sign * 12.945, 0, height),
                (.08, 16, .45), frame, .018)
        box("Rear broad spandrel", (0, -7.96, height), (26, .08, .45), frame, .018)


def windows():
    """Broad opaque office glazing groups, not a transparent interior or tiny grid."""
    for level, (height, pane_height) in enumerate(((3.05, 4.4), (7.8, 2.55), (11.4, 2.55))):
        for sign in (-1, 1):
            for index, x in enumerate((5.3, 10.3)):
                mat = highlight if (level, sign, index) == (1, 1, 0) else glass
                box("Front office window", (sign * x, 7.98, height),
                    (4.15, .035, pane_height), mat, .008)
            for y in (-5.25, 0, 5.25):
                box("Side office window", (sign * 12.98, y, height),
                    (.035, 4.5, pane_height), glass, .008)
        for x in (-9.6, -3.2, 3.2, 9.6):
            box("Rear office window", (x, -7.98, height),
                (5.5, .035, pane_height), glass, .008)
    for sign in (-1, 1):
        for x in (7.8, 12.65):
            box("Front continuous pier", (sign * x, 7.97, 6.6),
                (.3, .06, 12.6), stone, .012)
        for y in (-7.65, -2.625, 2.625, 7.65):
            box("Side continuous pier", (sign * 12.97, y, 6.6),
                (.06, .3, 12.6), frame, .012)


def entrance_and_roof():
    """Recess the closed entry; leave roof hardware and signage to shared families."""
    box("Deep entry back panel", (0, 6.49, 3.15), (5, .02, 5.7), frame, .005)
    for x in (-.85, .85):
        box("Closed lobby leaf", (x, 6.508, 1.7), (1.58, .025, 3.25), glass, .006)
    box("Door central mullion", (0, 6.522, 1.7), (.12, .02, 3.25), stone, .004)
    for x in (-.18, .18):
        box("Door vertical pull", (x, 6.58, 1.55), (.04, .10, .75), stone, .01)
    box("Inset entry canopy", (0, 7.225, 3.78), (5, 1.45, .36), frame, .03)
    box("Canopy pale soffit", (0, 7.2, 3.57), (4.65, 1.25, .06), stone, .012)
    box("Single magenta entry lintel", (0, 7.96, 3.79), (3.2, .035, .25), magenta, .006)
    for height in (7.8, 11.4):
        box("Recessed upper window", (0, 6.495, height), (3.8, .03, 2.55), glass, .006)
    # Roof notch makes the entry axis legible overhead without another luminous crown.
    box("Quiet rear roof", (0, -.6, 13.18), (25.4, 14.2, .08), indigo, 0)
    for sign in (-1, 1):
        box("Quiet wing roof", (sign * 7.75, 7.1, 13.18), (9.9, 1.2, .08), indigo, 0)
        box("Front parapet", (sign * 7.75, 7.8, 13.65), (10.5, .4, .9), slate, .025)
        box("Side parapet", (sign * 12.8, 0, 13.65), (.4, 15.2, .9), slate, .025)
        box("Notch parapet return", (sign * 2.7, 7.05, 13.65), (.4, 1.1, .9), slate, .025)
    box("Rear parapet", (0, -7.8, 13.65), (26, .4, .9), slate, .025)
    box("Notch parapet back", (0, 6.3, 13.65), (5.8, .4, .9), slate, .025)


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
root = bpy.data.objects.new("D04Podiums01", None)
collection.objects.link(root)
root["asset_id"] = "d04_podiums.01"
root["authorship"] = "Original Blender construction by commissioned asset worker"
root["front_axis"] = "Blender +Y maps to Godot -Z; Z up maps to Y up"
root["ground_pivot"] = "Centre of nominal 26 x 16 m footprint, ground Y=0 in Godot"
root["floor_pitch_m"] = FLOOR_PITCH
root["entry_recess_width_depth_m"] = [5.0, 1.5]
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
join_section("D04Podiums01_Mesh")
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
camera.location = (34, 42, 31)
aim(camera, (0, 0, 6))
data.type = "ORTHO"
data.ortho_scale = 52
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(), "export.py", "exec"))
for name, position, target, scale in [
    ("hero", (34, 42, 31), (0, 0, 6), 52),
    ("side", (40, 0, 6.8), (0, 0, 6.8), 33),
    ("entry_detail", (10, 23, 9), (0, 7, 3.6), 15),
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
