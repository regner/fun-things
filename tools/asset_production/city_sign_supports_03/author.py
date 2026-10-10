"""Construct the original civic noticeboard in pinned Blender; no external geometry."""
import math
from pathlib import Path
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "city_sign_supports_03"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
WIDTH, HEIGHT, DEPTH = 1.80, 2.10, 0.44
PANEL_HEIGHT, PANEL_CENTRE = 1.20, 1.42
FACE_WIDTH, FACE_HEIGHT = 1.64, 1.04
CORNER_SEGMENTS = 6


def material(name, srgb, metal, rough):
    """Keep the existing civic support palette, converted from sRGB to linear."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    rgb = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in srgb]
    mat.diffuse_color = (*rgb, 1)
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = rough
    return mat


def outline(width, height, radius):
    """Build the rounded X/Z outline used by the family's closed profiled frame."""
    points = []
    for x, z, start in (
        (width / 2 - radius, height / 2 - radius, 0),
        (-width / 2 + radius, height / 2 - radius, 90),
        (-width / 2 + radius, -height / 2 + radius, 180),
        (width / 2 - radius, -height / 2 + radius, 270),
    ):
        for i in range(CORNER_SEGMENTS + 1):
            angle = math.radians(start + 90 * i / CORNER_SEGMENTS)
            points.append((x + radius * math.cos(angle), z + radius * math.sin(angle)))
    return points


def finish(obj, mat, smooth=True):
    """Apply topology cleanup and broad weighted highlights before source saving."""
    obj.data.materials.append(mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=0.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    if smooth:
        for face in obj.data.polygons:
            face.use_smooth = True
        bpy.context.view_layer.objects.active = obj
        modifier = obj.modifiers.new("Broad weighted highlights", "WEIGHTED_NORMAL")
        modifier.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    return obj


def profile(name, profiles, mat, ring=False, smooth=True):
    """Create a closed ring or closed solid with a shared rounded panel contour."""
    count = 4 * (CORNER_SEGMENTS + 1)
    vertices = [(x, y, z + PANEL_CENTRE) for w, h, r, y in profiles
                for x, z in outline(w, h, r)]
    faces = []
    for j in range(len(profiles) - 1):
        for i in range(count):
            faces.append((j * count + i, j * count + (i + 1) % count,
                          (j + 1) * count + (i + 1) % count, (j + 1) * count + i))
    end = (len(profiles) - 1) * count
    if ring:
        for i in range(count):
            faces.append((end + i, end + (i + 1) % count, (i + 1) % count, i))
    else:
        faces.extend([tuple(reversed(range(count))), tuple(end + i for i in range(count))])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, mat, smooth)


