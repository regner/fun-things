"""Independent read-only review checks for the frozen fourth checkpoint."""
import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path('/home/regner/.paseo/worktrees/0u71f39f/plan-checkpoint-enet-profiles')
BASE = '8d60ff68bf2091f3077371de00b9b06960cec5ae'
HEAD = '0f87146c06135e1f22d7802d7450ee3df1f6207d'
PRIOR = '35adb47042fe6b27c1653d38636f5eaf7d47578b'
OUT = Path('/tmp/plan-check04-independent-review')

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def pairs(items):
    result = {}
    for k, v in items:
        assert k not in result, k
        result[k] = v
    return result

def parse_tasks(content):
    starts = list(re.finditer(r'^- \[ \] \*\*([A-Z0-9-]+) —', content, re.M))
    result = {}
    for n, m in enumerate(starts):
        end = starts[n+1].start() if n+1 < len(starts) else len(content)
        assert m[1] not in result
        result[m[1]] = re.split(r'(?m)^#{1,3} ', content[m.start():end])[0].rstrip()
    return result

assert git('rev-parse', 'HEAD').decode().strip() == HEAD
assert git('rev-parse', 'refs/heads/main').decode().strip() == BASE
assert git('status', '--porcelain=v1', '-uall') == b''
for a, b in [(PRIOR, BASE), (BASE, HEAD)]:
    subprocess.run(['git', 'merge-base', '--is-ancestor', a, b], cwd=ROOT, check=True)
assert git('rev-list', '--merges', PRIOR+'..'+HEAD) == b''
rows = git('log', '--reverse', '--format=%H %P', PRIOR+'..'+BASE).decode().splitlines()
assert len(rows) == 13
last = PRIOR
for row in rows:
    sha, parent = row.split()
    assert parent == last
    last = sha
assert last == BASE
print('PASS frozen SHA/base, clean status, actual 13 linear accepted commits and ancestry')

expected = set('P0-PROFILES S02 S03-S S03-R S04 S05 S06 S07 S08 P0-GATE M1-A1 M1-A2 M1-A3 M1-A-GATE M1-B1 M1-B2 M1-B3 M1-B4 M1-C1 M1-C2 M1-C3 M1-C4 M1-D1 M1-D2 M1-D3 M1-D4 M1-GATE'.split())
before = parse_tasks(git('show', BASE+':TODO.md').decode())
after = parse_tasks((ROOT/'TODO.md').read_text())
assert set(before) == expected and len(before) == 27
assert set(after) == expected | {'P0-DOC5'} and len(after) == 28
record = ROOT/'docs/reviews/plan-check-2026-10-07-04.md'
coverage = re.findall(r'^\| ([A-Z][A-Z0-9-]+) \|', record.read_text(), re.M)
assert len(coverage) == 28 and set(coverage) == set(after)
changed_tasks = {k for k in expected if before[k] != after[k]}
assert changed_tasks == {'P0-PROFILES', 'S03-R', 'S04', 'P0-GATE'}
print('PASS independent expected 27/28 IDs, once-only full coverage, four revised blocks/no removals')

allowed = {'TODO.md', 'docs/reviews/plan-checkpoints.md', 'docs/reviews/plan-check-2026-10-07-04.md'}
allowed |= {str(p.relative_to(ROOT)) for p in (ROOT/'docs/reviews/plan-check-04-evidence').iterdir()}
changed = set(git('diff', '--name-only', BASE, HEAD).decode().splitlines())
assert changed == allowed and len(changed) == 7
def tree(sha):
    return dict((row.split(b'\t')[1], row.split(b'\t')[0]) for row in git('ls-tree', '-r', sha).splitlines())
old, new = tree(BASE), tree(HEAD)
preserved = [p for p in old if p.decode() not in changed]
assert all(new.get(p) == old[p] for p in preserved)
assert len(preserved) == 914
print('PASS exact seven-path scope and 914 other base tree mode/blob entries retained')

manifest = json.loads((ROOT/'docs/reviews/plan-check-04-evidence/audit-manifest.json').read_text(), object_pairs_hook=pairs)
for item in manifest['consulted_exact_final_notes']:
    raw = git('notes', '--ref='+item['ref'], 'show', item['revision'])
    assert len(raw) == item['bytes']
    assert hashlib.sha256(raw).hexdigest() == item['sha256']
    (OUT/('note-'+item['revision'][:7]+'.txt')).write_bytes(raw)
print('PASS four full exact-final Git note byte counts/hashes; copies retained for review')

def heading_ids(path):
    seen, result = {}, set()
    for line in path.read_text().splitlines():
        match = re.match(r'^#{1,6} +(.+)$', line)
        if not match:
            continue
        label = re.sub(r'[`*_]', '', match[1].rstrip(' #')).lower()
        slug = ''.join(c for c in label if c in '-_ ' or unicodedata.category(c)[0] in {'L', 'N'}).replace(' ', '-')
        n = seen.get(slug, 0)
        seen[slug] = n+1
        result.add(slug if not n else slug+'-'+str(n))
    return result
links, jsons = 0, 0
for name in changed:
    path = ROOT/name
    raw = path.read_bytes()
    assert b'\r' not in raw and raw.endswith(b'\n')
    assert all(line.rstrip(b' \t') == line for line in raw.splitlines())
    if path.suffix == '.json':
        json.loads(raw, object_pairs_hook=pairs)
        jsons += 1
    if path.suffix != '.md':
        continue
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', raw.decode()):
        url = urlsplit(target.strip('<>'))
        if url.scheme:
            continue
        destination = (path.parent/unquote(url.path)).resolve() if url.path else path
        assert destination.exists(), (name, target)
        if url.fragment and destination.suffix == '.md':
            assert unquote(url.fragment) in heading_ids(destination), (name, target)
        links += 1
subprocess.run(['git', 'diff', '--check', BASE, HEAD], cwd=ROOT, check=True)
print(f'PASS independent {links} local links/anchors, {jsons} duplicate-key-checked JSONs, LF/whitespace')

fresh = json.loads((OUT/'discovery.json').read_text())
assert fresh[0]['profiles'] == []
models = {m['id']: m for m in fresh[2]['models']}
inspections = {r['selectedModel']: r for r in fresh[3:]}
proposals = json.loads((ROOT/'docs/workflows/p0-profiles-evidence/proposed.patch.json').read_text(), object_pairs_hook=pairs)['agentProfiles']
assert [(p['model'], p['thinkingOptionId']) for p in proposals] == [('gpt-6.1-sol', 'medium'), ('gpt-6.1-sol', 'high'), ('gpt-6-luna', 'high'), ('gpt-6-astra', 'high')]
for p in proposals:
    assert p['thinkingOptionId'] in {t['id'] for t in models[p['model']]['thinkingOptions']}
    assert p['modeId'] == 'auto-review' and p['provider'] == 'codex'
    assert set(p['featureValues']) <= {f['id'] for f in inspections[p['model']]['features']}
    assert all(v is False for v in p['featureValues'].values())
    assert p['notes'].strip()
print('PASS independent fresh empty inventory and four proposed declarations; no launch proof')
for marker in ['rebase-merge', 'rebase-apply', 'MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'BISECT_LOG', 'index.lock']:
    path = Path(git('rev-parse', '--git-path', marker).decode().strip())
    if not path.is_absolute():
        path = ROOT/path
    assert not path.exists(), marker
print('PASS no Git operation/index lock; only static checks executed')
