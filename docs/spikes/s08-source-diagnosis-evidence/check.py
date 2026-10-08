#!/usr/bin/env python3
"""Static-only S08 source, immutable evidence, closure and preservation checks."""
import argparse
import ast
import base64
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE = '85282adddd8182a6f31b2c80e4419d1d406b3bb2'
LIFE = 'fd375c03dcbb1b3d6d98ddb4c3e8e94d9c5fa07d'
HAND = '0add62579b3f98ec010badb31613c411e2ea7b12'
STANDARD = '52941da4b4c92a547a8066b5c13f733043ecbe48'
SRC = 'docs/spikes/s08-release-lifecycle-evidence/source/'
EVID = 'docs/spikes/s08-release-lifecycle-evidence/'
OWN = 'docs/spikes/s08-source-diagnosis'
ENGINE = 'c971f93e7e76b0ef919bf6009e7b868bea04db7f'
NOTES = {
    LIFE: '22243a163468812439018138e4d2ef4158373087',
    HAND: 'a6338d8a60479cc98486175cdf696d2c6f5b3f26',
    STANDARD: '7136e1e504b16daa151ba0bdd1b990abcd6076d6',
}
NATIVE = {
    'scene_cache_interface.cpp': 'modules/multiplayer/scene_cache_interface.cpp',
    'scene_multiplayer.cpp': 'modules/multiplayer/scene_multiplayer.cpp',
    'scene_rpc_interface.cpp': 'modules/multiplayer/scene_rpc_interface.cpp',
    'object.cpp': 'core/object/object.cpp',
    'variant-callable.cpp': 'core/variant/callable.cpp',
    'callable_bind.cpp': 'core/variant/callable_bind.cpp',
    'callable_mp.cpp': 'core/object/callable_mp.cpp',
    'callable_mp.h': 'core/object/callable_mp.h',
    'gdscript_vm.cpp': 'modules/gdscript/gdscript_vm.cpp',
}
ANCHORS = {
    'scene_cache_interface.cpp': ['SceneCacheInterface::_track',
        'SceneCacheInterface::_remove_node_cache', 'SceneCacheInterface::on_peer_change',
        'SceneCacheInterface::process_simplify_path', 'SceneCacheInterface::get_cached_object',
        'SceneCacheInterface::clear'],
    'object.cpp': ['Error Object::connect(', 'bool Object::_disconnect(',
        '// Disconnect all one-shot connections before emitting'],
    'variant-callable.cpp': ['const Callable *Callable::get_base_comparator()',
        'bool Callable::operator=='],
    'callable_bind.cpp': ['const Callable *CallableCustomBind::get_base_comparator()'],
    'callable_mp.cpp': ['bool CallableCustomMethodPointerBase::compare_equal',
        'void CallableCustomMethodPointerBase::_setup'],
    'scene_multiplayer.cpp': ['void SceneMultiplayer::set_multiplayer_peer',
        'SceneMultiplayer::SceneMultiplayer()', 'SceneMultiplayer::~SceneMultiplayer()'],
}


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def blob(revision, path):
    return git('show', revision + ':' + path)


