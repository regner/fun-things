"""Author the original continuous Signal Row parade; pinned Blender CLI only."""
import math
from pathlib import Path
import runpy

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_southern_shopping_parade_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
WIDTH, LENGTH, HEIGHT = 18.0, 60.0, 5.4
BAY_CENTRES = (25, 15, 5, -5, -15, -25)
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
root = bpy.data.objects.new("D06SouthernShoppingParade01", None)
collection.objects.link(root)
root["asset_id"] = "d06_southern_shopping_parade.01"
root["provenance"] = "Original Blender construction; no external geometry or textures"
root["datum"] = "Ground-centred 18x60m; north +Y Blender / -Z Godot; primary facade west -X"
parts = []


def material(name, swatch, metal=0, rough=.7):
    """Create opaque palette material from an sRGB reference swatch."""
    rgb = [int(swatch[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*linear, 1)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*linear, 1)
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Roughness"].default_value = rough
    return mat


wall = material("parade_muted_plum_render", "81777C")
roof = material("parade_quiet_blue_roof", "405B68", .12, .65)
trim = material("parade_warm_structural_trim", "BBB6A8")
base = material("parade_slate_plinth", "4A5358")
recess = material("parade_dark_coping_recess", "334950", .2, .55)


def mesh(name, vertices, faces, mat, bevel=0):
    """Build an editable closed component with applied architectural edge treatment."""
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
        modifier.segments = 3
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        for polygon in data.polygons:
            polygon.use_smooth = True
        modifier = obj.modifiers.new("Broad plane normals", "WEIGHTED_NORMAL")
        modifier.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    parts.append(obj)
    return obj


def box(name, lo, hi, mat, bevel=.015):
    """Author a solid bounded architectural component, not a runtime primitive."""
    a, b, c = lo
    d, e, f = hi
    vertices = [(a,b,c), (d,b,c), (d,e,c), (a,e,c),
                (a,b,f), (d,b,f), (d,e,f), (a,e,f)]
    faces = [(0,3,2,1), (4,5,6,7), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)]
    return mesh(name, vertices, faces, mat, bevel)


def west_facade():
    """Weld the entire 60 m frontage grid around six standard fitting apertures."""
    us = {-30, 30}
    for centre in BAY_CENTRES:
        us.update(centre + offset for offset in (-3.2, -2.47, .57, 1.24, 2.66, 3.2))
    us = sorted(us)
    zs = [0, .54, 2.42, 2.45, 5.25]
    vertices, indices, surfaces = [], {}, {}
    for a, b in zip(us, us[1:]):
        for c, d in zip(zs, zs[1:]):
            u, z = (a + b) / 2, (c + d) / 2
            if any((-2.47 < u - station < .57 and .54 < z < 2.42) or
                   (1.24 < u - station < 2.66 and 0 < z < 2.45)
                   for station in BAY_CENTRES):
                continue
            coords = [(-9,a,c), (-8.72,a,c), (-8.72,b,c), (-9,b,c),
                      (-9,a,d), (-8.72,a,d), (-8.72,b,d), (-9,b,d)]
            ids = []
            for point in coords:
                if point not in indices:
                    indices[point] = len(vertices)
                    vertices.append(point)
                ids.append(indices[point])
            for face in [(0,3,2,1), (4,5,6,7), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)]:
                value = tuple(ids[i] for i in face)
                key = tuple(sorted(value))
                if key in surfaces:
                    del surfaces[key]
                else:
                    surfaces[key] = value
    mesh("Continuous_west_wall_six_aperture_pairs", vertices, list(surfaces.values()), wall)


west_facade()
box("Continuous_rear_service_wall", (8.72,-30,0), (9,30,5.25), wall, 0)
box("North_end_reserved_for_member_03", (-8.72,29.72,0), (8.72,30,5.25), wall, 0)
box("South_end_wall", (-8.72,-30,0), (8.72,-29.72,5.25), wall, 0)
# Opaque backers close the visual volume without introducing an interior or duplicate fittings.
for number, centre in enumerate(BAY_CENTRES, 1):
    box(f"Bay_{number:02}_recess_backer", (-8.40,centre-2.60,0),
        (-8.30,centre+2.80,2.60), recess, 0)
    # Plinth gaps leave the shared entry surround's insertion and threshold clear.
    box(f"Bay_{number:02}_plinth", (-9.035,centre-3.2,0), (-8.70,centre+1.10,.30), base, 0)
