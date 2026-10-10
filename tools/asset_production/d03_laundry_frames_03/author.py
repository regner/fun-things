"""Original static laundry cloth shapes; pinned Blender construction, no simulation."""
import math
from pathlib import Path
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_laundry_frames_03"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
assert bpy.app.version_string == "5.2.2 LTS", bpy.app.version_string
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
source_scene = bpy.context.scene
source_scene.name = "ClothSources"
source_scene.unit_settings.system = "METRIC"
source_scene.unit_settings.scale_length = 1


def material(name, swatch):
    """Convert muted sRGB swatches into opaque rough Principled materials."""
    srgb = [int(swatch[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    rgb = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in srgb]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*rgb, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Roughness"].default_value = .88
    shader.inputs["Metallic"].default_value = 0
    return mat


def cloth(variant, width, drop, columns, amplitude, body_color, hem_color):
    """Sweep a broad folded cloth over a 20 mm radius line saddle, then close its shell."""
    collection = bpy.data.collections.new(f"export_{NID}_{variant}")
    source_scene.collection.children.link(collection)
    root_name = "D03LaundryFrames03" + variant.title()
    root = bpy.data.objects.new(root_name, None)
    collection.objects.link(root)
    root["asset_id"] = "d03_laundry_frames.03"
    root["provenance"] = "Original Blender construction; no downloaded meshes or textures"
    root["mount"] = "Top-centre line axis at origin; translate to Godot Y=2.18 on frame"
    root["state"] = "Static soft cloth dressing; no rig, simulation or gameplay collision"
    # The narrow extra rows near each end create broad hems without floating geometry.
    front = [1, .975, .93, .78, .60, .42, .25, .12, 0]
    rows = [("front", t) for t in front]
    rows += [("arch", i / 8) for i in range(1, 9)]
    rows += [("back", t) for t in (.25, .55, .85, .95, 1)]
    verts, faces = [], []
    for side, t in rows:
        for index in range(columns + 1):
            u = index / columns
            across = 2 * u - 1
            wave = math.sin(u * math.tau * (2 if variant == "sheet" else 1) + .35)
            if side == "arch":
                angle = math.pi * t
                x = across * width / 2
                y, z = .020 * math.cos(angle), .020 * math.sin(angle)
            else:
                reach = drop if side == "front" else .25
                sign = 1 if side == "front" else -1
                x = across * width / 2 * (1 - .035 * t)
                y = sign * (.020 + .10 * t + amplitude * wave * t)
                z = -reach * t + .020 * math.sin(u * math.pi) * t
            verts.append((x, y, z))
    stride = columns + 1
    for row in range(len(rows) - 1):
        for index in range(columns):
            a = row * stride + index
            faces.append((a, a + 1, a + stride + 1, a + stride))
    mesh = bpy.data.meshes.new(root_name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(root_name + "_Mesh", mesh)
    collection.objects.link(obj)
    obj.parent = root
    mesh.materials.append(material(f"laundry_{variant}_body", body_color))
    mesh.materials.append(material(f"laundry_{variant}_hem", hem_color))
    for face in mesh.polygons:
        row, column = divmod(face.index, columns)
        face.material_index = int(row in (0, len(rows) - 2))
        face.use_smooth = True
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    shell = obj.modifiers.new("Closed 8 mm stylized cloth thickness", "SOLIDIFY")
    shell.thickness = .008
    shell.offset = 0
    shell.use_even_offset = True
    bpy.ops.object.modifier_apply(modifier=shell.name)
    obj.select_set(False)
    return collection


sheet = cloth("sheet", 1.42, 1.04, 32, .048, "CCC9B5", "AEB1A3")
towel = cloth("towel", .76, .80, 24, .032, "B98377", "9C746B")

# A separate saved studio instances the source collections; export pivots stay untouched.
studio = bpy.data.scenes.new("Studio_MountedCloths")
studio.unit_settings.system = "METRIC"
studio.unit_settings.scale_length = 1
bpy.context.window.scene = studio
frame_path = ROOT / "art/source/models/environment/d03_laundry_frames_01/d03_laundry_frames_01.blend"
with bpy.data.libraries.load(str(frame_path), link=True) as (available, linked):
    linked.collections = ["export_d03_laundry_frames_01"]
frame_collection = linked.collections[0]
frame_collection.library.filepath = "//../d03_laundry_frames_01/d03_laundry_frames_01.blend"
for name, collection, position in [
    ("STUDIO_existing_frame", frame_collection, (0, 0, 0)),
    ("STUDIO_sheet", sheet, (-.62, .48, 2.18)),
    ("STUDIO_towel", towel, (.78, .48, 2.18)),
]:
    instance = bpy.data.objects.new(name, None)
    instance.instance_type = "COLLECTION"
    instance.instance_collection = collection
    instance.location = position
    studio.collection.objects.link(instance)

studio.world = bpy.data.worlds.new("STUDIO_world")
studio.world.use_nodes = True
studio.world.node_tree.nodes["Background"].inputs[0].default_value = (.24, .29, .37, 1)
studio.world.node_tree.nodes["Background"].inputs[1].default_value = .65
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.015))
ground = bpy.context.object
ground.name = "STUDIO_ground"
ground.data.materials.append(material("STUDIO_slate", "667783"))
bpy.ops.mesh.primitive_cube_add(size=1, location=(20, 0, .5))
reference = bpy.context.object
reference.name = "STUDIO_one_metre_reference"
reference.hide_render = True


def aim(obj, target):
    """Aim isolated studio cameras and lights, never exported geometry."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


for name, location, power, size in [("key", (1, 4, 7), 1100, 5),
                                   ("fill", (4, -3, 5), 850, 4),
                                   ("rim", (-4, -2, 6), 1400, 4)]:
    data = bpy.data.lights.new("STUDIO_" + name, "AREA")
    data.energy, data.size = power, size
    light = bpy.data.objects.new(data.name, data)
    studio.collection.objects.link(light)
    light.location = location
    aim(light, (0, 0, 1))
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new(data.name, data)
studio.collection.objects.link(camera)
studio.camera = camera
studio.render.engine = "CYCLES"
studio.cycles.device = "CPU"
studio.cycles.samples = 32
studio.cycles.use_denoising = True
studio.render.resolution_x, studio.render.resolution_y = 1280, 720
studio.render.resolution_percentage = 100
studio.render.image_settings.file_format = "PNG"
studio.render.image_settings.compression = 95
studio.render.dither_intensity = 0
studio.view_settings.view_transform = "AgX"
data.type, data.ortho_scale = "ORTHO", 6.2
camera.location = (5, 7, 4)
aim(camera, (0, 0, 1.1))
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.context.window.scene = source_scene
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
bpy.context.window.scene = studio
for name, location, target, scale in [
    ("hero", (5, 7, 4), (0, 0, 1.1), 6.2),
    ("side", (7, 0, 2.7), (0, .35, 1.6), 3.5),
    ("detail", (1.8, 4, 3), (0, .48, 1.83), 3.5),
]:
    camera.location = location
    aim(camera, target)
    data.ortho_scale = scale
    studio.render.filepath = str(EVIDENCE / (name + ".png"))
    bpy.ops.render.render(write_still=True)
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
studio.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
