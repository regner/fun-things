"""Original Terrace Ward upper-storey balcony insert; isolated pinned Blender construction only."""
import math
import runpy
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_09"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
# Provisional family interface in metres. +Y front in Blender, -Z in Godot.
BALCONY_WIDTH = 5.4
PROJECTION = 1.5
UNDERSIDE_HEIGHT = 3.2
DECK_THICKNESS = .18
GUARD_HEIGHT = 1.10
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


# The ground-level facade anchor intentionally carries a fully elevated visual.
# Keep the deck back at Y=0 for mounting to a closed facade; no door is cut into siblings.
half = BALCONY_WIDTH / 2
floor_top = UNDERSIDE_HEIGHT + DECK_THICKNESS
rail_top = floor_top + GUARD_HEIGHT
box("Bluegrey_deck", (-half, 0, UNDERSIDE_HEIGHT),
    (half, PROJECTION-.02, floor_top), wall, .025)
# Broad pale front nosing stays within the documented deck envelope.
box("Pale_front_nosing", (-half+.035, PROJECTION-.045, UNDERSIDE_HEIGHT+.035),
    (half-.035, PROJECTION, floor_top-.035), trim, .009)
# Three slim rails form a U; butt joins avoid overlapping coplanar corner tops.
box("Front_handrail", (-half+.04, PROJECTION-.17, rail_top-.09),
    (half-.04, PROJECTION-.03, rail_top), trim, .018)
for sign, label in ((-1, "Left"), (1, "Right")):
    x0, x1 = sorted((sign*(half-.17), sign*(half-.04)))
    box(label+"_handrail", (x0, 0, rail_top-.09),
        (x1, PROJECTION-.17, rail_top), trim, .014)
    # Quiet teal side screens contrast with the open front rail, not a closed loggia wall.
    box(label+"_side_screen", (x0+.025, .06, floor_top+.08),
        (x1-.025, PROJECTION-.20, rail_top-.17), teal, .012)
    for y in (.025, PROJECTION-.20):
        box(label+"_post", (x0, y, floor_top-.01),
            (x1, y+.09, rail_top-.085), trim, .01)
# Broad paired front infill panels preserve the 3 m domestic rhythm.
# Open space above each panel and a sparse picket rhythm keep this unmistakably a railing.
for left, right in ((-2.50, -.10), (.10, 2.50)):
    box("Front_teal_infill", (left, PROJECTION-.14, floor_top+.09),
        (right, PROJECTION-.07, floor_top+.72), teal, .015)
for centre in (-2.56, -1.50, 0, 1.50, 2.56):
    box("Front_guard_upright", (centre-.045, PROJECTION-.16, floor_top-.01),
        (centre+.045, PROJECTION-.05, rail_top-.085), trim, .01)

bpy.ops.object.select_all(action="DESELECT")
for part in parts:
    part.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
model = bpy.context.object
model.name = "D03ApartmentFamily09_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D03ApartmentFamily09", None)
collection.objects.link(root)
model.parent = root
root["asset_id"] = "d03_apartment_family.09"
root["provenance"] = "Original commissioned Blender construction; no external meshes or textures"
root["interface_m"] = "5.4 wide; 1.5 projection; underside 3.2 above ground facade anchor"
root["state"] = "Unreachable upper-storey balcony; visual-only; no interior, climbing or walk surface"
root["frontage_mount"] = "Place anchor at Godot (0,0,-6) relative to the base bay; never lower Y"

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
data.type, data.ortho_scale = "ORTHO", 8
camera.location = (8, 11, 8)
aim(camera, (0, .75, 3.8))
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
# Isolated inspection views: no context model is needed to inspect the underside/rail joins.
for name, location, target, scale in [
    ("side", (-8, -6, 6), (0, .75, 3.8), 8),
    ("railing_detail", (6, 8, 6), (1.65, 1.0, 3.95), 3.7),
]:
    camera.location = location
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / (name + ".png"))
    bpy.ops.render.render(write_still=True)
# Render-only linked sibling context, loaded AFTER saving/exporting this asset.
# No sibling geometry is copied into the delivered source or GLB.
sibling = ROOT / "art/source/models/environment/d03_apartment_family_05/d03_apartment_family_05.blend"
with bpy.data.libraries.load(str(sibling), link=True) as (available, loaded):
    loaded.collections = ["export_d03_apartment_family_05"]
for height in (0, 3.2):
    context = bpy.data.objects.new("STUDIO_linked_straight_bay", None)
    context.instance_type = "COLLECTION"
    context.instance_collection = loaded.collections[0]
    scene.collection.objects.link(context)
    context.location = (0, -6, height)
camera.location = (13, 17, 12)
aim(camera, (0, -4, 3.2))
data.ortho_scale = 24
scene.render.filepath = str(EVIDENCE / "hero.png")
bpy.ops.render.render(write_still=True)
camera.location = (0, -4, 47)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
