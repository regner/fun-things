#!/usr/bin/env python3
"""Author only the saved S05 observation camera through the private installed tools."""
import argparse
import json
from pathlib import Path
import subprocess

REQUEST = Path(__file__).with_name('request.py')


def call(log, name, args):
    """Check both SDK and installed handler results while preserving every raw response."""
    result = subprocess.run(['python', '-B', str(REQUEST), str(log), name, json.dumps(args)],
                            capture_output=True, text=True, timeout=45)
    print(result.stdout, end='', flush=True)
    print(result.stderr, end='', flush=True)
    if result.returncode:
        raise RuntimeError('owned request failed: ' + name)
    envelope = json.loads(result.stdout)
    for block in envelope.get('content', []):
        if block.get('type') == 'text':
            value = json.loads(block['text'])
            if value.get('success') is False or value.get('valid') is False:
                raise RuntimeError('owned handler rejected: ' + name)
            return value
    raise RuntimeError('no handler response: ' + name)


def main():
    """Save the import-free composition before opening any other scene."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    args = parser.parse_args()
    path = 'res://tests/fixtures/s05_draw/camera.tscn'
    call(args.log, 'scene_create', {'file_path': path, 'root_type': 'Node3D',
                                  'root_name': 'ObservationView', 'if_exists': 'fail'})
    call(args.log, 'scene_open', {'file_path': path})
    for name, kind in [('Camera3D', 'Camera3D'), ('Sun', 'DirectionalLight3D'),
                       ('Environment', 'WorldEnvironment')]:
        call(args.log, 'scene_create_node', {'class_name': kind, 'parent_path': '.',
                                           'node_name': name})
    values = [
        ('Camera3D', 'position', {'type': 'Vector3', 'x': 6, 'y': 47, 'z': 4}),
        ('Camera3D', 'rotation_degrees', {'type': 'Vector3', 'x': -90, 'y': 0, 'z': 0}),
        ('Camera3D', 'current', True), ('Camera3D', 'fov', 42),
        ('Camera3D', 'near', .1), ('Camera3D', 'far', 160),
        ('Sun', 'rotation_degrees', {'type': 'Vector3', 'x': -60, 'y': 30, 'z': 0}),
        ('Sun', 'light_energy', 1.2), ('Sun', 'shadow_enabled', True),
        ('Environment', 'environment', {'type': 'NewResource', 'class': 'Environment',
          'properties': {'background_mode': 1,
            'background_color': {'type': 'Color', 'r': .035, 'g': .065, 'b': .085, 'a': 1},
            'ambient_light_source': 2,
            'ambient_light_color': {'type': 'Color', 'r': .8, 'g': .85, 'b': 1, 'a': 1},
            'ambient_light_energy': .65}})]
    call(args.log, 'node_set_property', {'batch': [
        {'node_path': node, 'property': key, 'value': value} for node, key, value in values]})
    call(args.log, 'editor_save_scene', {})
    call(args.log, 'scene_get_tree', {'max_depth': -1, 'include_properties': True})


if __name__ == '__main__':
    main()
