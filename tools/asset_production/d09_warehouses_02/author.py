"""Author the wide, low six-bay sibling using the East Docks warehouse vocabulary."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d09_warehouses_02"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
LENGTH, DEPTH, EAVE = 36.0, 24.0, 6.4
ROOF_FRONT, ROOF_REAR = 6.58, 7.10
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

# Same closed exterior contract as .01, but a deeper footprint and no pitched ridge.
box("Continuous ground shoe", (0, 0, .18), (LENGTH, DEPTH, .36), base, .035)
prism("Low steel shell", LENGTH / 2 - .12,
      [(-11.86, .30), (11.86, .30), (11.86, EAVE), (-11.86, 6.92)], wall, .035)
# One broad shallow mono-pitch with actual thickness: this is not a third gabled shed.
prism("Wide blue low roof", 18.35,
      [(-12.4, 6.92), (12.4, 6.40), (12.4, ROOF_FRONT), (-12.4, ROOF_REAR)],
      roof, .035)
slope = math.atan2(ROOF_REAR - ROOF_FRONT, 24.8)
roof_centre = (ROOF_FRONT + ROOF_REAR) / 2
for x in (-12, -6, 0, 6, 12):
    box("Roof bay seam", (x, 0, roof_centre + .025), (.065, 24.79, .055),
        roof, .012, -slope)
# Low continuous edge flashings accent the rectangular roof silhouette, not neon bands.
for x in (-18.31, 18.31):
    flashing = prism("Sloping end flashing", .07,
                     [(-12.4, 7.09), (12.4, 6.57), (12.4, 6.69), (-12.4, 7.21)],
                     trim, .02)
    flashing.location.x = x
box("High rear flashing", (0, -12.40, 7.12), (36.7, .18, .18), trim, .025)
box("Low front gutter", (0, 12.40, 6.49), (36.7, .18, .20), trim, .035)
for sign in (-1, 1):
    for x in (-17.72, 17.72):
        box("Recessed corner downpipe", (x, sign * 11.92, 3.19),
            (.14, .12, 5.86), trim, .025)

# Two widely separated long opaque rooflight ribbons leave the central field quiet.
for x in (-9, 9):
    box("Long rooflight curb", (x, 0, roof_centre + .08), (1.65, 10.0, .14),
        trim, .035, -slope)
    box("Opaque rooflight ribbon", (x, 0, roof_centre + .165), (1.40, 9.74, .06),
        glass, .025, -slope)
    for y in (-2.5, 0, 2.5):
        z = roof_centre - y * math.tan(slope) + .205
        box("Rooflight crossbar", (x, y, z), (1.45, .07, .045), trim, .008, -slope)

# Repeated facade bays are a common family contract. Rear centre stays blank for the annex.
for index in range(7):
    x = -18 + index * BAY_PITCH
    x = max(-17.81, min(17.81, x))
    for sign in (-1, 1):
        box("Wall bay pier", (x, sign * 11.88, 3.33), (.18, .12, 6.06), wall, .02)
for x in (-15, -9, -3, 3):
    box("Loading recess frame", (x, 11.88, 2.47), (4.04, .15, 4.54), trim, .035)
    box("Closed industrial shutter", (x, 11.969, 2.40), (3.6, .04, 4.20), shutter, .015)
    # Broad shutter folds stop far short of a noisy fine corrugated texture.
    for z in (.85, 1.55, 2.25, 2.95, 3.65):
        box("Shutter broad fold", (x, 11.995, z), (3.46, .018, .045), trim, .006)
    box("Loading amber header", (x, 11.955, 4.78), (4.12, .10, .22), amber, .025)
    for dx in (-1.93, 1.93):
        box("Loading jamb accent", (x + dx, 11.963, 1.0), (.16, .065, 1.35), amber, .018)
    box("Flush loading threshold", (x, 11.88, .27), (3.75, .22, .12), base, .012)
# The last two front bays are quiet service wall, not two more giant doors.
box("Personnel door backing", (10.9, 11.905, 1.36), (1.35, .13, 2.35), trim, .025)
box("Closed personnel door", (10.9, 11.982, 1.34), (1.12, .035, 2.14), shutter, .015)
box("Personnel amber lintel", (10.9, 11.963, 2.62), (1.45, .07, .14), amber, .02)
box("Personnel pull", (11.30, 12.01, 1.31), (.05, .05, .35), base, .012)
for x in (9, 15):
    box("Front clerestory frame", (x, 11.912, 5.48), (3.60, .10, .76), trim, .025)
    box("Front clerestory opaque pane", (x, 11.978, 5.48), (3.32, .035, .51), glass, .015)
# Broad end-panel joints and one high vent per end: no dense industrial clutter.
for sign in (-1, 1):
    for y in (-9, -6, -3, 0, 3, 6, 9):
        box("End wall joint", (sign * 17.90, y, 3.2), (.05, .08, 5.65), trim, .008)
    box("High end vent frame", (sign * 17.91, -7.5, 5.55), (.12, 2.40, .82), trim, .025)
    for z in (5.35, 5.55, 5.75):
        box("High end vent blade", (sign * 17.986, -7.5, z), (.065, 2.16, .07), wall, .012)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "D09Warehouses02_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D09Warehouses02", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "d09_warehouses.02"
root["authorship"] = "Original Blender construction by commissioned production worker"
root["front_axis"] = "Blender +Y to Godot -Z; six loading bays along X; ground centre origin"
root["bay_pitch_m"] = BAY_PITCH
root["rear_annex_datum_godot"] = [0.0, 0.0, 12.0]

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
camera.location = (48, 62, 44)
aim(camera, (0, 0, 3.3))
data.type = "ORTHO"
data.ortho_scale = 57
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(), "export.py", "exec"))
for name, position, target, scale in [
    ("hero", (48, 62, 44), (0, 0, 3.3), 57),
    ("side", (0, 70, 22), (0, 0, 3.5), 43),
    ("loading_detail", (-8, 29, 12), (-10.5, 11.9, 2.6), 16),
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
