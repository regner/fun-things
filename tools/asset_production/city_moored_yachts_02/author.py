"""Construct the original small Old Quay sailing yacht in pinned Blender only."""
import math
from pathlib import Path
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "city_moored_yachts_02"
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
cushion = material("sail_canvas", (0.70, 0.67, 0.54), 0.0, 0.72)
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


# Narrow sailing hull with a raked transom and rising, pointed forefoot.
# Cross-section rings keep every component closed, including the submerged keel.
STATIONS = [
    (-5.80, 0.88, 0.73, -0.15), (-5.40, 1.14, 0.73, -0.35),
    (-4.40, 1.36, 0.74, -0.56), (-2.50, 1.53, 0.77, -0.70),
    (-0.60, 1.55, 0.82, -0.76), (1.30, 1.43, 0.87, -0.72),
    (2.90, 1.13, 0.94, -0.55), (4.20, 0.71, 1.02, -0.26),
    (5.25, 0.26, 1.09, 0.12), (5.80, 0.025, 1.13, 0.50),
]
rings = []
for y, width, top, bottom in STATIONS:
    rings.append([
        (-width, y, top), (-width, y, top - 0.14),
        (-width * 0.85, y, max(bottom + 0.18, -0.06)),
        (-width * 0.45, y, bottom + 0.10), (0, y, bottom),
        (width * 0.45, y, bottom + 0.10),
        (width * 0.85, y, max(bottom + 0.18, -0.06)),
        (width, y, top - 0.14), (width, y, top),
    ])
hull = loft("Slender sailing hull", rings, ivory)
hull.data.materials.append(navy)
for face in hull.data.polygons:
    if face.center.z < -0.12:
        face.material_index = 1
loft("Ivory sheer rim", [
    [(-w * 1.012, y, z - 0.015), (w * 1.012, y, z - 0.015),
     (w * 1.012, y, z + 0.055), (-w * 1.012, y, z + 0.055)]
    for y, w, z, _ in STATIONS
], ivory)
for side in (-1, 1):
    tube("Quiet navy rub strake", [(side * w * 1.008, y, z - 0.12)
         for y, w, z, _ in STATIONS], 0.025, navy)
# Fin keel and separate rudder are static submerged silhouette, not boat physics.
loft("Fin keel", [
    [(-0.19, -1.5, -0.55), (0.19, -1.5, -0.55),
     (0.19, 0.95, -0.55), (-0.19, 0.95, -0.55)],
    [(-0.12, -1.90, -1.60), (0.12, -1.90, -1.60),
     (0.12, -0.20, -1.60), (-0.12, -0.20, -1.60)],
], navy, 0.05)
loft("Rudder blade", [
    [(-0.075, -5.15, -0.05), (0.075, -5.15, -0.05),
     (0.075, -4.53, -0.05), (-0.075, -4.53, -0.05)],
    [(-0.055, -5.28, -1.18), (0.055, -5.28, -1.18),
     (0.055, -4.72, -1.18), (-0.055, -4.72, -1.18)],
], navy, 0.035)
# Broad inlays remain quiet at distance; no dense planking or painted graphics.
fore = [(-1.12, 1.55, 0.975), (-0.90, 2.90, 1.055), (-0.49, 4.20, 1.135),
        (0, 5.22, 1.205), (0.49, 4.20, 1.135), (0.90, 2.90, 1.055),
        (1.12, 1.55, 0.975)]
loft("Sand foredeck", [[(x, y, z + dz) for x, y, z in fore] for dz in (0, 0.045)], deck)
box("Cockpit floor inlay", (0, -3.72, 0.82), (2.00, 2.88, 0.08), deck, 0.12)
for side in (-1, 1):
    box("Cockpit coaming", (side * 1.07, -3.61, 1.035), (0.32, 2.78, 0.49), ivory, 0.09)
    box("Bench cushion", (side * 0.94, -3.54, 1.245), (0.50, 2.23, 0.13), cushion, 0.06)
