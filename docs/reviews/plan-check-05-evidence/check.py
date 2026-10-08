"""Static fifth-checkpoint integrity only; no project imports or live surface calls."""
import argparse
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
EVIDENCE = ROOT / 'docs/reviews/plan-check-05-evidence'
BASE = 'ca38e4fc55b32a379ef7e3bf947e27d4ca8edc4c'
PRIOR = '8d60ff68bf2091f3077371de00b9b06960cec5ae'
RECORD = 'docs/reviews/plan-check-2026-10-08-05.md'
INDEX = 'docs/reviews/plan-checkpoints.md'
REVIEW = 'docs/reviews/plan-check-review-2026-10-08-05.md'


def git(*args):
    """Read repository topology, tree identities and source bytes without mutation."""
    return subprocess.check_output(['git', *args], cwd=ROOT, timeout=30)


def pairs(entries):
    """Reject duplicate JSON keys that could hide conflicting evidence values."""
    result = {}
    for key, value in entries:
        assert key not in result, key
        result[key] = value
    return result


def read_json(path):
    """Parse local data without importing or executing repository tooling."""
    return json.loads(path.read_text(), object_pairs_hook=pairs)


def digest(raw):
    """Bind byte-faithful reports, logs and records to the supplied manifest."""
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def verify(raw, entry):
    """Check original bytes and count, allowing no newline or whitespace rewrites."""
    assert digest(raw) == {key: entry[key] for key in ('bytes', 'sha256')}, entry


def tasks(text):
    """Read complete active blocks, stopping at the next task or section heading."""
    matches = list(re.finditer(r'^- \[ \] \*\*([A-Z0-9-]+) —', text, re.M))
    result = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = re.split(r'(?m)^#{1,3} ', text[match.start():end], maxsplit=1)[0].rstrip()
        assert match[1] not in result
        result[match[1]] = block
    return result


def anchors(path):
    """Resolve local Markdown headings with GitHub punctuation and duplicate rules."""
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


def tree(revision):
    """Read mode/blob identity for every saved entry without import or editor access."""
    return {line.split('\t', 1)[1]: line.split('\t', 1)[0]
            for line in git('ls-tree', '-r', revision).decode().splitlines()}


def note_receipts(manifest):
    """Verify full accepted notes and their packed/delimited actual review payloads."""
    notes = {}
    for entry in manifest['notes']:
        raw = gzip.decompress((EVIDENCE / entry['snapshot']).read_bytes())
        verify(raw, entry)
        current = git('notes', '--ref=paseo-orchestration', 'show', entry['revision'])
        assert current.startswith(raw), 'Historical note may only gain root append receipts'
        notes[entry['revision'][:7]] = raw.decode()
    s04 = notes['2370ad1']
    packed = re.search(r'--- BEGIN BASE64 EXACT-FINAL ARTIFACT TAR.GZ ---\s*(.*?)\s*'
                       r'--- END BASE64 EXACT-FINAL ARTIFACT TAR.GZ ---', s04, re.S)
    raw = base64.b64decode(packed[1])
    assert hashlib.sha256(raw).hexdigest() == '739b2cdefcec27c682b1e57f5e7d5179b4e7f15c3a915f3d57b5cd1fda3ecd2a'
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        files = {item.name: archive.extractfile(item).read()
                 for item in archive.getmembers() if item.isfile()}
    retained = json.loads(files['final-retention-manifest.json'])
    for entry in retained['files']:
        raw = files.get(entry['path'])
        if raw is None:
            path = entry['path'].replace('final-followup/raw-',
                                        'docs/spikes/s04-evidence/fix-enet/') + '.gz'
            raw = gzip.decompress((ROOT / path).read_bytes())
        verify(raw, entry)
    assert files['review-2370ad1-final.md'].decode() in s04
    assert len(retained['files']) == manifest['s04_final_note_payloads_verified'] == 28
    compat = notes['ca38e4f']
    ledger = json.JSONDecoder().raw_decode(compat.split('Full artifact integrity ledger:\n', 1)[1])[0]
    for entry in ledger:
        path = entry['path']
        kind = 'WORKER RECEIPT' if path.startswith('worker/') else 'REBASE RECEIPT'
        name = path.removeprefix('worker/')
        raw = compat.split('--- BEGIN ' + kind + ' ' + name + ' ---\n', 1)[1].split(
            '\n--- END ' + kind + ' ' + name + ' ---', 1)[0].encode()
        assert any(digest(v) == {key: entry[key] for key in ('bytes', 'sha256')}
                   for v in (raw, raw[:-1], raw[:-2])), path
    assert len(ledger) == manifest['compatibility_final_note_payloads_verified'] == 17
    for entry in read_json(ROOT / 'docs/reviews/s03-s-compatibility-evidence/retention.json')['artifacts']:
        verify((ROOT / entry['retained']).read_bytes(), entry)
    print('PASS full accepted note snapshots, S04 28 packed/raw mappings, compatibility 17 note/23 original receipts')


