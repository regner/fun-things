"""Original short communal laundry frame, authored in pinned Blender only."""
import math
import runpy
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_laundry_frames_01"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
POST_X = 1.8
LINE_HEIGHT = 2.18
LINE_OFFSETS = (-.48, 0, .48)
assert bpy.app.version_string == "5.2.2 LTS", bpy.app.version_string
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
parts = []


def material(name, swatch, metallic, roughness):
    """Use opaque flat sRGB swatches converted to linear Principled inputs."""
    srgb = [int(swatch[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    rgb = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in srgb]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*rgb, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


frame = material("laundry_muted_teal_metal", "476D70", .35, .5)
shoe = material("laundry_dark_fittings", "29474C", .4, .48)
line = material("laundry_pale_line", "BBC4B6", .1, .68)


def finish(obj, name, mat, bevel=0):
    """Apply manufactured bevels and clean each closed component before joining."""
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Soft metal edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    modifier = obj.modifiers.new("Weighted metal normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    parts.append(obj)
    return obj


def box(name, location, dimensions, mat, bevel):
    """Build one editable closed metal component in metre dimensions."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    return finish(obj, name, mat, bevel)


def cylinder_between(name, start, end, radius, mat, sides=12):
    """Create a capped static line or socket without curves or runtime generation."""
    a, b = Vector(start), Vector(end)
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides, radius=radius,
                                       depth=(b - a).length, location=(a + b) / 2)
    obj = bpy.context.object
    obj.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    return finish(obj, name, mat)


for x in (-POST_X, POST_X):
    tag = "west" if x < 0 else "east"
    box(f"{tag}_ground_shoe", (x, 0, .04), (.30, .30, .08), shoe, .024)
    box(f"{tag}_upright", (x, 0, 1.10), (.14, .14, 2.12), frame, .018)
    box(f"{tag}_base_sleeve", (x, 0, .18), (.18, .18, .24), shoe, .016)
    box(f"{tag}_crossarm", (x, 0, 2.16), (.18, 1.30, .16), frame, .028)
    # Sparse cap seams imply simple welded hardware, not noisy nuts/bolts.
    for y in (-.63, .63):
        box(f"{tag}_arm_cap", (x, y, 2.16), (.184, .06, .152), shoe, .012)
    for index, y in enumerate(LINE_OFFSETS):
        inner = x - math.copysign(.14, x)
        cylinder_between(f"{tag}_line_socket_{index}", (x, y, LINE_HEIGHT),
                         (inner, y, LINE_HEIGHT), .033, shoe)
for index, y in enumerate(LINE_OFFSETS):
    cylinder_between(f"Taut_line_{index}", (-POST_X, y, LINE_HEIGHT),
                     (POST_X, y, LINE_HEIGHT), .014, line)

bpy.ops.object.select_all(action="DESELECT")
for part in parts:
    part.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
model = bpy.context.object
model.name = "D03LaundryFrames01_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
old_materials = list(model.data.materials)
ordered = [frame, shoe, line]
indices = [ordered.index(old_materials[face.material_index]) for face in model.data.polygons]
model.data.materials.clear()
for mat in ordered:
    model.data.materials.append(mat)
for face, index in zip(model.data.polygons, indices):
    face.material_index = index
root = bpy.data.objects.new("D03LaundryFrames01", None)
collection.objects.link(root)
model.parent = root
root["asset_id"] = "d03_laundry_frames.01"
root["provenance"] = "Original Blender construction; no downloaded geometry or textures"
root["axes"] = "Blender +Y to Godot -Z; ground-centred origin"
root["cloth_interface"] = "Godot Y=2.18, Z=-0.48/0/+0.48, usable X=-1.60..+1.60"
root["state"] = "Static intact dressing; no cloth simulation, interaction or destruction"

# Studio geometry, lights and camera are excluded from the explicit export collection.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.24, .29, .37, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .65
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.015))
ground = bpy.context.object
ground.name = "STUDIO_ground"
ground.data.materials.append(material("STUDIO_slate", "667783", 0, .8))
bpy.ops.mesh.primitive_cube_add(size=1, location=(20, 0, .5))
reference = bpy.context.object
reference.name = "STUDIO_one_metre_reference"
reference.hide_render = True


def aim(obj, target):
    """Aim studio lighting and cameras without changing exported geometry."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


for name, location, power, size in [("key", (1, 4, 7), 1100, 5),
                                   ("fill", (4, -3, 5), 850, 4),
                                   ("rim", (-4, -2, 6), 1400, 4)]:
    data = bpy.data.lights.new("STUDIO_" + name, "AREA")
    data.energy, data.size = power, size
    light = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(light)
    light.location = location
    aim(light, (0, 0, 1))
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new(data.name, data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.compression = 95
scene.render.dither_intensity = 0
scene.view_settings.view_transform = "AgX"
data.type, data.ortho_scale = "ORTHO", 6.2
camera.location = (5, 7, 4)
aim(camera, (0, 0, 1.1))
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
for name, location, target, scale in [
    ("hero", (5, 7, 4), (0, 0, 1.1), 6.2),
    ("side", (7, 0, 1.12), (0, 0, 1.12), 5.0),
    ("detail", (3.6, 2.6, 3.2), (1.65, 0, 2.14), 2.15),
]:
    camera.location = location
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / (name + ".png"))
    bpy.ops.render.render(write_still=True)
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
