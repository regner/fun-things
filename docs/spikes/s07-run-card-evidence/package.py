#!/usr/bin/env python3
"""Check the declared complete package and bind actual readback bytes, without encoding."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FOLDER = ROOT / 'docs/spikes/s07-run-card-evidence'


def main():
    """Reject missing/extra payloads and reread every manifest entry against source bytes."""
    expected = json.loads((FOLDER / 'expected-set.json').read_text())
    assert len(expected) == len(set(expected))
    actual = {str(p.relative_to(ROOT)) for p in FOLDER.rglob('*') if p.is_file()
              and p.name != 'manifest.json'}
    external = {'TODO.md', 'tools/s07/inventory.py', 'docs/spikes/s07-run-cards.md'}
    assert actual | external == set(expected), ('package path-set mismatch', actual, expected)
    rows = {}
    sources = {}
    for path in expected:
        data = (ROOT / path).read_bytes()
        sources[path] = data
        rows[path] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    manifest = {'format': 1, 'manifest_excluded_from_self_hash': True, 'payloads': rows}
    (FOLDER / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    readback = json.loads((FOLDER / 'manifest.json').read_bytes())
    assert set(readback['payloads']) == set(expected)
    for path, row in readback['payloads'].items():
        stored = (ROOT / path).read_bytes()
        assert stored == sources[path], path
        assert len(stored) == row['bytes']
        assert hashlib.sha256(stored).hexdigest() == row['sha256'], path
    print(f'PASS complete expected set and source/readback hashes: {len(expected)} payloads; '
          'manifest metadata excluded from self-hash')


if __name__ == '__main__':
    main()
