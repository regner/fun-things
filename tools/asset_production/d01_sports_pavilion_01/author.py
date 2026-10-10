"""Original low crescent pavilion; pinned isolated Blender source, export and renders."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = 'd01_sports_pavilion_01'
SOURCE = ROOT / f'art/source/models/environment/{NID}/{NID}.blend'
EVIDENCE = ROOT / f'docs/assets/production/{NID}-evidence'
# Provisional metre dimensions, not measurements taken from generated concept art.
OUTER_RADIUS = 28.0
INNER_RADIUS = 19.0
HALF_ANGLE = math.radians(55)
ARC_STEPS = 64
CENTRE_Y = (OUTER_RADIUS + INNER_RADIUS * math.cos(HALF_ANGLE)) / 2
POD_HALF_ANGLE = math.radians(50)
POD_OUTER_RADIUS = 26.0
POD_INNER_RADIUS = 24.0
POD_HEIGHT = 5.65


def material(name, color, metallic=0, roughness=.5):
    """Create an opaque, back-culled, texture-free Principled material."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*color, 1)
    shader = result.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    return result


def finish(obj, name, mat, bevel=0):
    """Bake transforms and local soft edges, preserving closed component topology."""
    obj.name = name
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        modifier.width = bevel
        modifier.segments = 2
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    for face in obj.data.polygons:
        face.use_smooth = True
    modifier = obj.modifiers.new('Weighted architectural normals', 'WEIGHTED_NORMAL')
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    parts.append(obj)
    return obj


def mesh_object(name, vertices, faces, mat, bevel=0):
    """Construct original editable geometry with explicit closed faces."""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, name, mat, bevel)


def box(name, position, size, mat, bevel=.025, yaw=0):
    """Construct a solid detail aligned with the two pavilion facade chords."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.dimensions = size
    obj.rotation_euler.z = yaw
    return finish(obj, name, mat, bevel)


def arc_point(radius, angle, height):
    """Map the crescent's plan into Blender +Y field-facing coordinates."""
    return (radius * math.sin(angle), CENTRE_Y - radius * math.cos(angle), height)


def swept_section(name, section, mat, steps=ARC_STEPS, angle_min=-HALF_ANGLE,
                  angle_max=HALF_ANGLE):
    """Sweep a closed radius/height profile along a smooth crescent arc."""
    width = len(section)
    vertices = [arc_point(r, angle_min + (angle_max - angle_min) * i / steps, z)
                for i in range(steps + 1) for r, z in section]
    faces = [tuple(reversed(range(width))), tuple(range(steps * width, (steps + 1) * width))]
    for i in range(steps):
        for j in range(width):
            a = i * width + j
            b = i * width + (j + 1) % width
            faces.append((a, b, b + width, a + width))
    return mesh_object(name, vertices, faces, mat)


def pod_outline(side):
    """Return one convex four-point service wedge, also documented for collision."""
    a, b = (0, POD_HALF_ANGLE) if side > 0 else (-POD_HALF_ANGLE, 0)
    return [arc_point(radius, angle, 0)[:2] for radius, angle in [
        (POD_OUTER_RADIUS, a), (POD_OUTER_RADIUS, b),
        (POD_INNER_RADIUS, b), (POD_INNER_RADIUS, a)]]


def prism(name, outline, low, high, mat):
    """Extrude the dimension-authored convex footprint without a render-mesh hull."""
    count = len(outline)
    vertices = [(x, y, z) for z in (low, high) for x, y in outline]
    faces = [tuple(reversed(range(count))), tuple(range(count, 2 * count))]
    faces += [(i, (i + 1) % count, (i + 1) % count + count, i + count)
              for i in range(count)]
    return mesh_object(name, vertices, faces, mat)


def facade_box(name, side, along, height, size, mat, outer=False, offset=0, bevel=.025):
    """Place flush original facade relief on a service wedge, never a traversable doorway."""
    angle = side * POD_HALF_ANGLE / 2
    radius = POD_OUTER_RADIUS if outer else POD_INNER_RADIUS
    midpoint = Vector(arc_point(radius * math.cos(POD_HALF_ANGLE / 2), angle, height))
    tangent = Vector((math.cos(angle), math.sin(angle), 0))
    field_normal = Vector((-math.sin(angle), math.cos(angle), 0))
    normal = -field_normal if outer else field_normal
    point = midpoint + along * tangent + (offset - size[1] / 2) * normal
    return box(name, point, size, mat, bevel, angle)


