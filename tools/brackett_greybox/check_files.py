#!/usr/bin/env python3
"""Focused greybox provenance, dependency, identity and frozen-plan checks."""
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'art/source/models/brackett_greybox'


def digest(path):
    """Hash the actual source/export bytes, including unchanged empty files."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uid(path):
    """Resolve a resource's saved identity without depending on disposable cache files."""
    if path.suffix == '.gd':
        return Path(str(path)+'.uid').read_text().strip()
    if path.suffix == '.glb':
        path = Path(str(path)+'.import')
    found = re.search(r'uid="([^"]+)"', path.read_text())
    assert found, path
    return found[1]


def main():
    """Reject stale exports, detached models, generated draw meshes and duplicate world IDs."""
    plan = json.loads((SOURCE/'authoring_plan.json').read_text())
    assert (ROOT/'art/source/.gdignore').exists()
    for name, sha in plan['reference_hashes'].items():
        assert digest(ROOT/name) == sha, name
    fingerprints = json.loads((ROOT/'art/models/brackett_greybox/fingerprints.json').read_text())
    for row in fingerprints:
        assert digest(ROOT/row['source']) == row['source_sha256'], row
        exported = ROOT/'art/models/brackett_greybox'/row['export']
        assert digest(exported) == row['export_sha256'], row
        data = exported.read_bytes()
        magic, version, total, length, kind = struct.unpack_from('<IIIII', data)
        assert (magic, version, total, kind) == (0x46546c67, 2, len(data), 0x4e4f534a)
        gltf = json.loads(data[20:20+length])
        assert not gltf.get('animations') and not gltf.get('skins') and not gltf.get('images')
        assert not gltf.get('cameras') and not gltf.get('extensionsUsed')
    scenes = list((ROOT/'scenes/world/brackett_greybox').rglob('*.tscn'))
    identities, placed, dependencies = {}, [], []
    for path in scenes:
        text = path.read_text()
        identity = uid(path)
        assert identity not in identities, (identity, path)
        identities[identity] = str(path.relative_to(ROOT))
        assert not re.search(r'type="(?:ArrayMesh|BoxMesh|CylinderMesh|SphereMesh|CSG\w+)"', text), path
        assert all('unique_id=' in b for b in re.findall(r'\[node [^\]]+\]', text)), path
        for block in re.findall(r'\[ext_resource [^\]]+\]', text):
            target = re.search(r'path="res://([^"]+)"', block)
            expected = re.search(r'uid="([^"]+)"', block)
            assert target and expected, (path, block)
            actual = ROOT/target[1]
            assert actual.exists() and uid(actual) == expected[1], (path, target[1], expected[1])
            dependencies.append([str(path.relative_to(ROOT)), target[1]])
        placed += re.findall(r'world_id = &"(brackett/district_\d+/building_\d+)"', text)
    assert len(placed) == len(set(placed)) == 290
    assert set(placed) == {p['world_id'] for p in plan['placements']}
    assert len(scenes) == 50 and len(fingerprints) == 40
    result = dict(scene_count=len(scenes), export_count=len(fingerprints), placement_count=len(placed),
                  source_count=len({p['source'] for p in fingerprints}), reference_hashes=plan['reference_hashes'],
                  dependencies=dependencies, resource_uids=identities)
    (SOURCE/'review/file_checks.json').write_text(json.dumps(result, indent=2)+'\n')
    print('BRACKETT_FILE_CHECKS', len(scenes), 'scenes;', len(fingerprints), 'exports;', len(placed), 'IDs')


if __name__ == '__main__':
    main()
