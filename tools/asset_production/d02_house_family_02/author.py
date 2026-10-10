"""Original paired Crescents house; run only in pinned, isolated Blender CLI."""
import math
from pathlib import Path
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_house_family_02"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
# Provisional metres: attached gabled homes with a 1.2 m front setback on the east half.
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


def profile_prism(name, profile, rear, front, mat, bevel=.015):
    """Extrude a closed X/Z polygon along depth, retaining editable roof and gable solids."""
    count = len(profile)
    vertices = [(x,y,z) for y in (rear,front) for x,z in profile]
    faces = [tuple(reversed(range(count))), tuple(range(count,2*count))]
    faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    return mesh(name, vertices, faces, mat, bevel)


# The thin folded roofs expose real rendered gable walls, not dark filled roof triangles.
for label, left, ridge, right, front, peak, mat in [
    ("West", -6.8, -3.2, 0, 5.2, 7.95, slate),
    ("East", 0, 3.2, 6.8, 4.0, 7.65, plum),
]:
    # One full-height gabled wall solid avoids overlapping coplanar facade surfaces.
    wall_left, wall_right = max(left,-6.4), min(right,6.4)
    left_height = 5.65+(peak-.20-5.65)*(wall_left-left)/(ridge-left)
    right_height = 5.65+(peak-.20-5.65)*(right-wall_right)/(right-ridge)
    profile_prism(label+"_gable_volume", [(wall_left,0),(wall_right,0),
                  (wall_right,right_height),(ridge,peak-.20),(wall_left,left_height)],
                  -4.8,front-.4,wall,.01)
    profile_prism(label+"_folded_roof", [(left,5.85),(ridge,peak),(right,5.85),
                  (right,5.65),(ridge,peak-.20),(left,5.65)], -5.2,front,mat,.015)
    # Bargeboard follows the roof underside, leaving the broad planes uninterrupted.
    for y in (-5.19,front-.10):
        profile_prism(label+"_bargeboard", [(left+.02,5.65),(ridge,peak-.20),
                      (right-.02,5.65),(right-.02,5.50),(ridge,peak-.35),
                      (left+.02,5.50)], y,y+.09,trim,.008)
    box(label+"_integral_ridge", (ridge-.055,-5.15,peak-.055),
        (ridge+.055,front-.05,peak),mat,.01)
box("West_plinth", (-6.44,-4.84,0), (.04,4.84,.28), base)
box("East_plinth", (0,-4.84,0), (6.44,3.64,.28), base)
# Small valley lining is part of the joined roof, not a duplicated chimney/dormer fixture.
box("Central_valley_lining", (-.065,-5.18,5.77), (.065,3.97,5.89),base,.008)
for label, x0, x1, front in [("West",-6.4,0,4.8),("East",0,6.4,3.6)]:
    box(label+"_front_floor_course", (x0+.22,front-.005,2.88),
        (x1-.22,front+.075,3.01),trim)
    for x in (x0+.02,x1-.21):
        box(label+"_front_corner_trim", (x,front-.004,.29),
            (x+.19,front+.08,5.50),trim,.012)
box("Rear_floor_course", (-6.38,-4.87,2.88), (6.38,-4.795,3.01),trim)
for x in (-6.4,6.4):
    box("Outer_floor_course", (x-.035,-4.78,2.88), (x+.035,3.38,3.01),trim)


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


# Exactly two domestic entries; west is at the forward wall, east recessed by 1.2 m.
for label, living, entry, front in [("West",-4.55,-1.55,4.8),("East",4.55,1.55,3.6)]:
    window(label+"_living",living,1.02,2.20,1.40,(0,front),occupied=label=="West")
    window(label+"_upper_living",living,3.64,2.20,1.42,(0,front))
    window(label+"_upper_entry",entry,3.64,1.40,1.42,(0,front),occupied=label=="East")
    facade_box(label+"_entry_casing",entry-.78,entry+.78,.005,.115,.015,2.56,
               warm,(0,front),0,.025)
    facade_box(label+"_closed_leaf",entry-.65,entry+.65,.114,.145,.02,2.40,
               glass,(0,front),0,.018)
    for bottom,top in ((.22,1.04),(1.20,2.22)):
        facade_box(label+"_door_panel",entry-.52,entry+.52,.144,.166,bottom,top,
                   warm,(0,front),0,.012)
    facade_box(label+"_door_pull",entry+.42,entry+.47,.16,.225,1.04,1.32,
               trim,(0,front),0,.008)
for x,angle in [(-6.4,math.pi/2),(6.4,-math.pi/2)]:
    for station in (-2.4,2.3):
        window("Outer_lower",station,1.05,1.8,1.35,(x,0),angle)
        window("Outer_upper",station,3.65,1.8,1.40,(x,0),angle)
for station in (-4.6,-1.65,1.65,4.6):
    window("Rear_lower",station,1.03,1.8,1.40,(0,-4.8),math.pi)
    window("Rear_upper",station,3.64,1.8,1.42,(0,-4.8),math.pi)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
model = bpy.context.object
model.name = "D02HouseFamily02_Mesh"
scene.cursor.location = (0,0,0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D02HouseFamily02", None)
collection.objects.link(root)
model.parent = root
root["asset_id"] = "d02_house_family.02"
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
data.type, data.ortho_scale = "ORTHO", 28
camera.location = (19,25,18)
aim(camera, (0,0,3.5))
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
for name, location, target, scale in [
    ("hero",(19,25,18),(0,0,3.5),28),
    ("side",(22,-2,11),(0,0,3.5),23),
    ("entrance_detail",(5,17,8),(0,4.2,2.8),13),
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
