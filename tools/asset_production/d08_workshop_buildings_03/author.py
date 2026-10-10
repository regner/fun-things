"""Original Ironreach larger depot; use only the pinned isolated Blender CLI."""
import math
from pathlib import Path
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d08_workshop_buildings_03"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
# Provisional family contract, metres. Front is Blender +Y / Godot -Z.
WIDTH = 18.0
DEPTH = 15.0
WALL_HEIGHT = 4.0
BAY_LENGTH = 3.0
HALF_WIDTH = WIDTH / 2
FRONT = DEPTH / 2
OVERHANG = .35
EAVE_HEIGHT = 4.10
ROOF_THICKNESS = .16
# Unequal adjacent pitches make a larger, compact depot rather than a dock warehouse bar.
ROOFS = [(-9.35, -3.675, 2.0, 6.70), (2.0, 5.675, 9.35, 5.65)]
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


def roof_z(x, profile):
    """Interpolate a paired pitch from its recorded valley, ridge and height."""
    left, ridge, right, height = profile
    distance = (ridge-x)/(ridge-left) if x < ridge else (x-ridge)/(right-ridge)
    return height - (height-EAVE_HEIGHT)*distance


def roof_sheet(name, x0, x1, y0, y1, profile, mat, thickness=ROOF_THICKNESS, lift=0.0):
    """Create a closed sheet on one slope; all repairs use the same roof plane."""
    z0, z1 = roof_z(x0, profile)+lift, roof_z(x1, profile)+lift
    return mesh(name, [(x0,y0,z0-thickness), (x1,y0,z1-thickness),
                       (x1,y1,z1-thickness), (x0,y1,z0-thickness),
                       (x0,y0,z0), (x1,y0,z1), (x1,y1,z1), (x0,y1,z0)],
                BOX_FACES, mat, .008)


def shutter(center, replacement_rows):
    """Reuse the sibling's 4.2m leaf, 0.24m jamb and dented twelve-fold recipe."""
    box("Shutter_shadow_reveal", (center-2.28,FRONT-.005,.03), (center+2.28,FRONT+0.035,3.32), recess)
    for x0, x1 in [(center-2.34,center-2.10), (center+2.10,center+2.34)]:
        box("Shutter_surround_jamb", (x0,FRONT+0.01,.02), (x1,FRONT+0.15,3.35), pale, .025)
    box("Shutter_surround_header", (center-2.34,FRONT+0.01,3.11),
        (center+2.34,FRONT+0.19,3.43), pale, .035)
    for row in range(12):
        z0 = .06 + row * .252
        xs = [center+offset for offset in (-2.10,-1.3,-.5,.4,1.3,2.10)]
        dent = [0,.012,.055,.030,0,0] if row in (3,4,5) else [0,0,0,0,0,0]
        vertices = []
        for x,d in zip(xs,dent):
            vertices.extend([(x,FRONT+0.038,z0), (x,FRONT+0.11-d,z0),
                             (x,FRONT+0.1-d,z0+.225), (x,FRONT+0.038,z0+.225)])
        faces = [(3,2,1,0), tuple(range(4*(len(xs)-1),4*len(xs)))]
        for index in range(len(xs)-1):
            for edge in range(4):
                a = index*4+edge
                b = index*4+(edge+1)%4
                faces.append((a,b,b+4,a+4))
        mesh("Dented_shutter_fold", vertices, faces,
             patch if row in replacement_rows else roof, .006)
    box("Shutter_bottom_rail", (center-2.1,FRONT+0.035,.02), (center+2.1,FRONT+0.14,.10), rust)
    box("Header_local_rust", (center-2.20,FRONT+0.191,3.20),
        (center-1.56,FRONT+0.21,3.32), rust, .006)
    box("Integral_task_lamp_casing", (center-.74,FRONT+0.04,3.43),
        (center+.74,FRONT+0.26,3.58), recess, .03)
    box("Integral_task_lamp_lens", (center-.62,FRONT+0.14,3.415),
        (center+.62,FRONT+0.245,3.445), amber, .008)


# One solid rectangle; pitches differ without inventing an interior or dock platform.
box("Worn_brick_base", (-HALF_WIDTH,-FRONT,0), (HALF_WIDTH,FRONT,.72), brick, .02)
box("Closed_wall_volume", (-HALF_WIDTH,-FRONT,.72), (HALF_WIDTH,FRONT,4), wall, .008)
for z in (.24,.48):
    for y0,y1 in [(-FRONT-.006,-FRONT+.002),(FRONT-.002,FRONT+.006)]:
        box("Brick_horizontal_mortar", (-HALF_WIDTH+.02,y0,z),
            (HALF_WIDTH-.02,y1,z+.018), wall, 0)
    for x0,x1 in [(-HALF_WIDTH-.006,-HALF_WIDTH+.002),(HALF_WIDTH-.002,HALF_WIDTH+.006)]:
        box("Brick_side_mortar", (x0,-FRONT+.02,z), (x1,FRONT-.02,z+.018), wall, 0)
for row in range(3):
    z0 = .025+row*.24
    offset = .6 if row == 1 else 0
    for index in range(14):
        x = -8.4+offset+index*1.2
        for y0,y1 in [(-FRONT-.006,-FRONT+.002),(FRONT-.002,FRONT+.006)]:
            box("Brick_front_joint", (x,y0,z0), (x+.018,y1,z0+.215), wall, 0)
    for index in range(11):
        y = -6.6+offset+index*1.2
        for x0,x1 in [(-HALF_WIDTH-.006,-HALF_WIDTH+.002),(HALF_WIDTH-.002,HALF_WIDTH+.006)]:
            box("Brick_side_joint", (x0,y,z0), (x1,y+.018,z0+.215), wall, 0)
