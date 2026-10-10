"""Original Ironreach sawtooth workshop; use only the pinned isolated Blender CLI."""
import math
from pathlib import Path
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d08_workshop_buildings_02"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
# Provisional family contract, metres. Front is Blender +Y / Godot -Z.
WIDTH = 14.0
DEPTH = 12.0
WALL_HEIGHT = 4.0
BAY_LENGTH = 3.0
ROOF_HALF_WIDTH = 7.35
ROOF_HALF_LENGTH = 6.35
EAVE_HEIGHT = 4.10
RIDGE_HEIGHT = 6.40
TOOTH_WIDTH = 4.90
TOOTH_COUNT = 3
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


def roof_z(x, start):
    """Map one tooth's inclined upper sheet; the next tooth resets at its valley."""
    return EAVE_HEIGHT + (RIDGE_HEIGHT - EAVE_HEIGHT) * (x - start) / TOOTH_WIDTH


def roof_sheet(name, x0, x1, y0, y1, start, mat, thickness=ROOF_THICKNESS, lift=0.0):
    """Make a closed sloped sheet or broad patch on a single sawtooth plane."""
    z0, z1 = roof_z(x0, start) + lift, roof_z(x1, start) + lift
    return mesh(name, [(x0,y0,z0-thickness), (x1,y0,z1-thickness),
                       (x1,y1,z1-thickness), (x0,y1,z0-thickness),
                       (x0,y0,z0), (x1,y0,z1), (x1,y1,z1), (x0,y1,z0)],
                BOX_FACES, mat, .008)


def shutter(center, replacement_rows):
    """Reuse the sibling's 4.2m leaf, 0.24m jamb and dented twelve-fold recipe."""
    box("Shutter_shadow_reveal", (center-2.28,5.995,.03), (center+2.28,6.035,3.32), recess)
    for x0, x1 in [(center-2.34,center-2.10), (center+2.10,center+2.34)]:
        box("Shutter_surround_jamb", (x0,6.01,.02), (x1,6.15,3.35), pale, .025)
    box("Shutter_surround_header", (center-2.34,6.01,3.11),
        (center+2.34,6.19,3.43), pale, .035)
    for row in range(12):
        z0 = .06 + row * .252
        xs = [center+offset for offset in (-2.10,-1.3,-.5,.4,1.3,2.10)]
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
        mesh("Dented_shutter_fold", vertices, faces,
             patch if row in replacement_rows else roof, .006)
    box("Shutter_bottom_rail", (center-2.1,6.035,.02), (center+2.1,6.14,.10), rust)
    box("Header_local_rust", (center-2.20,6.191,3.20),
        (center-1.56,6.21,3.32), rust, .006)
    box("Integral_task_lamp_casing", (center-.74,6.04,3.43),
        (center+.74,6.26,3.58), recess, .03)
    box("Integral_task_lamp_lens", (center-.62,6.14,3.415),
        (center+.62,6.245,3.445), amber, .008)


# No interior: base and upper walls meet, rather than covering the brick with paint geometry.
box("Worn_brick_base", (-7,-6,0), (7,6,.72), brick, .02)
box("Closed_wall_volume", (-7,-6,.72), (7,6,4.0), wall, .008)
for z in (.24,.48):
    for y0,y1 in [(-6.006,-5.998),(5.998,6.006)]:
        box("Brick_horizontal_mortar", (-6.98,y0,z), (6.98,y1,z+.018), wall, 0)
    for x0,x1 in [(-7.006,-6.998),(6.998,7.006)]:
        box("Brick_side_mortar", (x0,-5.98,z), (x1,5.98,z+.018), wall, 0)
for row in range(3):
    z0 = .025 + row*.24
    offset = .6 if row == 1 else 0
    for index in range(11):
        x = -6.6 + offset + index*1.2
        for y0,y1 in [(-6.006,-5.998),(5.998,6.006)]:
            box("Brick_staggered_front_joint", (x,y0,z0), (x+.018,y1,z0+.215), wall, 0)
    for index in range(9):
        y = -5.4 + offset + index*1.2
        for x0,x1 in [(-7.006,-6.998),(6.998,7.006)]:
            box("Brick_staggered_side_joint", (x0,y,z0), (x1,y+.018,z0+.215), wall, 0)
for side in (-1,1):
    x0,x1 = (6.94,7.045) if side == 1 else (-7.045,-6.94)
    for y in (-5.94,-3,0,3,5.94):
        box("Straight_bay_pilaster", (x0,y-.055,.72), (x1,y+.055,3.84), pale)
    x0,x1 = (6.98,7.05) if side == 1 else (-7.05,-6.98)
    box("Pale_side_eave_band", (x0,-6,3.65), (x1,6,3.90), pale)
    for y,length,z in [(-4.5,1.3,.20),(-.8,1.6,.46),(3.9,.9,.22)]:
        box("Base_repaired_bricks", (x0,y,z), (x1,y+length,z+.18), rust, .015)