def identity(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def strict(data):
    def pairs(rows):
        result = {}
        for key, value in rows:
            assert key not in result, ('duplicate JSON key', key)
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def reports(revision, note):
    if revision == LIFE:
        rows = {row['path']: row for row in note['payloads']}
        keys = ['review/report.md', 'review/final-report.md']
        return [(key, zlib.decompress(base64.b64decode(rows[key]['data'])), rows[key])
                for key in keys]
    if revision == STANDARD:
        rows = note['reviewer_payloads']
        return [(key, rows[key]['text'].encode(), rows[key])
                for key in ['report.md', 'final-report.md']]
    envelope = note['retained_payloads']
    compressed = base64.b64decode(envelope['data'])
    assert hashlib.sha256(compressed).hexdigest() == envelope['compressed_sha256']
    raw = gzip.decompress(compressed)
    assert hashlib.sha256(raw).hexdigest() == envelope['uncompressed_sha256']
    rows = strict(raw)
    keys = ['review/initial/report.md', 'review/fixed-final/report.md',
            'review/delivery30/report.md', 'review/delivery57/report.md']
    return [(key, base64.b64decode(rows[key]['base64']), rows[key]) for key in keys]


def reference_rows():
    rows = []
    paths = [SRC + name for name in NATIVE]
    paths += [EVID + 'source-provenance.json', EVID + 'index.json',
        EVID + 'release-preparation/package-binding.json',
        EVID + 'release-preparation/staged-input.json',
        EVID + 'release-preparation/scratch-config.json',
        EVID + 'debug01/result.json', EVID + 'release02/result.json',
        EVID + 'debug01/staged-input.json', EVID + 'release02/staged-input.json',
        'tools/s08/lifecycle_diagnostic.py', 'tools/s08/lifecycle_release.py',
        'tools/s08/lifecycle_edits.py', 'tools/run_s03.py',
        'tests/fixtures/s03/session.gd', 'tests/fixtures/s03/proof.gd',
        'tests/fixtures/s03/replication.gd', 'tests/fixtures/s03/match.gd',
        'tests/fixtures/s03/transport.gd', 'tests/fixtures/s03/boot.tscn']
    for path in paths:
        data = blob(LIFE, path)
        row = {'revision': LIFE, 'path': path,
               'blob': git('rev-parse', LIFE + ':' + path).decode().strip(), **identity(data)}
        name = path.removeprefix(SRC)
        if name in NATIVE:
            row['upstream'] = ('https://raw.githubusercontent.com/godotengine/godot/'
                               + ENGINE + '/' + NATIVE[name])
            lines = data.decode().splitlines()
            row['anchors'] = [{'text': token, 'line': next(i for i, line in enumerate(lines, 1)
                                                        if token in line)}
                              for token in ANCHORS.get(name, [])]
        rows.append(row)
    for revision, paths in [(STANDARD, ['docs/spikes/s08-standard-editor-release.md',
            'docs/spikes/s08-standard-editor-evidence/addon-free-release/pck-members.json',
            'tests/fixtures/s08/release_boot.gd', 'tests/fixtures/s08/release_boot.gd.uid',
            'tests/fixtures/s08/release_boot.tscn']),
        (HAND, ['docs/spikes/s08-exported-enet-handoff.md',
            'docs/spikes/s08-exported-enet-handoff-evidence/set01/binding.json',
            'docs/spikes/s08-exported-enet-handoff-evidence/set01/enet/result.json',
            'tools/s08/observe.py']),
        (LIFE, ['docs/spikes/s08-release-lifecycle.md'])]:
        for path in paths:
            data = blob(revision, path)
            rows.append({'revision': revision, 'path': path,
                'blob': git('rev-parse', revision + ':' + path).decode().strip(), **identity(data)})
    for revision, note_blob in NOTES.items():
        raw = git('show', note_blob)
        rows.append({'revision': revision, 'note_blob': note_blob, **identity(raw),
                     'reports': [{'selector': key, **identity(data)}
                                 for key, data, _ in reports(revision, strict(raw))]})
    return rows


def verify_historical():
    index = strict(blob(LIFE, EVID + 'index.json'))
    rows = index['payloads']
    if isinstance(rows, dict):
        rows = [dict(value, path=key) for key, value in rows.items()]
    assert set(index['expected_paths']) == {row['path'] for row in rows}
    for row in rows:
        data = blob(LIFE, EVID + row['path'])
        assert identity(data) == {key: row[key] for key in ['bytes', 'sha256']}, row['path']
    print('Historical lifecycle complete declared core set verified:', len(rows))
    for revision, note_blob in NOTES.items():
        note = strict(git('show', note_blob))
        for key, data, row in reports(revision, note):
            assert data and identity(data) == {k: row[k] for k in ['bytes', 'sha256']}
            print('Full historical report hash/readback:', revision[:8], key, identity(data))
    for name, expected in [('debug01', (120, 9659, 119, 9413)),
                           ('release02', (123, 9665, 122, 9419))]:
        result = strict(blob(LIFE, EVID + name + '/result.json'))
        traffic = [strict(line) for line in blob(LIFE, EVID + name + '/traffic.jsonl').splitlines()]
        counts = tuple(value for direction in ['recv', 'send'] for value in (
            sum(row['event'] == direction for row in traffic),
            sum(row['bytes'] for row in traffic if row['event'] == direction)))
        assert counts == expected
        for role, errors in [('host', 2), ('client', 6)]:
            stderr = blob(LIFE, EVID + name + '/' + role + '/stderr.log').decode()
            assert stderr.count('ERROR:') == (errors if name == 'release02' else 0)
        assert result['gameplay_ok'] is True
        assert result['ok'] is (name == 'debug01')
        held = [row['record']['reason'] for row in result['observations']
                if row.get('record', {}).get('event') == 'held_receipt']
        assert held == ['NOT_ADMITTED', 'OK', 'STALE_SEQUENCE', 'STALE_CONTEXT',
                        'INVALID', 'INVALID', 'WINDOW', 'WINDOW', 'WINDOW',
                        'NOT_ADMITTED', 'STALE_CONTEXT', 'OK']
        print(name, 'independent traffic/12-held/strict diagnostic expectations verified', counts)
    manifest = strict(blob(LIFE, EVID + 'release02/staged-input.json'))
    assert len(manifest) == 17
    for row in manifest:
        assert identity(blob(LIFE, row['path'])) == {k: row[k] for k in ['bytes', 'sha256']}
    pack = strict(blob(LIFE, EVID + 'release-preparation/package-binding.json'))
    assert pack['pck'] == {'bytes': 122748,
        'sha256': '43cc8236fcb7a06f328c28cf45fed752d6630e1699ebea04e68e34d9aa40e3d7'}
    assert len(pack['entries']) == 23 and len(pack['mappings']) == len(pack['uids']) == 10
    assert not any('/s08/' in row['path'] or '/s01/' in row['path'] for row in pack['entries'])
    edits_ast = ast.parse(blob(LIFE, 'tools/s08/lifecycle_edits.py'))
    edits = next(ast.literal_eval(node.value) for node in edits_ast.body
                 if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'EDITS'
                                                        for t in node.targets))
    for name, replacements in edits.items():
        original = blob(STANDARD, 'tests/fixtures/s03/' + name).decode()
        assert original == blob(HAND, 'tests/fixtures/s03/' + name).decode()
        restored = blob(LIFE, 'tests/fixtures/s03/' + name).decode()
        for old, new in reversed(replacements):
            if old == new:
                continue
            assert restored.count(new) == 1
            restored = restored.replace(new, old)
        assert restored == original
    assert blob(STANDARD, 'tests/fixtures/s08/release_boot.gd') == blob(BASE, 'tests/fixtures/s08/release_boot.gd')
    old = blob('a5756b4b6126a5c9756de981b39fdadc35f3c8fe', 'tools/s08/lifecycle_diagnostic.py')
    assert b'time.sleep(0.01)' in old
    assert b'time.sleep(POLL_SECONDS)' in blob(LIFE, 'tools/s08/lifecycle_diagnostic.py')
    assert b'POLL_SECONDS = 0.02' in blob(LIFE, 'tools/run_s03.py')
    binding = strict(blob(HAND, 'docs/spikes/s08-exported-enet-handoff-evidence/set01/binding.json'))
    assert len(binding['source_files']) == 34
    for row in binding['source_files']:
        assert identity(blob(STANDARD, row['path'])) == {k: row[k] for k in ['bytes', 'sha256']}
        assert blob(STANDARD, row['path']) == blob(HAND, row['path'])
    original_pack = strict(blob(STANDARD, 'docs/spikes/s08-standard-editor-evidence/'
                                       'addon-free-release/pck-members.json'))
    assert len(original_pack['entries']) == 48
    print('Original34/minimal17 closure, exact inverse, S08 identity and actual10/restored20 verified')


