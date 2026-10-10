"""Original compact Crescents corner home; run only in pinned, isolated Blender CLI."""
import math
from pathlib import Path
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_house_family_04"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
# Provisional metres: compact L footprint and perpendicular, unequal-height gables.
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


def prism(name, profile, start, end, mat, along_x=False, bevel=.012):
    """Extrude a closed gable/roof section on either axis for the corner's crossed ridges."""
    count = len(profile)
    vertices = [(depth,u,z) if along_x else (u,depth,z)
                for depth in (start,end) for u,z in profile]
    faces = [tuple(reversed(range(count))), tuple(range(count,2*count))]
    faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    return mesh(name, vertices, faces, mat, bevel)


# Two continuous gabled volumes form one closed L shell. The wing extends under the
# main roof to conceal its end; a source Boolean removes coplanar internal wall faces.
main = prism("Main_closed_volume", [(-4.2,0),(.6,0),(.6,5.691818),
             (-1.8,7.35),(-4.2,5.691818)], -4.2,4.2,wall,bevel=0)
wing = prism("Wing_closed_volume", [(-4.2,0),(.6,0),(.6,5.61),
             (-1.8,6.70),(-4.2,5.61)], -1.8,4.2,wall,along_x=True,bevel=0)
bpy.context.view_layer.objects.active = main
modifier = main.modifiers.new("Continuous corner shell", "BOOLEAN")
modifier.operation = "UNION"
modifier.solver = "EXACT"
modifier.object = wing
bpy.ops.object.modifier_apply(modifier=modifier.name)
parts.remove(wing)
bpy.data.objects.remove(wing, do_unlink=True)
# The two roof solids intersect along natural valleys, without duplicate coplanar planes.
for label, start, end, peak, mat, along_x in [
    ("Main",-4.55,4.55,7.55,slate,False),
    ("Wing",-1.8,4.55,6.90,plum,True),
]:
    profile = [(-4.55,5.65),(-1.8,peak),(.95,5.65),
               (.95,5.45),(-1.8,peak-.20),(-4.55,5.45)]
    roof = prism(label+"_folded_roof",profile,start,end,mat,along_x)
    if along_x:
        # Trim the hidden wing below the main roof plane. Merely overlapping both
        # roofs exposes an unwanted plum shelf through the rear gable overhang.
        cutter = prism("TEMP_main_roof_clearance",[(-4.55,0),(.95,0),(.95,5.65),
                       (-1.8,7.55),(-4.55,5.65)],-4.6,4.6,slate,bevel=0)
        bpy.context.view_layer.objects.active = roof
        modifier = roof.modifiers.new("Wing valley cut", "BOOLEAN")
        modifier.operation = "DIFFERENCE"
        modifier.solver = "EXACT"
        modifier.object = cutter
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        parts.remove(cutter)
        bpy.data.objects.remove(cutter, do_unlink=True)
    # Only exposed gable ends get fascia; no buried trim traverses the valley.
    ends = (start+.015,end-.10) if not along_x else (end-.10,)
    for edge in ends:
        prism(label+"_bargeboard",[(-4.53,5.45),(-1.8,peak-.20),(.93,5.45),
              (.93,5.29),(-1.8,peak-.36),(-4.53,5.29)],edge,edge+.085,trim,along_x,.008)
    if along_x:
        box("Wing_integral_ridge",(-1.76,-1.855,peak-.055),(4.51,-1.745,peak),mat,.01)
    else:
        box("Main_integral_ridge",(-1.855,-4.51,peak-.055),(-1.745,4.51,peak),mat,.01)
