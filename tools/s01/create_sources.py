"""Bootstrap neutral S01 fixtures; committed .blend files own subsequent authoring."""
import math
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]


def reset(asset):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1
    scene.render.fps = 30
    scene.frame_start, scene.frame_end = 1, 31
    collection = bpy.data.collections.new('export_' + asset)
    scene.collection.children.link(collection)
    return collection


def move(obj, collection):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (*color, 1)
    return mat


def box(name, dimensions, position, collection, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.name = name
    obj.scale = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new('small_bevel', 'BEVEL')
    bevel.width, bevel.segments = .025, 2
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    tri = obj.modifiers.new('explicit_triangles', 'TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier=tri.name)
    move(obj, collection)
    return obj


def empty(name, location, collection):
    obj = bpy.data.objects.new(name, None)
    collection.objects.link(obj)
    obj.location = location
    return obj


asset = 's01_static'
collection = reset(asset)
petrol = material('body_paint', (.02, .15, .20))
coral = material('front_accent', (1, .17, .11))
ivory = material('meter_reference', (.92, .88, .72))
# Ground-centred body, asymmetric +Y front; a separate exact one-metre ruler.
box('Body', (2, 1, 1), (0, 0, .5), collection, petrol)
box('Front', (.7, .25, .25), (0, .625, .75), collection, coral)
box('Meter', (.1, .1, 1), (1.3, 0, .5), collection, ivory)
empty('socket_muzzle', (0, .75, .75), collection)
empty('right_axis', (1, 0, 0), collection)
empty('up_axis', (0, 0, 1), collection)
# Editable original and explicit runtime PNG, no embedded GLB image.
image = bpy.data.images.new('s01_palette', width=8, height=8)
image.pixels = [c for y in range(8) for x in range(8)
                for c in ((.07, .21, .27, 1) if (x+y)%2 else (.08, .34, .31, 1))]
image.filepath_raw = str(ROOT / 'art/source/textures/spikes/s01_palette.png')
image.file_format = 'PNG'
image.save()
image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'art/source/models/spikes' / (asset+'.blend')))

asset = 's01_rig'
collection = reset(asset)
mat = material('body_paint', (.92, .88, .72))
body = box('Body', (.75, .4, 1.4), (0, 0, .7), collection, mat)
arm = box('Arm', (.2, .2, .6), (.5, 0, 1.3), collection, mat)
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
body.name = 'Skin'
bpy.ops.object.armature_add()
rig = bpy.context.object
rig.name = 'Rig'
move(rig, collection)
bpy.ops.object.mode_set(mode='EDIT')
root = rig.data.edit_bones[0]
root.name = 'root'
root.head, root.tail = (0,0,0), (0,0,1)
hand = rig.data.edit_bones.new('hand')
hand.head, hand.tail, hand.parent = (.5,0,1), (.5,0,1.6), root
bpy.ops.object.mode_set(mode='OBJECT')
body.parent = rig
modifier = body.modifiers.new('Skin', 'ARMATURE')
modifier.object = rig
for name in ('root','hand'):
    group = body.vertex_groups.new(name=name)
    indices = [v.index for v in body.data.vertices if (v.co.x > .38) == (name == 'hand')]
    group.add(indices, 1, 'REPLACE')
# Rest socket points Blender +Y / Godot -Z and follows hand bone.
socket = empty('socket_grip', (.5, .15, 1.6), collection)
socket.parent, socket.parent_type, socket.parent_bone = rig, 'BONE', 'hand'
# Bone-parent local coordinates: bone tail at z=1.6; Blender bone local Y points up.
socket.location = (0, .0, -.15)
socket.rotation_euler = (-math.pi / 2, 0, 0)
rig.animation_data_create()
for name, amplitude in [('idle',.1), ('walk',.4), ('run',.8), ('death',1.4)]:
    rig.animation_data.action = None
    pose = rig.pose.bones['hand']
    pose.rotation_mode = 'XYZ'
    for frame, angle in [(1,0), (16,amplitude), (31,amplitude if name=='death' else 0)]:
        pose.rotation_euler = (angle,0,0)
        pose.keyframe_insert('rotation_euler', frame=frame, group='hand')
    action = rig.animation_data.action
    action.name = name
    action.use_fake_user = True
    track = rig.animation_data.nla_tracks.new()
    track.name = name
    strip = track.strips.new(name, 1, action)
    strip.action_slot = rig.animation_data.action_slot
    track.mute = True
rig.animation_data.action = None
scene = bpy.context.scene
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'art/source/models/spikes' / (asset+'.blend')))
