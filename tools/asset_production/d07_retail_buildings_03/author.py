"""Author the original Broadlot attached entrance annex with pinned Blender."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d07_retail_buildings_03"
NAME = "D07RetailBuildings03"
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
        box(name + f" coping Y {sign}",
            (x, y + sign * (depth / 2 - .25) - (.06 if sign == 1 else 0), height - .16),
            (width - 1, .5, .32), blue, .06)
    # Dark broad reveal below the coping keeps the roof/wall transition readable.
    for sign in (-1, 1):
        box(name + f" reveal X {sign}", (x + sign * (width / 2 - .09), y, height - .65),
            (.16, depth - .3, .23), petrol, .025)
        box(name + f" reveal Y {sign}",
            (x, y + sign * (depth / 2 - .09) - (.06 if sign == 1 else 0), height - .65),
            (width - .3, .16, .23), petrol, .025)


# Attached closed vestibule: rear datum Blender Y=0 / Godot Z=0; front projects 4.8 m.
volume("Entrance annex", 0, 2.4, 10.8, 4.8, 4.0, plum)
# Close the inset rear to the giant sibling's wall, 0.12 m behind its shoe datum.
box("Rear wall closure", (0, 0, 1.82), (10.56, .24, 3.64), plum, .015)
box("Rear coping closure", (0, -.06, 3.84), (10.6, .12, .32), blue, .015)
# Broad opaque glazing gives a closed entrance, never an accessible interior.
for x, width in [(-3.6, 2.5), (0, 3.6), (3.6, 2.5)]:
    box(f"Entrance frame {x}", (x, 4.68, 1.62), (width + .18, .10, 2.65), frame, .025)
    box(f"Closed entrance glass {x}", (x, 4.745, 1.62), (width, .04, 2.45), glass, .015)
    box(f"Broad transom {x}", (x, 4.775, 2.48), (width, .03, .10), frame, .008)
box("Double door centre stile", (0, 4.78, 1.62), (.12, .03, 2.45), frame, .008)
# No protruding pulls or thresholds: closed presentation remains within the solid envelope.
box("Closed door kick plate", (0, 4.779, .58), (3.6, .03, .22), petrol, .008)
# Side glazing is grouped and sparse, with no competing service entrance.
for side in (-1, 1):
    box(f"Side frame {side}", (side * 5.28, 2.45, 1.72), (.10, 2.65, 2.3), frame, .025)
    box(f"Side opaque glass {side}", (side * 5.345, 2.45, 1.72), (.04, 2.45, 2.1), glass, .015)
    box(f"Side transom {side}", (side * 5.375, 2.45, 2.48), (.03, 2.45, .10), frame, .008)
# Slate end piers relate the plum annex to both retail shells.
for x in (-5.0, 5.0):
    box(f"Slate frontage pier {x}", (x, 4.70, 1.72), (.40, .15, 2.85), wall, .025)
# A restrained coral face and top return echo the parent, below its 4.15 m band.
# Recess the front coping/reveal 0.06 m and return 0.02 m: no coplanar fascia surfaces.
box("Coral entrance face", (0, 4.71, 3.53), (8.4, .18, .74), coral, .035)
box("Coral top return", (0, 4.28, 3.94), (8.4, 1.0, .28), coral, .04)

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
root["asset_id"] = "d07_retail_buildings.03"
root["authorship"] = "Original Blender construction by commissioned production worker"
root["front"] = "Blender +Y -> Godot -Z; ground datum zero"
root["provisional_dimensions"] = "10.8m width, 4.8m projection, 4m roof; coral crown 4.08m"

root["attachment"] = "Parent .01 (0,0,-19) Godot; rear collision Z=0; rear trim Z=+0.12"

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
camera.location = (15, 20, 12)
aim(camera, (0, 2.4, 1.8))
data.type = "ORTHO"
data.ortho_scale = 19
bpy.context.preferences.filepaths.save_version = 0
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(), "export.py", "exec"))
# Hero/detail isolate the annex. Side/overhead show its actual giant-store attachment.
# Read the existing sibling only for render context, after saving/exporting owned source.
parent_source = ROOT / "art/source/models/environment/d07_retail_buildings_01/d07_retail_buildings_01.blend"
with bpy.data.libraries.load(str(parent_source), link=False) as (available, loaded):
    loaded.objects = ["D07RetailBuildings01_Mesh"]
context_mesh = loaded.objects[0]
scene.collection.objects.link(context_mesh)
context_mesh.parent = None
context_mesh.location = (0, -19, 0)
context_mesh.name = "STUDIO_existing_giant_store_context"
for name, location, target, scale, attached in [
        ("hero", (15, 20, 12), (0, 2.4, 1.8), 19, False),
        ("side", (18, 22, 12), (0, 0, 2.2), 24, True),
        ("frontage_detail", (8, 17, 6.5), (0, 4, 1.9), 13, False)]:
    context_mesh.hide_render = not attached
    camera.location = location
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)
# Actual attachment at scale, north at image top; parent rear roof deliberately cropped.
context_mesh.hide_render = False
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
