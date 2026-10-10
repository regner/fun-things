"""Audit and render the saved Courier skin/player run actions; never mutate saved sources."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[4]
CLIPS = ('run', 'run_back', 'run_left', 'run_right')
FRAMES = (6, 8, 10, 1)


def aim(obj, target):
    """Point a temporary review camera or light at the saved asset."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def load_sources():
    """Use the production skin and saved actions, not a second authoring implementation."""
    skin_path = ROOT / 'art/source/models/characters/coral_courier/coral_courier.blend'
    motion = ROOT / 'art/source/models/characters/shared_humanoid/shared_humanoid_player_motion_v1.blend'
    bpy.ops.wm.open_mainfile(filepath=str(skin_path))
    with bpy.data.libraries.load(str(motion), link=False) as (_, target):
        target.actions = list(CLIPS)
    rig = bpy.data.objects['Rig']
    rig.animation_data_create()
    return rig, bpy.data.objects['Skin'], dict(zip(CLIPS, target.actions))


def audit(rig, skin, actions):
    """Measure topology, canonical rests, normals, ground clearance and rigid leg lengths."""
    rest = [{'name': b.name, 'parent': b.parent.name if b.parent else None,
             'head_blender_m': list(b.head_local), 'tail_blender_m': list(b.tail_local),
             'matrix_blender_armature': [list(row) for row in b.matrix_local]}
            for b in rig.data.bones]
    fingerprint = hashlib.sha256(json.dumps(rest, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    canonical = json.loads((ROOT / 'art/source/models/characters/shared_humanoid/shared_humanoid_v1.json').read_text())
    assert fingerprint == canonical['rest_sha256']
    skin.data.calc_loop_triangles()
    topology = bmesh.new()
    topology.from_mesh(skin.data)
    non_manifold = sum(not e.is_manifold for e in topology.edges)
    boundary = sum(e.is_boundary for e in topology.edges)
    topology.free()
    report = {'rest_sha256': fingerprint, 'bones': len(rest),
              'vertices': len(skin.data.vertices), 'triangles': len(skin.data.loop_triangles),
              'meshes': 1, 'material_surfaces': len(skin.data.materials),
              'degenerate_triangles': sum(t.area < 1e-10 for t in skin.data.loop_triangles),
              'non_manifold_edges': non_manifold, 'boundary_edges': boundary,
              'topology_note': 'Unchanged approved mesh; open bomber/collar fronts expose the shirt.',
              'maximum_normal_length_error': max(abs(v.normal.length - 1) for v in skin.data.vertices),
              'pivot': 'ground between rest feet; root unchanged', 'clips': {}}
    assert report['degenerate_triangles'] == 0
    assert non_manifold == boundary
    for name, action in actions.items():
        rig.animation_data.action = action
        rig.animation_data.action_slot = action.slots[0]
        low, high = [math.inf] * 3, [-math.inf] * 3
        length_error = 0.0
        for frame in range(21):
            bpy.context.scene.frame_set(frame)
            evaluated = skin.evaluated_get(bpy.context.evaluated_depsgraph_get())
            for vertex in evaluated.data.vertices:
                for axis in range(3):
                    low[axis] = min(low[axis], vertex.co[axis])
                    high[axis] = max(high[axis], vertex.co[axis])
            for side in ('r', 'l'):
                for parent, child in (('thigh_', 'shin_'), ('shin_', 'foot_')):
                    a, b = rig.pose.bones[parent + side], rig.pose.bones[child + side]
                    length_error = max(length_error, abs((b.matrix.translation - a.matrix.translation).length - a.bone.length))
            assert rig.pose.bones['root'].matrix == rig.data.bones['root'].matrix_local
        report['clips'][name] = {'aabb_blender_m': [low, high],
                                 'dimensions_blender_m': [b - a for a, b in zip(low, high)],
                                 'minimum_ground_clearance_m': low[2],
                                 'maximum_leg_length_error_m': length_error, 'frames_sampled': 21}
        assert low[2] >= -0.001, (name, low)
        assert length_error < 0.00001, (name, length_error)
    return report


def audit_unchanged_actions(baseline):
    """Compare every untouched action's saved transform keys with the pre-follow-up source."""
    motion = ROOT / 'art/source/models/characters/shared_humanoid/shared_humanoid_player_motion_v1.blend'
    manifest = json.loads(motion.with_suffix('.json').read_text())
    names = [clip['name'] for clip in manifest['clips'] if clip['name'] not in CLIPS]
    libraries = []
    for path in (baseline, motion):
        with bpy.data.libraries.load(str(path), link=False) as (_, target):
            target.actions = names[:]
        libraries.append(target.actions[:])
    result = {}
    for name, old, new in zip(names, *libraries):
        curves = []
        for action in (old, new):
            curves.append({(curve.data_path, curve.array_index):
                           [tuple(key.co) for key in curve.keyframe_points]
                           for layer in action.layers for strip in layer.strips
                           for bag in strip.channelbags for curve in bag.fcurves})
        assert curves[0].keys() == curves[1].keys(), name
        maximum_error = 0.0
        for key in curves[0]:
            assert len(curves[0][key]) == len(curves[1][key]), (name, key)
            for a, b in zip(curves[0][key], curves[1][key]):
                assert a[0] == b[0], (name, key)
                maximum_error = max(maximum_error, abs(a[1] - b[1]))
        assert maximum_error < 0.000001, (name, maximum_error)
        result[name] = {'maximum_saved_key_difference': maximum_error}
    return result


def studio():
    """Create disposable Blender-only review lighting/floor, excluded from all exports."""
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.compression = 95
    scene.render.resolution_percentage = 100
    scene.world = bpy.data.worlds.new('ReviewWorld')
    scene.world.color = (0.15, 0.15, 0.15)
    bpy.ops.mesh.primitive_plane_add(size=200)
    floor = bpy.context.object
    floor.name = 'ReviewFloor'
    material = bpy.data.materials.new('ReviewPetrol')
    material.diffuse_color = (0.028, 0.072, 0.085, 1)
    material.use_nodes = True
    material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = material.diffuse_color
    floor.data.materials.append(material)
    for location, power, size in [((2, 4, 6), 1100, 5), ((-4, 1, 3), 650, 4)]:
        bpy.ops.object.light_add(type='AREA', location=location)
        light = bpy.context.object
        light.data.energy, light.data.shape, light.data.size = power, 'DISK', size
        aim(light, (0, 0, 0.9))
    bpy.ops.object.camera_add()
    scene.camera = bpy.context.object
    scene.camera.data.type = 'PERSP'
    return scene


def main():
    """Write only scratch renders and measurements from the saved current asset."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline-motion', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.output.mkdir(parents=True, exist_ok=True)
    assert bpy.app.version_string == '5.2.2 LTS'
    rig, skin, actions = load_sources()
    report = audit(rig, skin, actions)
    report['unchanged_actions'] = audit_unchanged_actions(args.baseline_motion)
    (args.output / 'source_validation.json').write_text(json.dumps(report, indent=2) + '\n', newline='\n')
    scene = studio()
    for name, action in actions.items():
        rig.animation_data.action = action
        rig.animation_data.action_slot = action.slots[0]
        for frame in FRAMES:
            scene.frame_set(frame)
            scene.render.resolution_x, scene.render.resolution_y = 320, 520
            scene.camera.location = (3.3, 4.5, 2.0) if name in ('run', 'run_back') else (0, 5.4, 1.9)
            scene.camera.data.lens = 58
            aim(scene.camera, (0, 0, 0.87))
            scene.render.filepath = str(args.output / f'{name}_{frame}.png')
            bpy.ops.render.render(write_still=True)
        scene.frame_set(6)
        scene.render.resolution_x, scene.render.resolution_y = 1280, 720
        scene.camera.location = (0, 0, 47)
        scene.camera.rotation_euler = (0, 0, 0)
        # Godot FOV is vertical for the accepted keep-height 16:9 camera.
        scene.camera.data.sensor_fit = 'VERTICAL'
        scene.camera.data.angle = math.radians(42)
        scene.render.filepath = str(args.output / f'{name}_overhead.png')
        bpy.ops.render.render(write_still=True)
        scene.camera.data.sensor_fit = 'AUTO'
    print('RUN_SOURCE_REVIEW', json.dumps(report))


if __name__ == '__main__':
    main()
