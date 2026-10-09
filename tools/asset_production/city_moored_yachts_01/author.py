"""Construct the original compact Old Quay motor yacht in pinned Blender only."""
import math
from pathlib import Path
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "city_moored_yachts_01"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
parts = []


def material(name, rgb, metal=0.0, roughness=0.45):
    """Create an opaque, exportable flat-color Principled material."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = roughness
    mat.diffuse_color = (*rgb, 1)
    return mat


ivory = material("hull_ivory", (0.88, 0.87, 0.77), 0.08, 0.31)
petrol = material("glazing_petrol", (0.018, 0.066, 0.081), 0.3, 0.23)
navy = material("waterline_navy", (0.025, 0.045, 0.063), 0.05, 0.45)
deck = material("deck_sand", (0.38, 0.28, 0.17), 0.0, 0.65)
metal = material("hardware_slate", (0.39, 0.47, 0.49), 0.65, 0.3)
cushion = material("upholstery_cream", (0.70, 0.67, 0.54), 0.0, 0.72)
coral = material("accent_coral", (0.90, 0.19, 0.12), 0.0, 0.6)


def finish(obj, name, mat, bevel=0.0):
    """Bake bevels and clean topology before applying stable weighted normals."""
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Soft moulded edges", "BEVEL")
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
    modifier = obj.modifiers.new("Weighted surface normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    parts.append(obj)
    return obj


def mesh_part(name, vertices, faces, mat, bevel=0.0):
    """Make one closed authored mesh component from explicit section geometry."""
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    return finish(obj, name, mat, bevel)


def loft(name, rings, mat, bevel=0.0):
    """Bridge corresponding closed rings, with closed end caps."""
    count = len(rings[0])
    vertices = [v for ring in rings for v in ring]
    faces = [tuple(reversed(range(count)))]
    for row in range(len(rings) - 1):
        for index in range(count):
            a = row * count + index
            b = row * count + (index + 1) % count
            faces.append((a, b, b + count, a + count))
    faces.append(tuple(range((len(rings) - 1) * count, len(rings) * count)))
    return mesh_part(name, vertices, faces, mat, bevel)


def box(name, location, dimensions, mat, bevel=0.025):
    """Author a restrained rounded solid, never a runtime render primitive."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    return finish(obj, name, mat, bevel)


def tube(name, points, radius, mat, sides=10):
    """Sweep closed round sections along sparse rail or hardware control points."""
    rings = []
    for index, point in enumerate(points):
        previous = Vector(points[max(0, index - 1)])
        following = Vector(points[min(len(points) - 1, index + 1)])
        tangent = (following - previous).normalized()
        reference = Vector((0, 0, 1)) if abs(tangent.z) < 0.95 else Vector((1, 0, 0))
        across = tangent.cross(reference).normalized()
        other = tangent.cross(across).normalized()
        rings.append([
            tuple(Vector(point) + radius * (
                math.cos(i * math.tau / sides) * across
                + math.sin(i * math.tau / sides) * other
            )) for i in range(sides)
        ])
    return loft(name, rings, mat)


# Lengthwise sections: aft transom to rounded pointed bow. Keel has a true V,
# broad topsides and restrained rising sheer rather than a scaled ellipsoid.
STATIONS = [
    (-5.50, 1.43, 0.84, -0.65), (-5.10, 1.57, 0.86, -0.83),
    (-4.00, 1.70, 0.88, -0.96), (-2.00, 1.75, 0.92, -1.00),
    (0.00, 1.73, 0.98, -0.98), (1.80, 1.55, 1.06, -0.85),
    (3.30, 1.22, 1.14, -0.65), (4.50, 0.82, 1.22, -0.36),
    (5.50, 0.34, 1.29, -0.03), (6.05, 0.10, 1.33, 0.33),
    (6.20, 0.025, 1.34, 0.57),
]
rings = []
for y, width, top, bottom in STATIONS:
    rings.append([
        (-width, y, top), (-width, y, top - 0.16),
        (-width * 0.89, y, max(bottom + 0.22, -0.08)),
        (-width * 0.53, y, bottom + 0.14), (0, y, bottom),
        (width * 0.53, y, bottom + 0.14),
        (width * 0.89, y, max(bottom + 0.22, -0.08)),
        (width, y, top - 0.16), (width, y, top),
    ])
hull = loft("Sculpted V hull", rings, ivory)
hull.data.materials.append(navy)
# A navy submerged bottom keeps the exposed ivory topsides quiet.
for face in hull.data.polygons:
    if face.center.z < -0.18:
        face.material_index = 1
