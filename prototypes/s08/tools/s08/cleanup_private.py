"""Clean only a recorded, reaped S08 private editor's stale registration."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path('/tmp/s08-standard-555e0330')
REGISTRY = ROOT / 'scan-complete-attempt/private/data/godot-mcp-toolkit'
PROJECT = str(ROOT / 'project')


def strip_owned(projection, entry, pid):
    """Remove the matching canonical row while preserving unrelated projection data."""
    if entry['_key'] != PROJECT or entry['pid'] != pid:
        raise ValueError('entry is not recorded owned editor')
    expected = {key: value for key, value in entry.items() if key != '_key'}
    if projection['by_path'].get(PROJECT) != expected:
        raise ValueError('private projection differs from owned entry')
    result = json.loads(json.dumps(projection))
    del result['by_path'][PROJECT]
    return result


def main():
    """Retain before/after bytes, then delete only an exclusively owned stale entry."""
    output = ROOT / 'cleanup-before-run04'
    output.mkdir()
    receipt = json.loads((ROOT / 'actual-editor-run03/lifecycle.json').read_text())
    command = receipt['commands'][0]
    if not receipt['all_children_reaped'] or command['owned_pid'] != 561147 or not command['reaped']:
        raise ValueError('recorded own run03 not reaped')
    entry_path = REGISTRY / 'entries/e9fb882bfd3c.json'
    projection_path = REGISTRY / 'projects.json'
    before = {path.name: path.read_bytes() for path in [entry_path, projection_path]}
    for name, raw in before.items():
        (output / name).write_bytes(raw)
    entry = json.loads(before[entry_path.name])
    projection = json.loads(before[projection_path.name])
    after = strip_owned(projection, entry, 561147)
    unrelated = {'pid': 123456, 'port': 6554, 'token_path': '/tmp/unrelated'}
    fixture = json.loads(json.dumps(projection))
    fixture['by_path']['/tmp/unrelated-project'] = unrelated
    assert strip_owned(fixture, entry, 561147)['by_path']['/tmp/unrelated-project'] == unrelated
    assert PROJECT not in after['by_path'] and not after['by_path']
    assert {p.name for p in (REGISTRY / 'entries').iterdir()} == {entry_path.name}
    # Installed FileLock uses a regular PID:timestamp file; no writer/lock remains.
    assert not (REGISTRY / 'projects.json.lock').exists()
    entry_path.unlink()
    projection_path.write_text(json.dumps(after, indent=2) + '\n')
    result = {'ok': True, 'owned_reaped_pid': 561147, 'canonical_project': PROJECT,
              'entry_absent': not entry_path.exists(), 'projection_after': after,
              'unrelated_fixture_unchanged': True,
              'before': {name: {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                         for name, raw in before.items()},
              'after': {'bytes': projection_path.stat().st_size,
                        'sha256': hashlib.sha256(projection_path.read_bytes()).hexdigest()}}
    (output / 'after.json').write_bytes(projection_path.read_bytes())
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
