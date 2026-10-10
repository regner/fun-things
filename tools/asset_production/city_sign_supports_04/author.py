"""Original three-finger civic wayfinding post, authored only in pinned Blender."""
import math
from pathlib import Path
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "city_sign_supports_04"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
FINGERS = (("Lower", 2.75, 1), ("Middle", 3.20, -1), ("Upper", 3.65, 1))


def material(name, srgb, metal, rough):
    """Match the existing civic hardware's opaque, linear-space PBR palette."""
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


def finish(obj, mat, smooth=True):
    """Retain closed solids, applied geometry and broad manufactured highlights."""
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
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
        bpy.context.view_layer.objects.active = obj
        modifier = obj.modifiers.new("Broad weighted highlights", "WEIGHTED_NORMAL")
        modifier.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    return obj


def arrow(name, profiles, height, direction, mat, ring=False, smooth=True):
    """Sweep nested five-point arrow outlines into a closed frame or face carrier."""
    vertices = []
    for start, shoulder, tip, half_height, depth in profiles:
        contour = ((start, -half_height), (shoulder, -half_height), (tip, 0),
                   (shoulder, half_height), (start, half_height))
        vertices.extend((direction * x, depth, height + z) for x, z in contour)
    faces = []
    for j in range(len(profiles) - 1):
        for i in range(5):
            faces.append((j * 5 + i, j * 5 + (i + 1) % 5,
                          (j + 1) * 5 + (i + 1) % 5, (j + 1) * 5 + i))
    end = (len(profiles) - 1) * 5
    if ring:
        for i in range(5):
            faces.append((end + i, end + (i + 1) % 5, (i + 1) % 5, i))
    else:
        faces.extend([tuple(reversed(range(5))), tuple(end + i for i in range(5))])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, mat, smooth)


def cylinder(name, radius, bottom, top, mat, bevel=0.008):
    """Create a closed twenty-sided post component with softened edges."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=radius, depth=top - bottom,
                                      location=(0, 0, (top + bottom) / 2))
    obj = bpy.context.object
    obj.name = name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    modifier = obj.modifiers.new("Soft manufactured edges", "BEVEL")
    modifier.width, modifier.segments = bevel, 3
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    return finish(obj, mat)


def aim(obj, target):
    """Aim only the isolated studio cameras and lights."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def area(name, location, energy, size):
    """Create studio lighting outside the export collection."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.shape, data.size = energy, "DISK", size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    aim(obj, (0, 0, 2))


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
parts = [cylinder("Foot plate", 0.20, 0, 0.055, metal),
         cylinder("Cast shoe", 0.13, 0.035, 0.22, paint),
         cylinder("Mast", 0.075, 0.12, 3.89, paint),
         cylinder("Mast cap", 0.093, 3.86, 3.92, metal)]
carriers = []
for label, centre, direction in FINGERS:
    parts.append(cylinder(f"{label} mounting collar", 0.103, centre - 0.075,
                          centre + 0.075, metal))
    parts.append(arrow(f"{label} bevelled frame", [
        (0.048, 1.217, 1.428, 0.152, 0.070),
        (0.040, 1.220, 1.440, 0.160, 0.080),
        (0.040, 1.220, 1.440, 0.160, 0.180),
        (0.048, 1.217, 1.428, 0.152, 0.190),
        (0.077, 1.194, 1.392, 0.123, 0.190),
        (0.083, 1.190, 1.382, 0.117, 0.180),
        (0.083, 1.190, 1.382, 0.117, 0.070),
    ], centre, direction, paint, ring=True))
    parts.append(arrow(f"{label} closed rear", [
        (0.049, 1.215, 1.425, 0.150, 0.071),
        (0.049, 1.215, 1.425, 0.150, 0.145),
    ], centre, direction, paint))
    parts.append(arrow(f"{label} gasket", [
        (0.078, 1.195, 1.391, 0.124, 0.165),
        (0.078, 1.195, 1.391, 0.124, 0.180),
        (0.091, 1.181, 1.365, 0.108, 0.180),
        (0.091, 1.181, 1.365, 0.108, 0.165),
    ], centre, direction, seal, ring=True))
    carrier = arrow(f"CitySignSupports04_Artwork{label}", [
        (0.089, 1.182, 1.368, 0.110, 0.165),
        (0.085, 1.185, 1.375, 0.115, 0.173),
        (0.085, 1.185, 1.375, 0.115, 0.184),
    ], centre, direction, face, smooth=False)
    carrier.data.materials.append(metal)
    uv = carrier.data.uv_layers.new(name="UVMap")
    right_edge = 1.375 if direction == 1 else -0.085
    for polygon in carrier.data.polygons:
        polygon.material_index = 0 if polygon.normal.y > 0.999 else 1
        for loop_index in polygon.loop_indices:
            vertex = carrier.data.vertices[carrier.data.loops[loop_index].vertex_index].co
            uv.data[loop_index].uv = ((right_edge - vertex.x) / 1.29,
                                      (vertex.z - centre + 0.115) / 0.23)
    carriers.append(carrier)
bpy.ops.object.select_all(action="DESELECT")
for part in parts:
    part.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
hardware = bpy.context.object
hardware.name = "CitySignSupports04_Hardware"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CitySignSupports04", None)
collection.objects.link(root)
for obj in [hardware, *carriers]:
    obj.parent = root
root["asset_id"] = "city_sign_supports.04"
root["provenance"] = "Original Blender construction by commissioned production worker"
root["front"] = "Blender +Y / Godot -Z; ground-centred post pivot"
root["artwork"] = "Three independent sign_face slot 0 overrides; 129:23 aspect; no copy"
# Reproducible isolated studio: never exported as production geometry.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.22, 0.28, 0.34, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.65
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.008))
ground = bpy.context.object
ground.name = "STUDIO_ground"
ground.data.materials.append(material("STUDIO_slate", (0.39, 0.44, 0.47), 0, 0.7))
area("STUDIO_key", (-3, 4, 7), 750, 4)
area("STUDIO_rim", (3, -3, 5), 850, 3)
area("STUDIO_fill", (3, 4, 2), 180, 3)
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
data.ortho_scale = 8.0
camera.location = (3, 7, 4.8)
aim(camera, (0, 0, 1.95))
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
for name, position, target, scale in (
    ("hero", (3, 7, 4.8), (0, 0, 1.95), 8.0),
    ("side", (5, -4, 4.7), (0, 0, 1.95), 8.0),
    ("detail", (1.8, 4, 4.2), (0.45, 0, 3.38), 2.5),
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