# A closed thin toe cap follows the actual sheer along both sides.
loft("Ivory sheer cap", [
    [(-w * 1.015, y, z - 0.02), (w * 1.015, y, z - 0.02),
     (w * 1.015, y, z + 0.09), (-w * 1.015, y, z + 0.09)]
    for y, w, z, _ in STATIONS
], ivory)
# Dark rub strake below the cap, deliberately no pinstriped hull graphics.
for side in (-1, 1):
    tube("Continuous rub strake", [(side * w * 1.008, y, z - 0.15)
         for y, w, z, _ in STATIONS], 0.027, navy)

# Foredeck is an inset shaped slab following the bow, not dense planking.
fore = [(-1.32, 1.75, 1.115), (-1.04, 3.25, 1.20), (-0.66, 4.50, 1.28),
        (-0.22, 5.53, 1.35), (0, 5.85, 1.37), (0.22, 5.53, 1.35),
        (0.66, 4.50, 1.28), (1.04, 3.25, 1.20), (1.32, 1.75, 1.115)]
loft("Sand foredeck inlay", [[(x, y, z + dz) for x, y, z in fore]
                            for dz in (0.045, 0.095)], deck)
box("Aft cockpit inlay", (0, -3.83, 0.97), (2.73, 2.64, 0.09), deck, 0.12)
box("Swim platform rim", (0, -5.68, 0.44), (2.72, 1.04, 0.20), ivory, 0.10)
box("Swim platform inset", (0, -5.70, 0.553), (2.45, 0.82, 0.05), deck, 0.08)
box("Transom step", (0, -5.17, 0.69), (0.90, 0.60, 0.21), ivory, 0.05)

# Tiered low cabin: dark uninterrupted glazing under a broad ivory cap.
base_plan = [(-1.30, -2.53), (-1.32, 0.75), (-1.15, 2.14),
             (1.15, 2.14), (1.32, 0.75), (1.30, -2.53)]
glass_lower = [(-1.27, -2.40), (-1.29, 0.65), (-1.08, 1.85),
               (1.08, 1.85), (1.29, 0.65), (1.27, -2.40)]
glass_upper = [(-1.04, -2.16), (-1.06, 0.38), (-0.94, 0.91),
               (0.94, 0.91), (1.06, 0.38), (1.04, -2.16)]
loft("Cabin coaming", [[(x, y, 1.02) for x, y in base_plan],
                       [(x, y, 1.60) for x, y in glass_lower]], ivory, 0.065)
loft("Wraparound dark glazing", [[(x, y, 1.61) for x, y in glass_lower],
                                 [(x, y, 2.40) for x, y in glass_upper]], petrol, 0.045)
roof = [(x * 1.13, y, z) for x, y, z in [(x, y, 2.42) for x, y in glass_upper]]
loft("Low ivory cabin roof", [[(x, y, z + dz) for x, y, z in roof]
                              for dz in (0, 0.20)], ivory, 0.085)
# Narrow pillars divide the rear/side panes, leaving the broad windshield legible.
for side in (-1, 1):
    tube("Aft cabin pillar", [(side * 1.26, -2.38, 1.56),
                              (side * 1.04, -2.16, 2.45)], 0.065, ivory)
    tube("Side glazing pillar", [(side * 1.28, -0.65, 1.58),
                                  (side * 1.055, -0.70, 2.44)], 0.047, ivory)
# Roof hatch and low radar/antenna: no towering flybridge to compete with sailboat.
box("Roof hatch gasket", (0, -0.30, 2.635), (0.95, 1.17, 0.035), navy, 0.12)
box("Roof hatch", (0, -0.30, 2.662), (0.79, 1.01, 0.035), petrol, 0.10)
box("Antenna pedestal", (0, -1.52, 2.74), (0.35, 0.42, 0.25), ivory, 0.07)
box("Low radar bar", (0, -1.52, 2.90), (1.12, 0.30, 0.18), ivory, 0.085)
tube("Low aerial", [(0.32, -1.50, 2.90), (0.32, -1.50, 3.10)], 0.022, metal)

# Broad sun pads and a modest open aft lounge establish leisure-boat identity.
for side in (-1, 1):
    pad = box("Foredeck sun cushion", (side * 0.43, 3.12, 1.38),
              (0.80, 1.76, 0.22), cushion, 0.10)
    pad.rotation_euler.x = math.radians(3)
    bpy.context.view_layer.objects.active = pad
    pad.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    pad.select_set(False)
    box("Cockpit bench base", (side * 1.04, -3.73, 1.14), (0.55, 1.97, 0.40), ivory, 0.10)
    box("Cockpit seat", (side * 1.04, -3.73, 1.40), (0.56, 1.94, 0.18), cushion, 0.08)
    box("Cockpit backrest", (side * 1.32, -3.74, 1.56), (0.21, 2.04, 0.50), ivory, 0.09)
