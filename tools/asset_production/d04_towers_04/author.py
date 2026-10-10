"""Original Glassward mid-height stepped-crown tower; isolated Blender 5.2.2 LTS only."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_towers_04"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
LOBBY_HEIGHT = 6.0
FLOOR_PITCH = 3.6
FLOOR_COUNT = 6
CROWN_DATUM = LOBBY_HEIGHT + FLOOR_PITCH * FLOOR_COUNT
HEIGHT = 32.4


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
    return finish(obj, mat, bevel)


def finish(obj, mat, bevel):
    """Apply smooth bevels and normals to closed source geometry before joining sections."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
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
    """Retain lobby, facade and crown as separately named editable static sections."""
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


def lobby():
    """Six-metre closed lobby vocabulary; no enterable void or independent podium."""
    box("Ground shoe", (0, 0, .2), (24, 18, .4), stone, .025)
    box("Closed lobby core", (0, 0, 3.15), (23.9, 17.9, 5.7), indigo, .04)
    box("Lobby upper fascia", (0, 0, 5.6), (24, 18, .8), frame, .05)
    for sign in (-1, 1):
        for x in (-8.4, -4.2, 4.2, 8.4):
            box("Broad lobby glazing", (x, sign * 8.971, 2.8), (3.6, .05, 4.2), glass)
        for y in (-5.8, 0, 5.8):
            box("Side lobby glazing", (sign * 11.971, y, 2.8), (.05, 4.6, 4.2), glass)
        for x in (-11.7, -2.0, 2.0, 11.7):
            box("Lobby stone pier", (x, sign * 8.94, 2.9), (.5, .12, 5.0), stone)
    # The closed door faces the forecourt (-Z in Godot), not an implied interior route.
    box("Entry door surround", (0, 8.96, 1.9), (3.1, .08, 3.1), frame)
    for x in (-.7, .7):
        box("Closed lobby door", (x, 8.994, 1.83), (1.32, .012, 2.9), glass, .003)
    box("Entry centre mullion", (0, 8.995, 1.83), (.12, .01, 2.9), stone, .002)
    box("Entry lintel accent", (0, 8.97, 4.4), (3.2, .06, .35), magenta, .015)
    box("Cantilever entry canopy", (0, 9.35, 3.75), (6.0, 1.7, .3), frame, .05)
    box("Canopy inset soffit", (0, 9.35, 3.59), (5.4, 1.35, .06), stone, .02)
    join_section("D04Towers04_Lobby")


