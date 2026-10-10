"""Original Ironreach pitched shed; use only the pinned isolated Blender CLI."""
import math
from pathlib import Path
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d08_workshop_buildings_01"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
# Provisional family contract, metres. Front is Blender +Y / Godot -Z.
WIDTH = 10.0
DEPTH = 12.0
WALL_HEIGHT = 4.0
BAY_LENGTH = 3.0
ROOF_HALF_WIDTH = 5.35
ROOF_HALF_LENGTH = 6.35
EAVE_HEIGHT = 4.10
RIDGE_HEIGHT = 5.80
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
    """Map a roof-plane coordinate to its upper face, keeping patchwork on the same pitch."""
    return RIDGE_HEIGHT - (RIDGE_HEIGHT - EAVE_HEIGHT) * abs(x) / ROOF_HALF_WIDTH


def roof_sheet(name, x0, x1, y0, y1, mat, thickness=ROOF_THICKNESS, lift=0.0):
    """Make a closed pitched sheet; a piece never straddles the ridge."""
    z0, z1 = roof_z(x0) + lift, roof_z(x1) + lift
    return mesh(name, [(x0,y0,z0-thickness), (x1,y0,z1-thickness),
                       (x1,y1,z1-thickness), (x0,y1,z0-thickness),
                       (x0,y0,z0), (x1,y0,z1), (x1,y1,z1), (x0,y1,z0)],
                BOX_FACES, mat, .008)


# One closed exterior volume, not an implied enterable garage or invented interior.
box("Worn_brick_base", (-5,-6,0), (5,6,.72), brick, .02)
# Upper pentagon embeds slightly into the roof underside, avoiding an open eave slit.
gable_eave = roof_z(5) - ROOF_THICKNESS + .02
gable_ridge = RIDGE_HEIGHT - ROOF_THICKNESS + .02
mesh("Closed_wall_and_gable_volume", [(-5,-6,.72), (5,-6,.72), (5,-6,gable_eave),
                            (0,-6,gable_ridge), (-5,-6,gable_eave),
                            (-5,6,.72), (5,6,.72), (5,6,gable_eave),
                            (0,6,gable_ridge), (-5,6,gable_eave)],
     [(4,3,2,1,0), (5,6,7,8,9), (0,1,6,5), (1,2,7,6),
      (2,3,8,7), (3,4,9,8), (4,0,5,9)], wall, .008)
# Oversized masonry courses suggest worn brick, without texture noise or loose collision pieces.
for z in (.24,.48):
    for y0,y1 in [(-6.006,-5.998),(5.998,6.006)]:
        box("Brick_horizontal_mortar", (-4.98,y0,z), (4.98,y1,z+.018), wall, 0)
    for x0,x1 in [(-5.006,-4.998),(4.998,5.006)]:
        box("Brick_side_mortar", (x0,-5.98,z), (x1,5.98,z+.018), wall, 0)
for row in range(3):
    z0 = .025 + row*.24
    offset = .6 if row == 1 else 0
    for index in range(8):
        x = -4.7 + offset + index*1.2
        for y0,y1 in [(-6.006,-5.998),(5.998,6.006)]:
            box("Brick_staggered_front_joint", (x,y0,z0), (x+.018,y1,z0+.215), wall, 0)
    for index in range(9):
        y = -5.4 + offset + index*1.2
        for x0,x1 in [(-5.006,-4.998),(4.998,5.006)]:
            box("Brick_staggered_side_joint", (x0,y,z0), (x1,y+.018,z0+.215), wall, 0)
# Shared 3m straight bays, with no protruding base or individual collision snags.
for side in (-1, 1):
    for y in (-5.94, -3, 0, 3, 5.94):
        x0, x1 = (4.94,5.045) if side == 1 else (-5.045,-4.94)
        box("Straight_bay_pilaster", (x0,y-.055,.72), (x1,y+.055,3.84), pale)
    x0, x1 = (4.98,5.05) if side == 1 else (-5.05,-4.98)
    box("Pale_side_eave_band", (x0,-6,3.65), (x1,6,3.90), pale)
    # Broad, sparse masonry repair blocks, not fine procedural grime.
    for y, length, z in [(-4.5,1.3,.20), (-.8,1.6,.46), (3.9,.9,.22)]:
        box("Base_repaired_bricks", (x0,y,z), (x1,y+length,z+.18), rust, .015)
# Rear blank wall remains usable for repetition; front has one short work bay.
for y0, y1 in [(-6.05,-5.99), (5.99,6.05)]:
    box("Pale_gable_tie_band", (-5,y0,3.65), (5,y1,3.90), pale)
for x in (-4.94,4.78):
    box("Front_corner_post", (x,5.98,.72), (x+.16,6.055,3.65), pale)

# Closed 4.2 x 3.0m roller shutter. Horizontal folds carry two broad local dents.
box("Shutter_shadow_reveal", (-3.78,5.995,.03), (.78,6.035,3.32), recess)
for x0, x1 in [(-3.84,-3.60), (.60,.84)]:
    box("Shutter_surround_jamb", (x0,6.01,.02), (x1,6.15,3.35), pale, .025)
