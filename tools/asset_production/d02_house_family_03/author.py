"""Original short Crescents terrace; run only in pinned, isolated Blender CLI."""
import math
from pathlib import Path
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_house_family_03"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
# Provisional metres: three narrow homes; cross-frontage ridges and a shallower east end.
assert bpy.app.version_string == "5.2.2 LTS", bpy.app.version_string
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
parts = []


def material(name, swatch, rough=.65, metal=0.0):
    """Convert an original sRGB palette swatch to an opaque Principled material."""
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
    return mat


wall = material("crescents_warm_render", "ACA69E")
trim = material("crescents_ivory_trim", "D4CEBB", .55)
slate = material("crescents_blue_slate_roof", "3E526C", .58, .08)
plum = material("crescents_muted_plum_roof", "68566B", .62, .05)
glass = material("crescents_petrol_closed_glass", "263F4D", .3, .12)
warm = material("crescents_warm_entrance", "D4A16B", .55)
base = material("crescents_slate_plinth", "58636B", .75)


def mesh(name, vertices, faces, mat, bevel=.015):
    """Build a closed editable part and apply softened edges with weighted normals."""
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
        modifier = obj.modifiers.new("Soft architectural edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm = bmesh.new()
        bm.from_mesh(data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
        bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(data)
        bm.free()
        for polygon in data.polygons:
            polygon.use_smooth = True
        modifier = obj.modifiers.new("Broad plane normals", "WEIGHTED_NORMAL")
        modifier.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    parts.append(obj)
    return obj


def box(name, lo, hi, mat, bevel=.015):
    """Author a solid bounded component; no generated render geometry enters Godot scenes."""
    a, b, c = lo
    d, e, f = hi
    return mesh(name, [(a,b,c), (d,b,c), (d,e,c), (a,e,c),
                       (a,b,f), (d,b,f), (d,e,f), (a,e,f)],
                [(0,3,2,1), (4,5,6,7), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)],
                mat, bevel)


def crosswise_prism(name, profile, left, right, mat, bevel=.015):
    """Extrude a closed depth/height polygon along X for the terrace's lateral ridge."""
    count = len(profile)
    vertices = [(x,y,z) for x in (left,right) for y,z in profile]
    faces = [tuple(reversed(range(count))), tuple(range(count,2*count))]
    faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    return mesh(name, vertices, faces, mat, bevel)


# Two homes share the long main ridge; the third steps back and down, not a recolour.
for label, left, right, front, peak, mat in [
    ("Main_row", -7.8, 2.6, 4.0, 7.30, slate),
    ("East_end", 2.6, 7.8, 2.8, 6.95, plum),
]:
    rear, eave, thickness = -4.0, 5.55, .20
    ridge = (rear+front)/2
    roof_rear, roof_front = rear-.4, front+.4
    # Continuous gabled-end wall solids avoid coplanar body/gable seams.
    wall_edge_height = eave-thickness+(peak-thickness-(eave-thickness))*.4/(ridge-roof_rear)
    crosswise_prism(label+"_closed_volume", [(rear,0),(front,0),
                    (front,wall_edge_height),(ridge,peak-thickness),
                    (rear,wall_edge_height)], left,right,wall,.01)
    roof_left = left-.35 if left < 0 else left
    roof_right = right+.35 if right > 3 else right
    crosswise_prism(label+"_folded_roof", [(roof_rear,eave),(ridge,peak),
                    (roof_front,eave),(roof_front,eave-thickness),
                    (ridge,peak-thickness),(roof_rear,eave-thickness)],
                    roof_left,roof_right,mat,.012)
    # Integral fascia/bargeboards, not separately owned porch/dormer fixtures.
    for x in (roof_left+.01,roof_right-.10):
        crosswise_prism(label+"_bargeboard", [(roof_rear+.02,eave-thickness),
                        (ridge,peak-thickness),(roof_front-.02,eave-thickness),
                        (roof_front-.02,eave-.35),(ridge,peak-.35),
                        (roof_rear+.02,eave-.35)], x,x+.09,trim,.008)
    box(label+"_integral_ridge", (roof_left+.04,ridge-.055,peak-.055),
        (roof_right-.04,ridge+.055,peak),mat,.01)
    for y in (roof_rear+.01,roof_front-.09):
        box(label+"_eave_fascia", (roof_left+.02,y,5.20),
            (roof_right-.02,y+.08,5.36),trim,.012)
    box(label+"_plinth", (left-.04,rear-.04,0), (right+.04,front+.04,.28),base)
for label, x0, x1, front in [("West",-7.8,-2.6,4.0),
                             ("Middle",-2.6,2.6,4.0),("East",2.6,7.8,2.8)]:
    box(label+"_front_floor_course", (x0+.22,front-.005,2.78),
        (x1-.22,front+.075,2.91),trim)
    for x in (x0+.02,x1-.21):
        box(label+"_front_pier_trim", (x,front-.004,.29),
            (x+.19,front+.08,5.18),trim,.012)
box("Rear_floor_course", (-7.78,-4.075,2.78), (7.78,-3.995,2.91),trim)
for x,front in ((-7.8,4.0),(7.8,2.8)):
    box("End_floor_course", (x-.035,-3.98,2.78), (x+.035,front-.02,2.91),trim)


def facade_box(name, u0, u1, depth0, depth1, z0, z1, mat, origin, angle, bevel=.012):
    """Place a local +Y-facing box on an exterior wall and bake its transform."""
    obj = box(name, (u0,depth0,z0), (u1,depth1,z1), mat, bevel)
    obj.rotation_euler.z = angle
    obj.location = (origin[0], origin[1], 0)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return obj


def window(name, centre, bottom, width, height, origin, angle=0, occupied=False):
    """Author broad closed two-pane domestic glazing, recessed within a simple frame."""
    left, right = centre-width/2, centre+width/2
    top = bottom+height
    params = (origin, angle)
    facade_box(name+"_casing", left-.1,right+.1,.005,.075,bottom-.10,top+.10,
               trim,*params)
    facade_box(name+"_opaque_glass", left,right,.074,.09,bottom,top,glass,*params)
    if occupied:
        facade_box(name+"_warm_blind", left+.03,centre-.055,.090,.095,
                   bottom+.035,top-.035,warm,*params,.005)
    facade_box(name+"_mullion", centre-.045,centre+.045,.09,.14,
               bottom,top,trim,*params,.008)
    facade_box(name+"_sill", left-.15,right+.15,.025,.20,
               bottom-.14,bottom-.06,trim,*params,.012)


# Three grade-level entries make the short row legible in close views; none opens.
for label, entry, living, front in [("West",-6.45,-3.95,4.0),
                                    ("Middle",-1.25,1.25,4.0),
                                    ("East",3.95,6.45,2.8)]:
    window(label+"_living",living,1.02,1.80,1.40,(0,front),occupied=label=="Middle")
    window(label+"_upper_living",living,3.49,1.80,1.40,(0,front))
    window(label+"_upper_entry",entry,3.49,1.25,1.40,(0,front),occupied=label=="East")
    facade_box(label+"_entry_casing",entry-.73,entry+.73,.005,.115,.015,2.56,
               warm,(0,front),0,.025)
    facade_box(label+"_closed_leaf",entry-.60,entry+.60,.114,.145,.02,2.40,
               glass,(0,front),0,.018)
    for bottom,top in ((.22,1.04),(1.20,2.22)):
        facade_box(label+"_door_panel",entry-.47,entry+.47,.144,.166,bottom,top,
                   warm,(0,front),0,.012)
    facade_box(label+"_door_pull",entry+.37,entry+.42,.16,.225,1.04,1.32,
               trim,(0,front),0,.008)
for x,angle in [(-7.8,math.pi/2),(7.8,-math.pi/2)]:
    for station in (-1.8,1.8):
        window("End_lower",station,1.05,1.65,1.35,(x,0),angle)
        window("End_upper",station,3.49,1.65,1.40,(x,0),angle)
for station in (-6.45,-3.95,-1.25,1.25,3.95,6.45):
    window("Rear_lower",station,1.03,1.70,1.40,(0,-4.0),math.pi)
    window("Rear_upper",station,3.49,1.70,1.40,(0,-4.0),math.pi)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
model = bpy.context.object
model.name = "D02HouseFamily03_Mesh"
scene.cursor.location = (0,0,0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D02HouseFamily03", None)
collection.objects.link(root)
model.parent = root
root["asset_id"] = "d02_house_family.03"
root["provenance"] = "Original commissioned Blender construction; no external meshes or textures"
root["datum"] = "Ground-centred overall structural bounds; Blender +Y front = Godot -Z"
root["state"] = "Static intact closed exterior, no interior or roof traversal"

# Studio never exports; includes a hidden metre reference for editable source inspection.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.24,.29,.37,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .65
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,-.03))
ground = bpy.context.object
ground.name = "STUDIO_ground"
ground.data.materials.append(material("STUDIO_ground", "667783", .8))
bpy.ops.mesh.primitive_cube_add(size=1, location=(10,0,.5))
reference = bpy.context.object
reference.name = "STUDIO_one_metre_reference"
reference.hide_render = True


def aim(obj, target):
    """Point an isolated studio light or camera, leaving model placement unchanged."""
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()


for name, location, power, size in [("key",(-9,12,19),5000,11),
                                   ("fill",(10,4,12),2700,9),
                                   ("rim",(-3,-12,16),4300,10)]:
    data = bpy.data.lights.new("STUDIO_"+name, "AREA")
    data.energy, data.size = power, size
    lamp = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(lamp)
    lamp.location = location
    aim(lamp, (0,0,3))
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
scene.view_settings.view_transform = "AgX"
data.type, data.ortho_scale = "ORTHO", 30
camera.location = (19,25,18)
aim(camera, (0,0,3.5))
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
for name, location, target, scale in [
    ("hero",(19,27,18),(0,0,3.2),30),
    ("side",(24,-6,11),(0,0,3.2),25),
    ("entrance_detail",(7,19,8),(1.4,3.5,2.7),15),
]:
    camera.location = location
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / (name+".png"))
    bpy.ops.render.render(write_still=True)
camera.location = (0,0,47)
camera.rotation_euler = (0,0,0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
