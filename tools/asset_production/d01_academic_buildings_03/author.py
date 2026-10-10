"""Original Northpoint compact annex; isolated Blender source and evidence."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_academic_buildings_03"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
EAVE_HEIGHT, RIDGE_HEIGHT = 5.3, 8.15


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
    # Layer the transom above the mullion; coplanar crossing faces cause a dark render speck.
    box(name + ' transom', origin + facing * .155 + Vector((0, 0, .58)),
        (width, .04, .10), stone, .01, yaw)
    box(name + ' sill', origin + facing * .035 - Vector((0, 0, height / 2 + .17)),
        (width + .55, .25, .15), stone, .025, yaw)


def hip_roof():
    """Construct one closed four-slope roof, lower and squarer than the other campus roofs."""
    vertices = [(-7.6, -6.6, EAVE_HEIGHT), (7.6, -6.6, EAVE_HEIGHT),
                (7.6, 6.6, EAVE_HEIGHT), (-7.6, 6.6, EAVE_HEIGHT),
                (0, -2.6, RIDGE_HEIGHT), (0, 2.6, RIDGE_HEIGHT)]
    faces = [(3, 2, 1, 0), (0, 1, 4), (1, 2, 5, 4), (2, 3, 5), (3, 0, 4, 5)]
    mesh = bpy.data.meshes.new('Compact hipped roof')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new('Compact hipped roof', mesh)
    collection.objects.link(obj)
    finish(obj, 'Compact hipped slate roof', slate, .025)
    box('Short green ridge', (0, 0, RIDGE_HEIGHT), (.24, 5.2, .16), green, .035)


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

# A small single-storey volume keeps the annex subordinate to the hall and teaching wing.
box('Continuous foundation', (0, 0, .25), (14.4, 12.4, .5), base, .025)
box('Annex brick walls', (0, 0, 2.65), (14, 12, 4.8), brick, .04)
box('Low stone belt', (0, 0, .8), (14.16, 12.16, .3), stone)
box('Pale cornice', (0, 0, 5.07), (14.38, 12.38, .3), stone)
box('Green eave', (0, 0, 5.27), (15.2, 13.2, .14), green)
hip_roof()
# Tall windows retain the collegiate rhythm, without a second storey or noisy roof furniture.
for x in (-4.2, 4.2):
    window('Front annex bay', x, 6.025, 2.7, width=2.05, height=2.8)
for x in (-4.2, 0, 4.2):
    window('Rear annex bay', x, -6.025, 2.7, math.pi, width=2.05, height=2.8)
for y in (-3.9, 0, 3.9):
    window('West annex bay', -7.025, y, 2.7, math.pi / 2, width=1.85, height=2.8)
    window('East annex bay', 7.025, y, 2.7, -math.pi / 2, width=1.85, height=2.8)
for x in (-6.78, 6.78):
    for y in (-5.96, 5.96):
        for z in (1.65, 3.55):
            box('Restrained corner quoin', (x, y, z), (.45, .25, .7), stone, .025)
# A shallow blind pediment marks a closed portal, not a porch or an elevated route.
box('Portal pale surround', (0, 6.03, 2.05), (3.45, .16, 4.1), stone, .025)
prism('Portal pale pediment', [(-1.85, 4.1), (1.85, 4.1), (0, 5.05)],
      .18, (0, 6.035, 0), stone, bevel=.02)
prism('Portal green tympanum', [(-1.30, 4.24), (1.30, 4.24), (0, 4.90)],
      .04, (0, 6.15, 0), green, bevel=.01)
box('Closed amber entry', (0, 6.135, 1.9), (2.9, .07, 3.8), amber, .025)
box('Entry head transom', (0, 6.185, 3.05), (2.8, .035, .13), green, .01)
box('Entry centre stile', (0, 6.185, 1.5), (.10, .035, 3), green, .01)
for x in (-.75, .75):
    box('Door field frame', (x, 6.18, 1.6), (1.2, .035, 2.3), green, .02)
    box('Door amber inset', (x, 6.2075, 1.65), (1.0, .025, 2.02), amber, .015)
    box('Door pull', (x * .24, 6.245, 1.6), (.05, .035, .5), stone, .01)
for x in (-2.08, 2.08):
    box('Mint entrance route accent', (x, 6.08, 2.95), (.16, .12, 1.05), mint, .025)

# One material-batched mesh under a metre-scale ground-centred export root.
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = 'D01AcademicBuildings03_Mesh'
obj.data.name = 'D01AcademicBuildings03_Geometry'
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
root = bpy.data.objects.new('D01AcademicBuildings03', None)
collection.objects.link(root)
obj.parent = root
root['asset_id'] = 'd01_academic_buildings.03'
root['authorship'] = 'Original Blender construction by commissioned production worker'
root['front_axis'] = 'Blender +Y maps to Godot -Z; +Z maps to +Y'
root['ground_pivot'] = 'Centre of rectangular annex footprint at ground zero'

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
camera.location = (26, 34, 24)
aim(camera, (0, 0, 3.2))
data.type = 'ORTHO'
data.ortho_scale = 29
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / 'export.py').read_text(), 'export.py', 'exec'))
for name, position, target, scale in [
    ('hero', (26, 34, 24), (0, 0, 3.2), 29),
    ('side', (26, -34, 20), (0, 0, 3.2), 29),
    ('entrance_detail', (5, 27, 10), (0, 6, 2.9), 12),
]:
    camera.location = position
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f'{name}.png')
    bpy.ops.render.render(write_still=True)
# Calibrated vertical-down view: the full compact roof fits without reframing.
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type = 'PERSP'
data.sensor_fit = 'VERTICAL'
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / 'overhead_47m_42deg.png')
bpy.ops.render.render(write_still=True)
