"""Original Coral Stub authoring; saved Blender source owns subsequent revisions."""
from pathlib import Path
import json
import math
import bpy

ROOT = Path(__file__).resolve().parents[2]
ASSET = 'pistol_coral_stub'
assert ROOT.name == 'brackett-pistol', ROOT
assert Path.cwd() == ROOT
assert bpy.app.version_string == '5.2.2 LTS', bpy.app.version_string
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
scene.render.fps = 30
collection = bpy.data.collections.new('export_' + ASSET)
scene.collection.children.link(collection)


def material(name, rgb, roughness, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    color = tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
                  for v in (c / 255 for c in rgb))
    shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metallic
    mat.diffuse_color = (*color, 1)
    return mat


mats = {
    'coral_shell': material('coral_shell', (255, 112, 99), .56, .1),
    'cream_rear': material('cream_rear', (246, 235, 210), .66),
    'petrol_frame': material('petrol_frame', (25, 42, 53), .65, .15),
    'dark_grip': material('dark_grip', (19, 25, 32), .85),
    'cyan_status': material('cyan_status', (59, 225, 233), .55),
    'muzzle_dark': material('muzzle_dark', (8, 13, 18), .95),
}


def finish(obj, mat, bevel=0.0):
    obj.data.materials.append(mats[mat])
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if bevel:
        mod = obj.modifiers.new('authored_soft_edges', 'BEVEL')
        mod.width, mod.segments = bevel, 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    for face in obj.data.polygons:
        face.use_smooth = True
    mod = obj.modifiers.new('authored_weighted_normals', 'WEIGHTED_NORMAL')
    mod.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mod = obj.modifiers.new('explicit_triangles', 'TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.select_set(False)
    return obj


def box(name, size, pos, mat, bevel):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(pos[0], -pos[2], pos[1]))
    obj = bpy.context.object
    obj.name = name
    obj.scale = (size[0], size[2], size[1])
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return finish(obj, mat, bevel)


def profile(name, yz, width, mat, bevel):
    # Input uses Godot local coordinates; convert once for Blender +Y front.
    verts = [(x, -z, y) for x in (-width / 2, width / 2) for y, z in yz]
    n = len(yz)
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    # Recalculate outward normals before baking the bevel.
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    return finish(obj, mat, bevel)


box('CoralSlide', (.142, .104, .345), (0, .128, -.2225), 'coral_shell', .012)
box('CreamRearCap', (.15, .107, .12), (0, .1295, .01), 'cream_rear', .016)
box('LowerFrame', (.124, .081, .385), (0, .0395, -.1825), 'petrol_frame', .013)
profile('AngledGrip', [( .049, .047), (.043, -.065), (-.205, .030),
                      (-.205, .140), (-.16, .143)], .117, 'petrol_frame', .016)
profile('GripInsert', [(.012, .029), (.005, -.044), (-.177, .039),
                      (-.177, .121)], .122, 'dark_grip', .009)
# A single authored guard arch leaves a broad visible opening under the frame.
profile('TriggerGuard', [(.01, -.068), (.01, -.261), (-.025, -.28),
                        (-.105, -.256), (-.111, -.117), (-.088, -.094),
                        (-.083, -.124), (-.079, -.23), (-.031, -.244),
                        (-.019, -.224), (-.019, -.08)], .058, 'petrol_frame', .006)
profile('TriggerVisual', [(.015, -.145), (.013, -.165), (-.044, -.182),
                        (-.057, -.166), (-.026, -.15)], .026, 'coral_shell', .003)
box('MuzzleCollar', (.147, .116, .038), (0, .122, -.401), 'petrol_frame', .009)
box('RearSight', (.058, .022, .025), (0, .193, .022), 'petrol_frame', .004)
box('FrontSight', (.027, .021, .036), (0, .1905, -.351), 'petrol_frame', .004)
box('TopStatusInsert', (.034, .003, .023), (0, .184, -.025), 'cyan_status', .001)

# Shallow dark aperture is cosmetic geometry, not a ballistic bore or collider.
segments = 20
verts = [(0, .421, .122)]
verts += [(.024 * math.cos(i * math.tau / segments), .421,
           .122 + .024 * math.sin(i * math.tau / segments)) for i in range(segments)]
mesh = bpy.data.meshes.new('MuzzleAperture_mesh')
mesh.from_pydata(verts, [], [(0, (i + 1) % segments + 1, i + 1) for i in range(segments)])
mesh.update()
obj = bpy.data.objects.new('MuzzleAperture', mesh)
scene.collection.objects.link(obj)
finish(obj, 'muzzle_dark')

for name, position in {'socket_grip': (0, 0, 0),
                       'socket_muzzle': (0, .122, -.421)}.items():
    empty = bpy.data.objects.new(name, None)
    collection.objects.link(empty)
    empty.location = (position[0], -position[2], position[1])
    empty.empty_display_type = 'ARROWS'
    empty.empty_display_size = .075

source = ROOT / 'art/source/models/weapons/pistol_coral_stub/pistol_coral_stub.blend'
source.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(source))
manifest = {
    'asset_id': ASSET, 'source': str(source.relative_to(ROOT)),
    'collection': collection.name,
    'members': sorted(o.name for o in collection.all_objects),
    'materials': list(mats),
    'sockets_godot_m': {'socket_grip': [0, 0, 0], 'socket_muzzle': [0, .122, -.421]},
    'muzzle_aperture_radius_m': .024,
    'animation': 'None; static presentation prop, no moving-part requirement selected',
}
(Path(__file__).parent / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('PISTOL_SOURCE', source, manifest)
