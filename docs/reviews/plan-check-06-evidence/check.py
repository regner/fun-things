"""Sixth checkpoint static integrity; no historical tool execution or live surface access."""
import argparse
import ast
import base64
import gzip
import hashlib
import io
import json
import re
import subprocess
import tarfile
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / 'docs/reviews/plan-check-06-evidence'
BASE = '754a0b501fe705c93675ff09b43d5bfca201cd94'
PRIOR = 'ca38e4fc55b32a379ef7e3bf947e27d4ca8edc4c'
RECORD = 'docs/reviews/plan-check-2026-10-08-06.md'
INDEX = 'docs/reviews/plan-checkpoints.md'
REVIEW = 'docs/reviews/plan-check-review-2026-10-08-06.md'
MODIFIED_TASKS = {'P0-PROFILES', 'S05', 'S07', 'P0-GATE'}
NEW_TASKS = {'P0-DOC8', 'P0-DOC9'}


def git(*args):
    """Read bounded Git topology, immutable files and notes."""
    return subprocess.check_output(['git', *args], cwd=ROOT, timeout=30)


def pairs(entries):
    """Reject duplicate JSON keys rather than hide conflicting evidence."""
    result = {}
    for key, value in entries:
        assert key not in result, key
        result[key] = value
    return result


def parse(raw):
    """Read local JSON without importing project tooling."""
    return json.loads(raw, object_pairs_hook=pairs)


def digest(raw):
    """Bind original artifact lengths and hashes, including empty outputs."""
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def verify(raw, entry):
    """Compare exact stored bytes against an independent recorded identity."""
    assert digest(raw) == {key: entry[key] for key in ('bytes', 'sha256')}, entry


def tasks(text):
    """Read complete current task blocks, preserving all acceptance text."""
    matches = list(re.finditer(r'^- \[ \] \*\*([A-Z0-9-]+) —', text, re.M))
    result = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = re.split(r'(?m)^#{1,3} ', text[match.start():end], maxsplit=1)[0].rstrip()
        assert match[1] not in result
        result[match[1]] = block
    return result


def anchors(path):
    """Resolve Markdown heading anchors and duplicate suffixes."""
    counts, result = {}, set()
    text = re.sub(r'(?ms)^```.*?^```[^\n]*\n?', '', path.read_text())
    for line in text.splitlines():
        match = re.match(r'^#{1,6}\s+(.+?)\s*#*$', line)
        if match:
            title = re.sub(r'[`*_]', '', match[1]).lower()
            slug = ''.join(c for c in title if c in '-_ ' or unicodedata.category(c)[0] in 'LN')
            slug = slug.replace(' ', '-')
            count = counts.get(slug, 0)
            counts[slug] = count + 1
            result.add(slug + (f'-{count}' if count else ''))
    return result


def archive(raw):
    """Read safe regular archive members in memory without extracting or executing."""
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as pack:
        result = {}
        for member in pack.getmembers():
            if member.isdir():
                continue
            assert member.isfile() and not Path(member.name).is_absolute()
            assert '..' not in Path(member.name).parts and member.name not in result
            result[member.name] = pack.extractfile(member).read()
    return result