def source_claims():
    cache = blob(LIFE, SRC + 'scene_cache_interface.cpp').decode()
    assert cache.index('nodes_cache[oid] = NodeCache()') < cache.index('p_node->connect(')
    assert 'Object::CONNECT_ONE_SHOT' in cache
    clear = cache[cache.index('void SceneCacheInterface::clear()'):]
    assert clear.index('obj->disconnect(') < clear.index('nodes_cache.clear()')
    assert 'last_send_cache_id = 1;' in clear
    obj = blob(LIFE, SRC + 'object.cpp').decode()
    connect = obj[obj.index('Error Object::connect('):obj.index('bool Object::is_connected(')]
    disconnect = obj[obj.index('bool Object::_disconnect('):obj.index('bool Object::_uses_signal_mutex(')]
    assert connect.count('get_base_comparator()') == 3
    assert disconnect.count('get_base_comparator()') == 3
    bind = blob(LIFE, SRC + 'callable_bind.cpp').decode()
    assert 'return callable.get_base_comparator();' in bind
    mp = blob(LIFE, SRC + 'callable_mp.h').decode()
    assert 'memset(&data, 0, sizeof(Data))' in mp
    assert 'T *instance;' in mp and 'uint64_t object_id;' in mp
    assert 'memcmp(a->comp_ptr, b->comp_ptr, a->comp_size * 4)' in blob(LIFE, SRC + 'callable_mp.cpp').decode()
    for name in ['session.gd', 'proof.gd', 'transport.gd']:
        assert 'await' not in ''.join(line for line in blob(LIFE, 'tests/fixtures/s03/' + name).decode().splitlines()
                                      if 'tree_exited' in line)
    print('Native register/remove/base-comparator/method-pointer call paths verified')


