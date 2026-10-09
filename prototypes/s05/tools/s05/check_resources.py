#!/usr/bin/env python3
"""Check the scoped S05 source links, saved identities and UID/path agreement."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def uid(path):
    if path.suffix == '.gd':
        return Path(str(path) + '.uid').read_text().strip()
    pattern = r'uid="(uid://[^"]+)"'
    source = path.read_text() if path.suffix == '.tscn' else Path(str(path) + '.import').read_text()
    return re.search(pattern, source).group(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='c0eda26f7f010af75bbf10c272ec5cb001442331')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    files = subprocess.check_output(['git', 'ls-tree', '-rz', args.base], cwd=ROOT).split(b'\0')
    original = []
    # Every pre-existing technical source/resource/tool remains immutable. Only the
    # explicitly owned S05 TODO status and concurrent documentation can change.
    prefixes = ('art/', 'tests/', 'tools/', 'addons/', '.agents/', 'project.godot',
                'mise.toml', 'gdstyle.toml', '.gdstyle-version', 'AGENTS.md')
    for entry in files:
        if not entry:
            continue
        metadata, raw = entry.split(b'\t', 1)
        path = raw.decode()
        if not path.startswith(prefixes):
            continue
        expected = subprocess.check_output(['git', 'show', args.base + ':' + path], cwd=ROOT)
        actual = (ROOT / path).read_bytes()
        assert actual == expected, 'original changed: ' + path
        original.append({'path': path, 'sha256': hashlib.sha256(actual).hexdigest()})
    scenes = {}
    for path in sorted((ROOT / 'tests/fixtures/s05').glob('*.tscn')):
        text = path.read_text()
        assert 'ArrayMesh' not in text and 'PrimitiveMesh' not in text and 'CSG' not in text
        dependencies = []
        for declared, relative in re.findall(r'\[ext_resource[^\n]*uid="([^"]+)" path="res://([^"]+)"', text):
            expected = uid(ROOT / relative)
            assert declared == expected, f'UID/path mismatch: {path.name} -> {relative}'
            dependencies.append({'path': relative, 'uid': expected})
        ids = re.findall(r'^\[node[^\n]*unique_id=(\d+)', text, re.MULTILINE)
        assert ids and len(ids) == len(set(ids)), 'missing/repeated saved identity: ' + path.name
        scenes[path.name] = {'uid': uid(path), 'ids': ids, 'dependencies': dependencies,
                            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    assert len(scenes) == 3, 'exact car/boot/burst scene scope'
    scripts = {p.name: uid(p) for p in (ROOT / 'tests/fixtures/s05').glob('*.gd')}
    assert len(scripts) == 7 and len(set(scripts.values())) == 7
    result = {'ok': True, 'base': args.base, 'original_files': original,
              'scenes': scenes, 'scripts': scripts,
              'source': 'art/source/models/spikes/s04_kit.blend',
              'outputs': ['art/models/spikes/s04_car.glb', 'art/models/spikes/s04_track.glb']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS', len(original), 'original files preserved; 3 scenes/7 scripts UID and identity checks')


if __name__ == '__main__':
    main()