box("West_eave_fascia",(-4.54,-4.53,5.29),(-4.46,4.53,5.45),trim)
box("Main_recess_eave_fascia",(.86,.96,5.29),(.94,4.53,5.45),trim)
box("Wing_recess_eave_fascia",(.96,.86,5.29),(4.53,.94,5.45),trim)
box("Wing_rear_eave_fascia",(.96,-4.54,5.29),(4.53,-4.46,5.45),trim)
# Exterior plinth strips only: avoid a coplanar doubled slab at the return.
for label,lo,hi in [
    ("Front",(-4.24,4.17,0),(.64,4.24,.28)),
    ("West",(-4.24,-4.24,0),(-4.17,4.17,.28)),
    ("Rear",(-4.17,-4.24,0),(4.24,-4.17,.28)),
    ("East",(4.17,-4.17,0),(4.24,.64,.28)),
    ("Entry_return",(.6,.57,0),(4.17,.64,.28)),
    ("Main_return",(.57,.64,0),(.64,4.17,.28)),
]:
    box(label+"_plinth",lo,hi,base)


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


# Front and east elevations both read as domestic street faces. The sole warm entry
# sits within the open corner setback, not at a shop-like chamfer or on a new porch.
for bottom in (1.02,3.49):
    window("Front_pair",-1.8,bottom,2.65,1.40,(0,4.2),occupied=bottom==1.02)
    window("East_pair",1.8,bottom,2.65,1.40,(4.2,0),-math.pi/2)
    window("Return_main",-2.6,bottom,1.45,1.40,(.6,0),-math.pi/2)
    window("Rear_west",1.8,bottom,2.20,1.40,(0,-4.2),math.pi)
    window("Rear_east",-2.4,bottom,2.10,1.40,(0,-4.2),math.pi)
    for station in (-2.2,2.2):
        window("West_pair",station,bottom,1.9,1.40,(-4.2,0),math.pi/2)
window("Entry_upper",2.6,3.49,1.55,1.40,(0,.6),occupied=True)
entry = 2.6
facade_box("Entry_casing",entry-.78,entry+.78,.005,.115,.015,2.56,
           warm,(0,.6),0,.025)
facade_box("Closed_leaf",entry-.65,entry+.65,.114,.145,.02,2.40,
           glass,(0,.6),0,.018)
for bottom,top in ((.22,1.04),(1.20,2.22)):
    facade_box("Door_panel",entry-.52,entry+.52,.144,.166,bottom,top,
               warm,(0,.6),0,.012)
facade_box("Door_pull",entry+.42,entry+.47,.16,.225,1.04,1.32,
           trim,(0,.6),0,.008)
# Courses and corner piers are facade-bound with deliberate non-overlapping ends.
for name, origin, angle, left, right in [
    ("Front",(0,4.2),0,-4.2,.6), ("East",(4.2,0),-math.pi/2,-4.2,.6),
    ("Return_entry",(0,.6),0,.6,4.2), ("Return_main",(.6,0),-math.pi/2,.6,4.2),
    ("Rear",(0,-4.2),math.pi,-4.2,4.2), ("West",(-4.2,0),math.pi/2,-4.2,4.2),
]:
    # East-facing local u maps to Blender -Y; its occupied span is -.6..4.2.
    if name == "East":
        left,right = -.6,4.2
    elif name == "Return_main":
        left,right = -4.2,-.6
    facade_box(name+"_course",left+.22,right-.22,.005,.075,2.78,2.91,
               trim,origin,angle)
    for u in (left+.02,right-.21):
        facade_box(name+"_pier",u,u+.19,.005,.08,.29,5.18,trim,origin,angle)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
model = bpy.context.object
model.name = "D02HouseFamily04_Mesh"
scene.cursor.location = (0,0,0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D02HouseFamily04", None)
collection.objects.link(root)
model.parent = root
root["asset_id"] = "d02_house_family.04"
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
data.type, data.ortho_scale = "ORTHO", 22
camera.location = (19,25,18)
aim(camera, (0,0,3.5))
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
for name, location, target, scale in [
    ("hero",(19,25,18),(0,0,3.2),22),
    ("side",(22,-15,13),(0,0,3.2),21),
    ("entrance_detail",(14,17,9),(1.2,1.8,2.65),12),
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