for y0,y1 in [(-6.05,-5.99),(5.99,6.05)]:
    box("Pale_front_rear_band", (-7,y0,3.65), (7,y1,3.90), pale)
for x in (-6.94,6.78):
    box("Front_corner_post", (x,5.98,.72), (x+.16,6.055,3.65), pale)
shutter(-3.50, (1,2))
shutter(1.50, (8,))
# Same service-door dimensions, positioned beyond the second shutter's surround.
box("Service_door_surround", (4.86,6.005,.02), (6.34,6.12,2.54), pale, .025)
box("Closed_service_door", (5.00,6.115,.04), (6.20,6.14,2.39), recess)
box("Service_door_amber_glazing", (5.14,6.14,1.38), (6.06,6.16,2.22), amber)
box("Service_door_crossbar", (5.12,6.16,1.72), (6.08,6.18,1.79), pale)
box("Door_pull", (5.97,6.14,.91), (6.04,6.23,1.20), pale)
box("Front_paint_loss", (4.00,6.003,.73), (4.72,6.025,1.04), rust)
box("Rear_paint_loss", (-3.8,-6.025,.74), (-2.1,-6.003,1.02), rust)
# Forward high window leaves the right-rear 3m office connection entirely blank below its band.
box("Side_high_window_frame", (7.005,1.77,2.12), (7.105,4.83,3.33), pale, .02)
box("Side_high_window_glass", (7.10,1.92,2.27), (7.125,4.68,3.18), recess)
for y in (2.82,3.78):
    box("Side_window_mullion", (7.12,y,2.27), (7.15,y+.07,3.18), pale)

for tooth in range(TOOTH_COUNT):
    start = -ROOF_HALF_WIDTH + tooth*TOOTH_WIDTH
    end = start + TOOTH_WIDTH
    # Closed taper infill: end wall recessed 10cm below the roof lip, no hollow interior.
    a,b = start,end-.10
    low,high = roof_z(a,start)-.14,roof_z(b,start)-.14
    mesh("Sawtooth_closed_infill", [(a,-6,3.92),(b,-6,3.92),(b,6,3.92),(a,6,3.92),
                                   (a,-6,low),(b,-6,high),(b,6,high),(a,6,low)],
         BOX_FACES, wall, .006)
    roof_sheet("Sawtooth_roof_plane",start,end-.02,-6.34,6.34,start,roof)
    for index in range(19):
        y = -5.90 + index*.65
        roof_sheet("Broad_roof_corrugation",start,end-.02,y,y+.065,start,roof,.035,.032)
    # Clerestory strips face +X, not a second roof pitch: opaque glazing avoids interior promises.
    face = end-.10
    box("Clerestory_dark_strip", (face-.005,-5.8,4.48), (face+.024,5.8,6.05), recess)
    for z in (4.43,6.03):
        box("Clerestory_horizontal_frame", (face+.018,-5.88,z),
            (face+.07,5.88,z+.09), pale)
    for y in (-5.83,-3,0,3,5.77):
        box("Clerestory_mullion", (face+.018,y,4.48), (face+.072,y+.06,6.07), pale)
    # Cap remains proud of sheet/rib ends: avoid coplanar end-face speckling.
    box("Raised_peak_cap", (end-.12,-6.35,6.30), (end,6.35,6.50), pale, .014)
    # One amber band, not three competing luminous stripes or a duplicated landmark model.
    if tooth == 0:
        roof_sheet("Amber_work_bay_roof_band",start,end-.02,4.65,5.23,start,amber,.045,.055)
    patches = [(.55,3.95,-3.7,-.65,patch),(.70,3.80,.35,2.55,wall),(.8,3.6,2.6,3.95,rust)]
    x0,x1,y0,y1,mat = patches[tooth]
    roof_sheet("Mismatched_repair_sheet",start+x0,start+x1,y0,y1,start,mat,.065,.085)
    for index in range(int((y1-y0)/.42)):
        y = y0+.15+index*.42
        roof_sheet("Repair_sheet_corrugation",start+x0,start+x1,y,y+.055,start,mat,.028,.108)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "D08WorkshopBuildings02_Mesh"
scene.cursor.location = (0,0,0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D08WorkshopBuildings02",None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "d08_workshop_buildings.02"
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
camera.location = (23,28,20)
aim(camera,(0,0,2.1))
data.type = "ORTHO"
data.ortho_scale = 27
SOURCE.parent.mkdir(parents=True,exist_ok=True)
EVIDENCE.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")),run_name="__main__")
for name,loc,target,scale in [
    ("hero",(23,28,20),(0,0,2.4),27),
    ("side",(25,0,9),(0,0,2.7),22),
    ("clerestory_detail",(18,15,13),(1.8,1.7,4.8),15),
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