def aim(obj, target):
    """Aim only isolated studio cameras and lights."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def light(name, position, power, size):
    """Create broad fill outside the export collection."""
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = power
    data.shape = 'DISK'
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (0, 0, 2))


assert bpy.app.version_string == '5.2.2 LTS'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f'export_{NID}')
scene.collection.children.link(collection)
parts = []
slate = material('pavilion_slate_roof', (.065, .105, .155), .18, .44)
green = material('pavilion_field_green', (.028, .115, .095), .12, .46)
stone = material('pavilion_pale_stone', (.70, .64, .49), 0, .65)
base = material('pavilion_base_stone', (.25, .27, .25), 0, .7)
glass = material('pavilion_opaque_glass', (.023, .071, .085), .2, .3)
mint = material('pavilion_wayfinding_mint', (.23, .70, .52), .05, .42)
amber = material('pavilion_occupied_amber', (.85, .43, .11), .06, .42)

# Two deliberately solid rear wedges support a column-free open field-facing shelter.
# No deck mesh, steps, interior, stands, equipment or ground are in the export.
for side in (-1, 1):
    outline = pod_outline(side)
    prism('Service wedge pale walls', outline, .36, 4.95, stone)
    prism('Service wedge dark foot', outline, 0, .36, base)
    prism('Service wedge green head', outline, 4.95, POD_HEIGHT, green)
    for outer in (False, True):
        for along in (-6.4, -2.15, 2.15, 6.4):
            facade_box('Recessed clerestory glazing', side, along, 4.38,
                       (3.30, .09, .70), glass, outer, offset=.012)
            facade_box('Clerestory sill', side, along, 3.99,
                       (3.5, .09, .09), green, outer, offset=.035, bevel=.012)
        # Quiet broad wall rhythms instead of small repeated stadium/window noise.
        for along in (-8.5, 0, 8.5):
            facade_box('Pale wall pilaster', side, along, 2.35,
                       (.28, .14, 3.75), stone, outer, offset=.045)
    # Two closed service entrances, distinct from the fully open sheltered apron.
    along = -side * 5.0
    facade_box('Mint entry surround', side, along, 1.57, (2.8, .11, 3.14),
               mint, offset=.022, bevel=.018)
    facade_box('Closed green double leaves', side, along, 1.48, (2.38, .08, 2.96),
               green, offset=.046, bevel=.018)
    for dx in (-.6, .6):
        facade_box('Amber door vision panel', side, along + dx, 1.85, (1.0, .06, 1.72),
                   amber, offset=.060, bevel=.018)
    facade_box('Closed door centre stile', side, along, 1.48, (.10, .05, 2.96),
               green, offset=.079, bevel=.01)
    facade_box('Entry head marker', side, along, 3.36, (2.8, .12, .16),
               mint, offset=.035, bevel=.02)

# Smooth broad curved roof: open front, continuous pale soffit and quiet slate crown.
swept_section('Pale cantilever soffit', [(19, 5.5), (28, 5.5), (28, 5.76), (19, 5.76)], stone)
swept_section('Slate shallow crowned canopy', [
    (19, 5.73), (28, 5.73), (28, 6.02), (26.5, 6.23),
    (23.5, 6.50), (20.5, 6.23), (19, 6.02)], slate)
# Fascias extend 3 cm beyond the soffit, avoiding coincident material faces.
for name, radius in [('Field-facing green fascia', 18.97), ('Rear green fascia', 27.85)]:
    swept_section(name, [(radius, 5.58), (radius + .18, 5.58),
                         (radius + .18, 5.93), (radius, 5.93)], green)
# Four broad radial seams articulate scale without making the roof visually busy.
for angle in (-38, -14, 14, 38):
    radians = math.radians(angle)
    swept_section('Raised radial roof seam', [(19.4, 6.10), (20.5, 6.24),
        (23.5, 6.51), (26.5, 6.24), (27.6, 6.10), (27.6, 6.145),
        (26.5, 6.285), (23.5, 6.555), (20.5, 6.285), (19.4, 6.145)],
        green, steps=1, angle_min=radians - .0014, angle_max=radians + .0014)

bpy.ops.object.select_all(action='DESELECT')
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = 'D01SportsPavilion01_Mesh'
obj.data.name = 'D01SportsPavilion01_Geometry'
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
root = bpy.data.objects.new('D01SportsPavilion01', None)
collection.objects.link(root)
obj.parent = root
root['asset_id'] = 'd01_sports_pavilion.01'
root['authorship'] = 'Original commissioned Blender construction; no external meshes or images'
root['front_axis'] = 'Blender +Y / Godot -Z opens toward the sports field'
root['ground_pivot'] = 'Overall roof plan centre projected to flat ground; open apron at origin'
root['roof_access'] = 'None; overhead decoration above 5.5 m, not a walkable deck'

scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.22, .28, .35, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .65
bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, -.025))
bpy.context.object.name = 'STUDIO_ground_not_exported'
bpy.context.object.data.materials.append(material('STUDIO_slate', (.13, .18, .19)))
light('STUDIO_key', (20, 35, 45), 50000, 30)
light('STUDIO_rim', (-30, -20, 35), 42000, 25)
light('STUDIO_fill', (-10, 28, 15), 19000, 20)
data = bpy.data.cameras.new('STUDIO_camera')
camera = bpy.data.objects.new('STUDIO_camera', data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_percentage = 100
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.compression = 95
scene.render.image_settings.color_mode = 'RGB'
scene.render.image_settings.color_depth = '8'
scene.render.dither_intensity = 0
scene.view_settings.view_transform = 'AgX'
data.type = 'ORTHO'
data.ortho_scale = 58
camera.location = (37, 57, 34)
aim(camera, (0, 0, 2.5))
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / 'export.py').read_text(), 'export.py', 'exec'))
for name, position, target, scale in [
    ('hero', (37, 57, 34), (0, 0, 2.5), 58),
    ('side', (60, 12, 18), (0, 0, 2.6), 37),
    ('entry_detail', (12, 21, 7.5), (4.7, -3.2, 2.9), 15),
]:
    camera.location = position
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f'{name}.png')
    bpy.ops.render.render(write_still=True)
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type = 'PERSP'
data.sensor_fit = 'VERTICAL'
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / 'overhead_47m_42deg.png')
bpy.ops.render.render(write_still=True)
