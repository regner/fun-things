"""Read-only checkpoint audit; never execute historical probes, engines or archive members."""
import argparse
import ast
import base64
import gzip
import hashlib
import io
import json
import re
import stat
import subprocess
import tarfile
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
BASE = '7fb302ba2829966c9a687a12a7f00d09ce6a7824'
PRIOR = '754a0b501fe705c93675ff09b43d5bfca201cd94'
EVIDENCE = ROOT / 'docs/reviews/plan-check-07-evidence'
COMMITS = ['6b4a69e', '096469f', '1691424', 'dbce2f9', '6c36c12',
           '9cfa3c0', '92f5471', 'bb7e902', '1c49113', '7fb302b']
TASKS = ['P0-PROFILES', 'S02', 'S03-S', 'S03-R', 'S04', 'S05', 'S06', 'S07', 'S08',
         'P0-GATE', 'M1-A1', 'M1-A2', 'M1-A3', 'M1-A-GATE', 'M1-B1', 'M1-B2',
         'M1-B3', 'M1-B4', 'M1-C1', 'M1-C2', 'M1-C3', 'M1-C4', 'M1-D1', 'M1-D2',
         'M1-D3', 'M1-D4', 'M1-GATE']
REVISED = ['P0-PROFILES', 'S06', 'S07', 'P0-GATE']


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pairs(items):
    result = {}
    for key, value in items:
        assert key not in result, ('duplicate JSON key', key)
        result[key] = value
    return result


