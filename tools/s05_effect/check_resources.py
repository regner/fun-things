#!/usr/bin/env python3
"""Check saved S05 effect ancestry/identity and immutable accepted technical bytes."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = 'ef730df936b5b159f0894033f5d01e2b7124386c'
FOLDER = ROOT / 'tests/fixtures/s05_effect'
OUT = Path('/tmp/s05-author-56eb6b28-run04/resource-check.json')


def uid(path):
    """Read actual engine-owned resource identity from its saved file or companion."""
    if path.suffix == '.gd':
        return Path(str(path) + '.uid').read_text().strip()
    if path.suffix == '.glb':
        path = Path(str(path) + '.import')
    return re.search(r'uid="(uid://[^\"]+)"', path.read_text())[1]


def check_scene(name, source):
    """Assert literal authored links and forbid embedded/generated rendering resources."""
    assert not any(word in source for word in ['ArrayMesh', 'PrimitiveMesh', 'CSG'])
    identities = re.findall(r'^\[node[^\n]*unique_id=(\d+)', source, re.M)
    assert identities and len(identities) == len(set(identities)), name + ' node identities'
    for declared, path in re.findall(r'uid="([^\"]+)" path="res://([^\"]+)"', source):
        assert declared == uid(ROOT / path), 'UID/path mismatch: ' + path
    if name == 'explosion':
        assert 'uid="uid://dbge3dp3s53r3"' in source and 'unique_id=1935466903]' in source
        assert 'path="res://art/models/spikes/s05_explosion_carrier.glb"' in source, 'missing linked GLB'
        assert '[node name="Model" parent="Visuals"' in source
        assert 'Collision' not in source
    elif name in ['boot', 'burst']:
        assert 'path="res://tests/fixtures/s05/' + name + '.tscn"' in source
        assert len(re.findall(r'^\[node name="Slot[0-7]"', source, re.M)) == 8
        assert 'transform =' not in source, 'must inherit original cars/track placement'
    return {'uid': uid(FOLDER / (name + '.tscn')), 'node_ids': identities,
            'sha256': hashlib.sha256(source.encode()).hexdigest()}


def main():
    """Verify actual saved artifacts and prove the GLB omission check fails independently."""
    scenes = {name: check_scene(name, (FOLDER / (name + '.tscn')).read_text())
              for name in ['explosion', 'boot', 'burst', 'editor_harness']}
    text = (FOLDER / 'explosion.tscn').read_text()
    omitted = '\n'.join(line for line in text.splitlines()
                        if 'path="res://art/models/spikes/s05_explosion_carrier.glb"' not in line)
    try:
        check_scene('explosion', omitted)
    except AssertionError as error:
        assert str(error) == 'missing linked GLB'
    else:
        raise AssertionError('omission mutation escaped required linked ancestry')
    original = json.loads((ROOT / 'docs/spikes/s05-saved-presentation-evidence/original-bytes.json').read_text())
    for row in original:
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
    scripts = {p.name: uid(p) for p in FOLDER.glob('*.gd')}
    assert len(scripts) == 4 and len(set(scripts.values())) == 4
    result = {'ok': True, 'base': BASE, 'scenes': scenes, 'scripts': scripts,
              'original_files_unchanged': len(original), 'linked_model_omission_rejected': True}
    OUT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'ok': True, 'original_files': len(original), 'scenes': 4, 'scripts': 4,
                      'negative_missing_glb_rejected': True}))


if __name__ == '__main__':
    main()