def authored_checks():
    changed = git('diff', '--name-only', BASE).decode().splitlines()
    assert all(path.startswith(OWN) or path == 'docs/plans/task-requirements.md' for path in changed)
    index = 'docs/plans/task-requirements.md'
    strip = lambda s: re.sub(r'(?ms)^- \*\*S08:\*\*.*?(?=^- \*\*)', '', s)
    assert strip(blob(BASE, index).decode()) == strip((ROOT / index).read_text())
    for path in [ROOT / 'docs/spikes/s08-source-diagnosis.md', *HERE.iterdir()]:
        if not path.is_file():
            continue
        data = path.read_bytes()
        assert b'\r' not in data and data.endswith(b'\n'), path
        assert all(line.rstrip() == line for line in data.splitlines()), path
        if path.suffix == '.json':
            strict(data)
        if path.suffix == '.md':
            for target in re.findall(r'\]\(\s*([^\s)]+)\s*\)', data.decode()):
                if '://' not in target:
                    assert (path.parent / target.split('#')[0]).exists(), (path, target)
    subprocess.run(['git', 'diff', '--check', BASE], cwd=ROOT, check=True)
    assert b'- [ ] **S08' in (ROOT / 'TODO.md').read_bytes()
    print('Owned scope, non-S08 index preservation, JSON, links, LF/whitespace and open TODO verified')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record-references', action='store_true')
    args = parser.parse_args()
    rows = reference_rows()
    if args.record_references:
        (HERE / 'references.json').write_text(json.dumps({'schema': 1, 'base': BASE,
            'engine_source': ENGINE, 'references': rows}, indent=2) + '\n')
        print('Recorded immutable references:', len(rows))
        return
    ledger = strict((HERE / 'references.json').read_bytes())
    assert ledger['references'] == rows
    verify_historical()
    source_claims()
    authored_checks()
    print('PASS: STATIC ONLY; no runtime, compiler, export or socket testing')


if __name__ == '__main__':
    main()
