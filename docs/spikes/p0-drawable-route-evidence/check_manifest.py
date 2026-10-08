"""Freeze or verify one complete evidence path set, without recursively hashing itself."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def main():
    """Compare index-derived expected paths, actual paths and every retained byte hash."""
    manifest = ROOT / 'manifest.json'
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()
              and p != manifest}
    result = subprocess.run(['git', 'ls-files', '-z', '--', str(ROOT)], cwd=REPO,
                            capture_output=True, check=True)
    expected = {Path(p.decode()).relative_to(ROOT.relative_to(REPO)).as_posix()
                for p in result.stdout.split(b'\0') if p}
    expected.discard('manifest.json')
    assert actual == expected, {'missing': sorted(expected - actual),
                                'extra': sorted(actual - expected)}
    if '--freeze' in sys.argv:
        rows = {}
        for name in sorted(expected):
            data = (ROOT / name).read_bytes()
            rows[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        manifest.write_text(json.dumps({'expected_paths': sorted(expected), 'files': rows},
                                       indent=2) + '\n')
    data = json.loads(manifest.read_text())
    assert set(data['expected_paths']) == expected == set(data['files'])
    for name in sorted(expected):
        payload = (ROOT / name).read_bytes()
        assert data['files'][name] == {'bytes': len(payload),
                                     'sha256': hashlib.sha256(payload).hexdigest()}, name
    print(json.dumps({'complete_expected_set': len(expected), 'readback': 'pass',
                      'manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