box("Coral aft cushion", (0.94, -4.20, 1.34), (0.43, 0.46, 0.11), coral, 0.045)
box("Aft locker top", (0, -5.02, 0.91), (1.65, 0.44, 0.17), ivory, 0.065)
# Lower than .01: only a low coachroof and broad side ports, no motor-yacht cabin.
lower_plan = [(-1.03, -2.14), (-1.03, 0.9), (-0.72, 2.13),
              (0.72, 2.13), (1.03, 0.9), (1.03, -2.14)]
upper_plan = [(-0.82, -2.03), (-0.82, 0.8), (-0.61, 1.68),
              (0.61, 1.68), (0.82, 0.8), (0.82, -2.03)]
loft("Low coachroof", [[(x, y, 0.87) for x, y in lower_plan],
                        [(x, y, 1.55) for x, y in upper_plan]], ivory, 0.065)
# Solid sloped glazing panels sit flush to the tapered coachroof sides.
for side in (-1, 1):
    loft("Coachroof side glazing", [
        [(side * x, y, z) for x, y, z in [
            (0.95 + d, -1.57, 1.17), (0.95 + d, 0.52, 1.17),
            (0.855 + d, 0.43, 1.48), (0.855 + d, -1.51, 1.48)]]
        for d in (0.0, 0.025)
    ], petrol, 0.025)
box("Companionway recess", (0, -2.125, 1.25), (0.72, 0.05, 0.47), petrol, 0.055)
box("Sliding companionway hatch", (0, -1.60, 1.59), (0.85, 0.92, 0.09), ivory, 0.06)
box("Forward hatch rim", (0, 2.71, 1.10), (0.77, 0.88, 0.09), navy, 0.08)
box("Forward hatch glazing", (0, 2.71, 1.16), (0.63, 0.73, 0.05), petrol, 0.055)
# The tiller reads as one substantial handle rather than a wheel/helm superstructure.
tube("Rudder stock", [(0, -4.87, 0.91), (0, -4.87, 1.25)], 0.055, metal)
tube("Wooden tiller", [(0, -4.87, 1.25), (0.10, -3.58, 1.30)], 0.052, deck)
for side in (-1, 1):
    tube("Winch pedestal", [(side * 1.0, -2.46, 1.23),
                              (side * 1.0, -2.46, 1.42)], 0.105, metal, 12)
    tube("Winch crown", [(side * 1.0, -2.46, 1.39),
                          (side * 1.0, -2.46, 1.46)], 0.125, navy, 12)

# Single tapering spar, one spreader and only four stays. No running-rigging web.
MAST_Y = 0.63
loft("Tapered single mast", [
    [(radius * math.cos(i * math.tau / 12), MAST_Y + radius * math.sin(i * math.tau / 12), z)
     for i in range(12)] for z, radius in [(1.45, 0.115), (5.8, 0.095), (10.0, 0.060)]
], metal)
box("Mast step collar", (0, MAST_Y, 1.61), (0.35, 0.38, 0.18), navy, 0.045)
tube("Boom", [(0, 0.53, 2.15), (0, -3.50, 2.15)], 0.078, metal, 12)
tube("Single spreader", [(-1.16, MAST_Y, 5.75), (1.16, MAST_Y, 5.75)], 0.044, metal)
# Folded sail is a compact scalloped bundle above the boom, never a deployed triangle.
# A flattened, asymmetrical oval cross-section makes broad cloth folds, not rope noise.
loft("Furled mainsail canvas", [
    [(width * math.cos(i * math.tau / 12), y,
      2.35 + height * math.sin(i * math.tau / 12)) for i in range(12)]
    for y, width, height in [(0.42, 0.17, 0.16), (0.08, 0.27, 0.24),
                             (-0.60, 0.25, 0.20), (-1.22, 0.29, 0.23),
                             (-1.84, 0.24, 0.19), (-2.49, 0.26, 0.20),
                             (-3.02, 0.22, 0.16), (-3.43, 0.13, 0.12)]
], cushion)
for y, w, h in [(-0.60, 0.255, 0.205), (-1.84, 0.245, 0.195), (-3.02, 0.225, 0.165)]:
    loft("Broad sail tie", [
        [(w * math.cos(i * math.tau / 12), y + dy,
          2.35 + h * math.sin(i * math.tau / 12)) for i in range(12)]
        for dy in (-0.045, 0.045)
    ], navy)