def block(name, centre, size, mat, bevel):
    """Author a closed bevelled manufactured part with applied metre transforms."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=centre)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    modifier = obj.modifiers.new("Soft manufactured edges", "BEVEL")
    modifier.width = bevel
    modifier.segments = 3
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    return finish(obj, mat)


def aim(obj, target):
    """Aim an isolated studio camera or light, never a production model root."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def area(name, location, energy, size):
    """Create a soft studio light outside the declared export collection."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.shape, data.size = energy, "DISK", size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    aim(obj, (0, 0, 0.75))


assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for old in list(bpy.data.collections):
    bpy.data.collections.remove(old)
bpy.context.preferences.filepaths.save_version = 0
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
paint = material("support_petrol", (0.105, 0.205, 0.232), 0.18, 0.32)
seal = material("recess_gasket", (0.043, 0.075, 0.087), 0, 0.72)
metal = material("mount_metal", (0.31, 0.39, 0.41), 0.65, 0.38)
face = material("sign_face", (0.66, 0.70, 0.67), 0, 0.56)
parts = [profile("Rounded frame", [
    (1.776, 1.176, 0.048, -0.060), (WIDTH, PANEL_HEIGHT, 0.060, -0.044),
    (WIDTH, PANEL_HEIGHT, 0.060, 0.056), (1.776, 1.176, 0.048, 0.080),
    (1.676, 1.076, 0.032, 0.080), (1.660, 1.060, 0.024, 0.066),
    (1.660, 1.060, 0.024, -0.060),
], paint, ring=True)]
parts.append(profile("Rear shell", [
    (1.75, 1.15, 0.044, -0.062), (1.77, 1.17, 0.054, -0.05),
    (1.77, 1.17, 0.054, 0.025),
], paint))
parts.append(profile("Face gasket", [
    (1.674, 1.074, 0.028, 0.048), (1.674, 1.074, 0.028, 0.066),
    (1.632, 1.032, 0.018, 0.066), (1.632, 1.032, 0.018, 0.048),
], seal, ring=True))
carrier = profile("CitySignSupports03_ArtworkCarrier", [
    (1.632, 1.032, 0.018, 0.051), (FACE_WIDTH, FACE_HEIGHT, 0.022, 0.057),
    (FACE_WIDTH, FACE_HEIGHT, 0.022, 0.071),
], face, smooth=False)
carrier.data.materials.append(metal)
uv = carrier.data.uv_layers.new(name="UVMap")
for polygon in carrier.data.polygons:
    polygon.material_index = 0 if polygon.normal.y > 0.999 else 1
    for loop_index in polygon.loop_indices:
        vertex = carrier.data.vertices[carrier.data.loops[loop_index].vertex_index].co
        uv.data[loop_index].uv = ((0.82 - vertex.x) / FACE_WIDTH,
                                  (vertex.z - 0.90) / FACE_HEIGHT)
for x, side in ((-0.67, "Left"), (0.67, "Right")):
    parts.append(block(f"{side} foot", (x, 0, 0.0275), (0.30, DEPTH, 0.055), metal, 0.018))
    parts.append(block(f"{side} shoe", (x, -0.018, 0.095), (0.16, 0.16, 0.11), paint, 0.016))
    parts.append(block(f"{side} post", (x, -0.018, 0.96), (0.11, 0.11, 1.84), paint, 0.012))
    parts.append(block(f"{side} rear clamp", (x, -0.090, 1.40),
                       (0.18, 0.055, 0.15), metal, 0.012))
parts.append(block("Shallow rain cap", (0, 0.03, 2.05),
                   (1.90, 0.30, 0.10), paint, 0.024))
bpy.ops.object.select_all(action="DESELECT")
for part in parts:
    part.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
hardware = bpy.context.object
hardware.name = "CitySignSupports03_Hardware"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CitySignSupports03", None)
collection.objects.link(root)
hardware.parent = root
carrier.parent = root
root["asset_id"] = "city_sign_supports.03"
root["provenance"] = "Original Blender construction by commissioned production worker"
root["front"] = "Blender +Y / Godot -Z; ground-centred origin"
root["artwork"] = "ArtworkCarrier sign_face only; 41:26 image aspect, no district copy"
# The studio is retained for reproducible source previews but excluded from export.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.22, 0.28, 0.34, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.65
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.008))
ground = bpy.context.object
ground.name = "STUDIO_ground"
ground.data.materials.append(material("STUDIO_slate", (0.39, 0.44, 0.47), 0, 0.7))
area("STUDIO_key", (-3, 4, 6), 600, 4)
area("STUDIO_rim", (3, -3, 4), 750, 3)
area("STUDIO_fill", (3, 4, 2), 160, 3)
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new("STUDIO_camera", data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.view_settings.view_transform = "AgX"
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.compression = 95
scene.render.dither_intensity = 0
data.type = "ORTHO"
data.ortho_scale = 4.8
camera.location = (2.5, 4, 2.2)
aim(camera, (0, 0, 1.04))
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
for name, position, target, scale in (
    ("hero", (2.8, 4.5, 2.8), (0, 0, 1.04), 4.8),
    ("side", (4, -1.6, 2.6), (0, 0, 1.04), 4.8),
    ("detail", (1.7, 3.3, 2.55), (0.55, 0, 1.85), 1.4),
):
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
