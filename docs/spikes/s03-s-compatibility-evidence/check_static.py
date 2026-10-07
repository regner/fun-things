"""Scoped documentation/evidence integrity, not Steam conformance acceptance."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
BASE = '04f16d332636200e71e74862f64282224774d077'


def git(*args: str) -> str:
    """Read this worktree's repository state only."""
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True)


def allowed(path: str) -> bool:
    """Limit edits to the single probe, historical supplement and review retention."""
    return path in ['TODO.md', 'docs/spikes/s03-s.md',
                    'docs/spikes/s03-s-compatibility.md', 'tools/probe_s03_s_compatibility.py'] or (
        path.startswith('docs/spikes/s03-s-compatibility-evidence/') or
        path.startswith('docs/reviews/s03-s-compatibility'))


def headings(text: str) -> set[str]:
    """Resolve current local Markdown anchors for the scoped record links."""
    result = set()
    for line in text.splitlines():
        match = re.match(r'^#{1,6} (.*)', line)
        if match:
            result.add(re.sub(r'[^\w -]', '', match[1].lower()).replace(' ', '-'))
    return result


changed = set(git('diff', '--name-only', BASE).splitlines())
changed.update(git('ls-files', '--others', '--exclude-standard').splitlines())
assert changed and all(allowed(p) for p in changed), changed
base_paths = git('ls-tree', '-r', '--name-only', BASE).splitlines()
preserved = 0
for name in base_paths:
    if name in changed:
        continue
    original = subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=ROOT)
    assert (ROOT / name).read_bytes() == original, name
    preserved += 1
before = git('show', BASE + ':TODO.md')
after = (ROOT / 'TODO.md').read_text()
pattern = r'(?ms)^- \[ \] \*\*([A-Z0-9-]+) —.*?(?=^- \[ \]|^## |\Z)'
a = {m[1]: m[0] for m in re.finditer(pattern, before)}
b = {m[1]: m[0] for m in re.finditer(pattern, after)}
assert a.keys() == b.keys() and len(a) == 27
assert all(a[key] == b[key] for key in a if key != 'S03-S')
assert a['S03-S'] != b['S03-S'] and 'full S03-S remains OPEN' in b['S03-S']
old = git('show', BASE + ':docs/spikes/s03-s.md')
assert (ROOT / 'docs/spikes/s03-s.md').read_text().startswith(old)
links = 0
for name in sorted(changed):
    path = ROOT / name
    data = path.read_bytes()
    assert b'\r' not in data and data.endswith(b'\n'), name
    if path.suffix in ['.py', '.md', '.json', '.txt']:
        assert all(line.rstrip() == line for line in data.splitlines()), name
    if path.suffix == '.json':
        json.loads(data)
    if path.suffix == '.md':
        for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', data.decode()):
            if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', target):
                continue
            dest, _, anchor = unquote(target).partition('#')
            resolved = (path.parent / dest).resolve() if dest else path
            assert resolved.is_file(), (name, target)
            if anchor:
                assert anchor in headings(resolved.read_text()), (name, target)
            links += 1
manifest = json.loads((ROOT / 'docs/spikes/s03-s-evidence/provenance.json').read_text())
for item in manifest['native']:
    assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']
assert not git('rev-list', '--merges', BASE + '..HEAD').strip()
subprocess.run(['git', 'diff', '--check', BASE], cwd=ROOT, check=True)
for operation in ['rebase-merge', 'rebase-apply', 'MERGE_HEAD', 'CHERRY_PICK_HEAD', 'index.lock']:
    assert not Path(git('rev-parse', '--git-path', operation).strip()).exists(), operation
print(f'PASS scoped paths={len(changed)}, preserved original blobs={preserved}, local links={links}')
print('PASS 27 tasks unchanged except S03-S supplement; original preparation prefix preserved')
print('PASS all22 original native hashes, JSON/LF/whitespace, linear ancestry, no Git operations')
print('Evidence kinds: static/synthetic/registration only; no native network/lifecycle acceptance')