def main():
    """Check complete scope, examination, plan retention and static evidence fidelity."""
    argparse.ArgumentParser(description=__doc__).parse_args()
    head = git('rev-parse', 'HEAD').decode().strip()
    assert git('rev-parse', 'refs/heads/main').decode().strip() == BASE, 'Accepted delta reconciliation required'
    print(f'HEAD {head}; base/main {BASE}; examined EXCLUSIVE {PRIOR} .. INCLUSIVE {BASE}')
    manifest = read_json(EVIDENCE / 'audit-manifest.json')
    assert manifest['base'] == manifest['inclusive_watermark'] == BASE
    assert manifest['prior_exclusive'] == PRIOR
    revisions = git('rev-list', '--reverse', PRIOR + '..' + BASE).decode().splitlines()
    assert len(revisions) == manifest['accepted_commit_count'] == 11
    assert revisions == [entry['revision'] for entry in manifest['commits']]
    for entry in manifest['commits']:
        assert entry['parents'] == git('show', '-s', '--format=%P', entry['revision']).decode().split()
        assert entry['paths'] == git('diff-tree', '--no-commit-id', '--name-only', '-r', entry['revision']).decode().splitlines()
    for ancestor, descendant in [(PRIOR, BASE), (BASE, head)]:
        subprocess.run(['git', 'merge-base', '--is-ancestor', ancestor, descendant], cwd=ROOT, check=True)
    assert not git('rev-list', '--merges', PRIOR + '..' + head).strip()
    print('PASS exact 11 accepted commits, initial8/new3, parents/paths/ancestry, no merge commits')

    before = tasks(git('show', BASE + ':TODO.md').decode())
    after = tasks((ROOT / 'TODO.md').read_text())
    assert list(before) == manifest['base_task_ids'] and len(before) == 27
    assert len(after) == 29 and set(after) - set(before) == {'P0-DOC6', 'P0-DOC7'}
    assert not set(before) - set(after)
    rows = re.findall(r'^\| ([A-Z][A-Z0-9-]+) \|', (ROOT / RECORD).read_text(), re.M)
    assert sorted(rows) == sorted(after), 'Every current task needs exactly one disposition'
    revised = {'P0-PROFILES', 'S04', 'S05', 'S06', 'P0-GATE'}
    for key in set(before) - revised:
        assert before[key] == after[key], key
    assert not set(after) & {'P0-DOC1', 'P0-DOC2', 'P0-DOC3', 'P0-DOC4', 'P0-DOC5', 'S01', 'S03', 'P0-03'}
    assert 'P0-DOC6/P0-DOC7' in after['P0-GATE']
    print('PASS 27 base / 29 delivered tasks, DOC6/DOC7 alone added, all covered once; unrelated blocks/S03-S retained')

    changed = set(git('diff', '--name-only', BASE).decode().splitlines())
    changed.update(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
    allowed = {'TODO.md', INDEX, RECORD, REVIEW}
    assert all(path in allowed or path.startswith('docs/reviews/plan-check-05-evidence/')
               for path in changed), changed
    old_tree, new_tree = tree(BASE), tree(head)
    kept = 0
    for path, identity in old_tree.items():
        if path not in {'TODO.md', INDEX}:
            assert new_tree.get(path) == identity, path
            assert (ROOT / path).read_bytes() == git('show', BASE + ':' + path), path
            kept += 1
    for entry in manifest['consulted_records']:
        verify(git('show', entry['revision'] + ':' + entry['path']), entry)
    print(f'PASS scoped checkpoint docs/evidence; {kept} other base mode/blob/working bytes and historical consulted records')

    links = json_count = 0
    raw_retention = EVIDENCE / 'retention.json'
    receipts = {}
    if raw_retention.exists():
        for entry in read_json(raw_retention)['files']:
            verify((ROOT / entry['retained']).read_bytes(), entry)
            receipts[entry['retained']] = entry
        print(f'PASS {len(receipts)} full independent report/check artifacts retained byte-faithfully')
    paths = {'TODO.md', INDEX, RECORD}
    paths.update(str(path.relative_to(ROOT)) for path in EVIDENCE.rglob('*') if path.is_file())
    if (ROOT / REVIEW).exists():
        paths.add(REVIEW)
    for name in sorted(paths):
        path = ROOT / name
        raw = path.read_bytes()
        if path.suffix == '.gz':
            gzip.decompress(raw)
            continue
        if name not in receipts:
            assert b'\r' not in raw and raw.endswith(b'\n'), name
            assert all(line == line.rstrip(b' \t') for line in raw.splitlines()), name
        if path.suffix == '.json':
            read_json(path)
            json_count += 1
        if path.suffix != '.md':
            continue
        content = re.sub(r'(?ms)^```.*?^```[^\n]*\n?', '', raw.decode())
        for match in re.finditer(r'!?\[[^\]]*\]\(([^)]+)\)', content):
            target = urlsplit(match[1].strip('<>'))
            if target.scheme:
                continue
            dest = (path.parent / unquote(target.path)).resolve() if target.path else path
            assert dest.exists(), (name, match[1])
            if target.fragment and dest.suffix == '.md':
                assert unquote(target.fragment) in anchors(dest), (name, match[1])
            links += 1
    assert BASE in (ROOT / INDEX).read_text() and Path(RECORD).name in (ROOT / INDEX).read_text()
    subprocess.run(['git', 'diff', '--check', BASE], cwd=ROOT, check=True)
    print(f'PASS {links} local links/anchors, {json_count} JSONs; authored LF/newline/whitespace, latest exact examined index')
    note_receipts(manifest)
    discovery = read_json(EVIDENCE / 'profile-discovery.json')
    assert discovery['profiles']['structuredContent']['profiles'] == []
    supported = {model['id']: model for model in discovery['models']['structuredContent']['models']}
    proposal = read_json(ROOT / 'docs/workflows/p0-profiles-evidence/proposed.patch.json')['agentProfiles']
    assert len(proposal) == len({p['id'] for p in proposal}) == 4
    assert [(p['model'], p['thinkingOptionId']) for p in proposal] == [
        ('gpt-6.1-sol', 'medium'), ('gpt-6.1-sol', 'high'), ('gpt-6-luna', 'high'), ('gpt-6-astra', 'high')]
    for profile in proposal:
        assert profile['thinkingOptionId'] in {o['id'] for o in supported[profile['model']]['thinkingOptions']}
        assert profile['notes'].strip() and profile['modeId'] == 'auto-review'
    sol = discovery['corrected_sol_inspection']['structuredContent']
    assert sol['selectedModel'] == 'gpt-6.1-sol'
    assert sol['features'] == [dict(type='toggle', id='plan_mode', label='Plan',
                                 description='Switch Codex into planning-only collaboration mode',
                                 tooltip='Toggle plan mode', icon='list-todo', value=False)]
    print('PASS zero installed/four inert profiles, supported role/effort IDs, exact Sol inspection plan off; no launch/config proof')
    operations = ['rebase-merge', 'rebase-apply', 'MERGE_HEAD', 'CHERRY_PICK_HEAD',
                  'REVERT_HEAD', 'BISECT_LOG', 'index.lock', 'sequencer']
    assert not any(Path(git('rev-parse', '--git-path', op).decode().strip()).exists() for op in operations)
    print('PASS no active Git operations/index lock; static children completed; no shared lease/experiment')
    print('Status including untracked:', git('status', '--porcelain=v1', '-uall').decode().strip() or 'clean')


if __name__ == '__main__':
    main()
