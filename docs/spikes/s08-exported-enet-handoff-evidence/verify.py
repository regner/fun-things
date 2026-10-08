#!/usr/bin/env python3
"""Read the complete expected evidence set and independently check reported contracts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
E = Path(__file__).resolve().parent
BASE = '52941da4b4c92a547a8066b5c13f733043ecbe48'


def expected_paths():
    """Derive required payloads from the declared attempts rather than index entries."""
    paths = ['README.md', 'raw-requirements.md', 'commands.json', 'launch-receipt.json',
             'uid-preservation.json', 'preflight-expected.json', 'network-expected.json',
             'verify.py', 'offline.stdout', 'offline.stderr', 'bind.stdout', 'bind.stderr',
             'set01.stdout', 'set01.stderr', 'set01/stream-readback.json']
    paths += ['offline/'+name for name in ['logger.c', 'compile.stdout', 'compile.stderr',
              'regular.stdout', 'regular.stderr', 'line-buffered.stdout',
              'line-buffered.stderr', 'result.json', 'observe-executed.py']]
    paths += ['offline/'+case+'/enet/'+name for case in
              ['partial', 'coalesced-failure', 'silent-deadline'] for name in
              ['result.json', 'proxy.jsonl', 'host/command.json', 'host/stdout.log',
               'host/stderr.log', 'host/engine.log']]
    paths += ['set01/'+name for name in ['binding.json', 'staged-input.json',
              'output-folder.json', 'executable-template.json', 'pck-members.json',
              'exclusions.json', 'logical-export-map.json', 'cache-inspection.json',
              'enet/result.json', 'enet/proxy.jsonl']]
    paths += ['set01/enet/'+role+'/'+name for role in ['host', 'client'] for name in
              ['command.json', 'stdout.log', 'stderr.log', 'engine.log']]
    return set(paths)


def identity(data):
    """Bind exact stored bytes including empty streams."""
    return {'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()}


def check():
    """Verify partial outcomes, literal API source, preservation and scope offline."""
    expected = expected_paths()
    actual = {p.relative_to(E).as_posix() for p in E.rglob('*') if p.is_file()}
    assert actual == expected | {'index.json'}
    index = json.loads((E/'index.json').read_text())
    assert set(index['expected_paths']) == expected
    assert set(index['payloads']) == expected
    for name in expected:
        assert identity((E/name).read_bytes()) == index['payloads'][name]
    b = json.loads((E/'set01/binding.json').read_text())
    assert b['ok'] and b['accepted_source'] == BASE and b['pck_members'] == 48
    for row in b['source_files']:
        assert identity((ROOT/row['path']).read_bytes()) == {
            'bytes':row['bytes'], 'sha256':row['sha256']}
    metadata = json.loads((E/'uid-preservation.json').read_text())
    for row in metadata['files']:
        data=(ROOT/row['path']).read_bytes()
        assert data == row['content'].encode()
        assert identity(data) == {'bytes':row['bytes'], 'sha256':row['sha256']}
    r = json.loads((E/'set01/enet/result.json').read_text())
    assert not r['ok'] and r['host_ready_before_client'] and r['handoff_seconds'] < 4
    assert r['observations'][0]['event'] == 'ready' and r['observations'][0]['child_live']
    assert r['duration_seconds'] < 30
    assert r['all_children_reaped'] and r['streams_closed'] and r['proxy_closed']
    assert r['proxy_count'] == 0 and r['proxy_events'] == []
    pck = {x['path']:x for x in json.loads((E/'set01/pck-members.json').read_text())['entries']}
    role_events = {}
    for role in ['host', 'client']:
        d=E/'set01/enet'/role
        command=json.loads((d/'command.json').read_text())
        assert command['exit'] == 1 and command['child_reaped']
        assert command['argv'][:2] == ['/usr/bin/stdbuf', '-oL']
        lines=(d/'stdout.log').read_text().splitlines()
        assets=[json.loads(x[4:]) for x in lines if x.startswith('S08 ')]
        assert len(assets) == 1 and assets[0]['ok'] and assets[0]['role'] == role
        assert len(assets[0]['resources']) == 22 and len(assets[0]['checks']) == 173
        count=0
        for resource in assets[0]['resources']:
            for row in resource['runtime_bytes']:
                member=pck[row['path'][6:]]
                assert row['bytes'] == member['bytes'] and row['sha256'] == member['sha256']
                count+=1
        assert count == 44
        role_events[role]=[json.loads(x[4:]) for x in lines if x.startswith('S03 ')]
        assert role_events[role][-1]['ok'] is False
    assert role_events['host'][-1]['cases'] == ['provisional_rollback']
    assert role_events['client'][-1]['cases'] == [
        'provider_substitution_late_cleanup', 'baseline_cancel_retry']
    assert (E/'set01/enet/client/stderr.log').read_text().count('ERROR:') == 6
    assert (E/'set01/enet/host/stderr.log').read_bytes() == b''
    proof=(ROOT/'tests/fixtures/s03/proof.gd').read_text()
    for label in ['journal before admission', 'resync retains injured health', 'motion preserves health']:
        assert 'health == 70, "'+label+'"' in proof
    replication=(ROOT/'tests/fixtures/s03/replication.gd').read_text()
    assert 'var journal_applied: bool = match_state.apply_journal(' in replication
    assert 'assert(match_state.apply_journal' not in replication
    offline=json.loads((E/'offline/result.json').read_text())
    assert [x['ready_at_150ms'] for x in offline['buffering']['runs']] == [False, True]
    assert all(x['child_live'] and x['exit'] == 1 for x in offline['buffering']['runs'])
    assert len(offline['coordination']) == 3
    assert all(x['launcher_calls'] == 1 for x in offline['coordination'])
    old=subprocess.check_output(['git','show',BASE+':TODO.md'],cwd=ROOT).decode()
    current=(ROOT/'TODO.md').read_text()
    begin='- [ ] **S08 —'; end='- [ ] **P0-GATE'
    # The next task header supplies an independent S08-block-only boundary.
    start=old.index(begin); finish=old.index('\n- [ ] **',start+len(begin))
    now_start=current.index(begin); now_finish=current.index('\n- [ ] **',now_start+len(begin))
    assert old[:start] == current[:now_start] and old[finish:] == current[now_finish:]
    return {'ok':True, 'expected_payloads':len(expected), 'required_empty_paths':sorted(
        name for name in expected if not (E/name).stat().st_size),
        'network_sets':1, 'network_full_acceptance':False, 'children_reaped':True,
        'same_source_public_API_health_expectations':True, 'TODO_only_S08':True,
        'candidate':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'index':identity((E/'index.json').read_bytes())}


def main():
    """Build before freeze; check exact committed readback once after freeze."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['build','check'])
    args=parser.parse_args()
    if args.mode == 'build':
        expected=expected_paths()
        index={'expected_paths':sorted(expected), 'self_exclusion':'index.json bound in final note',
               'payloads':{name:identity((E/name).read_bytes()) for name in sorted(expected)}}
        (E/'index.json').write_text(json.dumps(index,indent=2)+'\n')
    result=check()
    if args.mode == 'check':
        for name in expected_paths() | {'index.json'}:
            data=subprocess.check_output(['git','show','HEAD:'+str((E/name).relative_to(ROOT))],cwd=ROOT)
            assert data == (E/name).read_bytes()
        assert subprocess.check_output(['git','status','--porcelain'],cwd=ROOT) == b''
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
