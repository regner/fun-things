"""Bootstrap new S04 blockout sources in Blender; saved .blend owns subsequent authoring."""
import json
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
scene.render.fps = 30


def material(name, rgb):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    color = tuple(((v / 255 + .055) / 1.055) ** 2.4 if v > 10 else v / 3294.6 for v in rgb)
    node = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    node.inputs['Base Color'].default_value = (*color, 1)
    node.inputs['Roughness'].default_value = .8
    mat.diffuse_color = (*color, 1)
    return mat


mats = {n: material(n, c) for n, c in {
    'petrol': (18, 54, 70), 'emerald': (21, 86, 79), 'coral': (255, 114, 93),
    'cobalt': (35, 95, 204), 'amber': (255, 192, 90), 'ivory': (246, 241, 220),
    'slate': (133, 146, 157), 'charcoal': (30, 34, 43),
}.items()}


def collection(asset):
    col = bpy.data.collections.new('export_' + asset)
    scene.collection.children.link(col)
    return col


def box(col, name, size, pos, color, bevel=.04):
    # Input dimensions/positions use Godot axes, converted once into Blender axes.
    bpy.ops.mesh.primitive_cube_add(size=1, location=(pos[0], -pos[2], pos[1]))
    obj = bpy.context.object
    obj.name = name
    obj.scale = (size[0], size[2], size[1])
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    col.objects.link(obj)
    obj.data.materials.append(mats[color])
    if bevel:
        mod = obj.modifiers.new('broad_bevel', 'BEVEL')
        mod.width, mod.segments = bevel, 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    mod = obj.modifiers.new('explicit_triangles', 'TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier=mod.name)
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj


def marker(col, name, pos):
    obj = bpy.data.objects.new(name, None)
    col.objects.link(obj)
    obj.location = (pos[0], -pos[2], pos[1])


col = collection('s04_car')
box(col, 'Body', (1.8, .65, 3.4), (0, .6, 0), 'coral', .12)
box(col, 'Cabin', (1.55, .65, 1.8), (0, 1.15, .25), 'petrol', .12)
box(col, 'Roof', (1.48, .08, 1.15), (0, 1.50, .42), 'coral', .06)
box(col, 'FrontStripe', (1.35, .03, .2), (0, .94, -1.35), 'ivory', .01)
for x in [-.84, .84]:
    for z in [-1.06, 1.06]:
        box(col, 'Wheel_%s_%s' % (x,z), (.2, .5, .6), (x, .25, z), 'charcoal', .08)
for name, pos in {
 'socket_driver': (0, .8, .1),
 'socket_entry_left': (-1.3, 0, .1), 'socket_entry_right': (1.3, 0, .1),
 'socket_exit_left': (-1.5, 0, .1), 'socket_exit_right': (1.5, 0, .1),
}.items(): marker(col, name, pos)
col = collection('s04_track')
box(col, 'Pad', (80, .2, 80), (0,-.1,0), 'petrol', .01)
box(col, 'Wall', (20,2,1), (0,1,-20), 'slate', .04)
box(col, 'LeftBoundary', (1,2,60), (-30,1,0), 'emerald', .04)
box(col, 'RightBoundary', (1,2,60), (30,1,0), 'emerald', .04)
box(col, 'SouthBoundary', (60,2,1), (0,1,30), 'emerald', .04)
box(col, 'LaneMark', (.2,.02,20), (10,.01,10), 'ivory', .005)
source=ROOT / 'art/source/models/spikes/s04_kit.blend'
assert not source.exists(), 'Bootstrap never overwrites an existing source'
bpy.ops.wm.save_as_mainfile(filepath=str(source))
manifest={col.name:sorted(o.name for o in col.all_objects) for col in scene.collection.children}
(ROOT / 'tools/s04/export_members.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('S04_SOURCE',bpy.app.version_string,bpy.app.build_hash,source)
