#!/usr/bin/env python3
"""Retain the one consumed attempt with an independently declared required payload set."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / 'docs/spikes/s05-vsync-image-observation-evidence'
RUN = Path('/tmp/p0-image-01a11bc0-attempt01')
CHECKS = Path('/tmp/s05-vsync-image-checks')
EXECUTED = '4a50808ba0441a7c116d14d78a4286a6f89f7691'
CHECK_NAMES = ['offline01', 'style01', 'static01', 'offline02', 'format01',
               'offline03-corrected', 'evaluation01', 'attempt01']


def fingerprint(data):
    """Bind exact stored and decoded bytes, including zero-byte streams."""
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def main():
    """Package once; later unchanged-candidate review receipts belong to a Git note."""
    assert not (PACK / 'manifest.json').exists(), 'one declared package; do not overwrite history'
    payloads, expected, records = {}, set(), {}
    def require(name, source):
        """Declare each required actual payload before encoding it."""
        assert name not in expected
        expected.add(name)
        payloads[name] = (source.read_bytes(), str(source))
    life = json.loads((RUN / 'lifecycle.json').read_text())
    for name in ['lifecycle.json', 'copy-ledger.json', 'generated-imports.json']:
        require('attempt/' + name, RUN / name)
    for role in life['processes']:
        for name in ['stdout', 'stderr', 'engine.log']:
            require('attempt/' + role + '/' + name, RUN / role / name)
    require('attempt/host/draw.jsonl', RUN / 'host/data/godot/app_userdata/Fun Things/draw.jsonl')
    copied = json.loads((RUN / 'copy-ledger.json').read_text())['files']
    generated = json.loads((RUN / 'generated-imports.json').read_text())['files']
    for row in copied + generated:
        name = row['path']
        source = RUN / 'project' / name
        assert fingerprint(source.read_bytes()) == {'bytes': row['bytes'], 'sha256': row['sha256']}, name
        label = name.replace('.godot/', 'generated-imports/', 1) if name.startswith('.godot/') else name
        require('attempt/project/' + label, source)
    for name in CHECK_NAMES:
        for suffix in ['command.json', 'stdout', 'stderr']:
            require('checks/' + name + '.' + suffix, CHECKS / (name + '.' + suffix))
    for name in ['static01.json', 'evaluation01.json']:
        require('checks/' + name, CHECKS / name)
    for name in ['run.py', 'check.py', 'test_offline.py', 'record.py']:
        path = 'tools/s05_vsync_image/' + name
        expected.add('sources/executed/' + path)
        payloads['sources/executed/' + path] = (subprocess.check_output(
            ['git', 'show', EXECUTED + ':' + path], cwd=ROOT), 'Git ' + EXECUTED + ':' + path)
    # Recover the first offline draft from the committed second draft and exact authored edit.
    # This is byte-bound source recovery, NOT reconstruction of a missing runtime/proc receipt.
    draft = payloads['sources/executed/tools/s05_vsync_image/test_offline.py'][0].decode()
    start, end = draft.index('def evaluator_negatives():'), draft.index('def main():', draft.index('def evaluator_negatives():'))
    draft = draft[:start] + draft[end:]
    draft = draft.replace("'cases': results, 'evaluator_negatives': evaluator_negatives()", "'cases': results")
    data = draft.encode()
    command = json.loads((CHECKS / 'offline01.command.json').read_text())
    assert fingerprint(data) == command['sources']['tools/s05_vsync_image/test_offline.py']
    expected.add('sources/recovered-offline01-test_offline.py')
    payloads['sources/recovered-offline01-test_offline.py'] = (
        data, 'Recovered exact authored edit predecessor; verified against original command SHA256')
    for name in ['run.py', 'check.py', 'test_offline.py', 'record.py', 'retain.py']:
        require('sources/corrected-offline/tools/s05_vsync_image/' + name,
                ROOT / 'tools/s05_vsync_image' / name)
    for path in life['source_ancestry']:
        require('source-ancestry/' + path, ROOT / path)
    absent = {role: [stage for stage in stages if not list((RUN / role).rglob(stage + '.png'))]
              for role, stages in [('host', ['baseline', 'burst', 'expired']),
                 ('client', ['baseline', 'burst', 'expired']), ('late', ['hydrated'])]}
    assert absent == {'host': ['baseline', 'burst', 'expired'],
                      'client': ['baseline', 'burst', 'expired'], 'late': ['hydrated']}
    assert not (RUN / 'client').exists() and not (RUN / 'late').exists()
    excluded_caches = [str(p.relative_to(RUN)) for p in RUN.rglob('*') if p.is_file() and
                      ('shader_cache' in p.parts or 'cache' in p.parts)]
    for name in sorted(expected):
        data, source = payloads[name]
        relative = 'payloads/' + name + '.gz'
        path = PACK / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        stored = gzip.compress(data, mtime=0)
        path.write_bytes(stored)
        records[relative] = {'source': source, 'decoded': fingerprint(data),
                             'stored': fingerprint(stored)}
    raw_names = ['README.md', 'raw-commission.txt', 'raw-main-notification.txt',
                 'raw-stop-confirmation.txt']
    manifest = {'executed_candidate': EXECUTED, 'commissioned_base': life['base'],
                'required_payloads': sorted(expected), 'payloads': records,
                'raw_files': {name: fingerprint((PACK / name).read_bytes()) for name in raw_names},
                'expected_paths': sorted([*records, *raw_names, 'manifest.json', 'readback.json']),
                'absence': {'images': absent, 'never_launched': ['client', 'late'],
                    'no_post_draw_or_final_observer_row': True,
                    'failed_endpoint_lookup_inputs_not_retained': True},
                'excluded_reproducible_cache_files': excluded_caches,
                'exclusion_reason': 'driver/editor/shader caches are not proof streams or generated imports'}
    (PACK / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    actual = {str(p.relative_to(PACK)) for p in PACK.rglob('*') if p.is_file()}
    assert actual == set(manifest['expected_paths']) - {'readback.json'}
    for relative, row in records.items():
        actual = (PACK / relative).read_bytes()
        assert fingerprint(actual) == row['stored']
        decoded = gzip.decompress(actual)
        assert fingerprint(decoded) == row['decoded']
        assert decoded == payloads[relative.removeprefix('payloads/').removesuffix('.gz')][0]
    readback = {'complete_expected_set_verified': True, 'source_stored_decoded_equal': len(records),
                'manifest': fingerprint((PACK / 'manifest.json').read_bytes()),
                'absence_verified': True, 'raw_lookup_reconstruction': False}
    (PACK / 'readback.json').write_text(json.dumps(readback, indent=2) + '\n')
    assert {str(p.relative_to(PACK)) for p in PACK.rglob('*') if p.is_file()} == set(manifest['expected_paths'])
    print(json.dumps(readback, indent=2))


if __name__ == '__main__':
    main()
