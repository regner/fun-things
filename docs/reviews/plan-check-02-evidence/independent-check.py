import json
import re
import subprocess
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path('/home/regner/.paseo/worktrees/0u71f39f/plan-checkpoint-steam-deck-deferrals')
BASE = '6a012de162b0d65cdf0c77b2914788ad56fbecf1'
HEAD = '30a6802f100f23b18614a43c772591b6e2533e98'
WATERMARK = '3b50a915d06f7ad383a4d6dc70403729918c0268'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True)

assert git('rev-parse', 'HEAD').strip() == HEAD
assert git('rev-parse', 'refs/heads/main').strip() == BASE
assert not git('status', '--porcelain')
subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, HEAD], cwd=ROOT, check=True)
subprocess.run(['git', 'merge-base', '--is-ancestor', WATERMARK, BASE], cwd=ROOT, check=True)
assert not git('rev-list', '--merges', WATERMARK + '..' + HEAD)
subprocess.run(['git', 'diff', '--check', BASE, HEAD], cwd=ROOT, check=True)
paths = git('diff', '--name-only', BASE, HEAD).splitlines()
assert set(paths) == {
    'TODO.md', 'docs/reviews/plan-checkpoints.md',
    'docs/reviews/plan-check-2026-10-07-02.md',
    'docs/reviews/plan-check-02-evidence/profile-assessment.json',
    'docs/reviews/plan-check-02-evidence/raw-requirements.txt',
    'docs/reviews/plan-check-02-evidence/worker-checks.txt',
}
first = 'docs/reviews/plan-check-2026-10-07.md'
assert git('show', BASE + ':' + first) == (ROOT / first).read_text()
print('PASS exact candidate/main, clean status, six-path scope, preserved first record, watermark ancestry, zero merge commits, diff whitespace')

def headings(path):
    found = set()
    counts = {}
    for line in path.read_text().splitlines():
        m = re.match(r'^#{1,6}\s+(.+?)\s*#*$', line)
        if not m:
            continue
        s = m[1].lower().replace('`', '')
        s = ''.join(c for c in s if c in '-_ ' or unicodedata.category(c)[0] in 'LN')
        s = s.replace(' ', '-')
        n = counts.get(s, 0)
        counts[s] = n + 1
        found.add(s + (f'-{n}' if n else ''))
    return found

links = 0
for name in paths:
    path = ROOT / name
    raw = path.read_bytes()
    assert b'\r' not in raw, name
    assert all(line == line.rstrip(b' \t') for line in raw.splitlines()), name
    if name.endswith('.json'):
        json.loads(raw)
    if not name.endswith('.md'):
        continue
    content = re.sub(r'(?ms)^```.*?^```[^\n]*\n?', '', raw.decode())
    for m in re.finditer(r'!?\[[^\]]*\]\(([^)]+)\)', content):
        target = urlsplit(m[1])
        if target.scheme:
            continue
        dest = (path.parent / unquote(target.path)).resolve() if target.path else path
        assert dest.exists(), (name, m[1])
        if target.fragment and dest.suffix == '.md':
            assert unquote(target.fragment) in headings(dest), (name, m[1])
        links += 1
print(f'PASS three changed Markdown files: {links} local links/anchors; changed JSON parses; changed files LF and trailing whitespace')

todo = (ROOT / 'TODO.md').read_text()
prior = git('show', BASE + ':TODO.md')
task_ids = re.findall(r'^- \[ \] \*\*([A-Z0-9-]+) —', todo, re.M)
old_ids = re.findall(r'^- \[ \] \*\*([A-Z0-9-]+) —', prior, re.M)
record = (ROOT / 'docs/reviews/plan-check-2026-10-07-02.md').read_text()
rows = re.findall(r'^\| ([A-Z][A-Z0-9-]+) \|', record, re.M)
assert len(task_ids) == len(set(task_ids)) == 28
assert sorted(rows) == sorted(task_ids)
assert set(task_ids) - set(old_ids) == {'P0-DOC3'}
assert not set(old_ids) - set(task_ids)
assert all(x not in task_ids for x in ('P0-DOC1', 'P0-DOC2', 'P0-07', 'S03', 'P0-03'))
print('PASS all 28 remaining tasks covered once; only P0-DOC3 added; no task removals/reopened completed tasks')
print('Accepted range:', git('log', '--reverse', '--format=%H %s', WATERMARK + '..' + BASE).strip())
print('Main uncovered delta:', git('log', '--format=%H %s', BASE + '..refs/heads/main').strip() or 'none')
