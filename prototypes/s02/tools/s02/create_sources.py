"""Bootstrap S02 blockout sources in Blender; saved .blend owns subsequent authoring."""
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


col = collection('s02_ground')
box(col, 'Street', (64, .2, 64), (0, -.1, 0), 'petrol')
# One authored broad pavement strip; surface remains flat for the bounded motion proof.
box(col, 'WalkStrip', (4, .015, 30), (0, .0075, -7), 'slate', .005)
for asset, height, color in [('s02_low', 6, 'emerald'), ('s02_near', 46, 'emerald'),
                             ('s02_tall', 60, 'cobalt')]:
    col = collection(asset)
    box(col, asset + '_Mass', (8, height, 8), (0, height / 2, 0), color, .15)
    box(col, asset + '_Roof', (8.2, .25, 8.2), (0, height - .125, 0), 'slate', .08)
    for y in range(2, int(height), 4):
        box(col, asset + '_Band_' + str(y), (8.04, .16, 8.04), (0, y, 0), 'petrol', .02)
    box(col, asset + '_Door', (1.5, 2.4, .08), (0, 1.2, 4.03), 'amber', .02)
col = collection('s02_actor')
box(col, 'Jacket', (.75, .65, .4), (0, 1.14, 0), 'ivory', .12)
box(col, 'Head', (.38, .38, .4), (0, 1.61, -.01), 'coral', .14)
for x in [-.2, .2]:
    box(col, 'Leg_' + str(x), (.24, .75, .26), (x, .375, .01), 'charcoal', .07)
    box(col, 'Boot_' + str(x), (.27, .15, .4), (x, .075, -.055), 'charcoal', .05)
box(col, 'AimArm', (.22, .23, .72), (.43, 1.2, -.24), 'ivory', .07)
marker(col, 'socket_grip', (.43, 1.2, -.6))
col = collection('s02_target')
box(col, 'TargetBody', (.75, 1.45, .4), (0, .725, 0), 'coral', .12)
box(col, 'TargetHead', (.38, .35, .4), (0, 1.625, 0), 'amber', .13)
for asset, size, color in [('s02_pistol', (.18, .18, .42), 'charcoal'),
                            ('s02_smg', (.28, .24, .72), 'charcoal'),
                            ('s02_launcher', (.38, .36, 1.1), 'emerald')]:
    col = collection(asset)
    box(col, asset + '_Body', size, (0, 0, -size[2]/2), color, .05)
    box(col, asset + '_Sight', (.09, .05, size[2]*.8), (0, size[1]/2, -size[2]/2), 'amber', .015)
    marker(col, 'socket_muzzle_' + asset, (0, 0, -size[2]))
    if asset == 's02_smg':
        box(col, 'Stock', (.17, .16, .3), (0, 0, .15), 'slate')
    if asset == 's02_launcher':
        box(col, 'RearBell', (.48, .42, .16), (0, 0, .03), 'slate')

source = ROOT / 'art/source/models/spikes/s02_kit.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source))
manifest = {col.name: sorted(o.name for o in col.all_objects) for col in scene.collection.children}
(ROOT / 'tools/s02/export_members.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('S02_SOURCE', bpy.app.version_string, bpy.app.build_hash, source)
