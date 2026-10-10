"""Original Ironreach attached office; use only the pinned isolated Blender CLI."""
import math
from pathlib import Path
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d08_workshop_buildings_04"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
# Provisional attachment spans exactly one sibling 3m wall bay.
WIDTH = 6.0
DEPTH = 3.0
WALL_HEIGHT = 3.0
ROOF_THICKNESS = .16
assert bpy.app.version_string == "5.2.2 LTS", bpy.app.version_string
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
parts = []


def material(name, swatch, rough=.65, metal=0.0, emission=0.0):
    """Use broad original sRGB swatches, converted to opaque linear Principled values."""
    rgb = [int(swatch[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*linear, 1)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*linear, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Emission Color"].default_value = (*linear, 1)
    bsdf.inputs["Emission Strength"].default_value = emission
    return mat


wall = material("ironreach_faded_petrol", "627D7B", .76, .05)
roof = material("ironreach_roof_petrol", "294E58", .66, .22)
patch = material("ironreach_replacement_sheet", "7D9190", .7, .18)
pale = material("ironreach_pale_band", "C6C2AC", .72)
brick = material("ironreach_worn_brick", "82604E", .88)
rust = material("ironreach_local_rust", "A7653E", .9)
recess = material("ironreach_dark_recess", "20363F", .43, .18)
amber = material("ironreach_working_amber", "F5BA55", .48, .0, .3)


def mesh(name, vertices, faces, mat, bevel=.012):
    """Create a closed editable component with applied broad edge and normal treatment."""
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    data.materials.append(mat)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    if bevel:
        mod = obj.modifiers.new("Soft manufactured edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bm = bmesh.new()
        bm.from_mesh(data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
        bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(data)
        bm.free()
        for polygon in data.polygons:
            polygon.use_smooth = True
        mod = obj.modifiers.new("Broad plane normals", "WEIGHTED_NORMAL")
        mod.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    parts.append(obj)
    return obj


BOX_FACES = [(0,3,2,1), (4,5,6,7), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)]


def box(name, lo, hi, mat, bevel=.012):
    """Build bounded solid geometry; runtime scenes contain no generated render meshes."""
    a, b, c = lo
    d, e, f = hi
    return mesh(name, [(a,b,c), (d,b,c), (d,e,c), (a,e,c),
                       (a,b,f), (d,b,f), (d,e,f), (a,e,f)], BOX_FACES, mat, bevel)


def roof_z(x):
    """Fall gently away from the west attachment, below the siblings' pale eave band."""
    return 3.42 - (x + 3.0) * .05


def roof_sheet(name, x0, x1, y0, y1, mat, thickness=ROOF_THICKNESS, lift=0.0):
    """Keep corrugations and repair sheets on the same closed lean-to roof slope."""
    z0, z1 = roof_z(x0)+lift, roof_z(x1)+lift
    return mesh(name, [(x0,y0,z0-thickness), (x1,y0,z1-thickness),
                       (x1,y1,z1-thickness), (x0,y1,z0-thickness),
                       (x0,y0,z0), (x1,y0,z1), (x1,y1,z1), (x0,y1,z0)],
                BOX_FACES, mat, .008)


# Closed office, not an interior kit. The west plane remains bare for a flush attachment.
box("Worn_brick_base", (-3,-1.5,0), (3,1.5,.72), brick, .012)
box("Closed_office_wall", (-3,-1.5,.72), (3,1.5,3), wall, .008)
for z in (.24,.48):
    for y0,y1 in [(-1.506,-1.498),(1.498,1.506)]:
        box("Brick_horizontal_mortar", (-2.98,y0,z), (2.98,y1,z+.018), wall, 0)
    box("Brick_east_mortar", (2.998,-1.48,z), (3.006,1.48,z+.018), wall, 0)
for row in range(3):
    z0 = .025+row*.24
    for x in (-2.4,-1.2,0,1.2,2.4):
        x += .35 if row == 1 else 0
        for y0,y1 in [(-1.506,-1.498),(1.498,1.506)]:
            box("Brick_face_joint", (x,y0,z0), (x+.018,y1,z0+.215), wall, 0)
    for y in (-1.2,0,1.2):
        y += .15 if row == 1 else 0
        box("Brick_east_joint", (2.998,y,z0), (3.006,y+.018,z0+.215), wall, 0)
for y0,y1 in [(-1.55,-1.49),(1.49,1.55)]:
    box("Pale_lower_office_band", (-3,y0,2.65), (3,y1,2.90), pale)
for x in (-2.88,.35,2.82):
    box("Front_office_pier", (x,1.49,.72), (x+.13,1.555,2.65), pale)
box("Pale_east_band", (2.99,-1.5,2.65), (3.05,1.5,2.90), pale)
for y in (-1.46,1.33):
    box("East_corner_pier", (2.99,y,.72), (3.05,y+.13,2.65), pale)
for x0,x1,z in [(-2.35,-1.40,.24),(.05,.65,.48)]:
    box("Rear_repaired_bricks", (x0,-1.525,z), (x1,-1.50,z+.18), rust)
box("East_base_repair", (3,-1.24,.24), (3.025,-.45,.42), rust)
box("Localized_paint_loss", (2.52,1.5,.73), (2.76,1.52,1.02), rust)
# Broad service-counter window and a separate closed personnel door distinguish an office.
box("Counter_window_frame", (-2.58,1.51,1.02), (.12,1.61,2.43), pale, .025)
box("Counter_dark_glazing", (-2.43,1.606,1.17), (-.03,1.628,2.28), recess)
for x in (-1.67,-.87):
    box("Counter_mullion", (x,1.625,1.17), (x+.065,1.65,2.28), pale)
box("Counter_window_sill", (-2.63,1.51,.98), (.17,1.70,1.07), patch, .015)
c = 1.6
box("Service_door_surround", (c-.74,1.505,.02), (c+.74,1.62,2.54), pale, .025)
box("Closed_service_door", (c-.6,1.615,.04), (c+.6,1.64,2.39), recess)
box("Service_door_amber_glazing", (c-.46,1.64,1.38), (c+.46,1.66,2.22), amber)
box("Service_door_crossbar", (c-.48,1.66,1.72), (c+.48,1.68,1.79), pale)
box("Door_pull", (c+.37,1.64,.91), (c+.44,1.73,1.20), pale)
box("Integral_task_lamp", (c-.58,1.55,2.73), (c+.58,1.74,2.88), recess, .025)
box("Integral_amber_lens", (c-.47,1.66,2.715), (c+.47,1.725,2.745), amber, .006)
box("East_window_frame", (3.005,-1.08,1.23), (3.105,1.08,2.43), pale, .02)
box("East_window_glass", (3.10,-.93,1.38), (3.125,.93,2.28), recess)
box("East_window_mullion", (3.12,-.035,1.38), (3.15,.035,2.28), pale)
# Upper wedge closes the lean-to silhouette while leaving the 3m structural solid simple.
mesh("Closed_lean_to_infill", [(-3,-1.5,2.94),(3,-1.5,2.94),(3,1.5,2.94),(-3,1.5,2.94),
    (-3,-1.5,3.28),(3,-1.5,2.98),(3,1.5,2.98),(-3,1.5,3.28)], BOX_FACES, wall, .006)
roof_sheet("Lean_to_roof",-3.02,3.20,-1.70,1.70,roof)
for y in (-1.30,-.65,0,.65,1.30):
    roof_sheet("Broad_corrugation",-2.98,3.18,y,y+.065,roof,.035,.032)
for x0,x1,y0,y1,mat in [(-1.9,.35,-1.25,-.15,patch),(1.55,2.65,-.9,-.25,rust)]:
    roof_sheet("Mismatched_roof_patch",x0,x1,y0,y1,mat,.065,.08)
    for index in range(int((y1-y0)/.30)):
        y = y0+.12+index*.30
        roof_sheet("Patch_corrugation",x0,x1,y,y+.055,mat,.028,.103)
# High-side flashing buries the <=0.05m host trim seam; it does not imply an opening.
box("West_attachment_flashing",(-3.08,-1.70,3.37),(-2.80,1.70,3.55),pale,.012)
box("Low_eave_fascia",(3.15,-1.70,2.99),(3.20,1.70,3.12),pale,.008)
roof_sheet("Short_amber_entry_marker",1.0,2.2,1.02,1.55,amber,.045,.055)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "D08WorkshopBuildings04_Mesh"
scene.cursor.location = (0,0,0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D08WorkshopBuildings04",None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "d08_workshop_buildings.04"
root["provenance"] = "Original commissioned Blender construction; no external art or brands"
root["axes"] = "Blender +Y front / +Z up maps to Godot -Z front / +Y up"
root["attachment"] = "West plane x=-3; 3m bay; top 3.55m; closed shell with no passage"
# Source keeps the office only. Comparison instances are loaded for evidence after saving/export.
world = scene.world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.22,.29,.34,1)
world.node_tree.nodes["Background"].inputs[1].default_value = .55
bpy.ops.mesh.primitive_plane_add(size=200)
ground = bpy.context.object
ground.name = "STUDIO_ground"
ground.location.z = -.025
ground.data.materials.append(material("STUDIO_slate", "64737C", .8))


def aim(obj, target):
    """Point isolated studio lights/camera at the recorded target."""
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()


def light(name, location, power, size):
    """Use soft review lighting outside the export collection, never runtime lights."""
    data = bpy.data.lights.new(name,"AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    obj.location = location
    aim(obj,(0,0,2))


light("STUDIO_key",(8,12,20),4600,12)
light("STUDIO_rim",(-12,-8,16),3700,10)
light("STUDIO_fill",(10,5,8),1400,9)
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new("STUDIO_camera",data)
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
scene.view_settings.view_transform = "AgX"
camera.location = (10,14,10)
aim(camera,(0,0,1.6))
data.type = "ORTHO"
data.ortho_scale = 10.5
SOURCE.parent.mkdir(parents=True,exist_ok=True)
EVIDENCE.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")),run_name="__main__")
for name,loc,target,scale in [
    ("hero",(10,14,10),(0,0,1.5),12.5),
    ("side",(12,0,5),(0,0,1.6),11),
    ("office_detail",(3,12,5),(.1,1.4,1.6),8.3),
]:
    camera.location = loc
    aim(camera,target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE/(name+".png"))
    bpy.ops.render.render(write_still=True)
# Match the saved family reference exactly: two existing unequal sheds and one office.
root.location = (16,-2.5,0)
for sibling, location in [("01",(8,2,0)),("02",(-13,-1,0))]:
    nid = "d08_workshop_buildings_"+sibling
    source = ROOT / f"art/source/models/environment/{nid}/{nid}.blend"
    with bpy.data.libraries.load(str(source),link=False) as (available, loaded):
        loaded.collections = [f"export_{nid}"]
    comparison = loaded.collections[0]
    scene.collection.children.link(comparison)
    next(item for item in comparison.objects if item.parent is None).location = location
camera.location = (0,0,47)
camera.rotation_euler = (0,0,0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE/"overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