def strict(raw):
    def invalid(value):
        raise ValueError('nonstandard JSON numeric constant: ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def verify(raw, entry):
    assert len(raw) == entry.get('bytes', entry.get('size')), entry
    assert sha(raw) == entry['sha256'], entry


def tree(rev):
    result = {}
    for row in git('ls-tree', '-r', '-z', rev).split(b'\0'):
        if row:
            meta, path = row.split(b'\t')
            mode, kind, blob = meta.decode().split()
            assert kind == 'blob'
            result[path.decode()] = {'mode': mode, 'blob': blob}
    return result


def note(rev):
    blob = git('notes', '--ref=paseo-orchestration', 'list', rev).decode().split()[0]
    raw = git('cat-file', 'blob', blob)
    doc = strict(raw)
    payloads = {}
    ledger = []
    for item in doc.get('artifacts', doc.get('payloads', [])):
        name = item.get('source_path', item.get('name'))
        assert name not in payloads, name
        stored = base64.b64decode(item['data'], validate=True)
        if 'stored_bytes' in item:
            assert len(stored) == item['stored_bytes'] and sha(stored) == item['stored_sha256']
        decoded = gzip.decompress(stored) if 'gzip' in item.get('codec', '') else stored
        verify(decoded, item)
        payloads[name] = decoded
        ledger.append({k: v for k, v in item.items() if k != 'data'})
    return doc, payloads, {'revision': git('rev-parse', rev).decode().strip(),
                          'notes_commit': git('rev-parse', 'refs/notes/paseo-orchestration').decode().strip(),
                          'git_blob': blob, 'bytes': len(raw), 'sha256': sha(raw),
                          'payloads': ledger}


def archive(raw):
    result = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as pack:
        for member in pack.getmembers():
            assert member.isfile() and not member.name.startswith('/')
            assert '..' not in Path(member.name).parts and member.name not in result
            result[member.name] = pack.extractfile(member).read()
    return result


def archive_set(members, entries, extra):
    indexed = {e['path']: e for e in entries}
    assert len(indexed) == len(entries)
    assert set(members) == set(indexed) | set(extra), (set(members) ^ (set(indexed) | set(extra)))
    for name, entry in indexed.items():
        verify(members[name], entry)
    return {'expected_paths': sorted(members), 'indexed_count': len(indexed),
            'members': len(members)}


def blocks(text):
    starts = list(re.finditer(r'^- \[ \] \*\*([^ —]+) —', text, re.M))
    result = {}
    for match in starts:
        end = re.search(r'^(?:- \[ \]|##+ )', text[match.end():], re.M)
        stop = match.end() + end.start() if end else len(text)
        result[match[1]] = text[match.start():stop].rstrip()
    return result


def accepted():
    rows = []
    previous = PRIOR
    for short in COMMITS:
        rev = git('rev-parse', short).decode().strip()
        parents = git('show', '-s', '--format=%P', rev).decode().split()
        assert parents == [previous]
        old, new = tree(previous), tree(rev)
        changed = {p: {'before': old.get(p), 'after': new.get(p)}
                   for p in sorted(set(old) | set(new)) if old.get(p) != new.get(p)}
        diff = git('diff', previous, rev, '--', 'TODO.md', 'README.md', 'docs',
                   ':!docs/spikes/*-evidence', ':!docs/reviews/*-evidence')
        rows.append({'commit': rev, 'parent': previous, 'subject': git('show', '-s', '--format=%s', rev).decode().strip(),
                     'changed_paths': changed, 'planning_diff_bytes': len(diff),
                     'planning_diff_sha256': sha(diff)})
        previous = rev
    assert previous == BASE
    assert len(git('rev-list', '--reverse', PRIOR + '..' + BASE).splitlines()) == 10
    assert not git('rev-list', '--merges', PRIOR + '..' + BASE).strip()
    assert subprocess.run(['git', 'merge-base', '--is-ancestor', PRIOR, BASE], cwd=ROOT).returncode == 0
    notes = {}
    for rev in ['096469f', '6c36c12', BASE]:
        doc, payload, identity = note(rev)
        notes[rev] = identity
        if rev == '6c36c12':
            assert len(payload) == 177
            coverage = []
            for directory, count in [('doc89-independent-review', 66),
                                     ('doc89-independent-final-review', 27),
                                     ('doc89-independent-renewed-review', 16)]:
                prefix = '/tmp/' + directory + '/'
                manifest = strict(payload[prefix + 'manifest.json'])
                entries = manifest['entries']
                assert len(entries) == count
                expected = {prefix + e['path'] for e in entries} | {prefix + 'manifest.json', prefix + 'SHA256SUMS'}
                actual = {p for p in payload if p.startswith(prefix)}
                assert actual == expected, (actual ^ expected)
                for e in entries:
                    verify(payload[prefix + e['path']], e)
                coverage.append({'root': prefix, 'input_count': count, 'expected_paths': sorted(expected)})
            identity['manifest_sets'] = coverage
        if rev == BASE:
            assert len(payload) == 15
            # S06 payloads use source_path for location but name for semantic lookup.
            by_name = {a['name']: payload[a['source_path']] for a in doc['payloads']}
            final = strict(by_name['final-manifest'])
            members = archive(by_name['all-185-final-review-artifacts'])
            identity['final_review_set'] = archive_set(members, final['local_artifacts'],
                                                      ['manifest.json', 'handoff-hashes.json'])
            assert len(final['local_artifacts']) == 183 and len(members) == 185
            refs = doc['committed_experiment_artifact_references'] + doc['source_and_task_references']
            assert len(refs) == 552 and len({r['path'] for r in refs}) == 552
            for entry in refs:
                raw = git('cat-file', 'blob', entry['git_blob'])
                verify(raw, entry)
                assert git('rev-parse', BASE + ':' + entry['path']).decode().strip() == entry['git_blob']
            identity['committed_ref_count'] = len(refs)
            prior = doc['verified_prior_note_reference']
            prior_raw = git('cat-file', 'blob', prior['git_blob'])
            verify(prior_raw, prior)
            old = strict(prior_raw)
            assert len(old['payloads']) == 11
            assert doc['payloads'][:11] == old['payloads']
            assert subprocess.run(['git', 'merge-base', '--is-ancestor', prior['notes_commit'],
                                   'refs/notes/paseo-orchestration'], cwd=ROOT).returncode == 0
            assert prior['git_blob'] in git('ls-tree', '-r', prior['notes_commit']).decode()
            identity['historical_note'] = prior
            ack = strict(by_name['complete-acknowledgement-manifest'])
            supplementary = archive(by_name['all-supplementary-acknowledgement-raw-artifacts'])
            retained = strict(by_name['supplementary-retention-and-exact-note-blob-references'])
            history = {e['path']: e for e in retained['two_identical_historical_note_readbacks_retained_by_exact_blob_references']}
            expected = {e['path'] for e in ack['artifacts']}
            assert len(expected) == 11
            assert set(supplementary) == (expected - set(history)) | {'note-acknowledgement-manifest.json', 'note-acknowledgement-retention.json'}
            for entry in ack['artifacts']:
                verify(prior_raw if entry['path'] in history else supplementary[entry['path']], entry)
            identity['acknowledgement_set'] = {'expected_inputs': sorted(expected),
                                              'archive_paths': sorted(supplementary), 'historical_refs': history}
    manifest = strict((ROOT / 'docs/spikes/s06-evidence/manifest.json').read_bytes())
    assert len(manifest['artifacts']) == 509
    for entry in manifest['artifacts']:
        verify((ROOT / 'docs/spikes/s06-evidence' / entry['artifact']).read_bytes(), entry)
    original = strict(git('show', 'bb7e902:docs/spikes/s06-evidence/manifest.json'))
    assert len(original['artifacts']) == 359
    for entry in original['artifacts']:
        matches = [e for e in manifest['artifacts']
                   if e.get('original_artifact', e['artifact']) == entry['artifact']]
        assert any(all(e[k] == entry[k] for k in ['bytes', 'sha256', 'input'])
                   for e in matches), entry['artifact']
    substantive = strict((ROOT / 'docs/spikes/s06-evidence/review/substantive-manifest.json').read_bytes())
    original_pack = archive((ROOT / 'docs/spikes/s06-evidence/review/substantive-artifacts.tar.gz').read_bytes())
    original_set = archive_set(original_pack, substantive['local_artifacts'], ['manifest.json', 'handoff-hashes.json'])
    assert len(substantive['local_artifacts']) == 216 and len(original_pack) == 218
    receipt_path = Path('/tmp/s06-editor-relocation/receipt.json')
    receipt_raw = receipt_path.read_bytes()
    assert len(receipt_raw) == 23635 and sha(receipt_raw) == 'ad8b5589fe3d0dab5c7e75d9cb8ebb953b299ba06f6d9296319417c7f676bfa9'
    receipt = strict(receipt_raw)
    current_note = strict(git('notes', '--ref=paseo-orchestration', 'show', BASE))
    relocation = next(r for r in current_note['root_receipts'] if 'complete_receipt' in r)
    assert relocation['complete_receipt'] == receipt
    assert relocation['external_receipt_sha256'] == sha(receipt_raw)
    assert len(receipt['artifact_ledger']) == 150
    for name, entry in receipt['artifact_ledger'].items():
        verify((receipt_path.parent / name).read_bytes(), entry)
    inputs = ['AGENTS.md', '.agents/skills/paseo-orchestrator/SKILL.md', 'TODO.md', 'README.md',
              'docs/development.md', 'docs/architecture.md', 'docs/api-contracts.md', 'docs/scene-structure.md',
              'docs/multiplayer.md', 'docs/assets.md', 'docs/design.md', 'docs/art-direction.md', 'docs/world-layout.md',
              'docs/asset-catalogue.md', 'docs/assets/s02_kit.md', 'docs/assets/s04_kit.md',
              'docs/reviews/plan-checkpoints.md', 'docs/reviews/plan-check-2026-10-08-06.md',
              'docs/reviews/plan-check-review-2026-10-08-06.md', 'docs/reviews/p0-doc8.md', 'docs/reviews/p0-doc9.md',
              'docs/spikes/s06.md', 'docs/spikes/s06-contracts.md', 'docs/spikes/s06-source-handoff.md',
              'docs/spikes/s06-evidence/README.md', 'docs/spikes/s06-evidence/review/substantive-report.md',
              'docs/spikes/s07.md', 'tools/s06/run.py', 'tools/s06/check_resources.py', 'tools/s06/editor_probe.gd',
              'docs/workflows/p0-profiles-proposal.md', 'docs/workflows/p0-profiles-evidence.md',
              'docs/workflows/p0-profiles-evidence/proposed.patch.json',
              'tests/fixtures/s06/intersection.tscn', 'tests/fixtures/s06/intersection_wide.tscn',
              'tests/fixtures/s06/west.tscn', 'tests/fixtures/s06/east.tscn']
    consulted = []
    for path in inputs:
        raw = git('show', BASE + ':' + path)
        consulted.append({'path': path, 'revision': BASE, 'git_blob': git('rev-parse', BASE + ':' + path).decode().strip(),
                          'bytes': len(raw), 'sha256': sha(raw)})
    return {'prior_exclusive': PRIOR, 'watermark_inclusive': BASE, 'commits': rows,
            'accepted_notes': notes, 'consulted_inputs': consulted,
            's06_manifest_count': 509, 'original_preserved_count': 359, 'substantive_review_set': original_set,
            'root_receipt': {'path': str(receipt_path), 'bytes': len(receipt_raw), 'sha256': sha(receipt_raw),
                             'ledger_verified': 150, 'receipt': receipt,
                             'readback': strict((receipt_path.parent / 'receipt-readback.json').read_bytes())}}


def candidate():
    old = blocks(git('show', BASE + ':TODO.md').decode())
    new = blocks((ROOT / 'TODO.md').read_text())
    assert list(old) == TASKS and len(new) == 29
    assert set(new) - set(old) == {'P0-DOC10', 'P0-DOC11'} and not set(old) - set(new)
    changed = [p for p in old if old[p] != new[p]]
    assert changed == REVISED, changed
    for task in TASKS + ['P0-DOC10', 'P0-DOC11']:
        record = (ROOT / 'docs/reviews/plan-check-2026-10-08-07.md').read_text()
        assert '| ' + task + (' (new)' if task.startswith('P0-DOC1') else '') + ' |' in record
    preserved = 0
    for path, entry in tree(BASE).items():
        if path in ['TODO.md', 'docs/reviews/plan-checkpoints.md']:
            continue
        p = ROOT / path
        raw = p.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        assert blob == entry['blob'], path
        mode = '100755' if p.stat().st_mode & stat.S_IXUSR else '100644'
        assert mode == entry['mode'], path
        preserved += 1
    changed_paths = set(git('diff', '--name-only', BASE).decode().splitlines())
    untracked = set(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
    allowed = lambda p: p in ['TODO.md', 'docs/reviews/plan-checkpoints.md', 'docs/reviews/plan-check-2026-10-08-07.md',
                             'docs/reviews/plan-check-review-2026-10-08-07.md'] or p.startswith('docs/reviews/plan-check-07-evidence/')
    assert all(allowed(p) for p in changed_paths | untracked), changed_paths | untracked
    files = [ROOT / p for p in changed_paths | untracked]
    links = []
    for path in files:
        if path.suffix in ['.md', '.json', '.py', '.txt']:
            raw = path.read_bytes()
            assert b'\r' not in raw and raw.endswith(b'\n'), path
            if path.suffix == '.json': strict(raw)
            if path.suffix == '.py': ast.parse(raw)
        if path.suffix != '.md': continue
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            if re.match(r'\w+://', target): continue
            target = unquote(target)
            dest, _, anchor = target.partition('#')
            resolved = path.parent / dest if dest else path
            assert resolved.exists(), (path, target)
            if anchor:
                headings = re.findall(r'^#+\s+(.+)$', resolved.read_text(), re.M)
                slugs = [re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-') for h in headings]
                assert anchor in slugs, (path, target, slugs)
            links.append({'file': str(path.relative_to(ROOT)), 'target': target})
    proc = subprocess.run(['git', 'diff', '--check', BASE], cwd=ROOT, capture_output=True)
    assert proc.returncode == 0, proc.stdout.decode()
    assert git('rev-parse', 'refs/heads/main').decode().strip() == BASE
    assert subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, 'HEAD'], cwd=ROOT).returncode == 0
    assert not git('rev-list', '--merges', BASE + '..HEAD').strip()
    for name in ['MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply', 'sequencer', 'BISECT_LOG', 'index.lock']:
        assert not Path(git('rev-parse', '--git-path', name).decode().strip()).exists(), name
    return {'head': git('rev-parse', 'HEAD').decode().strip(), 'base': BASE, 'base_tasks': len(old),
            'candidate_tasks': len(new), 'added': sorted(set(new) - set(old)), 'revised': changed,
            'preserved_base_files': preserved, 'links': links, 'authored_whitespace_exit': proc.returncode,
            'scope_paths': sorted(changed_paths | untracked), 'status': git('status', '--porcelain=v1').decode(),
            'checks': 'static only; accepted runtime proofs not rerun'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--accepted-output', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.accepted_output:
        audit = accepted()
        args.accepted_output.write_text(json.dumps(audit, indent=2) + '\n')
    result = candidate()
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['head', 'base_tasks', 'candidate_tasks', 'revised', 'preserved_base_files']}))
    print('links=' + str(len(result['links'])) + '; static PASS')


if __name__ == '__main__':
    main()
