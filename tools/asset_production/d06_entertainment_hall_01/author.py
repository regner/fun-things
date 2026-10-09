"""Author the original rounded Signal Row hall shell in pinned Blender."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_entertainment_hall_01"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
WIDTH, DEPTH, RADIUS = 26.0, 18.0, 6.0
WALL_HEIGHT, ROOF_HEIGHT = 8.0, 9.6
CORNER_STEPS = 16


def material(name, color, metallic=0.0, roughness=0.5):
    """Create an opaque, texture-free exported Principled material."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.diffuse_color = (*color, 1)
    result.use_backface_culling = True
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return result


def outline(inset=0.0, scale=1.0):
    """Return a counterclockwise rounded rectangle with fixed corner centres."""
    points = []
    for cx, cy, start in ((7, 3, 0), (-7, 3, 90), (-7, -3, 180), (7, -3, 270)):
        for step in range(CORNER_STEPS + 1):
            angle = math.radians(start + 90 * step / CORNER_STEPS)
            points.append(((cx + (RADIUS - inset) * math.cos(angle)) * scale,
                           (cy + (RADIUS - inset) * math.sin(angle)) * scale))
    return points


def finish(obj, name, mat=None, bevel=0.0):
    """Apply static transforms, clean topology, and retain editable source meshes."""
    obj.name = name
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if mat:
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
    for face in obj.data.polygons:
        face.use_smooth = True
    # Analytic roof normals must remain continuous; weighted normals are for fittings.
    if bevel:
        modifier = obj.modifiers.new("Weighted architectural normals", "WEIGHTED_NORMAL")
        modifier.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    parts.append(obj)
    return obj


def loft(name, rings, materials, band_slots):
    """Build a closed horizontal-profile solid; each band owns its material."""
    vertices = [(x, y, height) for height, inset, scale in rings
                for x, y in outline(inset, scale)]
    count = len(outline())
    faces = [tuple(reversed(range(count)))]
    slots = [band_slots[0]]
    for ring in range(len(rings) - 1):
        for index in range(count):
            a = ring * count + index
            b = ring * count + (index + 1) % count
            faces.append((a, b, b + count, a + count))
            slots.append(band_slots[ring])
    faces.append(tuple(range((len(rings) - 1) * count, len(rings) * count)))
    slots.append(band_slots[-1])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    for mat in materials:
        mesh.materials.append(mat)
    for face, slot in zip(mesh.polygons, slots):
        face.material_index = slot
    return finish(obj, name)


def box(name, position, size, mat, bevel=0.03, yaw=0.0):
    """Build a bevelled solid fitting without creating runtime geometry."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.dimensions = size
    obj.rotation_euler.z = yaw
    return finish(obj, name, mat, bevel)


def aim(obj, target):
    """Point a studio-only camera or light at a measured target."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def light(name, position, energy, size):
    """Add an isolated area light outside the export collection."""
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
petrol = material("hall_wall_petrol", (0.035, 0.105, 0.125), 0.12, 0.53)
roof = material("hall_roof_emerald", (0.027, 0.105, 0.091), 0.20, 0.43)
base = material("hall_base_slate", (0.13, 0.19, 0.21), 0.1, 0.6)
glass = material("hall_glazing_opaque", (0.012, 0.038, 0.057), 0.35, 0.27)
frame = material("hall_frame_teal", (0.09, 0.20, 0.22), 0.5, 0.38)
entry = material("hall_entry_plum", (0.13, 0.055, 0.105), 0.1, 0.5)

# Solid exterior: no hidden interior, traversable roof, animated or open doors.
loft("Ground shoe", [(0, .07, 1), (.08, 0, 1), (.32, 0, 1), (.44, .15, 1)],
     [base], [0, 0, 0])
loft("Rounded wall and clerestory",
     [(.32, .15, 1), (.55, .15, 1), (4.8, .15, 1), (4.88, .19, 1),
      (6.25, .19, 1), (6.33, .15, 1), (7.92, .15, 1), (8, .22, 1)],
     [petrol, glass, frame], [0, 0, 2, 1, 2, 0, 0])
