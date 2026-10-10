"""Original Harbour Hall exterior; isolated pinned Blender construction and evidence."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_harbour_hall_01"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
WIDTH, DEPTH = 26.0, 18.0
EAVE_HEIGHT, RIDGE_HEIGHT = 6.05, 9.1


def material(name, color, metallic=0.0, roughness=0.5):
    """Create an opaque, back-culled Principled surface without external textures."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*color, 1)
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return result


def finish(obj, name, mat, bevel=0.03):
    """Apply transforms and small edge radii, then clean and weight static normals."""
    obj.name = name
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new("Soft architectural edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=0.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    for face in obj.data.polygons:
        face.use_smooth = True
    modifier = obj.modifiers.new("Weighted architectural normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    parts.append(obj)
    return obj


def box(name, position, size, mat, bevel=0.03, yaw=0.0):
    """Build a closed bevelled block in the original Blender export collection."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.dimensions = size
    obj.rotation_euler.z = yaw
    return finish(obj, name, mat, bevel)


def window(name, x, y, yaw=0.0):
    """Author a broad opaque civic window, with a quiet transom and stone surround."""
    facing = Vector((-math.sin(yaw), math.cos(yaw), 0))
    origin = Vector((x, y, 2.8))
    box(name + " stone surround", origin, (2.5, .16, 3.05), limestone, .06, yaw)
    box(name + " frame", origin + facing * .095, (2.24, .08, 2.79), teal, .035, yaw)
    box(name + " opaque glazing", origin + facing * .143,
        (2.04, .025, 2.59), glass, .018, yaw)
    box(name + " transom", origin + facing * .16 + Vector((0, 0, .52)),
        (2.1, .04, .10), teal, .015, yaw)
    box(name + " sill", origin + facing * .05 + Vector((0, 0, -1.54)),
        (2.68, .32, .14), limestone, .035, yaw)


def aim(obj, target):
    """Aim an isolated studio light or camera, never exported geometry."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def light(name, position, energy, size):
    """Add broad studio fill outside the named export collection."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (0, 0, 3))


assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
parts = []
wall = material("harbour_hall_warm_render", (.62, .43, .25), 0, .65)
stone = material("harbour_hall_base_stone", (.32, .31, .26), 0, .66)
limestone = material("harbour_hall_limestone_trim", (.78, .70, .53), 0, .56)
teal = material("harbour_hall_teal_metal", (.035, .15, .15), .35, .42)
glass = material("harbour_hall_opaque_glazing", (.022, .065, .09), .2, .28)
roof = material("harbour_hall_slate_roof", (.045, .085, .115), .18, .49)
amber = material("harbour_hall_entry_amber", (.73, .37, .105), .1, .43)

# Ground-centred closed civic mass. No interior, open door or rooftop gameplay.
box("Ground plinth", (0, 0, .175), (26.4, 18.4, .35), stone, .045)
box("Warm civic wall mass", (0, 0, 3.075), (WIDTH, DEPTH, 5.85), wall, .07)
box("Low stone belt", (0, 0, .61), (26.12, 18.12, .24), limestone, .03)
box("Upper cornice", (0, 0, 5.64), (26.35, 18.35, .30), limestone, .045)
box("Quiet teal eave fascia", (0, 0, 5.885), (27.6, 19.6, .25), teal, .045)

# A closed six-sided hip roof with one broad ridge. No tiles, dormers or equipment.
vertices = [(-13.8, -9.8, 5.94), (13.8, -9.8, 5.94),
            (13.8, 9.8, 5.94), (-13.8, 9.8, 5.94),
            (-13.8, -9.8, EAVE_HEIGHT), (13.8, -9.8, EAVE_HEIGHT),
            (13.8, 9.8, EAVE_HEIGHT), (-13.8, 9.8, EAVE_HEIGHT),
            (-4.0, 0, RIDGE_HEIGHT), (4.0, 0, RIDGE_HEIGHT)]
faces = [(3, 2, 1, 0), (0, 1, 5, 4), (1, 2, 6, 5),
         (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 9, 8),
         (5, 6, 9), (6, 7, 8, 9), (7, 4, 8)]
mesh = bpy.data.meshes.new("Broad hipped roof")
mesh.from_pydata(vertices, [], faces)
mesh.update()
obj = bpy.data.objects.new("Broad hipped roof", mesh)
collection.objects.link(obj)
finish(obj, "Broad hipped roof", roof, .045)
box("Short ridge cap", (0, 0, 9.09), (8.36, .25, .22), teal, .07)

# Four front/rear bays and three side bays are broad enough to stay quiet at distance.
for x in (-9.4, -5.7, 5.7, 9.4):
    window("Front window", x, 9.015)
for x in (-9.4, -3.2, 3.2, 9.4):
    window("Rear window", x, -9.015, math.pi)
for y in (-5.6, 0, 5.6):
    window("East window", 13.015, y, -math.pi / 2)
    window("West window", -13.015, y, math.pi / 2)
for x in (-12.6, 12.6):
    for y in (-9.045, 9.045):
        box("Corner stone pier", (x, y, 3.06), (.42, .15, 4.58), limestone, .035)

# Central closed entry; the separate canopy attaches above, not built into this GLB.
box("Entry stone surround", (0, 9.025, 1.96), (6.25, .20, 3.32), limestone, .065)
box("Entry teal frame", (0, 9.14, 1.87), (5.86, .075, 3.10), teal, .025)
for x in (-2.19, -.73, .73, 2.19):
    box("Closed entry glazed panel", (x, 9.19, 1.85), (1.32, .028, 2.84), glass, .025)
    box("Entry amber kick panel", (x, 9.211, .61), (1.28, .018, .33), amber, .014)
for x in (-.14, .14):
    box("Closed entrance pull", (x, 9.25, 1.72), (.04, .065, .57), limestone, .015)
# Three shallow risers retain the concept's step appearance. Prefab smooth ramp is separate.
box("Entry landing", (0, 9.4, .15), (8.4, .4, .3), stone, .018)
for name, y, depth, height in (("Upper step", 9.8, .4, .3),
                             ("Middle step", 10.2, .4, .2),
                             ("Lower step", 10.6, .4, .1)):
    box(name, (0, y, height / 2), (8.4, depth, height), stone, .012)
# Oversized lintel separates the entrance from future civic identity hardware/artwork.
box("Entry lintel", (0, 9.08, 3.64), (6.6, .27, .20), limestone, .035)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "D05HarbourHall01_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D05HarbourHall01", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "d05_harbour_hall.01"
root["authorship"] = "Original Blender construction by commissioned production worker"
root["front_axis"] = "Blender +Y maps to Godot -Z; +Z maps to +Y"
root["ground_pivot"] = "Body footprint centre at ground zero, not forward step AABB centre"
root["canopy_wall_datum_godot"] = [0.0, 3.85, -9.0]
root["canopy_clearance_minimum_godot_y_m"] = 3.3

# Isolated studio is retained for reproduction but excluded by collection export.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.22, .27, .32, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .55
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.025))
bpy.context.object.name = "STUDIO_ground"
bpy.context.object.data.materials.append(material("STUDIO_slate", (.14, .18, .21)))
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
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.compression = 95
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.color_depth = "8"
scene.render.dither_intensity = 0
scene.view_settings.view_transform = "AgX"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
camera.location = (32, 42, 28)
aim(camera, (0, 0, 3.3))
data.type = "ORTHO"
data.ortho_scale = 39
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(), "export.py", "exec"))
for name, position, target, scale in [
    ("hero", (32, 42, 28), (0, 0, 3.3), 39),
    ("side", (35, 0, 14), (0, 0, 3.8), 30),
    ("entry_detail", (12, 28, 10), (0, 9.1, 2.2), 15),
]:
    camera.location = position
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
