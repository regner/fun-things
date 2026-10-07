"""Local documentation integrity checks only; never imports project tooling."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path.cwd()
BASE = '8b6dc3083fcb875febe778e362da1182ac4d67d1'
CORE = {'README.md', 'docs/development.md', 'docs/assets/s02_kit.md',
        'TODO.md', 'docs/reviews/p0-doc5.md'}

def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()

head = git('rev-parse', 'HEAD')
main = git('rev-parse', 'refs/heads/main')
assert main == BASE, f'accepted main advanced: {main}; reconcile before delivery'
subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, head], check=True)
assert not git('rev-list', '--merges', BASE + '..' + head)
changed = set(git('diff', '--name-only', BASE).splitlines())
changed |= set(git('ls-files', '--others', '--exclude-standard').splitlines())
assert CORE <= changed, changed
assert all(p in CORE or p == 'docs/reviews/p0-doc5-review.md'
           or p.startswith('docs/reviews/p0-doc5-evidence/') for p in changed), changed
subprocess.run(['git', 'diff', '--check', BASE], check=True)

links = 0
for name in sorted(p for p in changed if p.endswith('.md')):
    path = ROOT / name
    data = path.read_bytes()
    assert b'\r' not in data and data.endswith(b'\n'), name
    assert all(line.rstrip() == line for line in data.splitlines()), name
    text = data.decode()
    for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', text):
        if re.match(r'[a-zA-Z]+:', target):
            continue
        destination, _, fragment = unquote(target).partition('#')
        resolved = (path.parent / destination).resolve() if destination else path
        assert resolved.exists(), (name, target)
        if fragment:
            assert resolved.suffix == '.md', (name, target)
            headings = re.findall(r'^#{1,6}\s+(.+?)\s*#*$', resolved.read_text(), re.M)
            counts = {}
            anchors = set()
            for heading in headings:
                heading = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', heading)
                slug = re.sub(r'[^\w\-\s]', '', heading.lower()).replace(' ', '-')
                repeat = counts.get(slug, 0)
                counts[slug] = repeat + 1
                anchors.add(slug + (f'-{repeat}' if repeat else ''))
            assert fragment in anchors, (name, target, anchors)
        links += 1
for name in changed:
    data = (ROOT / name).read_bytes()
    assert b'\r' not in data and data.endswith(b'\n'), name

base_todo = subprocess.check_output(['git', 'show', BASE + ':TODO.md'], text=True)
todo = (ROOT / 'TODO.md').read_text()
ids = lambda t: re.findall(r'^- \[ \] \*\*([A-Z0-9-]+) —', t, re.M)
assert set(ids(base_todo)) - set(ids(todo)) == {'P0-DOC5'}
assert set(ids(todo)) - set(ids(base_todo)) == set()
assert len(ids(base_todo)) == 28 and len(ids(todo)) == 27
# Every unaffected task keeps its complete block through the next task/section.
blocks = lambda t: dict(re.findall(
    r'(^- \[ \] \*\*([A-Z0-9-]+) —.*?)(?=^- \[ \] |^#{1,3} |\Z)', t, re.M | re.S))
for block, task in blocks(base_todo).items():
    if task not in {'P0-DOC5', 'P0-GATE'}:
        assert block in todo, f'unrelated task block changed: {task}'
assert '8d60ff68bf2091f3077371de00b9b06960cec5ae' in (
    ROOT / 'docs/reviews/plan-checkpoints.md').read_text()
# All tracked paths outside authorized guides/TODO/evidence retain original bytes.
entries = subprocess.check_output(['git', 'ls-tree', '-r', '-z', BASE]).split(b'\0')
preserved = 0
for entry in filter(None, entries):
    metadata, raw_path = entry.split(b'\t', 1)
    name = raw_path.decode()
    if name in changed:
        continue
    blob = metadata.split()[2].decode()
    assert (ROOT / name).read_bytes() == subprocess.check_output(['git', 'cat-file', 'blob', blob]), name
    preserved += 1
receipt = json.loads((ROOT / 'docs/spikes/s03-r-evidence/editor/original-preservation-final.json').read_text())
assert len(receipt['paths']) == 82
for row in receipt['paths']:
    assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
for operation in ['rebase-merge', 'rebase-apply', 'MERGE_HEAD', 'CHERRY_PICK_HEAD',
                  'REVERT_HEAD', 'BISECT_LOG', 'index.lock']:
    assert not Path(git('rev-parse', '--git-path', operation)).exists(), operation
print(f'HEAD {head}; held local-main/base {main}')
print(f'PASS scoped {len(changed)} paths; {links} local links/anchors; LF/final newline/whitespace')
print(f'PASS only DOC5 removed: 28 -> 27 tasks; unrelated task blocks retained')
print(f'PASS {preserved} unchanged base files; original 82 fingerprints; checkpoint/history/watermark retained')
print('PASS base ancestry, zero merges and no active Git operations/index lock')
print('Static documentation checks only; no engine/tool runner/tests/import/network/reexport/config/launch proof')
print('Git status including untracked: ' + (git('status', '--porcelain=v1', '-uall') or 'clean'))
