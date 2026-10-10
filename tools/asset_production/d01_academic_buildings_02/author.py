"""Original Northpoint long teaching wing; isolated Blender source and evidence."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_academic_buildings_02"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
EAVE_HEIGHT, RIDGE_HEIGHT = 9.5, 12.25


def material(name, color, metallic=0.0, roughness=0.5):
    """Create an opaque, back-culled Principled surface without external textures."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*color, 1)
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return result


def finish(obj, name, mat, bevel=0.03):
    """Apply transforms and small edge radii, then clean and weight static normals."""
    obj.name = name
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new("Soft architectural edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 1
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=0.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    for face in obj.data.polygons:
        face.use_smooth = True
    modifier = obj.modifiers.new("Weighted architectural normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    parts.append(obj)
    return obj


def box(name, position, size, mat, bevel=0.03, yaw=0.0):
    """Build a closed bevelled block in the original Blender export collection."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.dimensions = size
    obj.rotation_euler.z = yaw
    return finish(obj, name, mat, bevel)


def aim(obj, target):
    """Aim an isolated studio light or camera, never exported geometry."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def light(name, position, energy, size):
    """Add broad studio fill outside the named export collection."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (0, 0, 3))


def prism(name, outline, depth, position, mat, yaw=0, bevel=.015):
    """Extrude a closed X/Z profile along Y, for gables and the blind entrance arch."""
    count = len(outline)
    vertices = [(x, y, z) for y in (-depth / 2, depth / 2) for x, z in outline]
    faces = [tuple(reversed(range(count))), tuple(range(count, 2 * count))]
    faces += [(i, (i + 1) % count, (i + 1) % count + count, i + count)
              for i in range(count)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = position
    obj.rotation_euler.z = yaw
    return finish(obj, name, mat, bevel)


def window(name, x, y, z, yaw=0, width=1.85, height=3.1):
    """Place a tall paired-light opaque window with broad pale stone framing."""
    facing = Vector((-math.sin(yaw), math.cos(yaw), 0))
    origin = Vector((x, y, z))
    box(name + ' surround', origin, (width + .32, .16, height + .32), stone, .025, yaw)
    box(name + ' dark glass', origin + facing * .09,
        (width, .05, height), glass, .012, yaw)
    box(name + ' mullion', origin + facing * .13,
        (.09, .04, height), stone, .01, yaw)
    box(name + ' transom', origin + facing * .13 + Vector((0, 0, .58)),
        (width, .04, .10), stone, .01, yaw)
    box(name + ' sill', origin + facing * .035 - Vector((0, 0, height / 2 + .17)),
        (width + .55, .25, .15), stone, .025, yaw)


def roof_bar(name, width, length, position, yaw=0):
    """Build a solid pitched roof with a quiet slate field and raised ridge cap."""
    prism(name, [(-width / 2, EAVE_HEIGHT), (width / 2, EAVE_HEIGHT),
                 (0, RIDGE_HEIGHT)], length, position, slate, yaw, .03)
    box(name + ' ridge', Vector(position) + Vector((0, 0, RIDGE_HEIGHT)),
        (.24, length, .16), green, .035, yaw)


assert bpy.app.version_string == '5.2.2 LTS'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f'export_{NID}')
scene.collection.children.link(collection)
parts = []
brick = material('academic_brick', (.32, .105, .065), 0, .72)
stone = material('academic_pale_stone', (.70, .64, .49), 0, .62)
base = material('academic_base_stone', (.25, .27, .25), 0, .7)
slate = material('academic_slate_roof', (.065, .105, .155), .12, .52)
green = material('academic_field_green', (.028, .115, .095), .15, .48)
glass = material('academic_opaque_glass', (.023, .071, .085), .22, .3)
amber = material('academic_occupied_amber', (.85, .43, .11), .06, .42)
mint = material('academic_wayfinding_mint', (.23, .70, .52), .05, .42)

# One separate teaching building: a long closed bar, lower than the main hall.
box('Continuous foundation', (0, 0, .25), (36.4, 10.4, .5), base, .025)
box('Teaching wing brick walls', (0, 0, 4.75), (36, 10, 9), brick, .04)
box('Low stone belt', (0, 0, .8), (36.16, 10.16, .3), stone)
box('Storey string', (0, 0, 4.8), (36.20, 10.20, .2), stone)
box('Pale cornice', (0, 0, 9.27), (36.38, 10.38, .3), stone)
box('Green eave', (0, 0, 9.47), (37.2, 11.2, .14), green)
roof_bar('Long slate roof', 11.2, 37.2, (0, 0, 0), math.pi / 2)
# A single cross-gable identifies the entrance without competing with the hall clock tower.
roof_bar('Entry cross gable', 6.4, 5.6, (0, 2.8, 0))
prism('Entry pale pediment', [(-3.2, 9.5), (3.2, 9.5), (0, 12.22)],
      .12, (0, 5.6, 0), stone, bevel=.02)
prism('Entry green tympanum', [(-2.5, 9.78), (2.5, 9.78), (0, 11.90)],
      .06, (0, 5.69, 0), green, bevel=.02)
box('Entry pediment base', (0, 5.57, 9.55), (6.65, .35, .2), stone)
# End gable fields tie to the hall's pale/green pediments, but without clock or oculi.
for x, yaw in [(-18.6, math.pi / 2), (18.6, -math.pi / 2)]:
    prism('End pale pediment', [(-5.6, 9.5), (5.6, 9.5), (0, 12.22)],
          .12, (x, 0, 0), stone, yaw, .02)
    offset = -.09 if x < 0 else .09
    prism('End green tympanum', [(-4.6, 9.79), (4.6, 9.79), (0, 11.89)],
          .06, (x + offset, 0, 0), green, yaw, .02)
# Tall paired lights on two storeys, with broad bays rather than texture noise.
for z in (2.65, 7.10):
    for x in (-15.75, -11.25, -6.75, 6.75, 11.25, 15.75):
        window('Front teaching bay', x, 5.025, z, width=2.15, height=2.85)
    for x in (-15.75, -11.25, -6.75, -2.25, 2.25, 6.75, 11.25, 15.75):
        window('Rear teaching bay', x, -5.025, z, math.pi, width=2.15, height=2.85)
    for y in (-2.35, 2.35):
        window('West end bay', -18.025, y, z, math.pi / 2, width=1.85, height=2.85)
        window('East end bay', 18.025, y, z, -math.pi / 2, width=1.85, height=2.85)
window('Entry upper bay', 0, 5.025, 7.10, width=2.25, height=2.85)
# Narrow pale pilasters distinguish the central portal while staying above the same plinth.
for x in (-2.75, 2.75):
    box('Portal pilaster', (x, 5.04, 4.7), (.35, .16, 8.95), stone, .025)
for x in (-17.78, 17.78):
    for y in (-4.96, 4.96):
        for z in (1.65, 3.45, 5.85, 8.25):
            box('Restrained corner quoin', (x, y, z), (.45, .25, .7), stone, .025)
# Closed amber paired door: no porch, stairs, interior or implied through route.
box('Portal pale surround', (0, 5.03, 2.15), (3.65, .16, 4.3), stone, .025)
box('Closed amber entry', (0, 5.135, 2.0), (3.1, .07, 4), amber, .025)
box('Entry head transom', (0, 5.185, 3.15), (3.0, .035, .13), green, .01)
box('Entry centre stile', (0, 5.185, 1.55), (.10, .035, 3.1), green, .01)
for x in (-.8, .8):
    box('Door field frame', (x, 5.18, 1.7), (1.25, .035, 2.30), green, .02)
    box('Door amber inset', (x, 5.2075, 1.75), (1.04, .025, 2.02), amber, .015)
    box('Door pull', (x * .24, 5.245, 1.6), (.05, .035, .5), stone, .01)
for x in (-2.12, 2.12):
    box('Mint entrance route accent', (x, 5.08, 2.95), (.16, .12, 1.05), mint, .025)

# One material-batched mesh under a metre-scale ground-centred export root.
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = 'D01AcademicBuildings02_Mesh'
obj.data.name = 'D01AcademicBuildings02_Geometry'
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
root = bpy.data.objects.new('D01AcademicBuildings02', None)
collection.objects.link(root)
obj.parent = root
root['asset_id'] = 'd01_academic_buildings.02'
root['authorship'] = 'Original Blender construction by commissioned production worker'
root['front_axis'] = 'Blender +Y maps to Godot -Z; +Z maps to +Y'
root['ground_pivot'] = 'Centre of rectangular teaching-wing footprint at ground zero'

scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.22, .28, .35, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .65
bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, -.025))
bpy.context.object.name = 'STUDIO_ground'
bpy.context.object.data.materials.append(material('STUDIO_slate', (.13, .18, .19)))
light('STUDIO_key', (25, 40, 60), 65000, 35)
light('STUDIO_rim', (-35, -25, 45), 55000, 30)
light('STUDIO_fill', (-15, 35, 25), 24000, 25)
data = bpy.data.cameras.new('STUDIO_camera')
camera = bpy.data.objects.new('STUDIO_camera', data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.compression = 95
scene.render.image_settings.color_mode = 'RGB'
scene.render.image_settings.color_depth = '8'
scene.render.dither_intensity = 0
scene.view_settings.view_transform = 'AgX'
scene.render.resolution_x = 1120
scene.render.resolution_y = 630
camera.location = (44, 58, 35)
aim(camera, (0, 0, 5))
data.type = 'ORTHO'
data.ortho_scale = 54
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / 'export.py').read_text(), 'export.py', 'exec'))
for name, position, target, scale in [
    ('hero', (44, 58, 35), (0, 0, 5), 54),
    ('side', (42, -52, 27), (0, 0, 5), 52),
    ('entrance_detail', (6, 30, 15), (0, 5, 5.4), 23),
]:
    camera.location = position
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f'{name}.png')
    bpy.ops.render.render(write_still=True)
# Calibrated vertical-down view: long axis runs across the landscape viewport.
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type = 'PERSP'
data.sensor_fit = 'VERTICAL'
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / 'overhead_47m_42deg.png')
bpy.ops.render.render(write_still=True)
