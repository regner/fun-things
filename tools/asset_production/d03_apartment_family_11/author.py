"""Original height-step flashing; reused wall and cap remain separate linked assets."""
import math
import runpy
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_11"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
STOREY_HEIGHT = 3.2
assert bpy.app.version_string == "5.2.2 LTS", bpy.app.version_string
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = None
parts = []


def material(name, swatch, roughness, metallic=0):
    """Match the straight bay's opaque sRGB swatches using linear Principled inputs."""
    srgb = [int(swatch[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    rgb = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in srgb]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*rgb, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    return mat


trim = material("terrace_pale_frame", "C5CABF", .53)
roof = material("terrace_bluegrey_roof", "526B7B", .80)


def section(name, profile, z_min, z_max):
    """Extrude a closed X/Y sheet-metal profile along Godot Z, with manufactured folds."""
    count = len(profile)
    vertices = [(x, -z, y) for z in (z_min, z_max) for x, y in profile]
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    faces.extend((i, (i + 1) % count, (i + 1) % count + count, i + count)
                 for i in range(count))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(roof)
    mesh.materials.append(trim)
    # Pale upper counterflashing folds, quiet roof-blue sloped apron and return faces.
    for polygon in mesh.polygons:
        polygon.material_index = int(all(vertices[i][2] >= 3.739 for i in polygon.vertices))
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    parts.append(obj)


collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
# Toe penetrates the roof field (3.42) and coping (3.52); top remains above both.
section("Continuous_sloped_flashing", [(.10, 3.40), (.50, 3.40), (.50, 3.58),
        (.46, 3.60), (.24, 3.74), (.24, 3.80), (.10, 3.80)], -5.98, 5.98)
# End returns deliberately cover the existing wall/low-roof coplanar fascia seam.
profile = [(-.12, 3.18), (.50, 3.18), (.50, 3.58), (.46, 3.60),
           (.24, 3.74), (.24, 3.80), (-.12, 3.80)]
section("North_return_apron", profile, -6.12, -5.98)
section("South_return_apron", profile, 5.98, 6.12)
bpy.ops.object.select_all(action="DESELECT")
for part in parts:
    part.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
model = bpy.context.object
model.name = "D03ApartmentFamily11_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D03ApartmentFamily11", None)
collection.objects.link(root)
model.parent = root
root["asset_id"] = "d03_apartment_family.11"
root["provenance"] = "Original Blender flashing; no duplicated wall or roof-cap geometry"
root["interface"] = "Ground-reference end-wall anchor; exposed +X; 3.2m local height drop"
root["state"] = "Overhead-only inaccessible roof junction; no new collision or roof gameplay"

# Studio is excluded from the named export collection.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.24, .29, .37, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .65
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.025))
ground = bpy.context.object
ground.name = "STUDIO_ground"
ground.data.materials.append(material("STUDIO_slate", "667783", .8))
bpy.ops.mesh.primitive_cube_add(size=1, location=(25, 0, .5))
reference = bpy.context.object
reference.name = "STUDIO_one_metre_reference"
reference.hide_render = True


def aim(obj, target):
    """Aim studio cameras/lights without changing exported transforms."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


for name, location, power, size in [("key", (-12, 18, 25), 10000, 18),
                                   ("fill", (18, 12, 20), 8500, 16),
                                   ("rim", (-4, -18, 25), 9000, 16)]:
    data = bpy.data.lights.new("STUDIO_" + name, "AREA")
    data.energy, data.size = power, size
    light = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(light)
    light.location = location
    aim(light, (0, 0, 1.5))
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
data.type, data.ortho_scale = "ORTHO", 24
camera.location = (-30, 42, 35)
aim(camera, (0, 0, 1.6))
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
# Load unchanged sibling collections only AFTER source save/export, never into the asset source.
context_collections = {}


def context(sibling, variant, position, yaw=0):
    """Instance original sibling source geometry for evidence only, at documented Godot transforms."""
    key = sibling + variant
    if key not in context_collections:
        source = ROOT / f"art/source/models/environment/{sibling}/{sibling}.blend"
        name = f"export_{sibling}" + ("_" + variant if variant else "")
        with bpy.data.libraries.load(str(source), link=False) as (available, loaded):
            loaded.collections = [name]
        context_collections[key] = loaded.collections[0]
    item = bpy.data.objects.new("EVIDENCE_" + key, None)
    scene.collection.objects.link(item)
    item.instance_type = "COLLECTION"
    item.instance_collection = context_collections[key]
    x, y, z = position
    item.location = (x, -z, y)
    item.rotation_euler.z = math.radians(yaw)
    return item


# Local .11 prefab composition, at the origin: same links as its saved Godot wrapper.
context("d03_apartment_family_07", "", (0, 3.2, 0))
context("d03_apartment_family_10", "end", (0, 3.2, 0))
# High west bay and low east bay, with outer ends finished using the existing kit.
hosts = []
for position in [(-3.12, 0, 0), (-3.12, 3.2, 0), (2.88, 0, 0)]:
    hosts.append(context("d03_apartment_family_05", "", position))
for position, yaw in [((-6.24, 0, 0), 180), ((-6.24, 3.2, 0), 180), ((6, 0, 0), 0)]:
    hosts.append(context("d03_apartment_family_07", "", position, yaw))
for variant, position, yaw in [("straight", (-3.12, 3.2, 0), 0),
                              ("straight", (2.88, 0, 0), 0),
                              ("end", (-6.24, 3.2, 0), 180), ("end", (6, 0, 0), 0)]:
    hosts.append(context("d03_apartment_family_10", variant, position, yaw))
for name, location, target, scale in [
    ("hero", (21, 26, 20), (0, 0, 3.0), 27),
    ("side", (20, -25, 14), (0, 0, 3.0), 27),
    ("junction_detail", (5, 11, 7), (.1, 5.5, 3.7), 4.8),
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
