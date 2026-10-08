#!/usr/bin/env python3
"""Retain the complete bounded S05 receipts with explicit expected-set and source readback."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
RUN = Path('/tmp/s05-draw-8c398027-run01')
DEST = ROOT / 'docs/spikes/s05-render-observation-evidence'


def digest(data):
    """Bind both stored and decoded bytes; an empty stream remains a real payload."""
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def expected_sources():
    """Derive complete finite source requirements, including failures and absent images."""
    sources = {}
    author = RUN / 'author-log'
    for name in ['commands-before-engine.json', 'lifecycle.json', 'context.gd', 'client.mjs',
                 'tool-inventory.json', 'observe.stdout', 'observe.stderr',
                 'observe.engine.log', 'connector.stderr']:
        sources['author/' + name] = author / name
    for index in range(1, 45):
        for kind in ['request', 'response']:
            name = f'call-{index:03d}.{kind}.json'
            sources['author/' + name] = author / name
    for index in range(1, 43):
        name = f'{index:03d}.json'
        sources['author/requests/' + name] = author / 'requests' / name
        if index <= 41:
            sources['author/responses/' + name] = author / 'responses' / name
    for group, roles in [('group01', ['host']), ('group02', ['host', 'client', 'late'])]:
        for name in ['copy-ledger.json', 'lifecycle.json']:
            sources[group + '/' + name] = RUN / group / name
        for suffix in ['stdout', 'stderr']:
            name = group + '-supervisor.' + suffix
            sources[name] = RUN / name
        for role in roles:
            for name in ['stdout', 'stderr', 'engine.log']:
                sources[group + '/' + role + '/' + name] = RUN / group / role / name
            if group == 'group02':
                sources[group + '/' + role + '/draw.jsonl'] = (
                    RUN / group / role / 'data/godot/app_userdata/Fun Things/draw.jsonl')
    for name in ['preparation.json', 'roundtrip.json', 'observer-script.request.json',
                 'camera-author.stdout', 'camera-author.stderr',
                 'engine-help.stdout', 'engine-help.stderr', 'python-static.json',
                 'pre-graphical-check.json', 'pre-graphical-check.stdout',
                 'pre-graphical-check.stderr', 'observation-check.json',
                 'observation-check.stdout', 'observation-check.stderr', 'candidate-check.json']:
        sources['checks/' + name] = RUN / name
    sources['author/inputs.json'] = RUN / 'author-state/inputs.json'
    for name in ['format-initial', 'lint-initial', 'format-final', 'lint-final',
                 'format-candidate', 'lint-candidate', 'check-candidate', 'diff-check']:
        for suffix in ['stdout', 'stderr']:
            sources['checks/' + name + '.' + suffix] = RUN / (name + '.' + suffix)
        if name not in ['format-initial', 'lint-initial']:
            sources['checks/' + name + '.command.json'] = RUN / (name + '.command.json')
    for suffix in ['stdout', 'stderr']:
        sources['author/supervisor.' + suffix] = Path('/tmp/s05-draw-8c398027-supervisor.' + suffix)
    for name in ['final-static', 'old-run04-history']:
        for suffix in ['py', 'json', 'stdout', 'stderr']:
            sources['checks/' + name + '.' + suffix] = RUN / (name + '.' + suffix)
    sources['checks/final-static-observation.json'] = RUN / 'final-static-observation.json'
    for index in range(4):
        for suffix in ['stdout', 'stderr']:
            name = f'final-static-{index}.{suffix}'
            sources['checks/' + name] = RUN / name
    for suffix in ['py', 'stdout', 'stderr', '-0.stdout', '-0.stderr']:
        name = ('final-static-invocation-failed' + ('' if suffix.startswith('-') else '.')
                + suffix)
        sources['checks/' + name] = RUN / name
    for name in ['budget-check.stdout', 'budget-check.stderr', 'budget-check.command.json',
                 'budget-check-initial.py', 'budget-check-initial.stdout',
                 'budget-check-initial.stderr']:
        sources['checks/' + name] = RUN / name
    return sources


def main():
    """Write one proportionate pack, then read every source/stored/decoded payload back."""
    sources = expected_sources()
    manifest = {}
    folder = DEST / 'payloads'
    for name, source in sources.items():
        data = source.read_bytes()
        encoded = gzip.compress(data, mtime=0)
        target = folder / (name + '.gz')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encoded)
        manifest[name] = {'source': str(source), 'stored_path': target.relative_to(DEST).as_posix(),
                          'decoded': digest(data), 'stored': digest(encoded)}
    actual = {p.relative_to(folder).as_posix()[:-3] for p in folder.rglob('*.gz')}
    assert actual == set(sources), 'complete expected payload set mismatch'
    for name, source in sources.items():
        entry = manifest[name]
        stored = (DEST / entry['stored_path']).read_bytes()
        decoded = gzip.decompress(stored)
        assert digest(stored) == entry['stored'] and digest(decoded) == entry['decoded']
        assert decoded == source.read_bytes(), 'source readback mismatch: ' + name
    absent = {
        'group01_draw_stream': not any((RUN / 'group01').rglob('draw.jsonl')),
        'group01_client_late_not_launched': set(json.loads((RUN / 'group01/lifecycle.json')
                                                         .read_text())['processes']) == {'host'},
        'all_workload_pngs_absent': not any(RUN.glob('group*/**/*.png'))}
    assert all(absent.values())
    record = {'schema': 1, 'expected_payloads': sorted(sources), 'payloads': manifest,
              'absent_expected_outputs': absent,
              'originals_and_resources_ledger': 'checks/candidate-check.json',
              'executed_sources': [
                  {'ref': '0550686', 'path': 'tools/s05_draw/private_author.py'},
                  {'ref': '63e75c5', 'path': 'tools/s05_draw/observe.py', 'group': 1},
                  {'ref': 'f6c8544', 'path': 'tools/s05_draw/observe.py', 'group': 2},
                  {'ref': '63e75c5', 'path': 'tests/fixtures/s05_draw/observer.gd'},
                  {'ref': '48aef3dbd133876743f504f94a1b788a26d5638f',
                   'path': 'tools/s05_effect/private_author.py'}]}
    for row in record['executed_sources']:
        data = subprocess.check_output(['git', 'show', row['ref'] + ':' + row['path']], cwd=ROOT)
        row.update(digest(data))
    (DEST / 'manifest.json').write_text(json.dumps(record, indent=2) + '\n')
    readback = {'ok': True, 'complete_expected_set': len(sources),
                'source_stored_decoded_matches': len(sources), 'absent_expected_outputs': absent,
                'manifest': digest((DEST / 'manifest.json').read_bytes())}
    (DEST / 'readback.json').write_text(json.dumps(readback, indent=2) + '\n')
    required = {'README.md', 'manifest.json', 'readback.json', 'raw-commission.txt',
                'raw-camera-and-review-grant.txt', 'raw-deferred-pause.txt',
                'raw-main-notification.txt'} | {
                    entry['stored_path'] for entry in manifest.values()}
    actual = {p.relative_to(DEST).as_posix() for p in DEST.rglob('*') if p.is_file()}
    assert actual - {'envelope.json'} == required, 'complete evidence envelope mismatch'
    envelope = {'expected_paths': sorted(required | {'envelope.json'}),
                'files': {name: digest((DEST / name).read_bytes()) for name in sorted(required)},
                'raw_brief_source': 'Verbatim commissioned user messages, in supplied order.',
                'source_readback': readback}
    (DEST / 'envelope.json').write_text(json.dumps(envelope, indent=2) + '\n')
    for name, expected in envelope['files'].items():
        assert digest((DEST / name).read_bytes()) == expected
    assert {p.relative_to(DEST).as_posix() for p in DEST.rglob('*') if p.is_file()} == set(
        envelope['expected_paths'])
    print(json.dumps(readback, indent=2))


if __name__ == '__main__':
    main()