def accepted_notes():
    """Verify original complete reports/payloads and current root metadata separately."""
    results = {}
    fifth = git('notes', '--ref=paseo-orchestration', 'show', 'c0eda26')
    encoded = re.search(rb'--- BEGIN BASE64 EXACT-FINAL CHECKPOINT ARTIFACT TAR.GZ ---\s*(.*?)\s*'
                        rb'--- END BASE64 EXACT-FINAL CHECKPOINT ARTIFACT TAR.GZ ---', fifth, re.S)[1]
    packed = base64.b64decode(encoded)
    files = archive(packed)
    rows = parse(files['final-note-artifact-manifest.json'])['files']
    assert len(rows) == 35
    for entry in rows:
        verify(files[entry['path']], entry)
    assert len(files['exact-final-report.md']) == 15291
    results['fifth'] = {'revision': 'c0eda26f7f010af75bbf10c272ec5cb001442331',
                       'artifacts': 35, 'bundle': digest(packed),
                       'report': digest(files['exact-final-report.md'])}
    doc_note = git('notes', '--ref=paseo-orchestration', 'show', 'c8096b5')
    encoded = re.search(rb'--- BEGIN BASE64 LOSSLESS ARTIFACT TAR.GZ ---\s*(.*?)\s*'
                        rb'--- END BASE64 LOSSLESS ARTIFACT TAR.GZ ---', doc_note, re.S)[1]
    packed = base64.b64decode(encoded)
    assert hashlib.sha256(packed).hexdigest() == '5dd77ba9cf98c494ebbeaada74caff3834ccf24b5040eae87a86171e75aba035'
    files = archive(packed)
    ledger = parse(files['manifest.json'])['files']
    assert len(ledger) == 462 and set(files) == {e['path'] for e in ledger} | {'manifest.json'}
    for entry in ledger:
        verify(files[entry['path']], entry)
    assert len(files['reviewer/report.md']) == 23086
    assert len(files['reviewer/retention-followup/report.md']) == 12036
    results['doc67'] = {'revision': 'c8096b55ef97412552366fdaa74c220b976ed82e',
                        'artifacts': len(ledger), 'bundle': digest(packed),
                        'substantive': digest(files['reviewer/report.md']),
                        'followup': digest(files['reviewer/retention-followup/report.md'])}
    note = parse(git('notes', '--ref=paseo-orchestration', 'show', BASE))
    assert note['handoff']['final_head'] == BASE and len(note['artifacts']) == 20
    entries, decoded = [], {}
    for entry in note['artifacts']:
        stored = base64.b64decode(entry['data'])
        verify(stored, {'bytes': entry['stored_bytes'], 'sha256': entry['stored_sha256']})
        raw = gzip.decompress(stored)
        verify(raw, entry)
        decoded[entry['source_path']] = raw
        entries.append({k: v for k, v in entry.items() if k != 'data'})
    final_report = decoded['/tmp/s05-independent-final-review/report.md']
    assert len(final_report) == 14250
    assert hashlib.sha256(final_report).hexdigest() == '8b5a709c25134ff7b5d0a8222b46ab94efa69e2292924fe0e4fa79cca23c88c9'
    packed = decoded['/tmp/s05-independent-final-review/final-review-artifacts.tar.gz']
    files = archive(packed)
    ledger = parse(decoded['/tmp/s05-independent-final-review/final-manifest.json'])
    rows = ledger.get('entries', ledger.get('files'))
    assert len(rows) == 14
    for entry in rows:
        verify(files[entry['path']], entry)
    source = ROOT / 'docs/spikes/s05-evidence'
    raw_rows = parse((source / 'retention.json').read_bytes())
    assert len(raw_rows) == 250
    for entry in raw_rows:
        stored = (source / entry['path']).read_bytes()
        verify(stored, {'bytes': entry['stored_bytes'], 'sha256': entry['stored_sha256']})
        raw = gzip.decompress(stored) if entry['gzip'] else stored
        verify(raw, {'bytes': entry['raw_bytes'], 'sha256': entry['raw_sha256']})
    substantive = archive((source / 'review/review-artifacts.tar.gz').read_bytes())
    rows = parse((source / 'review/review-manifest.json').read_bytes())['entries']
    assert len(rows) == 51
    for entry in rows:
        verify(substantive[entry['path']], entry)
    root = next(e for e in note['root_receipts'] if 'receipt' in e)
    relocation = Path('/tmp/s05-editor-relocation')
    for name, key in [('receipt.json', 'receipt'), ('hash-ledger.json', 'hash_ledger'),
                      ('ledger-verification.json', 'ledger_verification'),
                      ('managed-cwd-references.json', 'managed_cwd_references')]:
        raw = (relocation / name).read_bytes()
        assert parse(raw) == root[key], name
    raw = (relocation / 'hash-ledger.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == 'cb355f9be4b6a7a2ca38ecd6574ec5d2819e1dd3b7425375fc30e2a7544e6193'
    ledger = parse(raw)['entries']
    assert len(ledger) == 31
    for entry in ledger:
        verify((relocation / entry['path']).read_bytes(), entry)
    results['s05_final'] = {'revision': BASE, 'artifacts': entries,
                           'report': digest(final_report), 'bundle': digest(packed),
                           'relocation_ledger': digest(raw), 'relocation_entries': len(ledger)}
    # Original artifact identity remains stable across root metadata additions.
    assert results == parse((EVIDENCE / 'accepted-payloads.json').read_bytes())
    print('PASS fifth35/DOC6/7 462 artifacts;S05 raw250/substantive51/note20/final14/report14250;root31')


def main():
    """Check the delivered docs-only range, every task and static artifact fidelity."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    head = git('rev-parse', 'HEAD').decode().strip()
    assert git('rev-parse', 'refs/heads/main').decode().strip() == BASE
    manifest = parse((EVIDENCE / 'audit-manifest.json').read_bytes())
    assert manifest['prior_exclusive'] == PRIOR and manifest['inclusive_watermark'] == BASE
    revisions = git('rev-list', '--reverse', PRIOR + '..' + BASE).decode().splitlines()
    assert len(revisions) == 10 and revisions == [e['revision'] for e in manifest['commits']]
    for entry in manifest['commits']:
        assert entry['parents'] == git('show', '-s', '--format=%P', entry['revision']).decode().split()
        assert entry['paths'] == git('diff-tree', '--no-commit-id', '--name-only', '-r', entry['revision']).decode().splitlines()
    for ancestor, descendant in [(PRIOR, BASE), (BASE, head)]:
        subprocess.run(['git', 'merge-base', '--is-ancestor', ancestor, descendant], cwd=ROOT, check=True)
    assert not git('rev-list', '--merges', PRIOR + '..' + head).strip()
    for entry in manifest['consulted']:
        verify((ROOT / entry['path']).read_bytes(), entry)
    print('PASS exact ten-commit range, parents/paths/consulted hashes/linear ancestry')
    before = tasks(git('show', BASE + ':TODO.md').decode())
    after = tasks((ROOT / 'TODO.md').read_text())
    assert len(before) == 27 and len(after) == 29
    assert set(after) - set(before) == NEW_TASKS and not set(before) - set(after)
    changed = {task for task in before if before[task] != after[task]}
    assert changed == MODIFIED_TASKS, changed
    record = (ROOT / RECORD).read_text()
    rows = re.findall(r'^\| ([A-Z][A-Z0-9-]+)(?: \(new\))? \|', record, re.M)
    assert len(rows) == len(set(rows)) == 29 and set(rows) == set(after)
    for task in NEW_TASKS:
        block = after[task]
        assert all(value in block for value in ['Owner role:', 'Files:', 'Prerequisites:',
                                               'Evidence:', 'Done when:', 'Remove'])
    print('PASS every27 accepted-base task, exactly DOC8/DOC9 added,29 dispositions/four revised blocks')
    allowed = {'TODO.md', INDEX, RECORD, REVIEW}
    def permitted(path):
        return path in allowed or path.startswith('docs/reviews/plan-check-06-evidence/')
    base_entries = git('ls-tree', '-rz', BASE).split(b'\0')
    preserved = 0
    for entry in base_entries:
        if not entry:
            continue
        metadata, raw_path = entry.split(b'\t', 1)
        path = raw_path.decode()
        if permitted(path):
            continue
        mode, kind, blob = metadata.decode().split()
        raw = git('cat-file', kind, blob)
        assert (ROOT / path).read_bytes() == raw, path
        assert bool((ROOT / path).stat().st_mode & 0o111) == (mode == '100755'), path
        assert git('ls-tree', 'HEAD', '--', path).split(b'\t', 1)[0].decode() == metadata.decode(), path
        preserved += 1
    current = set(git('diff', '--name-only', BASE).decode().splitlines())
    current |= set(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
    assert all(permitted(path) for path in current), current
    links = []
    authored = [ROOT / 'TODO.md', ROOT / INDEX, ROOT / RECORD]
    authored += [p for p in EVIDENCE.rglob('*') if p.is_file() and p.suffix in {'.py', '.json', '.txt', '.md'}]
    if (ROOT / REVIEW).exists():
        authored.append(ROOT / REVIEW)
    for path in authored:
        raw = path.read_bytes()
        assert b'\r' not in raw and raw.endswith(b'\n') and not raw.endswith(b'\n\n'), path
        assert not re.search(rb'[ \t]+\n', raw), path
        if path.suffix == '.json':
            parse(raw)
        if path.suffix == '.py':
            ast.parse(raw)
        if path.suffix != '.md':
            continue
        if raw.startswith(b'---\n'):
            assert re.search(rb'\n---\n', raw[4:]), path
        for match in re.finditer(r'(?<!!)\[[^\]]*\]\(([^)]+)\)', raw.decode()):
            ref = unquote(match[1].strip('<>'))
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / url.path).resolve() if url.path else path
            assert target.exists(), (path, ref)
            if url.fragment and target.suffix == '.md':
                assert url.fragment in anchors(target), (path, ref)
            links.append({'source': str(path.relative_to(ROOT)), 'ref': ref})
    discovered = parse((EVIDENCE / 'profile-discovery.json').read_bytes())
    assert discovered[0]['value']['structuredContent']['profiles'] == []
    models = {row['id']: row for row in discovered[2]['value']['structuredContent']['models']}
    for model, effort in [('gpt-6.1-sol', 'medium'), ('gpt-6.1-sol', 'high'),
                          ('gpt-6-luna', 'high'), ('gpt-6-astra', 'high')]:
        assert effort in {row['id'] for row in models[model]['thinkingOptions']}
    proposals = parse((ROOT / 'docs/workflows/p0-profiles-evidence/proposed.patch.json').read_bytes())
    assert len(proposals['agentProfiles']) == 4
    runtime = parse((EVIDENCE / 'worker-runtime.json').read_bytes())['structuredContent']['snapshot']
    assert runtime['model'] == 'gpt-6.1-sol' and runtime['effectiveThinkingOptionId'] == 'high'
    assert runtime['currentModeId'] == 'auto-review'
    accepted_notes()
    for entry in parse((EVIDENCE / 'worker-retention.json').read_bytes())['artifacts']:
        stored = (EVIDENCE / entry['retained']).read_bytes()
        verify(stored, {'bytes': entry['stored_bytes'], 'sha256': entry['stored_sha256']})
        verify(gzip.decompress(stored), entry)
    # Expected historical raw EOF diagnostics, never a blanket whitespace waiver.
    full = subprocess.run(['git', 'diff', '--check', PRIOR, BASE], cwd=ROOT, capture_output=True)
    exceptions = ['docs/spikes/s05-evidence/raw-s05-todo.md',
                  'docs/spikes/s05-evidence/editor/protocol-queue-before-measurement.md']
    assert full.returncode == 2
    assert set(re.findall(r'(?m)^([^:\n]+):\d+:', full.stdout.decode())) == set(exceptions)
    scoped = subprocess.run(['git', 'diff', '--check', PRIOR, BASE, '--', '.',
                             *[':(exclude)' + p for p in exceptions]], cwd=ROOT, capture_output=True)
    assert scoped.returncode == 0
    candidate = subprocess.run(['git', 'diff', '--check', BASE], cwd=ROOT, capture_output=True)
    assert candidate.returncode == 0, candidate.stdout
    for marker in ['MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge',
                   'rebase-apply', 'sequencer', 'BISECT_LOG', 'index.lock']:
        assert not Path(git('rev-parse', '--git-path', marker).decode().strip()).exists(), marker
    result = {'head': head, 'base': BASE, 'prior_exclusive': PRIOR, 'accepted_commits': 10,
              'tasks_before': 27, 'tasks_after': 29, 'modified_tasks': sorted(changed),
              'new_tasks': sorted(NEW_TASKS), 'preserved_entries': preserved, 'links': links,
              'accepted_whitespace': {'exit': full.returncode, 'stdout': full.stdout.decode(),
                                      'stderr': full.stderr.decode(), 'exact_exclusions': exceptions,
                                      'excluded_exit': scoped.returncode},
              'candidate_whitespace_exit': candidate.returncode,
              'scope': sorted(current), 'no_active_git_operations': True}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(f'PASS {preserved} preserved base mode/blob/working entries;{len(links)} links;JSON/LF/AST/authored whitespace')
    print('PASS raw accepted-range exit2/exact two historical receipts;authored diff exit0;no Git operations')
    print(f'HEAD {head}; held LOCAL main/base {BASE}; output {args.output}')


if __name__ == '__main__':
    main()
