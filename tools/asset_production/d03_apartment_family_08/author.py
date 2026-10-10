"""Original Terrace Ward ground-floor entrance bay; isolated pinned Blender construction only."""
import math
import runpy
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_08"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
# Provisional family interface in metres. +Y front in Blender, -Z in Godot.
BAY_WIDTH = 6.0
BUILDING_DEPTH = 12.0
STOREY_HEIGHT = 3.2
assert bpy.app.version_string == "5.2.2 LTS", bpy.app.version_string
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
parts = []


def material(name, swatch, roughness, metallic=0):
    """Store opaque sRGB palette swatches as linear Principled base colors."""
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
warm = material("terrace_warm_entry", "E7B46E", .58)


def box(name, lo, hi, mat, bevel=0):
    """Author a closed solid, preserving exact bounds and flat connector faces."""
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


# No interiors: a single closed core gives deterministic seams and a matching solid collider.
# Deliberately no bevel at X +/-3 or Z 0/3.2: adjacent modules must meet without pinholes.
box("Closed_structural_core", (-BAY_WIDTH / 2, -BUILDING_DEPTH / 2, 0),
    (BAY_WIDTH / 2, BUILDING_DEPTH / 2, STOREY_HEIGHT), wall)


def facade_box(name, x0, x1, outward0, outward1, z0, z1, mat, side, bevel=.012):
    """Mirror frontage parts to the rear without negative object scales."""
    y0, y1 = sorted((side * (BUILDING_DEPTH / 2 + outward0),
                     side * (BUILDING_DEPTH / 2 + outward1)))
    return box(name, (x0, y0, z0), (x1, y1, z1), mat, bevel)


for side, label in ((-1, "Rear"),):
    # Square-ended floor ribbon is continuous when bays repeat; no per-bay end pilasters.
    facade_box(label + "_floor_ribbon", -3, 3, -.01, .10, .04, .20, trim, side, 0)
    for index, centre in enumerate((-1.5, 1.5)):
        name = f"{label}_window_{index + 1}"
        left, right = centre - 1.05, centre + 1.05
        # Teal apron and broad opaque two-pane glazing provide domestic rather than office rhythm.
        facade_box(name + "_teal_apron", left-.10, right+.10, -.008, .045,
                   .35, 1.01, teal, side)
        facade_box(name + "_frame_back", left-.10, right+.10, -.008, .095,
                   .90, 2.65, trim, side, .02)
        facade_box(name + "_closed_glass", left, right, .094, .105,
                   1.00, 2.55, glass, side, .009)
        facade_box(name + "_mullion", centre-.045, centre+.045, .103, .14,
                   1.00, 2.55, trim, side, .008)
        facade_box(name + "_sill", left-.15, right+.15, .005, .18,
                   .85, .97, trim, side, .015)
        facade_box(name + "_head", left-.15, right+.15, .015, .16,
                   2.61, 2.74, trim, side, .015)

# Front entry replaces, rather than overlays, the ordinary pair of domestic windows.
# Closed exterior: there is no threshold step, recess route, operable leaf or stair interior.
for left, right in ((-3, -2.25), (.45, 3)):
    facade_box("Front_floor_ribbon", left, right, -.01, .10, .04, .20, trim, 1, 0)
facade_box("Entry_warm_portal", -2.25, .45, -.008, .09, 0, 2.78, warm, 1, .018)
facade_box("Entry_pale_liner", -2.08, .28, .088, .105, 0, 2.57, trim, 1, .012)
for label, left, right in (("Left", -1.98, -.94), ("Right", -.86, .18)):
    facade_box(label + "_closed_door", left, right, .104, .116,
               .035, 2.30, glass, 1, .01)
    facade_box(label + "_kickplate", left+.055, right-.055, .114, .13,
               .10, .36, teal, 1, .01)
# Broad transom and paired small pulls are static facade cues, not interaction sockets.
facade_box("Entry_transom", -1.98, .18, .104, .116, 2.39, 2.49, glass, 1, .009)
for centre in (-1.10, -.70):
    facade_box("Entry_fixed_pull", centre-.028, centre+.028, .115, .175,
               .98, 1.38, warm, 1, .01)
facade_box("Entry_head_brow", -2.38, .58, .01, .18, 2.70, 2.88, warm, 1, .02)
# Tall stair-core facade strip: staggered landing bands distinguish it from apartment windows.
facade_box("Core_pale_surround", 1.12, 2.48, -.008, .095, .35, 3.02, trim, 1, .018)
facade_box("Core_closed_glass", 1.24, 2.36, .094, .108, .48, 2.90, glass, 1, .01)
for index, (height, left, right) in enumerate(((1.10, 1.24, 2.05), (1.91, 1.55, 2.36))):
    facade_box(f"Core_landing_band_{index}", left, right, .106, .145,
               height, height+.11, trim, 1, .01)
facade_box("Core_teal_base", 1.24, 2.36, .094, .108, .37, .48, teal, 1, .009)

bpy.ops.object.select_all(action="DESELECT")
for part in parts:
    part.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
model = bpy.context.object
model.name = "D03ApartmentFamily08_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D03ApartmentFamily08", None)
collection.objects.link(root)
model.parent = root
root["asset_id"] = "d03_apartment_family.08"
root["provenance"] = "Original commissioned Blender construction; no external meshes or textures"
root["interface_m"] = "width 6; depth 12; storey 3.2; ground-centred; Blender +Y front"
root["state"] = "Closed ground entrance and exterior stair-core treatment; no interior or stair gameplay"
root["frontage_mount"] = "Godot front/rear walls Z=-6/+6; max trim Z=-6.18/+6.18"

# Studio is excluded from the named export collection.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.24, .29, .37, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .65
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.025))
ground = bpy.context.object
ground.name = "STUDIO_ground"
ground.data.materials.append(material("STUDIO_slate", "667783", .8))
bpy.ops.mesh.primitive_cube_add(size=1, location=(9, 0, .5))
reference = bpy.context.object
reference.name = "STUDIO_one_metre_reference"
reference.hide_render = True


def aim(obj, target):
    """Aim studio objects without changing asset transforms."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


for name, location, power, size in [("key", (-8, 12, 17), 4200, 10),
                                   ("fill", (10, 7, 10), 2400, 8),
                                   ("rim", (-4, -11, 15), 3800, 9)]:
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
# Avoid film dithering noise in the lean, flat-color PNG evidence.
scene.render.dither_intensity = 0
scene.view_settings.view_transform = "AgX"
data.type, data.ortho_scale = "ORTHO", 20
camera.location = (14, 22, 13)
aim(camera, (0, 0, 1.6))
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
for name, location, target, scale in [
    ("hero", (14, 22, 13), (0, 0, 1.6), 20),
    ("side", (-15, -22, 11), (0, 0, 1.6), 20),
    ("entrance_detail", (4, 19, 5), (0, 6, 1.55), 7.5),
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
