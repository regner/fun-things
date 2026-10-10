"""Original Northpoint main university hall; isolated Blender source and evidence."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_academic_buildings_01"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
EAVE_HEIGHT, RIDGE_HEIGHT = 10.8, 14.1


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


def clock(name, position, yaw):
    """Author an integrated static 10:10 clock face, indices and hands without fonts."""
    origin = Vector(position)
    facing = Vector((-math.sin(yaw), math.cos(yaw), 0))
    across = Vector((math.cos(yaw), math.sin(yaw), 0))
    for suffix, radius, depth, offset, mat in [
        (' stone rim', 1.34, .16, 0, stone), (' face', 1.14, .06, .105, ivory)
    ]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth,
                                           location=origin + facing * offset)
        obj = bpy.context.object
        obj.rotation_euler = (math.pi / 2, 0, yaw)
        finish(obj, name + suffix, mat, .015)
    for index in range(12):
        angle = index * math.tau / 12
        point = origin + facing * .151 + across * (.94 * math.sin(angle))
        point += Vector((0, 0, .94 * math.cos(angle)))
        box(name + ' hour index', point, (.075, .035, .13), green, .008, yaw)
    # Hands are enclosed beams between the centre and the 10 / 2 positions.
    for angle, length in [(-math.pi / 3, .65), (math.pi / 3, .85)]:
        delta = across * (length * math.sin(angle)) + Vector((0, 0, length * math.cos(angle)))
        box_obj = box(name + ' hand', origin + facing * .177 + delta / 2,
                      (.09, .05, length), green, .012, yaw)
        # Rotate around the face normal after positioning; apply before joining.
        rotation = Vector((0, 0, 1)).rotation_difference(delta.normalized())
        box_obj.rotation_mode = 'QUATERNION'
        box_obj.rotation_quaternion = rotation
        bpy.context.view_layer.objects.active = box_obj
        bpy.ops.object.select_all(action='DESELECT')
        box_obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


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
ivory = material('academic_clock_ivory', (.90, .84, .64), 0, .5)

# Three closed masses leave an actual U court; no mesh ground, interiors or stairs.
for name, x, y, width, depth in [('Main hall', 0, -14, 44, 12),
                               ('West connected wing', -17, 6, 10, 28),
                               ('East connected wing', 17, 6, 10, 28)]:
    box(name + ' foundation', (x, y, .25), (width + .4, depth + .4, .5), base, .025)
    box(name + ' brick walls', (x, y, 5.5), (width, depth, 10.5), brick, .04)
    box(name + ' low stone belt', (x, y, .8), (width + .16, depth + .16, .3), stone)
    box(name + ' storey string', (x, y, 5.45), (width + .20, depth + .20, .20), stone)
    box(name + ' pale cornice', (x, y, 10.55), (width + .38, depth + .38, .30), stone)
    box(name + ' green eave', (x, y, 10.77), (width + 1.2, depth + 1.2, .14), green)
# Main roof lies across the rear; attached wings run towards the open court mouth.
roof_bar('Main cross roof', 13.2, 45.2, (0, -14, 0), math.pi / 2)
roof_bar('West wing roof', 11.2, 34.6, (-17, 3.3, 0))
roof_bar('East wing roof', 11.2, 34.6, (17, 3.3, 0))
# Broad ordered bays: no brick/roof-tile noise at gameplay distance.
for z in (2.95, 7.95):
    for x in (-18, -13.5, -9, -4.5, 0, 4.5, 9, 13.5, 18):
        window('Rear hall bay', x, -20.025, z, math.pi)
    for x in (-9, -5, 5, 9):
        window('Court hall bay', x, -7.975, z)
    for y in (-16, -11):
        window('Hall west end', -22.025, y, z, math.pi / 2)
        window('Hall east end', 22.025, y, z, -math.pi / 2)
    for y in (-4, 1, 6, 11, 16):
        window('West wing outer', -22.025, y, z, math.pi / 2)
        window('West wing court', -11.975, y, z, -math.pi / 2)
        window('East wing outer', 22.025, y, z, -math.pi / 2)
        window('East wing court', 11.975, y, z, math.pi / 2)
    for x in (-19.65, -17, -14.35, 14.35, 17, 19.65):
        window('Wing front bay', x, 20.025, z, width=1.55)
# Stone corner accents, not a repetitive brick texture.
for x in (-21.78, -12.22, 12.22, 21.78):
    for z in (1.65, 3.35, 6.25, 9.1):
        box('Front quoin', (x, 20.035, z), (.44, .19, .80), stone, .025)
for x in (-17, 17):
    prism('Wing pale pediment', [(-5.28, 10.83), (5.28, 10.83), (0, 13.92)],
          .12, (x, 20.60, 0), stone, bevel=.025)
    prism('Wing green tympanum', [(-4.12, 11.12), (4.12, 11.12), (0, 13.48)],
          .06, (x, 20.69, 0), green, bevel=.025)
    box('Wing pediment base', (x, 20.56, 10.9), (10.9, .4, .22), stone, .03)
    # Recessed blind oculus is well above movement height.
    clock_position = (x, 20.745, 12.05)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=.43, depth=.04,
                                       location=clock_position, rotation=(math.pi / 2, 0, 0))
    finish(bpy.context.object, 'Wing attic oculus', stone, .01)

# Closed formal central arch: amber leaves visibly fill the profile to ground.
arch_profile = [(-2, 0), (2, 0), (2, 3.15)]
arch_profile += [(2 * math.cos(a * math.pi / 20), 3.15 + 2 * math.sin(a * math.pi / 20))
                 for a in range(1, 21)]
prism('Closed amber arched entrance', arch_profile, .16, (0, -7.86, 0), amber)
for x in (-2.24, 2.24):
    box('Arch stone jamb', (x, -7.86, 1.63), (.45, .24, 3.26), stone, .025)
for i in range(16):
    a, b = i * math.pi / 16, (i + 1) * math.pi / 16
    outline = [(r * math.cos(t), 3.15 + r * math.sin(t))
               for r, t in [(2.03, a), (2.48, a), (2.48, b), (2.03, b)]]
    prism('Arch voussoir', outline, .23, (0, -7.86, 0), stone, bevel=.012)
box('Entrance centre stile', (0, -7.744, 1.55), (.10, .055, 3.1), green, .012)
box('Entrance transom', (0, -7.743, 3.15), (3.95, .055, .12), green, .012)
for x in (-1, 1):
    box('Closed door inset', (x, -7.764, 1.82), (1.53, .03, 2.13), green, .025)
    box('Door amber inset', (x, -7.742, 1.94), (1.27, .024, 1.74), amber, .018)
    box('Door pull', (x * .21, -7.711, 1.6), (.055, .048, .55), stone, .012)
for x in (-3.10, 3.10):
    box('Mint entry route accent', (x, -7.875, 3.15), (.20, .15, 1.2), mint, .025)
window('Central tall upper bay', 0, -7.975, 8, width=2.6, height=3)

# Modest integrated clock tower, not a separate prop, and no real light or animation.
box('Clock tower brick', (0, -11.2, 14.25), (5.8, 5.8, 8.3), brick, .035)
for x in (-2.72, 2.72):
    for y in (-13.92, -8.48):
        box('Tower pale corner', (x, y, 15.8), (.38, .38, 4.9), stone, .025)
box('Tower lower belt', (0, -11.2, 14.32), (6.02, 6.02, .22), stone, .025)
box('Tower crown cornice', (0, -11.2, 18.34), (6.26, 6.26, .30), stone, .035)
clock('Front clock', (0, -8.26, 16.40), 0)
clock('Back clock', (0, -14.14, 16.40), math.pi)
clock('East clock', (2.94, -11.2, 16.40), -math.pi / 2)
clock('West clock', (-2.94, -11.2, 16.40), math.pi / 2)
vertices = [(-3.22, -14.42, 18.5), (3.22, -14.42, 18.5),
            (3.22, -7.98, 18.5), (-3.22, -7.98, 18.5), (0, -11.2, 21)]
mesh = bpy.data.meshes.new('Tower pyramidal slate cap')
mesh.from_pydata(vertices, [], [(3, 2, 1, 0), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)])
mesh.update()
obj = bpy.data.objects.new('Tower pyramidal slate cap', mesh)
collection.objects.link(obj)
finish(obj, 'Tower pyramidal slate cap', slate, 0)
for face in obj.data.polygons:
    face.use_smooth = False

# One material-batched mesh under a metre-scale ground-centred export root.
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = 'D01AcademicBuildings01_Mesh'
obj.data.name = 'D01AcademicBuildings01_Geometry'
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
root = bpy.data.objects.new('D01AcademicBuildings01', None)
collection.objects.link(root)
obj.parent = root
root['asset_id'] = 'd01_academic_buildings.01'
root['authorship'] = 'Original Blender construction by commissioned production worker'
root['front_axis'] = 'Blender +Y maps to Godot -Z; +Z maps to +Y'
root['ground_pivot'] = 'Centre of overall U footprint, in open court, at ground zero'

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
camera.location = (58, 78, 56)
aim(camera, (0, 0, 5))
data.type = 'ORTHO'
data.ortho_scale = 82
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / 'export.py').read_text(), 'export.py', 'exec'))
for name, position, target, scale in [
    ('hero', (58, 78, 56), (0, 0, 5), 82),
    ('side', (70, 7, 33), (0, 0, 7), 65),
    ('entrance_clock_detail', (7, 35, 20), (0, -8, 10.5), 42),
]:
    camera.location = position
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f'{name}.png')
    bpy.ops.render.render(write_still=True)
# Honest local gameplay crop: a whole campus hall exceeds this camera's vertical coverage.
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
camera.location = (0, -3, 47)
camera.rotation_euler = (0, 0, 0)
data.type = 'PERSP'
data.sensor_fit = 'VERTICAL'
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / 'overhead_47m_42deg.png')
bpy.ops.render.render(write_still=True)
