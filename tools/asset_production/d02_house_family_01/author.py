"""Original detached Crescents house; run only in pinned, isolated Blender CLI."""
import math
from pathlib import Path
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_house_family_01"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
# Provisional metres: deep main house plus a lower rear-aligned side wing.
MAIN_MIN = (-5.0, -5.3, 0.0)
MAIN_MAX = (3.0, 5.3, 5.6)
WING_MIN = (3.0, -5.3, 0.0)
WING_MAX = (5.0, 0.7, 3.15)
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


box("Main_two_storey_closed_volume", MAIN_MIN, MAIN_MAX, wall, .035)
box("Lower_side_wing_closed_volume", WING_MIN, WING_MAX, wall, .035)
# Bases terminate inside adjoining volumes rather than leaving coplanar exterior caps.
box("Main_ground_plinth", (-5.04,-5.34,0), (3.04,5.34,.28), base, .015)
box("Wing_ground_plinth", (3.04,-5.34,0), (5.04,.74,.28), base, .015)
# Deep hipped roof: broad uninterrupted planes, short central ridge, no tile noise.
box("Main_eave_fascia", (-5.4,-5.7,5.48), (3.4,5.7,5.72), trim, .025)
mesh("Main_closed_hip_roof", [(-5.4,-5.7,5.71), (3.4,-5.7,5.71),
     (3.4,5.7,5.71), (-5.4,5.7,5.71), (-5.4,-5.7,5.88),
     (3.4,-5.7,5.88), (3.4,5.7,5.88), (-5.4,5.7,5.88),
     (-1,-1.3,8.2), (-1,1.3,8.2)],
     [(0,3,2,1), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7),
      (4,5,8), (5,6,9,8), (6,7,9), (7,4,8,9)], slate, .025)
box("Short_integral_ridge_cap", (-1.065,-1.26,8.12), (-.935,1.26,8.20), slate, .02)
# Single slope over the side wing creates an asymmetric plan/height silhouette.
mesh("Wing_closed_lean_to_roof", [(2.97,-5.7,3.75), (5.4,-5.7,3.10),
     (5.4,1.1,3.10), (2.97,1.1,3.75), (2.97,-5.7,3.93), (5.4,-5.7,3.28),
     (5.4,1.1,3.28), (2.97,1.1,3.93)],
     [(0,3,2,1), (4,5,6,7), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)], plum, .02)
box("Wing_outer_fascia", (5.23,-5.67,3.0), (5.38,1.07,3.20), trim, .02)
# Domestic floor rhythm remains subordinate to the quiet roof silhouette.
box("Front_floor_course", (-4.77,5.295,2.88), (2.77,5.37,3.01), trim)
box("Back_floor_course", (-4.98,-5.37,2.88), (2.98,-5.295,3.01), trim)
box("Left_floor_course", (-5.07,-5.28,2.88), (-4.995,5.28,3.01), trim)
for x in (-4.98, 2.77):
    box("Front_corner_trim", (x,5.296,.29), (x+.21,5.38,5.46), trim, .012)


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


window("Front_living", -2.70,1.02,2.35,1.40,(0,5.3),occupied=True)
window("Front_upper_left", -2.70,3.64,2.35,1.42,(0,5.3))
window("Front_upper_right", 1.12,3.64,1.65,1.42,(0,5.3),occupied=True)
# West elevation is fully visible; east ground floor belongs to the side wing.
for station in (-2.8, 2.8):
    window("West_lower", station,1.05,1.85,1.35,(-5,0),math.pi/2)
    window("West_upper", station,3.65,1.85,1.40,(-5,0),math.pi/2)
# This rear upper sill clears the attached wing roof rather than intersecting its flashing line.
window("East_upper", 1.8,4.12,1.9,.93,(3,0),-math.pi/2)
window("East_upper_front", -3.1,3.65,1.6,1.40,(3,0),-math.pi/2)
window("Wing_east", 2.6,1.08,2.20,1.25,(5,0),-math.pi/2)
window("Wing_front", 4,1.05,1.1,1.35,(0,.7))
for station in (-1.0, 2.7):
    window("Rear_lower", station,1.03,1.85,1.40,(0,-5.3),math.pi)
    window("Rear_upper", station,3.64,1.85,1.42,(0,-5.3),math.pi)
# One closed, grade-level entrance. Porch canopies remain a separately owned fixture.
facade_box("Warm_entry_casing", .34,1.90,.005,.115,.015,2.56,warm,(0,5.3),0,.025)
facade_box("Closed_entry_leaf", .47,1.77,.114,.145,.02,2.40,glass,(0,5.3),0,.018)
facade_box("Entry_lower_panel", .60,1.64,.144,.166,.22,1.04,warm,(0,5.3),0,.012)
facade_box("Entry_upper_panel", .60,1.64,.144,.166,1.20,2.22,warm,(0,5.3),0,.012)
facade_box("Entry_pull", 1.54,1.59,.16,.225,1.04,1.32,trim,(0,5.3),0,.008)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
model = bpy.context.object
model.name = "D02HouseFamily01_Mesh"
scene.cursor.location = (0,0,0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D02HouseFamily01", None)
collection.objects.link(root)
model.parent = root
root["asset_id"] = "d02_house_family.01"
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
bpy.ops.mesh.primitive_cube_add(size=1, location=(8,0,.5))
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
data.type, data.ortho_scale = "ORTHO", 23
camera.location = (16,21,16)
aim(camera, (0,0,3.5))
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
for name, location, target, scale in [
    ("hero",(16,21,16),(0,0,3.5),23),
    ("side",(22,-2,11),(0,0,3.5),21),
    ("entrance_detail",(5,17,8),(.0,5.2,2.65),10),
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
