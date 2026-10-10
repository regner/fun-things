"""Original cantilevered civic entry canopy; pinned isolated Blender authoring."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_harbour_hall_02"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
WIDTH, PROJECTION = 8.0, 2.4
MOUNT_HEIGHT = 3.85


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


def chamfered_slab(name, width, depth, corner, rear_y, bottom, rear_top, front_top, mat):
    """Construct a closed six-corner plan with a shallow falling roof, never a render primitive."""
    half = width / 2
    outline = [(-half, rear_y), (half, rear_y), (half, rear_y + depth - corner),
               (half - corner, rear_y + depth), (-half + corner, rear_y + depth),
               (-half, rear_y + depth - corner)]
    vertices = [(x, y, bottom) for x, y in outline]
    vertices += [(x, y, rear_top + (front_top - rear_top) * (y - rear_y) / depth)
                 for x, y in outline]
    count = len(outline)
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    faces += [(i, (i + 1) % count, (i + 1) % count + count, i + count)
              for i in range(count)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, name, mat, .018)


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
# Match the completed hall's linear PBR swatches, not a competing waterside palette.
teal = material("harbour_hall_teal_metal", (.035, .15, .15), .35, .42)
limestone = material("harbour_hall_limestone_trim", (.78, .70, .53), 0, .56)
recess = material("harbour_hall_canopy_soffit", (.022, .065, .09), .2, .48)

# No posts or low brackets: this shallow cantilever clears the existing entry lintel.
box("Wall contact rail", (0, .06, .175), (7.8, .12, .45), teal, .018)
chamfered_slab("Warm rolled edge tray", WIDTH, PROJECTION, .32, 0,
               -.005, .09, .09, limestone)
chamfered_slab("Quiet teal falling hood", 7.92, 2.34, .30, .01,
               .065, .39, .24, teal)
chamfered_slab("Inset dark soffit", 7.48, 2.04, .25, .14,
               -.018, .008, .008, recess)
for x in (-2.55, 0, 2.55):
    box("Cantilever soffit rib", (x, 1.13, -.0225), (.12, 2.04, .045), teal, .012)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "D05HarbourHall02_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D05HarbourHall02", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "d05_harbour_hall.02"
root["authorship"] = "Original Blender construction by commissioned production worker"
root["front_axis"] = "Blender +Y maps to Godot -Z; +Z maps to +Y"
root["pivot_contract"] = "Wall-contact mounting datum, not ground contact"
root["hall_mount_godot"] = [0.0, MOUNT_HEIGHT, -9.0]
root["collision_contract"] = "Overhead visual only; no posts or traversable surface"

# Isolated studio remains outside the export collection. Its floor is at hall ground.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.22, .27, .32, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .55
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -MOUNT_HEIGHT - .025))
bpy.context.object.name = "STUDIO_ground"
bpy.context.object.data.materials.append(material("STUDIO_slate", (.14, .18, .21)))
light("STUDIO_key", (8, 12, 16), 3800, 10)
light("STUDIO_rim", (-10, -7, 12), 4500, 10)
light("STUDIO_fill", (-4, 12, 4), 1400, 8)
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
camera.location = (9, 12, 7)
aim(camera, (0, 1.1, 0))
data.type = "ORTHO"
data.ortho_scale = 10.5
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(), "export.py", "exec"))
for name, position, target, scale in [
    ("hero", (9, 12, 7), (0, 1.1, 0), 10.5),
    ("side", (10, 5, -1.7), (0, 1.1, .08), 9.5),
]:
    camera.location = position
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    # The underside view needs no distant studio-floor horizon.
    bpy.data.objects["STUDIO_ground"].hide_render = name == "side"
    bpy.ops.render.render(write_still=True)
bpy.data.objects["STUDIO_ground"].hide_render = False

# Read the sibling's source only for mounted evidence, after source save/export.
# No copied carrier geometry, dependency edit or reference geometry enters our GLB/.blend.
hall_source = ROOT / "art/source/models/environment/d05_harbour_hall_01/d05_harbour_hall_01.blend"
with bpy.data.libraries.load(str(hall_source), link=False) as (available, requested):
    requested.collections = ["export_d05_harbour_hall_01"]
hall_collection = requested.collections[0]
scene.collection.children.link(hall_collection)
hall_root = hall_collection.objects["D05HarbourHall01"]
hall_root.location = (0, -9, -MOUNT_HEIGHT)
camera.location = (12, 20, 7)
aim(camera, (0, .25, -1.2))
data.ortho_scale = 14
# Slightly smaller detail evidence retains the mount while keeping the PNG below 400 KiB.
scene.render.resolution_x = 1152
scene.render.resolution_y = 648
scene.render.filepath = str(EVIDENCE / "mount_detail.png")
bpy.ops.render.render(write_still=True)
# True vertical-down perspective: ground is -3.85, so camera altitude is 47 m.
camera.location = (0, -9, 47 - MOUNT_HEIGHT)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