for side in (-1,1):
    x0,x1 = (8.94,9.045) if side == 1 else (-9.045,-8.94)
    for y in (-7.44,-4.5,-1.5,1.5,4.5,7.44):
        box("Straight_bay_pilaster", (x0,y-.055,.72), (x1,y+.055,3.84), pale)
    x0,x1 = (8.98,9.05) if side == 1 else (-9.05,-8.98)
    box("Pale_side_eave_band", (x0,-FRONT,3.65), (x1,FRONT,3.90), pale)
    for y,length,z in [(-5.5,1.3,.20),(-.8,1.6,.46),(4.9,.9,.22)]:
        box("Base_repaired_bricks", (x0,y,z), (x1,y+length,z+.18), rust, .015)
for y0,y1 in [(-FRONT-.05,-FRONT+.01),(FRONT-.01,FRONT+.05)]:
    box("Pale_front_rear_band", (-HALF_WIDTH,y0,3.65), (HALF_WIDTH,y1,3.90), pale)
for x in (-8.94,8.78):
    box("Front_corner_post", (x,FRONT-.02,.72), (x+.16,FRONT+.055,3.65), pale)
for center, replacement_rows in [(-6,(1,2)),(-1,(8,)),(4,(2,3))]:
    shutter(center,replacement_rows)
# Service door occupies the remaining front-right pier; shares the first two assets' dimensions.
c = 7.6
box("Service_door_surround", (c-.74,FRONT+.005,.02), (c+.74,FRONT+.12,2.54), pale, .025)
box("Closed_service_door", (c-.6,FRONT+.115,.04), (c+.6,FRONT+.14,2.39), recess)
box("Service_door_amber_glazing", (c-.46,FRONT+.14,1.38), (c+.46,FRONT+.16,2.22), amber)
box("Service_door_crossbar", (c-.48,FRONT+.16,1.72), (c+.48,FRONT+.18,1.79), pale)
box("Door_pull", (c+.37,FRONT+.14,.91), (c+.44,FRONT+.23,1.20), pale)
box("Front_paint_loss", (6.45,FRONT+.003,.73), (6.78,FRONT+.025,1.04), rust)
box("Rear_paint_loss", (-5.8,-FRONT-.025,.74), (-3.5,-FRONT-.003,1.02), rust)
# Forward high window leaves the rear-right 3m attachment bay free of window/door fittings.
box("Side_high_window_frame", (9.005,3.27,2.12), (9.105,6.33,3.33), pale, .02)
box("Side_high_window_glass", (9.10,3.42,2.27), (9.125,6.18,3.18), recess)
for y in (4.32,5.28):
    box("Side_window_mullion", (9.12,y,2.27), (9.15,y+.07,3.18), pale)

for index,profile in enumerate(ROOFS):
    left,ridge,right,height = profile
    # Gable extends only over the structural footprint; sheet underside overlaps its top.
    a,b = max(left,-HALF_WIDTH),min(right,HALF_WIDTH)
    e0,e1,peak = roof_z(a,profile)-.14,roof_z(b,profile)-.14,height-.14
    mesh("Closed_depot_gable", [(a,-FRONT,3.90),(b,-FRONT,3.90),(b,-FRONT,e1),
         (ridge,-FRONT,peak),(a,-FRONT,e0),(a,FRONT,3.90),(b,FRONT,3.90),
         (b,FRONT,e1),(ridge,FRONT,peak),(a,FRONT,e0)],
         [(4,3,2,1,0),(5,6,7,8,9),(0,1,6,5),(1,2,7,6),
          (2,3,8,7),(3,4,9,8),(4,0,5,9)], wall, .008)
    for x0,x1 in [(left,ridge),(ridge,right)]:
        roof_sheet("Paired_pitched_roof",x0,x1,-FRONT-OVERHANG,FRONT+OVERHANG,profile,roof)
        for rib in range(23):
            y = -7.10+rib*.65
            roof_sheet("Broad_corrugation",x0,x1,y,y+.065,profile,roof,.035,.032)
        if index == 0:
            roof_sheet("Amber_work_bay_band",x0,x1,5.85,6.43,profile,amber,.045,.055)
    # Pale caps rise over the corrugations/band; major roof is capped at 6.80m.
    box("Pitched_ridge_cap",(ridge-.095,-7.85,height-.06),
        (ridge+.095,7.85,height+.10),pale,.018)
    repairs = [(-8.7,-4.4,-4.8,-1.3,patch),(-2.8,1.3,.3,2.7,wall)] if index == 0 else [
        (2.6,5.15,-4.0,-1.7,rust),(6.1,8.75,2.4,4.9,patch)]
    for x0,x1,y0,y1,mat in repairs:
        roof_sheet("Mismatched_repair_sheet",x0,x1,y0,y1,profile,mat,.065,.085)
        for rib in range(int((y1-y0)/.42)):
            y = y0+.15+rib*.42
            roof_sheet("Repair_corrugation",x0,x1,y,y+.055,profile,mat,.028,.108)
# A restrained valley flashing covers the pitched-sheet seam without a false third ridge.
box("Valley_flashing",(1.87,-7.85,4.08),(2.13,7.85,4.19),recess,.012)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "D08WorkshopBuildings03_Mesh"
scene.cursor.location = (0,0,0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D08WorkshopBuildings03",None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "d08_workshop_buildings.03"
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
    ("hero",(26,32,23),(0,0,2.5),34),
    ("side",(29,0,10),(0,0,2.8),28),
    ("frontage_detail",(6,28,10),(1,6.9,2.6),25),
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
