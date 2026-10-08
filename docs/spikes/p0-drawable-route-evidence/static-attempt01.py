"""Check source acquisition, scoped links and preservation without engine execution."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
BASE = '233493abc7d2e3c106fb620105cfb766f542813b'


def unique_pairs(pairs):
    """Reject duplicated JSON keys rather than silently accepting overwritten evidence."""
    result = {}
    for key, value in pairs:
        assert key not in result, key
        result[key] = value
    return result


def verify(row):
    """Compare the actual retained bytes against their original acquisition identity."""
    data = (ROOT / row['path']).read_bytes()
    assert len(data) == row['bytes'], row['path']
    assert hashlib.sha256(data).hexdigest() == row['sha256'], row['path']


def main():
    """Check the complete declared acquisition and unchanged original tracked paths."""
    first = json.loads((ROOT / 'acquisition.json').read_text(), object_pairs_hook=unique_pairs)
    fifo = json.loads((ROOT / 'fifo-acquisition.json').read_text(), object_pairs_hook=unique_pairs)
    source_paths = []
    inventory_paths = []
    for row in first:
        if 'url' in row:
            assert row['status'] == 200 and '/c971f93e7e76b0ef919bf6009e7b868bea04db7f/' in row['url']
            verify(row['payload'])
            source_paths.append(row['payload']['path'])
        if 'argv' in row:
            assert row['exit'] == 0
            for stream in ['stdout', 'stderr']:
                verify(row[stream])
                inventory_paths.append(row[stream]['path'])
    for row in fifo:
        assert row['status'] == 200 and '/c971f93e7e76b0ef919bf6009e7b868bea04db7f/' in row['url']
        verify(row)
        source_paths.append(row['path'])
    assert len(source_paths) == 9 and len(set(source_paths)) == 9
    assert set(source_paths) == {p.relative_to(ROOT).as_posix() for p in (ROOT / 'source').rglob('*') if p.is_file()}
    assert set(inventory_paths) == {f'inventory/{index}.{stream}' for index in range(4) for stream in ['stdout', 'stderr']}
    assert set(inventory_paths) == {p.relative_to(ROOT).as_posix() for p in (ROOT / 'inventory').iterdir()}
    links = 0
    for path in [ROOT / 'README.md', ROOT.parent / 'p0-drawable-route.md']:
        data = path.read_bytes()
        assert b'\r' not in data and data.endswith(b'\n'), str(path)
        for target in re.findall(r'\]\(([^)]+)\)', data.decode()):
            if '://' in target or target.startswith('#'):
                continue
            assert (path.parent / target.split('#')[0]).resolve().exists(), target
            links += 1
    for name in ['discover.py', 'supplement.py', 'static_check.py']:
        ast.parse((ROOT / name).read_text(), filename=name)
    for path in ROOT.rglob('*.json'):
        json.loads(path.read_text(), object_pairs_hook=unique_pairs)
    command = ['git', 'diff', '--name-only', BASE, '--']
    result = subprocess.run(command, cwd=REPO, capture_output=True, check=False)
    assert result.returncode == 0 and result.stderr == b''
    changed = result.stdout.decode().splitlines()
    assert all(path == 'docs/spikes/p0-drawable-route.md' or
               path.startswith('docs/spikes/p0-drawable-route-evidence/') for path in changed), changed
    result = subprocess.run(['git', 'diff', '--check', BASE], cwd=REPO, capture_output=True, check=False)
    assert result.returncode == 0 and not result.stdout and not result.stderr
    summary = {'source_files': len(source_paths), 'metadata_streams': len(inventory_paths),
               'local_links': links, 'python_ast': 'pass', 'strict_json': 'pass',
               'base': BASE, 'scope_and_whitespace': 'pass', 'engine_operations': 0,
               'argv': ['python3', 'docs/spikes/p0-drawable-route-evidence/static_check.py']}
    (ROOT / 'static-result.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
