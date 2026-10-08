#!/usr/bin/env python3
"""Verify the full declared evidence/readback set and independent required streams, offline."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    """Reject omitted required payloads, changed bytes, lost empties or out-of-scope changes."""
    index_path = HERE / 'index.json'
    index_bytes = index_path.read_bytes()
    assert subprocess.check_output(['git', 'show', 'HEAD:' +
        index_path.relative_to(ROOT).as_posix()], cwd=ROOT) == index_bytes
    index = json.loads(index_bytes)
    expected = set(index['expected_paths'])
    assert len(expected) == len(index['expected_paths'])
    actual = {path.relative_to(HERE).as_posix() for path in HERE.rglob('*') if path.is_file()
              and '__pycache__' not in path.parts and path.name != 'index.json'}
    assert actual == expected, {'missing': sorted(expected - actual), 'extra': sorted(actual - expected)}
    required = {'README.md', 'verify.py', 'raw-requirements.md', 'raw-user-messages.json',
        'original-operation-receipts.jsonl', 'historical-reference.json', 'launch-receipt.json'}
    required |= {'author/call-%03d.%s.json' % (number, kind)
                 for number in range(1, 21) for kind in ['request', 'response']}
    required |= {'author/requests/%03d.json' % number for number in range(1, 19)}
    required |= {'author/responses/%03d.json' % number for number in range(1, 18)}
    required |= {'author/' + name for name in ['observe.stdout', 'observe.stderr', 'observe.engine.log',
        'connector.stderr', 'context.gd', 'client.mjs', 'lifecycle.json', 'preparation.json', 'inputs.json']}
    for group in ['debug01', 'release02', 'release-preparation']:
        declared = json.loads((HERE / group / 'expected.json').read_text())
        required.add(group + '/expected.json')
        required |= {group + '/' + name for name in declared['required_paths']}
        for name in declared['required_empty']:
            assert (HERE / group / name).read_bytes() == b''
    for group in ['debug01', 'release02']:
        for role in ['host', 'client']:
            required |= {group + '/' + role + '/' + name
                         for name in ['command.json', 'stdout.log', 'stderr.log', 'engine.log']}
        required |= {group + '/' + name for name in ['result.json', 'traffic.jsonl', 'proxy.jsonl',
            'staged-input.json', 'cache-config-readback.json']}
    assert required <= expected, sorted(required - expected)
    rows = {row['path']: row for row in index['payloads']}
    assert set(rows) == expected and len(rows) == len(index['payloads'])
    for name in sorted(expected):
        data = (HERE / name).read_bytes()
        assert len(data) == rows[name]['bytes']
        assert hashlib.sha256(data).hexdigest() == rows[name]['sha256']
        assert rows[name]['required_empty'] == (len(data) == 0)
        committed = subprocess.check_output(['git', 'show', 'HEAD:' +
            (HERE / name).relative_to(ROOT).as_posix()], cwd=ROOT)
        assert committed == data, name
    changed = subprocess.check_output(['git', 'diff', '--name-only', index['delivery_base'], 'HEAD'],
                                      cwd=ROOT, text=True).splitlines()
    for name in changed:
        assert (name in ['TODO.md', 'tests/fixtures/s03/session.gd', 'tests/fixtures/s03/proof.gd']
                or name == 'docs/spikes/s08-release-lifecycle.md'
                or name.startswith('docs/spikes/s08-release-lifecycle-evidence/')
                or name.startswith('tools/s08/lifecycle_')), name
    base_todo = subprocess.check_output(['git', 'show', index['delivery_base'] + ':TODO.md'], cwd=ROOT).decode()
    current_todo = (ROOT / 'TODO.md').read_text()

    def outside_s08(text):
        """Compare every unowned task and cell while allowing only the declared S08 cell."""
        start = text.index('- [ ] **S08 —')
        end = text.index('- [ ] **P0-GATE', start)
        return (text[:start] + text[end:]).replace('S08 release-cache/entrypoint diagnosis',
                                                   'S08 runner follow-up')

    assert outside_s08(base_todo) == outside_s08(current_todo)
    print(json.dumps({'payload_count': len(expected), 'required_empty_count': sum(
        row['required_empty'] for row in rows.values()), 'complete_set_hash_readback': True,
        'scope_and_unrelated_TODO_preserved': True, 'delivery_base': index['delivery_base']}))


if __name__ == '__main__':
    main()