def facade():
    """Repeat broad three-floor window groups on a 3.6 m pitch, not a pixel grid."""
    shaft_height = CROWN_DATUM - LOBBY_HEIGHT
    box("Indigo shaft", (0, 0, 6 + shaft_height / 2), (21.8, 15.8, shaft_height), indigo, .05)
    for sign in (-1, 1):
        for group in range(FLOOR_COUNT // 3):
            bottom = 6.5 + group * 3 * FLOOR_PITCH
            center = bottom + 4.85
            for index, x in enumerate((-7.8, -2.6, 2.6, 7.8)):
                mat = highlight if (group, index, sign) in ((1, 2, 1), (0, 0, -1)) else glass
                box("Three-floor front glazing", (x, sign * 7.921, center),
                    (4.65, .06, 9.7), mat, .025)
            for y in (-5.0, 0, 5.0):
                box("Three-floor side glazing", (sign * 10.921, y, center),
                    (.06, 4.25, 9.7), glass, .025)
        for x in (-10.8, -5.2, 0, 5.2, 10.8):
            box("Continuous vertical front pier", (x, sign * 7.95, 6 + shaft_height / 2),
                (.4, .1, shaft_height), frame, .025)
        for y in (-7.8, -2.5, 2.5, 7.8):
            box("Continuous vertical side pier", (sign * 10.95, y, 6 + shaft_height / 2),
                (.1, .4, shaft_height), frame, .025)
        for floor in range(1, FLOOR_COUNT):
            z = 6 + floor * FLOOR_PITCH
            band_height = .42 if floor % 3 == 0 else .14
            box("Restrained floor spandrel front", (0, sign * 7.962, z),
                (21.5, .05, band_height), indigo, .012)
            box("Restrained floor spandrel side", (sign * 10.962, 0, z),
                (.05, 15.5, band_height), indigo, .012)
    join_section("D04Towers04_Facade")


def rectangular_rim(name, half_width, half_depth, width, bottom, top):
    """Author one closed annular rim, avoiding overlapping mitred corner pieces."""
    outer = [(half_width, half_depth), (-half_width, half_depth),
             (-half_width, -half_depth), (half_width, -half_depth)]
    inner = [(half_width - width, half_depth - width),
             (-half_width + width, half_depth - width),
             (-half_width + width, -half_depth + width),
             (half_width - width, -half_depth + width)]
    count = len(outer)
    verts = [(x, y, z) for z in (bottom, top) for loop in (outer, inner) for x, y in loop]
    faces = []
    for i in range(count):
        j = (i + 1) % count
        faces += [(i, j, j + 2 * count, i + 2 * count),
                  (i + count, i + 3 * count, j + 3 * count, j + count),
                  (i + 2 * count, j + 2 * count, j + 3 * count, i + 3 * count),
                  (i, i + count, j + count, j)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    finish(obj, cyan, .04)


def crown():
    """Two broad rectangular tiers form a low stepped crown, not rooftop machinery."""
    box("Rectangular crown seat", (0, 0, CROWN_DATUM + .15), (22, 16, .3), frame, .03)
    box("Lower indigo crown drum", (0, 0, 28.7), (21.6, 15.6, 1.6), indigo, .04)
    rectangular_rim("Lower cyan shoulder rim", 11.4, 8.4, .8, 29.1, 29.7)
    box("Setback upper crown drum", (0, 0, 30.55), (15.2, 9.2, 2.1), indigo, .04)
    rectangular_rim("Upper cyan crown rim", 8, 5, .8, 31.5, HEIGHT)
    join_section("D04Towers04_Crown")


def aim(obj, target):
    """Aim studio objects without changing the asset orientation."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def light(name, position, energy, size):
    """Provide broad studio fill, excluded from the export collection."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (0, 0, 16))


assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
root = bpy.data.objects.new("D04Towers04", None)
collection.objects.link(root)
root["asset_id"] = "d04_towers.04"
root["authorship"] = "Original Blender construction by commissioned asset worker"
root["front_axis"] = "Blender +Y maps to Godot -Z; Z up maps to Y up"
root["lobby_height_m"] = LOBBY_HEIGHT
root["floor_pitch_m"] = FLOOR_PITCH
root["crown_datum_m"] = CROWN_DATUM
root["height_m"] = HEIGHT
parts = []
indigo = material("glassward_indigo", (.033, .052, .15), .22, .46)
frame = material("glassward_frame", (.12, .18, .28), .32, .42)
glass = material("glassward_glazing_opaque", (.055, .145, .24), .42, .3)
highlight = material("glassward_glazing_highlight", (.09, .22, .32), .38, .3)
cyan = material("glassward_crown_cyan", (.065, .63, .77), .18, .32, .35)
magenta = material("glassward_accent_magenta", (.62, .035, .25), .1, .4, .12)
stone = material("glassward_lobby_stone", (.32, .39, .46), .0, .6)
lobby()
facade()
crown()

scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.22, .27, .34, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .55
bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, -.035))
bpy.context.object.name = "STUDIO_ground"
bpy.context.object.data.materials.append(material("STUDIO_slate", (.18, .23, .27)))
light("STUDIO_key", (36, 40, 78), 105000, 45)
light("STUDIO_rim", (-34, -28, 62), 125000, 36)
light("STUDIO_fill", (10, 48, 24), 42000, 30)
data = bpy.data.cameras.new("STUDIO_camera")
data.clip_end = 3000
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
camera.location = (65, 82, 50)
aim(camera, (0, 0, 16.2))
data.type = "ORTHO"
data.ortho_scale = 82
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(), "export.py", "exec"))
for name, position, target, scale in [
    ("hero", (65, 82, 50), (0, 0, 16.2), 82),
    ("side", (85, 0, 16.2), (0, 0, 16.2), 72),
    ("crown_detail", (34, 45, 58), (0, 0, 29.8), 42),
]:
    camera.location = position
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)
# Forecourt vantage: retain partial crown/facade and open ground, without a cutaway.
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
camera.location = (14, 12, 47)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