# Continuous horizontal courses prevent a row-of-pavilions read.
box("West_head_course", (-9.04,-30,4.48), (-8.64,30,4.63), trim)
box("Rear_head_course", (8.64,-30,4.48), (9.04,30,4.63), trim)
box("Rear_plinth", (8.70,-30,0), (9.035,30,.30), base, 0)
for y in (-30.035, 29.735):
    box("End_plinth", (-8.70,y,0), (8.70,y+.30,.30), base, 0)
# One uninterrupted roof pan with four continuous perimeter caps, no separate tenant roofs.
box("Single_continuous_roof_pan", (-8.72,-29.72,4.95), (8.72,29.72,5.13), roof, .04)
for x in (-9, 8.58):
    box("Long_parapet_coping", (x,-30,5.25), (x+.42,30,5.40), recess, .03)
for y in (-30, 29.58):
    box("End_parapet_coping", (-8.58,y,5.25), (8.58,y+.42,5.40), recess, .03)
for x in (-3, 3):
    box("Quiet_longitudinal_roof_fold", (x-.035,-29.50,5.125),
        (x+.035,29.50,5.175), roof, .012)
# Quiet broad structural bay piers stay outside the standard 6.4 m fitting stations.
for y in (-30, -20.22, -10.22, -.22, 9.78, 19.78, 29.56):
    box("West_structural_pier", (-9.045,y,.30), (-8.68,y+.44,4.48), trim)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
model = bpy.context.object
model.name = "D06SouthernShoppingParade01_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
model.parent = root

# Mounts preserve the accepted 6.4 m shop interface in each local facade frame.
mounts = {"entrance_single": (1.95,0), "door_single": (1.95,0),
          "display_window": (-.95,.48), "canopy": (-.95,3), "fascia": (-.95,3.8)}
for side, x, angle in (("west", -9, math.pi/2), ("east", 9, -math.pi/2)):
    for number, centre in enumerate(BAY_CENTRES, 1):
        station = bpy.data.objects.new(f"{side}_bay_{number:02}", None)
        collection.objects.link(station)
        station.parent = root
        station.location = (x, centre, 0)
        station.rotation_euler.z = angle
        for name, (u, z) in mounts.items():
            marker = bpy.data.objects.new(f"{side}_bay_{number:02}_mount_{name}", None)
            collection.objects.link(marker)
            marker.parent = station
            marker.location = (u, 0, z)
# North facade and forecourt anchor are interfaces only; no bridge or ground built here.
marker = bpy.data.objects.new("north_facade_datum", None)
collection.objects.link(marker)
marker.parent = root
marker.location = (0, 30, 0)

# Isolated studio is not an export member.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.24,.28,.34,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .7
bpy.ops.mesh.primitive_plane_add(size=250, location=(0,0,-.025))
ground = bpy.context.object
ground.name = "STUDIO_ground"
ground.data.materials.append(material("STUDIO_ground", "687780"))
bpy.ops.mesh.primitive_cube_add(size=1, location=(13,0,.5))
reference = bpy.context.object
reference.name = "STUDIO_one_metre_reference"
reference.hide_render = True


def aim(obj, target):
    """Aim a studio camera or light without affecting export transforms."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


for name, location, power, size in [("key",(-20,20,45),42000,35),
                                     ("fill",(25,-20,30),30000,30)]:
    data = bpy.data.lights.new("STUDIO_" + name, "AREA")
    data.energy, data.size = power, size
    lamp = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(lamp)
    lamp.location = location
    aim(lamp, (0,0,0))
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new(data.name, data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"
data.type = "ORTHO"
data.ortho_scale = 73
camera.location = (-52,65,53)
aim(camera, (0,0,2))
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
for name, location, target, scale in [
    ("hero", (-52,65,53), (0,0,2), 73),
    ("side", (-60,8,19), (0,0,2.5), 68),
    ("bay_detail", (-22,24,10), (-8,23,2.6), 15),
]:
    camera.location = location
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.resolution_x, scene.render.resolution_y = 1280, 800
    scene.render.filepath = str(EVIDENCE / (name + ".png"))
    bpy.ops.render.render(write_still=True)
# A 60 m north/south shell cannot fit the ~32 m roof-height vertical frustum.
# Keep the mandated camera unmodified and deliberately show a central gameplay crop.
camera.location = (-6,0,47)
camera.rotation_euler = (0,0,0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
