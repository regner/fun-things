"""Read-only static checkpoint checks; run from this worktree's repository root."""
import json
import re
import subprocess
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path.cwd()
BASE = '35adb47042fe6b27c1653d38636f5eaf7d47578b'
PRIOR = '6a012de162b0d65cdf0c77b2914788ad56fbecf1'
RECORD = ROOT / 'docs/reviews/plan-check-2026-10-07-03.md'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, f'duplicate JSON key: {key}'
        result[key] = value
    return result


def anchors(path):
    result, counts = set(), {}
    content = re.sub(r'(?ms)^```.*?^```[^\n]*\n?', '', path.read_text())
    for line in content.splitlines():
        match = re.match(r'^#{1,6}\s+(.+?)\s*#*$', line)
        if not match:
            continue
        slug = match[1].lower().replace('`', '')
        slug = ''.join(c for c in slug if c in '-_ ' or unicodedata.category(c)[0] in 'LN')
        slug = slug.replace(' ', '-')
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(slug + (f'-{count}' if count else ''))
    return result


head = git('rev-parse', 'HEAD')
main = git('rev-parse', 'refs/heads/main')
print(f'HEAD {head}; main {main}; examined {PRIOR}..{BASE}')
subprocess.run(['git', 'merge-base', '--is-ancestor', PRIOR, BASE], check=True)
subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, head], check=True)
assert not git('rev-list', '--merges', PRIOR + '..' + head)
assert len(git('rev-list', PRIOR + '..' + BASE).splitlines()) == 12
print('PASS examined 12-commit accepted range, base ancestry and no merge commits')

for name in ['plan-check-2026-10-07.md', 'plan-check-2026-10-07-02.md',
             'plan-check-review-2026-10-07-02.md']:
    path = 'docs/reviews/' + name
    before = subprocess.check_output(['git', 'show', BASE + ':' + path])
    assert before == (ROOT / path).read_bytes(), path
print('PASS earlier checkpoint/review bytes preserved')

todo = (ROOT / 'TODO.md').read_text()
prior_todo = git('show', BASE + ':TODO.md')
ids = re.findall(r'^- \[ \] \*\*([A-Z0-9-]+) —', todo, re.M)
old_ids = re.findall(r'^- \[ \] \*\*([A-Z0-9-]+) —', prior_todo, re.M)
rows = re.findall(r'^\| ([A-Z][A-Z0-9-]+) \|', RECORD.read_text(), re.M)
assert len(ids) == len(set(ids)) == 28
assert sorted(rows) == sorted(ids)
assert set(ids) - set(old_ids) == {'P0-DOC4'}
assert not set(old_ids) - set(ids)
assert not {'P0-DOC1', 'P0-DOC2', 'P0-DOC3', 'S01', 'S03', 'P0-03'} & set(ids)
print('PASS all 28 tasks covered once; only DOC4 added; no closure/recreated completed tasks')

paths = {'TODO.md', 'docs/reviews/plan-checkpoints.md', str(RECORD.relative_to(ROOT))}
paths.update(str(p.relative_to(ROOT)) for p in (ROOT / 'docs/reviews/plan-check-03-evidence').iterdir()
             if p.is_file())
review = ROOT / 'docs/reviews/plan-check-review-2026-10-07-03.md'
if review.exists():
    paths.add(str(review.relative_to(ROOT)))
changed = set(git('diff', '--name-only', BASE).splitlines())
assert changed <= paths, changed - paths
links = 0
json_count = 0
for name in sorted(paths):
    path = ROOT / name
    raw = path.read_bytes()
    assert b'\r' not in raw, name
    assert all(line == line.rstrip(b' \t') for line in raw.splitlines()), name
    if path.suffix == '.json':
        json.loads(raw, object_pairs_hook=unique_pairs)
        json_count += 1
    if path.suffix != '.md':
        continue
    content = re.sub(r'(?ms)^```.*?^```[^\n]*\n?', '', raw.decode())
    for match in re.finditer(r'!?\[[^\]]*\]\(([^)]+)\)', content):
        target = urlsplit(match[1])
        if target.scheme:
            continue
        dest = (path.parent / unquote(target.path)).resolve() if target.path else path
        assert dest.exists(), (name, match[1])
        if target.fragment and dest.suffix == '.md':
            assert unquote(target.fragment) in anchors(dest), (name, match[1])
        links += 1
subprocess.run(['git', 'diff', '--check', BASE], check=True)
print(f'PASS allowed doc/evidence scope, {links} local links/anchors, {json_count} JSONs, LF/whitespace')
print('Unchecked main advance:', git('log', '--format=%H %s', BASE + '..refs/heads/main') or 'none')
print('Status (including untracked):', git('status', '--porcelain=v1', '-uall') or 'clean')