tube("Forestay", [(0, 5.39, 1.20), (0, MAST_Y, 9.72)], 0.022, metal, 8)
tube("Backstay", [(0, -5.24, 1.13), (0, MAST_Y, 9.72)], 0.022, metal, 8)
for side in (-1, 1):
    tube("Single side shroud", [(side * 1.41, 0.33, 0.94),
                                (side * 1.16, MAST_Y, 5.75),
                                (0, MAST_Y, 9.72)], 0.022, metal, 8)
    # Short pulpit and stern pushpit only; continuous lifelines would clutter the plan.
    tube("Bow pulpit", [(side * 0.76, 3.50, 1.63),
                         (side * 0.38, 4.65, 1.71), (0, 5.42, 1.78)], 0.030, metal)
    for x, y, z in [(0.76, 3.50, 1.04), (0.38, 4.65, 1.11)]:
        tube("Pulpit foot", [(side * x, y, z), (side * x, y, z + 0.59)], 0.025, metal)
    tube("Stern pushpit", [(side * 1.06, -4.67, 1.37),
                           (side * 0.85, -5.28, 1.37), (side * 0.37, -5.32, 1.37)],
         0.030, metal)
    for x, y in [(1.06, -4.67), (0.37, -5.32)]:
        tube("Pushpit foot", [(side * x, y, 0.83), (side * x, y, 1.37)], 0.025, metal)
    for y, x, z in [(-4.80, 1.02, 0.90), (4.12, 0.55, 1.14)]:
        box("Cleat foot", (side * x, y, z), (0.14, 0.22, 0.05), metal, 0.018)
        tube("Cleat stem", [(side * x, y, z), (side * x, y, z + 0.10)], 0.032, metal)
        tube("Cleat horn", [(side * x, y - 0.16, z + 0.10),
                             (side * x, y + 0.16, z + 0.10)], 0.035, metal)
    for y, x in [(-2.05, 1.54), (0.1, 1.51)]:
        box("Moored fender", (side * x, y, 0.37), (0.32, 0.32, 0.78), cushion, 0.15)
        tube("Fender tie", [(side * x, y, 0.72), (side * (x - 0.04), y, 0.97)],
             0.019, navy, 8)

# One static mesh / seven material surfaces; disconnected closed parts intentionally
# overlap at manufactured joins. Root is waterline, not the bottom of the keel.
bpy.ops.object.select_all(action="DESELECT")
for part in parts:
    part.select_set(True)
bpy.context.view_layer.objects.active = hull
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "CityMooredYachts02_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityMooredYachts02", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "city_moored_yachts.02"
root["datum"] = "Waterline centre at Z=0; bow Blender +Y / Godot -Z"
root["authorship"] = "Original commissioned Blender construction; no external geometry"
root["role"] = "Static moored scenery; no boarding, interior or vehicle simulation"

# Isolated presentation only; studio geometry never belongs to the export collection.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.22, 0.29, 0.34, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.55
bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, -1.625))
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
camera.location = (16, 20, 15)
aim(camera, (0, 0, 4.0))
data.type = "ORTHO"
data.ortho_scale = 23.0
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
for name, position, target, scale in [
    ("hero", (16, 20, 15), (0, 0, 4.0), 23.0),
    ("side", (18, 0, 5.7), (0, 0, 4.0), 23.0),
    ("detail", (8, -12, 9), (0, -1.35, 1.7), 11.0),
]:
    camera.location = position
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
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
