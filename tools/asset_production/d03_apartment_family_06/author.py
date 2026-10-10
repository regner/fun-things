"""Original inside/outside Terrace Ward elbows; compatible with the delivered straight bay."""
import math
import runpy
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_06"
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


wall = material("terrace_bluegrey_render", "829398", .76)
trim = material("terrace_pale_frame", "C5CABF", .53)
teal = material("terrace_teal_spandrel", "31656A", .65)
glass = material("terrace_petrol_closed_glass", "1E3645", .29, .12)
coral = material("terrace_coral_corner", "FF725D", .62)


def box(name, lo, hi, mat, bevel=0):
    """Author closed facade trim with applied soft edges, using the sibling's recipe."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object
    obj.name = name
    obj.location = [(a + b) / 2 for a, b in zip(lo, hi)]
    obj.dimensions = [b - a for a, b in zip(lo, hi)]
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Soft facade edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
        bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(obj.data)
        bm.free()
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
        modifier = obj.modifiers.new("Broad plane normals", "WEIGHTED_NORMAL")
        modifier.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    parts.append(obj)
    return obj


def prism(name, footprint, bottom, top, mat):
    """Extrude a documented Godot X/Z footprint as a watertight Blender solid."""
    count = len(footprint)
    verts = [(x, -z, y) for y in (bottom, top) for x, z in footprint]
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    faces.extend((i, (i + 1) % count, (i + 1) % count + count, i + count)
                 for i in range(count))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(mat)
    parts.append(obj)
    return obj


def face_box(name, a0, a1, d0, d1, y0, y1, mat, axis, plane, direction, bevel=.012):
    """Place trim outward from an X or Z wall, converting Godot coordinates once."""
    low, high = sorted((plane + direction * d0, plane + direction * d1))
    if axis == "z":
        return box(name, (a0, -high, y0), (a1, -low, y1), mat, bevel)
    return box(name, (low, -a1, y0), (high, -a0, y1), mat, bevel)


def windows(label, centres, axis, plane, direction, accent_centre):
    """Preserve the sibling's glazing, frame, sill and height datums on exposed returns."""
    for index, centre in enumerate(centres):
        name = f"{label}_window_{index + 1}"
        left, right = centre - 1.05, centre + 1.05
        apron = coral if centre == accent_centre else teal
        face_box(name + "_apron", left-.10, right+.10, -.008, .045,
                 .35, 1.01, apron, axis, plane, direction)
        face_box(name + "_frame", left-.10, right+.10, -.008, .095,
                 .90, 2.65, trim, axis, plane, direction, .02)
        face_box(name + "_glass", left, right, .094, .105,
                 1.00, 2.55, glass, axis, plane, direction, .009)
        face_box(name + "_mullion", centre-.045, centre+.045, .103, .14,
                 1.00, 2.55, trim, axis, plane, direction, .008)
        face_box(name + "_sill", left-.15, right+.15, .005, .18,
                 .85, .97, trim, axis, plane, direction, .015)
        face_box(name + "_head", left-.15, right+.15, .015, .16,
                 2.61, 2.74, trim, axis, plane, direction, .015)


roots = {}
for variant in ("outside", "inside"):
    collection = bpy.data.collections.new(f"export_{NID}_{variant}")
    scene.collection.children.link(collection)
    parts = []
    edge = 6 if variant == "outside" else 9
    footprint = ([(-6, -6), (6, -6), (6, 6), (-6, 6)] if variant == "outside"
                 else [(-9, -9), (9, -9), (9, 3), (3, 3), (3, 9), (-9, 9)])
    prism("Closed_corner_core", footprint, 0, STOREY_HEIGHT, wall)
    # One bent ribbon avoids coplanar overlaps at the exposed arris.
    prism("Outer_floor_ribbon", [(-edge-.1, -edge-.1), (edge, -edge-.1),
          (edge, -edge+.01), (-edge+.01, -edge+.01),
          (-edge+.01, edge), (-edge-.1, edge)], .04, .20, trim)
    prism("Outer_coral_arris", [(-edge-.06, -edge-.06), (-edge+.24, -edge-.06),
          (-edge+.24, -edge+.005), (-edge+.005, -edge+.005),
          (-edge+.005, -edge+.24), (-edge-.06, -edge+.24)], .24, 3.12, coral)
    centres = [-edge + 1.5 + 3 * i for i in range(int(edge * 2 / 3))]
    for axis in ("z", "x"):
        windows("Outer_" + axis, centres, axis, -edge, -1, centres[0])
    if variant == "inside":
        prism("Court_floor_ribbon", [(2.99, 2.99), (9, 2.99), (9, 3.1),
              (3.1, 3.1), (3.1, 9), (2.99, 9)], .04, .20, trim)
        prism("Court_coral_arris", [(2.995, 2.995), (3.24, 2.995), (3.24, 3.06),
              (3.06, 3.06), (3.06, 3.24), (2.995, 3.24)], .24, 3.12, coral)
        for axis in ("z", "x"):
            windows("Court_" + axis, [4.5, 7.5], axis, 3, 1, 4.5)
    bpy.ops.object.select_all(action="DESELECT")
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    model = bpy.context.object
    name = "D03ApartmentFamily06" + variant.title()
    model.name = name + "_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    old_slots = list(model.data.materials)
    ordered = [wall, trim, teal, glass, coral]
    indices = [ordered.index(old_slots[face.material_index]) for face in model.data.polygons]
    model.data.materials.clear()
    for mat in ordered:
        model.data.materials.append(mat)
    for face, index in zip(model.data.polygons, indices):
        face.material_index = index
    root = bpy.data.objects.new(name, None)
    collection.objects.link(root)
    model.parent = root
    root["asset_id"] = "d03_apartment_family.06"
    root["provenance"] = "Original Blender construction; no external geometry or textures"
    root["interface"] = "6m bay pitch; 12m run depth; 3.2m stack; ground/AABB-centred pivot"
    root["state"] = "Closed exterior, top mating plane; no roof or interior gameplay"
    roots[variant] = root

# Studio is excluded from both named export collections.
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
data.type, data.ortho_scale = "ORTHO", 46
camera.location = (-30, 42, 30)
aim(camera, (0, 0, 1.6))
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
# Presentation offsets apply only AFTER saving/exporting the identity-transform source.
roots["outside"].location.x = -11
roots["inside"].location.x = 8
for name, location, target, scale in [
    ("hero", (-30, 42, 30), (0, 0, 1.6), 46),
    ("side", (34, -44, 34), (0, 0, 1.6), 46),
    ("corner_detail", (21, -16, 10), (12.5, -4.5, 1.6), 12),
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
