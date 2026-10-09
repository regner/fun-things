#!/usr/bin/env python3
"""Bind accepted cached artifacts and execute only the predeclared exported ENet set."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import zipfile

import observe

ACCEPTED = '52941da4b4c92a547a8066b5c13f733043ecbe48'
CACHED = Path('/tmp/s08-addon-free-555e0330-release01')
ARCHIVE = Path('/tmp/s08-observation-stpco415/Godot_v4.8-dev7_export_templates.tpz')
EVIDENCE = observe.ROOT/'docs/spikes/s08-standard-editor-evidence/addon-free-release'
STDBUF = Path('/usr/bin/stdbuf')
STDBUF_LIBRARY = Path('/usr/lib/coreutils/libstdbuf.so')


def bind(task):
    """Reject any uncertainty in source, archive, template, PCK, manifest or exclusions."""
    if any(name in os.environ for name in ['LD_PRELOAD', '_STDBUF_O', '_STDBUF_E', '_STDBUF_I']):
        raise RuntimeError('inherited output/preload override: STOP before engine')
    original = json.loads((EVIDENCE/'template-rebind.json').read_text())
    assert observe.identity(ARCHIVE) == original['tpz']
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert archive.read('templates/version.txt').decode().strip() == '4.8.dev7'
        for row in original['members']:
            assert archive.getinfo(row['path']).file_size == row['bytes']
            with archive.open(row['path']) as stream:
                assert hashlib.file_digest(stream, 'sha256').hexdigest() == row['sha256']
    assert observe.identity(CACHED/'custom_template/release') == original['template']
    assert observe.identity(Path(observe.ENGINE)) == {
        'bytes':151398728, 'sha256':observe.ENGINE_SHA}
    expected = json.loads((EVIDENCE/'output-folder.json').read_text())
    assert {p.name for p in (CACHED/'export-folder').iterdir()} == {r['path'] for r in expected}
    for row in expected:
        assert observe.identity(CACHED/'export-folder'/row['path']) == {
            'bytes':row['bytes'], 'sha256':row['sha256']}
    staged = json.loads((EVIDENCE/'staged-input.json').read_text())
    assert len(staged) == 34
    for row in staged:
        data = observe.git_blob(row['path'], ACCEPTED)
        assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
        assert (CACHED/'project'/row['path']).read_bytes() == data
        assert (observe.ROOT/row['path']).read_bytes() == data
    (task/'export-folder').symlink_to(CACHED/'export-folder', target_is_directory=True)
    (task/'custom_template').symlink_to(CACHED/'custom_template', target_is_directory=True)
    (task/'staged-input.json').write_bytes((EVIDENCE/'staged-input.json').read_bytes())
    observe.pck_manifest(task, saved_entrypoint=True)
    members = json.loads((task/'pck-members.json').read_text())
    assert members == json.loads((EVIDENCE/'pck-members.json').read_text())
    data = (CACHED/'export-folder/FunThingsS08.pck').read_bytes()
    manifest = next(row for row in members['entries'] if row['path'] == 's08_inputs.json')
    payload = data[manifest['offset']:manifest['offset']+manifest['bytes']]
    assert json.loads(payload) == staged
    assert payload == (CACHED/'project/s08_inputs.json').read_bytes()
    # Bind scratch config bytes used for this exact package, including normal saved main.
    configs = json.loads((EVIDENCE/'scratch-config.json').read_text())
    for name, expected_identity in configs.items():
        assert observe.identity(CACHED/'project'/name) == expected_identity
    settings = (CACHED/'project/project.godot').read_text()
    assert 'run/main_scene="res://tests/fixtures/s08/release_boot.tscn"' in settings
    assert '[autoload]' not in settings and '[editor_plugins]' not in settings
    assert 'flush_stdout_on_print' not in settings
    result = {'ok':True, 'accepted_source':ACCEPTED, 'source_files':staged,
              'tpz':original, 'output':expected, 'pck_members':len(members['entries']),
              'scratch_configs':configs, 'engine':observe.identity(Path(observe.ENGINE)),
              'launcher':{str(p):observe.identity(p) for p in [STDBUF, STDBUF_LIBRARY]},
              'cached_folder':str(CACHED/'export-folder'), 'engine_operations':0}
    observe.write_json(task/'binding.json', result)


def main():
    """Fresh output only; bind once, or run once after exact binding readback."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['bind', 'run'])
    parser.add_argument('task', type=Path)
    args = parser.parse_args()
    task = args.task.resolve()
    if not task.is_relative_to(Path('/tmp/s08-handoff-8cae02a7')):
        parser.error('only own predeclared scratch root')
    if args.mode == 'bind':
        task.mkdir()
        bind(task)
    else:
        record = json.loads((task/'binding.json').read_text())
        assert record['ok'] is True and record['accepted_source'] == ACCEPTED
        for path, expected in record['launcher'].items():
            assert observe.identity(Path(path)) == expected
        for row in record['output']:
            assert observe.identity(task/'export-folder'/row['path']) == {
                'bytes':row['bytes'], 'sha256':row['sha256']}
        # network creates enet exclusively: an existing attempt cannot be overwritten.
        observe.network(task, require_asset_receipts=True,
                        stdout_prefix=(str(STDBUF), '-oL'), readiness_seconds=4.0)
    print(json.dumps({'ok':True, 'mode':args.mode}))


if __name__ == '__main__':
    main()