box("Shutter_surround_header", (-3.84,6.01,3.11), (.84,6.19,3.43), pale, .035)
for row in range(12):
    z0 = .06 + row * .252
    # Six stations keep dents smooth and large enough to read without thin sliver faces.
    xs = [-3.60,-2.8,-2.0,-1.1,-.2,.60]
    dent = [0,.012,.055,.030,0,0] if row in (3,4,5) else [0,0,0,0,0,0]
    vertices = []
    for x,d in zip(xs,dent):
        vertices.extend([(x,6.038,z0), (x,6.11-d,z0),
                         (x,6.10-d,z0+.225), (x,6.038,z0+.225)])
    faces = [(3,2,1,0), tuple(range(4*(len(xs)-1),4*len(xs)))]
    for index in range(len(xs)-1):
        for edge in range(4):
            a = index*4+edge
            b = index*4+(edge+1)%4
            faces.append((a,b,b+4,a+4))
    mesh("Dented_shutter_fold", vertices, faces, patch if row in (1,2) else roof, .006)
box("Shutter_bottom_rail", (-3.60,6.035,.02), (.60,6.14,.10), rust)
# Integral work-door and opaque amber panes: appearance only, no real lights or opening state.
box("Service_door_surround", (2.56,6.005,.02), (4.04,6.12,2.54), pale, .025)
box("Closed_service_door", (2.70,6.115,.04), (3.90,6.14,2.39), recess)
box("Service_door_amber_glazing", (2.84,6.14,1.38), (3.76,6.16,2.22), amber)
box("Service_door_crossbar", (2.82,6.16,1.72), (3.78,6.18,1.79), pale)
box("Door_pull", (3.67,6.14,.91), (3.74,6.23,1.20), pale)
box("Integral_task_lamp_casing", (-2.24,6.04,3.43), (-.76,6.26,3.58), recess, .03)
box("Integral_task_lamp_lens", (-2.12,6.14,3.415), (-.88,6.245,3.445), amber, .008)
# One side high window in the forward bay, leaving the rear right office interface plain.
box("Side_high_window_frame", (5.005,1.77,2.12), (5.105,4.83,3.33), pale, .02)
box("Side_high_window_glass", (5.10,1.92,2.27), (5.125,4.68,3.18), recess)
for y in (2.82,3.78):
    box("Side_window_mullion", (5.12,y,2.27), (5.15,y+.07,3.18), pale)
# Broad paint loss at two panel feet and one shutter header end; no random micro-noise.
box("Front_paint_loss", (1.15,6.003,.73), (2.23,6.025,1.04), rust)
box("Rear_paint_loss", (-3.8,-6.025,.74), (-2.1,-6.003,1.02), rust)
box("Header_local_rust", (-3.70,6.191,3.20), (-3.06,6.21,3.32), rust, .006)

for x0,x1 in [(-ROOF_HALF_WIDTH,0), (0,ROOF_HALF_WIDTH)]:
    roof_sheet("Pitched_roof_plane", x0,x1,-ROOF_HALF_LENGTH,ROOF_HALF_LENGTH,roof)
    # Corrugation spacing .65m is intentionally coarser than real sheet steel at game scale.
    for index in range(19):
        y = -5.90 + index*.65
        roof_sheet("Broad_roof_corrugation", x0,x1,y,y+.065,roof,.035,.032)
    # Quiet front cross-roof amber repair band identifies the paired-yard family overhead.
    roof_sheet("Amber_work_bay_roof_band", x0,x1,4.65,5.23,amber,.045,.055)
# Mismatched rectangular repair sheets sit over (not coplanar with) the original roof ribs.
for name,x0,x1,y0,y1,mat in [
    ("Pale_replacement_sheet", .55,4.75,-3.6,-.35,patch),
    ("Faded_replacement_sheet", -4.85,-1.25,.1,2.3,wall),
    ("Localized_rusted_sheet", .9,3.9,2.05,3.43,rust),
]:
    roof_sheet(name,x0,x1,y0,y1,mat,.065,.085)
    for index in range(int((y1-y0)/.42)):
        y = y0+.15+index*.42
        roof_sheet(name+"_corrugation",x0,x1,y,y+.055,mat,.028,.108)
# A narrow solid ridge cap covers even the raised amber strip; literal overall height 5.88m.
box("Ridge_cap", (-.095,-6.35,5.74), (.095,6.35,5.88), pale, .018)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "D08WorkshopBuildings01_Mesh"
scene.cursor.location = (0,0,0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D08WorkshopBuildings01",None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "d08_workshop_buildings.01"
root["provenance"] = "Original commissioned Blender construction; no external art or brands"
root["axes"] = "Blender +Y front / +Z up maps to Godot -Z front / +Y up"
root["family_contract"] = "3m straight bays; 4m eaves; 4.2x3m closed shutter; see production handoff"
# Studio is saved outside the explicitly exported collection.
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
    """Point the isolated studio camera or lamp at a recorded target."""
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()


def light(name, location, power, size):
    """Add soft review lighting outside the export collection."""
    data = bpy.data.lights.new(name,"AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    obj.location = location
    aim(obj,(0,0,2))


light("STUDIO_key",(6,10,17),3600,10)
light("STUDIO_rim",(-9,-6,12),2900,8)
light("STUDIO_fill",(8,4,6),950,7)
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
camera.location = (19,25,18)
aim(camera,(0,0,2.1))
data.type = "ORTHO"
data.ortho_scale = 23
SOURCE.parent.mkdir(parents=True,exist_ok=True)
EVIDENCE.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")),run_name="__main__")
for name,loc,target,scale in [
    ("hero",(19,25,18),(0,0,2.1),23),
    ("side",(22,0,9),(0,0,2.1),19),
    ("shutter_detail",(8,23,8),(.1,5.7,2.0),13),
]:
    camera.location = loc
    aim(camera,target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE/(name+".png"))
    bpy.ops.render.render(write_still=True)
camera.location = (0,0,47)
camera.rotation_euler = (0,0,0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE/"overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
