"""Author a two-bay loading annex fitting both East Docks rear bearing datums."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d09_warehouses_03"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
LENGTH, DEPTH, EAVE = 12.0, 6.0, 5.0
ROOF_FRONT, ROOF_REAR = 5.15, 5.65
BAY_PITCH = 6.0


def material(name, color, metallic=0.0, roughness=0.5):
    """Create an opaque, back-culled Principled material with no external dependencies."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*color, 1)
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return result


def finish(obj, name, mat, bevel=0.02):
    """Apply static transforms and bevels; clean closed parts and preserve broad normals."""
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
        modifier = obj.modifiers.new("Soft manufactured edges", "BEVEL")
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
    for face in obj.data.polygons:
        face.use_smooth = True
    modifier = obj.modifiers.new("Weighted architectural normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    parts.append(obj)
    return obj


def box(name, position, size, mat, bevel=0.02, roll=0.0):
    """Construct a solid fitting, optionally aligned with the roof pitch about X."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.dimensions = size
    obj.rotation_euler.x = roll
    return finish(obj, name, mat, bevel)


def prism(name, half_length, section, mat, bevel=0.02):
    """Extrude a closed Y/Z cross-section along the warehouse ridge axis."""
    count = len(section)
    vertices = [(x, y, z) for x in (-half_length, half_length) for y, z in section]
    faces = [tuple(reversed(range(count))), tuple(range(count, 2 * count))]
    for index in range(count):
        other = (index + 1) % count
        faces.append((index, other, other + count, index + count))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, name, mat, bevel)


def aim(obj, target):
    """Aim a studio-only camera or light at a known metre-space target."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def light(name, position, energy, size):
    """Add broad blue-hour fill outside the declared export collection."""
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
wall = material("dock_wall_steel", (.12, .19, .23), .3, .56)
roof = material("dock_roof_blue", (.035, .105, .24), .38, .43)
trim = material("dock_frame_navy", (.025, .055, .085), .45, .42)
shutter = material("dock_shutter_teal", (.065, .12, .15), .32, .53)
amber = material("dock_loading_amber", (.95, .48, .095), .15, .42)
base = material("dock_base_slate", (.20, .25, .28), .0, .67)
glass = material("dock_glazing_opaque", (.075, .22, .30), .40, .27)

# A compact butt-attached component, not another warehouse assembly or an open interior.
box("Continuous ground shoe", (0, 0, .18), (LENGTH, DEPTH, .36), base, .035)
prism("Annex steel shell", 5.88,
      [(-2.86, .30), (2.86, .30), (2.86, EAVE), (-2.86, 5.47)], wall, .035)
# Rear roof/flashing returns 0.16 m past the bearing datum, overlapping the sibling
# steel face by 0.02 m. All attachment geometry stays below the 5.8 m family ceiling.
prism("Short blue lean-to roof", 6.15,
      [(-3.16, 5.47), (3.26, 4.97), (3.26, ROOF_FRONT), (-3.16, ROOF_REAR)],
      roof, .025)
slope = math.atan2(ROOF_REAR - ROOF_FRONT, 6.42)
box("Roof bay seam", (0, .05, 5.425), (.065, 6.40, .045), roof, .008, -slope)
for x in (-6.11, 6.11):
    flashing = prism("Sloping end flashing", .07,
                     [(-3.16, 5.63), (3.26, 5.13), (3.26, 5.25), (-3.16, 5.75)],
                     trim, .015)
    flashing.location.x = x
box("Rear wall apron flashing", (0, -3.09, 5.64), (12.30, .14, .22), trim, .015)
for x in (-5.90, 5.90):
    box("Rear vertical wall return", (x, -2.98, 2.90), (.16, .36, 5.20), wall, .015)
box("Low front gutter", (0, 3.26, 5.04), (12.30, .18, .20), trim, .025)
for x in (-5.72, 5.72):
    box("Recessed corner downpipe", (x, 2.92, 2.60), (.14, .12, 4.68), trim, .025)

# Exactly two 6 m loading bays, matching the siblings' closed shutters and amber headers.
for x in (-5.81, 0, 5.81):
    box("Front wall bay pier", (x, 2.88, 2.65), (.18, .12, 4.70), wall, .02)
for x in (-3, 3):
    box("Loading recess frame", (x, 2.88, 2.47), (4.04, .15, 4.54), trim, .035)
    box("Closed industrial shutter", (x, 2.969, 2.40), (3.6, .04, 4.20), shutter, .015)
    for z in (.85, 1.55, 2.25, 2.95, 3.65):
        box("Shutter broad fold", (x, 2.995, z), (3.46, .018, .045), trim, .006)
    box("Loading amber header", (x, 2.955, 4.78), (4.12, .10, .22), amber, .025)
    for dx in (-1.93, 1.93):
        box("Loading jamb accent", (x + dx, 2.963, 1.0), (.16, .065, 1.35), amber, .018)
    box("Flush loading threshold", (x, 2.88, .27), (3.75, .22, .12), base, .012)
# Ordinary side service door and high opaque light slot; no separate artwork or signage.
box("Personnel door backing", (5.905, -.8, 1.36), (.13, 1.35, 2.35), trim, .025)
box("Closed personnel door", (5.982, -.8, 1.34), (.035, 1.12, 2.14), shutter, .015)
box("Personnel amber lintel", (5.963, -.8, 2.62), (.07, 1.45, .14), amber, .02)
box("Personnel pull", (6.01, -.4, 1.31), (.05, .05, .35), base, .012)
for sign in (-1, 1):
    box("End clerestory frame", (sign * 5.912, -.6, 4.12), (.10, 2.70, .66), trim, .025)
    box("End clerestory opaque pane", (sign * 5.978, -.6, 4.12), (.035, 2.42, .41), glass, .015)
    for y in (-2.7, 0, 2.7):
        box("Side wall joint", (sign * 5.90, y, 2.63), (.05, .08, 4.66), trim, .008)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "D09Warehouses03_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D09Warehouses03", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "d09_warehouses.03"
root["authorship"] = "Original Blender construction by commissioned production worker"
root["front_axis"] = "Blender +Y to Godot -Z; two loading bays along X; ground centre origin"
root["bay_pitch_m"] = BAY_PITCH
root["rear_attachment_datum_godot"] = [0.0, 0.0, 3.0]

# Isolated studio setup is excluded by the named export collection filter.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.22, .27, .34, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .55
bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, -.03))
bpy.context.object.name = "STUDIO_ground"
bpy.context.object.data.materials.append(material("STUDIO_slate", (.14, .18, .21)))
light("STUDIO_key", (5, 25, 38), 32000, 28)
light("STUDIO_rim", (-25, -18, 32), 38000, 25)
light("STUDIO_fill", (20, 28, 16), 12000, 20)
data = bpy.data.cameras.new("STUDIO_camera")
data.clip_end = 10000
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
camera.location = (18, 23, 16)
aim(camera, (0, 0, 2.6))
data.type = "ORTHO"
data.ortho_scale = 22
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(), "export.py", "exec"))
for name, position, target, scale in [
    ("hero", (18, 23, 16), (0, 0, 2.6), 22),
    ("side", (22, 0, 9), (0, 0, 2.8), 20),
    ("loading_detail", (8, 16, 7), (2.6, 2.9, 2.5), 8.5),
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
