#!/usr/bin/env python3
"""Inventory bounded saved spike inputs without an engine, imports or process probes."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from check import glb  # Existing engine-independent GLB reader.
from s06.check_resources import uid as resource_uid
from s05_effect.check_resources import check_scene

BASE = '52941da4b4c92a547a8066b5c13f733043ecbe48'
GROUPS = ('s02', 's04', 's05', 's05_effect', 's06')
ROOTS = (
    's02/corner', 's02/corner_wide', 's02/weapon_studies',
    's04/boot', 's04/body_comparison', 's05/boot', 's05/burst',
    's05_effect/boot', 's05_effect/burst', 's06/intersection', 's06/intersection_wide',
)
ATTR = re.compile(r'(\w+)="([^"]*)"')
BLOCK = re.compile(r'^\[([^\n]+)\]\n(.*?)(?=^\[|\Z)', re.M | re.S)
REFERENCE = re.compile(r'res://([^"\s)]+)')


def digest(path):
    """Fingerprint actual bytes, including ignored Blender sources and import sidecars."""
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def scene(path):
    """Read literal declarations; property values stay Godot text, never evaluated."""
    text = (ROOT / path).read_text()
    assert not re.search(r'type="(?:ArrayMesh|\w*Mesh|CSG\w*)"', text), path
    dependencies, nodes, resources = {}, [], []
    for header, body in BLOCK.findall(text):
        attributes = dict(ATTR.findall(header))
        properties = dict(re.findall(r'^([^\n=]+?) = ([^\n]+)$', body, re.M))
        if header.startswith('ext_resource '):
            target = attributes['path'].removeprefix('res://')
            assert attributes['uid'] == resource_uid(ROOT / target), (path, target)
            dependencies[attributes['id']] = {
                'path': target, 'uid': attributes['uid'], 'type': attributes['type']}
        elif header.startswith('node '):
            match = re.search(r'instance=ExtResource\("([^"]+)"\)', header)
            target = dependencies[match[1]]['path'] if match else None
            identity = re.search(r'\bunique_id=(\d+)', header)
            assert identity, (path, header)
            nodes.append({'name': attributes['name'], 'parent': attributes.get('parent'),
                          'type': attributes.get('type'), 'unique_id': int(identity[1]),
                          'instance': target, 'properties': properties})
        elif header.startswith('sub_resource '):
            resources.append({'type': attributes['type'], 'id': attributes['id'],
                              'properties': {k: v for k, v in properties.items()
                                             if k in ('size', 'radius', 'height', 'point_count',
                                                      'bake_interval', 'background_mode')}})
    return {'uid': resource_uid(ROOT / path), 'dependencies': list(dependencies.values()),
            'nodes': nodes, 'sub_resources': resources}


def compose(path, scenes, stack=()):
    """Resolve only saved PackedScene inheritance/instances and literal overrides."""
    assert path not in stack, ('scene cycle', stack, path)
    row = scenes[path]
    tree = {}
    for node in row['nodes']:
        parent = node['parent']
        key = '.' if parent is None else (
            node['name'] if parent == '.' else parent + '/' + node['name'])
        target = node['instance']
        if target and target.endswith('.tscn'):
            child = compose(target, scenes, (*stack, path))
            for child_key, value in child.items():
                placed_key = key if child_key == '.' else (
                    child_key if key == '.' else key + '/' + child_key)
                assert placed_key not in tree, (path, placed_key)
                tree[placed_key] = deepcopy(value)
        value = tree.setdefault(key, {'type': None, 'properties': {}, 'glb': None})
        value['type'] = node['type'] or value['type']
        value['properties'].update(node['properties'])
        if target and target.endswith('.glb'):
            value['glb'] = target
        if target:
            value['instance'] = target
    return tree


def geometry(path, mapping):
    """Count GLB mesh definitions and mesh nodes, not Godot draw calls or residency."""
    model = glb(ROOT / path)
    assert all('uri' not in buffer for buffer in model.get('buffers', [])), path
    meshes = []
    for mesh in model['meshes']:
        primitives = []
        for primitive in mesh['primitives']:
            assert primitive.get('mode', 4) == 4, (path, 'non-triangle primitive')
            count = model['accessors'][primitive.get('indices',
                      primitive['attributes']['POSITION'])]['count']
            assert count % 3 == 0, (path, count)
            position = model['accessors'][primitive['attributes']['POSITION']]
            primitives.append({'triangles': count // 3, 'vertices': position['count'],
                               'material': primitive.get('material'),
                               'position_accessor_min': position.get('min'),
                               'position_accessor_max': position.get('max')})
        meshes.append({'name': mesh.get('name'), 'primitives': primitives})
    expected = mapping.get('members')
    if expected:
        assert sorted(n['name'] for n in model['nodes']) == sorted(expected), path
    assert (ROOT / mapping['source']).read_bytes().startswith(
        (b'BLENDER', b'\x1f\x8b', b'\x28\xb5\x2f\xfd')), mapping['source']
    sidecar = (ROOT / (path + '.import')).read_text()
    assert f'source_file="res://{path}"' in sidecar, path
    mesh_nodes = [node for node in model['nodes'] if 'mesh' in node]
    return {**mapping, 'uid': resource_uid(ROOT / path), 'meshes': meshes,
            'nodes': model['nodes'], 'materials': model.get('materials', []),
            'mesh_definitions': len(meshes), 'mesh_node_instances': len(mesh_nodes),
            'primitive_definitions': sum(len(m['primitives']) for m in meshes),
            'triangles_mesh_definitions': sum(p['triangles'] for m in meshes
                                              for p in m['primitives']),
            'triangles_mesh_nodes': sum(p['triangles'] for n in mesh_nodes
                                       for p in meshes[n['mesh']]['primitives']),
            'primitive_mesh_nodes': sum(len(meshes[n['mesh']]['primitives']) for n in mesh_nodes),
            'images': len(model.get('images', [])), 'textures': len(model.get('textures', [])),
            'skins': len(model.get('skins', [])), 'animations': len(model.get('animations', [])),
            'extensions_used': model.get('extensionsUsed', []),
            'buffer_bytes': sum(b['byteLength'] for b in model.get('buffers', []))}


def inventory(base):
    """Bind a fixed fixture scope, dependencies and source mappings to immutable Git bytes."""
    scenes = {}
    inputs = {
        'art/source/.gdignore', 'tools/check.py', 'tools/s06/check_resources.py',
        'tools/s05_effect/check_resources.py', 'docs/assets/s02_kit.md',
        'docs/assets/s04_kit.md', 'docs/spikes/s06-source-handoff.md',
        'docs/spikes/s05-saved-presentation.md',
        'docs/spikes/s05-saved-presentation-evidence/network/result.json.gz',
    }
    for group in GROUPS:
        inputs.update(str(p.relative_to(ROOT)) for p in
                      (ROOT / 'tests/fixtures' / group).iterdir() if p.is_file())
    scanned = set()
    unresolved_literals = []
    while True:
        todo = sorted(p for p in inputs - scanned
                      if p.endswith(('.tscn', '.tres', '.gd', '.gdshader')))
        if not todo:
            break
        for path in todo:
            scanned.add(path)
            if path.endswith(('.tscn', '.tres')):
                row = scene(path)
                scenes[path] = row
                inputs.update(dep['path'] for dep in row['dependencies'])
            elif not path.startswith('addons/'):
                # Script strings can name output files, not just load dependencies.
                for target in REFERENCE.findall((ROOT / path).read_text()):
                    if (ROOT / target).is_file():
                        inputs.add(target)
                    else:
                        unresolved_literals.append({'script': path, 'literal': target})
    mappings = {}
    for group, source in [('s02', 's02_kit'), ('s04', 's04_kit'),
                          ('s06', 's06_intersection')]:
        members_path = f'tools/{group}/export_members.json'
        inputs.add(members_path)
        for collection, members in json.loads((ROOT / members_path).read_text()).items():
            path = 'art/models/spikes/' + collection.removeprefix('export_') + '.glb'
            mappings[path] = {'source': f'art/source/models/spikes/{source}.blend',
                              'collection': collection, 'members': members,
                              'mapping_record': members_path}
    mappings['art/models/spikes/s05_explosion_carrier.glb'] = {
        'source': 'art/source/models/spikes/s05_explosion_carrier.blend',
        'collection': 'export_s05_explosion_carrier', 'members': ['ExplosionCarrier'],
        'mapping_record': 'docs/spikes/s05-effect-preparation.md'}
    inputs.add('docs/spikes/s05-effect-preparation.md')
    assert {p for p in inputs if p.endswith('.glb')} == set(mappings), 'GLB scope drift'
    models = {path: geometry(path, mapping) for path, mapping in sorted(mappings.items())}
    for path, mapping in mappings.items():
        inputs.update((path, path + '.import', mapping['source']))
    inputs.update(path + '.uid' for path in list(inputs) if path.endswith(('.gd', '.gdshader')))
    fingerprints = {}
    for path in sorted(inputs):
        actual = (ROOT / path).read_bytes()
        original = subprocess.check_output(['git', 'show', base + ':' + path], cwd=ROOT)
        assert actual == original, ('input differs from accepted base', path)
        fingerprints[path] = {'bytes': len(actual), 'sha256': digest(path)}
    effect_checks = {name: check_scene(name, (ROOT /
        f'tests/fixtures/s05_effect/{name}.tscn').read_text())
        for name in ('explosion', 'boot', 'burst', 'editor_harness')}
    compositions = {}
    for name in ROOTS:
        path = f'tests/fixtures/{name}.tscn'
        tree = compose(path, scenes)
        counts = Counter(v['glb'] for v in tree.values() if v['glb'])
        compositions[path] = {
            'saved_nodes_excluding_glb_internal_nodes': len(tree),
            'saved_types_excluding_glb_internal_nodes': dict(sorted(Counter(
                v['type'] or 'imported_root' for v in tree.values()).items())),
            'glb_placements': dict(sorted(counts.items())),
            'triangles_all_saved_glb_placements': sum(models[p]['triangles_mesh_nodes'] * n
                                                     for p, n in counts.items()),
            'primitives_all_saved_glb_placements': sum(models[p]['primitive_mesh_nodes'] * n
                                                      for p, n in counts.items()),
            'model_roots': {k: v for k, v in tree.items() if v['glb']},
            'cameras_and_lights': {k: v for k, v in tree.items() if v['type'] in
                                  ('Camera3D', 'DirectionalLight3D')},
        }
    return {'schema': 1, 'accepted_base': base, 'scope': list(GROUPS),
            'limitations': ['Saved declarations and GLB metadata only; no engine evaluation.',
                            'No measured draw calls, visible counts, active bodies, RAM or GPU bytes.',
                            'Accessor bounds are mesh-local, not transformed world AABBs.',
                            'Blender relationship comes from saved handoff/membership records; no reopen.',
                            'Runtime instantiation, script-created materials and caches are not expanded.',
                            'Editor harness dependencies are hashed; vendor script recursion stops at addons/.'],
            'inputs': fingerprints, 'unresolved_script_literals': unresolved_literals,
            'scenes_and_resources': scenes, 'models': models,
            'saved_compositions': compositions, 'reused_effect_link_checks': effect_checks}


def main():
    """Write deterministic JSON for readback or comparison against the committed receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default=BASE)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = inventory(args.base)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(f"PASS static inventory: {len(result['inputs'])} inputs, "
          f"{len(result['models'])} GLBs, {len(result['saved_compositions'])} compositions")


if __name__ == '__main__':
    main()
