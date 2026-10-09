"""Build the original short poster drum in pinned Blender; no external asset inputs."""
import math
from pathlib import Path
import runpy

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_poster_drum_01"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SEGMENTS = 64
WRAP_BOTTOM = 0.24
WRAP_TOP = 1.28
WRAP_RADIUS = 0.397


def material(name, color, metallic, roughness):
    """Create an opaque, exportable flat-color Principled material."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.diffuse_color = (*color, 1)
    result.use_backface_culling = True
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return result


def lathe(name, rings, materials, wrap=False):
    """Build closed smooth radial hardware with a seam at Blender -Y (Godot +Z)."""
    vertices = [
        (radius * math.cos(-math.pi / 2 + i * math.tau / SEGMENTS),
         radius * math.sin(-math.pi / 2 + i * math.tau / SEGMENTS), height)
        for height, radius in rings for i in range(SEGMENTS)
    ]
    faces = [tuple(reversed(range(SEGMENTS)))]
    for ring in range(len(rings) - 1):
        for i in range(SEGMENTS):
            a = ring * SEGMENTS + i
            b = ring * SEGMENTS + (i + 1) % SEGMENTS
            faces.append((a, b, b + SEGMENTS, a + SEGMENTS))
    faces.append(tuple(range((len(rings) - 1) * SEGMENTS, len(rings) * SEGMENTS)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.parent = root
    for mat in materials:
        mesh.materials.append(mat)
    uv = mesh.uv_layers.new(name="UVMap")
    for polygon in mesh.polygons:
        # Horizontal rings and closed ends stay flat; sloped rims and cylinder are smooth.
        polygon.use_smooth = abs(polygon.normal.z) < 0.99
        if polygon.index not in (0, len(mesh.polygons) - 1):
            ring = (polygon.index - 1) // SEGMENTS
            segment = (polygon.index - 1) % SEGMENTS
            z0, z1 = rings[ring][0], rings[ring + 1][0]
            is_wrap = wrap and abs(z0 - WRAP_BOTTOM) < 1e-6 and abs(z1 - WRAP_TOP) < 1e-6
            polygon.material_index = 1 if is_wrap else 0
            for loop_index, u, z in zip(polygon.loop_indices,
                                       (segment, segment + 1, segment + 1, segment),
                                       (z0, z0, z1, z1)):
                v = (z - WRAP_BOTTOM) / (WRAP_TOP - WRAP_BOTTOM) if is_wrap else z / 1.45
                uv.data[loop_index].uv = (u / SEGMENTS, v)
        else:
            for loop_index in polygon.loop_indices:
                vertex = mesh.vertices[mesh.loops[loop_index].vertex_index].co
                uv.data[loop_index].uv = (vertex.x / 0.9 + 0.5, vertex.y / 0.9 + 0.5)
    return obj


def aim(obj, target):
    """Orient a studio camera or light toward its subject."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def light(name, location, energy, size):
    """Add a soft studio-only area light outside the export collection."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    aim(obj, (0, 0, 0.7))


assert bpy.app.version_string == "5.2.2 LTS"
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
root = bpy.data.objects.new("D06PosterDrum01", None)
collection.objects.link(root)
root["asset_id"] = "d06_poster_drum.01"
root["authorship"] = "Original Blender construction, commissioned production specialist"
root["cap_seating_height_m"] = 1.35
root["front_axis"] = "Blender +Y / Godot -Z; wrap U=0.5 faces front"
petrol = material("drum_frame_petrol", (0.025, 0.075, 0.09), 0.4, 0.43)
ivory = material("poster_wrap", (0.922, 0.880, 0.716), 0, 0.7)
# Continuous, capped support: no decal shell, overlap, or open border in the poster surface.
lathe("D06PosterDrum01_Body", [
    (0, 0.41), (0.012, 0.433), (0.035, 0.445), (0.15, 0.445),
    (0.175, 0.433), (0.20, 0.415), (0.22, WRAP_RADIUS),
    (WRAP_BOTTOM, WRAP_RADIUS), (WRAP_TOP, WRAP_RADIUS),
    (1.30, 0.415), (1.32, 0.42), (1.35, 0.42),
], [petrol, ivory], wrap=True)
# The independent standard cap is replaceable at the 1.35 m seating plane by family .02.
lathe("D06PosterDrum01_Cap", [
    (1.35, 0.42), (1.365, 0.445), (1.38, 0.45),
    (1.415, 0.45), (1.438, 0.438), (1.45, 0.415),
], [petrol])
world = scene.world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.19, 0.24, 0.29, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.5
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.012))
ground = bpy.context.object
ground.name = "STUDIO_ground"
ground.data.materials.append(material("STUDIO_slate", (0.15, 0.19, 0.22), 0, 0.65))
light("STUDIO_key", (3, 4, 6), 650, 5)
light("STUDIO_rim", (-3, -2, 4), 700, 4)
light("STUDIO_fill", (1, 4, 2), 150, 3)
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new("STUDIO_camera", data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_percentage = 100
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"
camera.location = (3, 4, 2.6)
aim(camera, (0, 0, 0.72))
data.type = "ORTHO"
data.ortho_scale = 2.0
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
for name, location, target, scale in [
    ("hero", (3, 4, 2.6), (0, 0, 0.72), 2.0),
    ("side", (4, 0, 0.75), (0, 0, 0.72), 1.9),
    ("cap_detail", (1.8, 2.5, 2.5), (0, 0, 1.29), 1.15),
]:
    camera.location = location
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.resolution_x = 1280
scene.render.resolution_y = 800
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