# Shallow hipped dome: broad quiet centre and generous rolled shoulder, not roof clutter.
loft("Continuous shallow dome",
     [(7.91, .15, 1), (8.03, .15, 1), (8.28, .17, .985), (8.67, .17, .94),
      (9.03, .17, .87), (9.33, .17, .77), (9.53, .17, .63), (9.6, .17, .46)],
     [roof], [0] * 7)

# A sparse structural rhythm splits the dark upper ribbon into broad bays.
for x in (-6.6, -3.3, 0, 3.3, 6.6):
    for y in (-8.835, 8.835):
        box("Clerestory straight mullion", (x, y, 5.565), (.12, .09, 1.49), frame, .016)
for side in (-1, 1):
    box("Side clerestory mullion", (side * 12.835, 0, 5.565), (.09, .12, 1.49), frame, .016)
for cx, cy, start in ((7, 3, 0), (-7, 3, 90), (-7, -3, 180), (7, -3, 270)):
    for angle in (start + 30, start + 60):
        angle = math.radians(angle)
        point = (cx + 5.835 * math.cos(angle), cy + 5.835 * math.sin(angle), 5.565)
        box("Corner clerestory mullion", point, (.09, .12, 1.49), frame, .016, angle)

# Blank, closed entry assembly is part of the shell; cyan canopy is another record.
box("Plum entrance backing", (0, 8.875, 1.85), (8.8, .09, 3.5), entry, .04)
for x in (-3.1, -1.03, 1.03, 3.1):
    box("Closed entrance glazing", (x, 8.938, 1.69), (1.91, .034, 2.93), glass, .016)
    box("Entrance kick panel", (x, 8.965, .4), (1.89, .025, .32), frame, .008)
for x in (-4.18, -2.07, 0, 2.07, 4.18):
    box("Entrance vertical frame", (x, 8.955, 1.69), (.09, .085, 3.04), frame, .016)
box("Entrance head", (0, 8.953, 3.25), (8.5, .085, .14), frame, .02)
for x in (-.14, .14):
    box("Closed door pull", (x, 8.981, 1.48), (.035, .036, .56), base, .012)
# Large quiet blank wall panels beside the entry read as ordinary civic architecture.
for x in (-5.55, 5.55):
    box("Front blind panel", (x, 8.89, 2.1), (1.42, .075, 2.35), frame, .07)
    box("Front blind panel inset", (x, 8.936, 2.1), (1.18, .025, 2.1), petrol, .05)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh_object = bpy.context.object
mesh_object.name = "D06EntertainmentHall01_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D06EntertainmentHall01", None)
collection.objects.link(root)
mesh_object.parent = root
root["asset_id"] = "d06_entertainment_hall.01"
root["authorship"] = "Original Blender construction by commissioned production worker"
root["front_axis"] = "Blender +Y to Godot -Z; ground-centred origin"
root["ring_datum_godot_y_m"] = 7.2
root["canopy_datum_godot"] = [0.0, 3.6, -9.0]

# Studio-only geometry is never selected by the named-collection exporter.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.22, .27, .32, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .55
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.025))
bpy.context.object.name = "STUDIO_ground"
bpy.context.object.data.materials.append(material("STUDIO_ground_slate", (.14, .18, .21)))
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
scene.view_settings.view_transform = "AgX"
scene.render.resolution_x = 1280
scene.render.resolution_y = 800
camera.location = (32, 40, 29)
aim(camera, (0, 0, 3.5))
data.type = "ORTHO"
data.ortho_scale = 36
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(), "export.py", "exec"))
for name, position, target, scale in [
    ("hero", (32, 40, 29), (0, 0, 3.5), 36),
    ("side", (35, 0, 14), (0, 0, 4), 30),
    ("entry_detail", (13, 27, 10), (0, 8.7, 3), 15),
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
