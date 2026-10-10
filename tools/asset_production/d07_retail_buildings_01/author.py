"""Author the original Broadlot giant stepped retail shell with pinned Blender."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d07_retail_buildings_01"
NAME = "D07RetailBuildings01"
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


def material(name, color, metallic=0.1, roughness=0.5):
    """Create one opaque, back-culled flat-colour Principled surface."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


wall = material("retail_wall_slate", (.13, .19, .235))
plum = material("retail_wall_plum", (.14, .08, .14))
blue = material("retail_roof_blue", (.035, .12, .30), .18, .46)
petrol = material("retail_trim_petrol", (.028, .067, .092), .25, .47)
coral = material("retail_band_coral", (.88, .20, .12), .05, .48)
glass = material("retail_glazing_opaque", (.022, .065, .09), .32, .25)
frame = material("retail_frame_slate", (.24, .32, .36), .3, .42)


def box(name, center, dimensions, mat, bevel=.06):
    """Make a closed bevelled architectural part; apply transforms and corner normals."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Soft architectural edge", "BEVEL")
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
    obj.data.update()
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    modifier = obj.modifiers.new("Weighted architectural normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    parts.append(obj)
    return obj


def volume(name, x, y, width, depth, height, mat):
    """Use one shared wall, ground shoe, recessed blue roof and broad coping section."""
    box(name + " ground shoe", (x, y, .16), (width, depth, .32), petrol, .045)
    box(name + " wall", (x, y, (height - .36) / 2),
        (width - .24, depth - .24, height - .36), mat, .08)
    # The blue roof is recessed 0.26 m; no tiny equipment or tessellated roof noise.
    box(name + " blue roof", (x, y, height - .34),
        (width - .42, depth - .42, .16), blue, .05)
    for sign in (-1, 1):
        box(name + f" coping X {sign}", (x + sign * (width / 2 - .25), y, height - .16),
            (.5, depth, .32), blue, .06)
        box(name + f" coping Y {sign}", (x, y + sign * (depth / 2 - .25), height - .16),
            (width - 1, .5, .32), blue, .06)
    # Dark broad reveal below the coping keeps the roof/wall transition readable.
    for sign in (-1, 1):
        box(name + f" reveal X {sign}", (x + sign * (width / 2 - .09), y, height - .65),
            (.16, depth - .3, .23), petrol, .025)
        box(name + f" reveal Y {sign}", (x, y + sign * (depth / 2 - .09), height - .65),
            (width - .3, .16, .23), petrol, .025)


# Three solid blocks share the same section language but differ in plan and height.
# Front is Blender +Y, mapped by glTF to Godot -Z. Contact faces intentionally meet.
volume("High main sales hall", -8, -4, 48, 30, 9.6, wall)
volume("Plum side wing", 24, -7, 16, 24, 7.2, plum)
volume("Low front sales wing", -8, 15, 48, 8, 5.4, plum)
# Frontage: opaque inset glazing grouped in large bays, not individually lit windows.
# The central twelve metres remain blank for the separately produced entrance annex.
for x, width in [(-27, 7.2), (-18, 7.2), (-9, 4.8), (11, 7.2)]:
    box(f"Display backing {x}", (x, 18.865, 2.12), (width + .22, .11, 3.05), frame, .035)
    box(f"Opaque display {x}", (x, 18.935, 2.12), (width, .06, 2.8), glass, .025)
    box(f"Display broad transom {x}", (x, 18.974, 2.8), (width, .03, .095), frame, .01)
    box(f"Display centre mullion {x}", (x, 18.974, 2.12), (.12, .03, 2.8), frame, .01)
# Quiet vertical rhythms give human scale without making the roof look residential.
for y in (-15, -7, 1, 9):
    box(f"West wall pier {y}", (-31.925, y, 4.2), (.13, .38, 7.7), wall, .025)
for y in (-15, -7, 1):
    box(f"East wing pier {y}", (31.925, y, 3.05), (.13, .38, 5.6), plum, .025)
# Blank identity carrier is part of the architecture; graphics are a separate record.
box("Coral entrance band", (0, 18.91, 4.675), (20, .18, 1.05), coral, .045)
box("Coral top return", (0, 18.38, 5.32), (20, 1.24, .32), coral, .055)
# A broad high clerestory gives the stepped wall an ordinary retail reading.
box("High clerestory frame", (-8, 10.875, 7.4), (37, .12, 1.4), petrol, .04)
box("High clerestory glazing", (-8, 10.945, 7.4), (36.5, .06, 1.04), glass, .025)
for x in (-20, -8, 4):
    box(f"Clerestory mullion {x}", (x, 10.984, 7.4), (.18, .025, 1.08), frame, .01)

bpy.ops.object.select_all(action="DESELECT")
for part in parts:
    part.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = NAME + "_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new(NAME, None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "d07_retail_buildings.01"
root["authorship"] = "Original Blender construction by commissioned production worker"
root["front"] = "Blender +Y -> Godot -Z; ground datum zero"
root["annex_attachment_godot"] = [0.0, 0.0, -19.0]
root["annex_allowance"] = "12m width, <=6m projection, <=4.15m height; rear local Z=0"
root["provisional_dimensions"] = "64m width, 38m depth; roofs 9.6m/7.2m/5.4m"

# Isolated studio, excluded by the named export collection.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.19, .24, .32, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .6
bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, -.025))
ground = bpy.context.object
ground.name = "STUDIO_ground"
ground.data.materials.append(material("STUDIO_ground_slate", (.11, .15, .18), 0, .75))


def aim(obj, target):
    """Aim the studio object's local -Z at a fixed subject point."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


for name, location, energy, size in [
        ("key", (10, 25, 60), 80000, 45),
        ("fill", (-40, 10, 35), 45000, 40),
        ("rim", (20, -30, 45), 70000, 30)]:
    data = bpy.data.lights.new("STUDIO_" + name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    light = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(light)
    light.location = location
    aim(light, (0, 0, 0))
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new(data.name, data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.compression = 95
scene.render.dither_intensity = 0.0
scene.view_settings.view_transform = "AgX"
camera.location = (75, 90, 62)
aim(camera, (0, 0, 3))
data.type = "ORTHO"
data.ortho_scale = 88
bpy.context.preferences.filepaths.save_version = 0
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(), "export.py", "exec"))
for name, location, target, scale in [
        ("hero", (75, 90, 62), (0, 0, 3), 88),
        ("side", (90, 48, 28), (0, 0, 3), 78),
        ("frontage_detail", (23, 42, 18), (0, 15, 4), 36)]:
    camera.location = location
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)
# Actual scale necessarily crops this giant roof; centre on front edge/forecourt.
camera.location = (0, 19, 47)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