box("Coral lounge cushion", (1.06, -4.21, 1.54), (0.44, 0.55, 0.15), coral, 0.06)
# Hull-side glazed ports, elongated and widely spaced; no noisy porthole rows.
for side in (-1, 1):
    for y, x in [(-2.10, 1.75), (0.15, 1.70)]:
        box("Hull side port", (side * x, y, 0.42), (0.035, 1.03, 0.22), petrol, 0.07)

# Sparse fore rails; no fine rigging canopy. Cleats are integrated boat fittings.
rail_stations = [(0.85, 1.60, 1.02), (2.75, 1.27, 1.11),
                 (4.20, 0.86, 1.20), (5.55, 0.25, 1.29)]
for side in (-1, 1):
    rail = [(side * width, y, z + 0.68) for y, width, z in rail_stations]
    tube("Bow rail", rail + [(0, 5.82, 1.99)], 0.032, metal)
    for y, width, z in rail_stations:
        tube("Rail stanchion", [(side * width, y, z + 0.01),
                                 (side * width, y, z + 0.68)], 0.026, metal)
    for y, x, z in [(-4.50, 1.49, 0.97), (3.92, 0.85, 1.25)]:
        box("Cleat foot", (side * x, y, z), (0.17, 0.29, 0.055), metal, 0.02)
        tube("Cleat stem", [(side * x, y, z), (side * x, y, z + 0.14)], 0.035, metal)
        tube("Cleat crossbar", [(side * x, y - 0.20, z + 0.14),
                                 (side * x, y + 0.20, z + 0.14)], 0.042, metal)
    for y, x in [(-3.20, 1.74), (-0.65, 1.72)]:
        box("Moored fender", (side * x, y, 0.42), (0.32, 0.32, 0.86), cushion, 0.15)
        tube("Fender tie", [(side * x, y, 0.76), (side * (x - 0.03), y, 1.00)],
             0.020, navy, 8)

# One static mesh / seven material surfaces; disconnected closed parts intentionally
# overlap at manufactured joins. Root is waterline, not the bottom of the keel.
bpy.ops.object.select_all(action="DESELECT")
for part in parts:
    part.select_set(True)
bpy.context.view_layer.objects.active = hull
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "CityMooredYachts01_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityMooredYachts01", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "city_moored_yachts.01"
root["datum"] = "Waterline centre at Z=0; bow Blender +Y / Godot -Z"
root["authorship"] = "Original commissioned Blender construction; no external geometry"
root["role"] = "Static moored scenery; no boarding, interior or vehicle simulation"

# Isolated presentation only; studio geometry never belongs to the export collection.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.22, 0.29, 0.34, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.55
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -1.025))
ground = bpy.context.object
ground.name = "STUDIO_slate"
ground.data.materials.append(material("STUDIO_slate", (0.065, 0.13, 0.15), 0, 0.65))


def aim(obj, target):
    """Orient a studio camera or light without altering any export transform."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


for name, position, power, size in [
    ("key", (7, 3, 13), 2700, 9), ("rim", (-6, -5, 9), 2200, 7),
    ("fill", (0, 10, 7), 1300, 8),
]:
    data = bpy.data.lights.new("STUDIO_" + name, "AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    light = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(light)
    light.location = position
    aim(light, (0, 0, 0.7))
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new(data.name, data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_percentage = 100
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.compression = 95
# Disable output dithering so large quiet studio gradients compress as lean evidence.
scene.render.dither_intensity = 0
scene.view_settings.view_transform = "AgX"
camera.location = (14, 17, 12)
aim(camera, (0, 0, 0.8))
data.type = "ORTHO"
data.ortho_scale = 16.0
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
for name, position, target, scale in [
    ("hero", (14, 17, 12), (0, 0, 0.8), 16.0),
    ("side", (16, 0, 4.4), (0, 0, 0.8), 14.3),
    ("detail", (8, -12, 10), (0, -2.85, 1.45), 8.8),
]:
    camera.location = position
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.resolution_x = 1024 if name == "detail" else 1280
    scene.render.resolution_y = 576 if name == "detail" else 720
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)
# The lean-evidence cap supersedes historical 1280x800: keep the same vertical FOV
# and height at 1280x720, with a vertical-down, north-up view of the static waterline.
ground.location.z = -0.015
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
