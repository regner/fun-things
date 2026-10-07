"""Read-only static checkpoint audit; no engine, service or configuration execution."""
import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
BASE = '8d60ff68bf2091f3077371de00b9b06960cec5ae'
PRIOR = '35adb47042fe6b27c1653d38636f5eaf7d47578b'
RECORD = 'docs/reviews/plan-check-2026-10-07-04.md'
INDEX = 'docs/reviews/plan-checkpoints.md'
REVIEW = 'docs/reviews/plan-check-review-2026-10-07-04.md'
EVIDENCE = ROOT / 'docs/reviews/plan-check-04-evidence'


def git(*args):
    """Read exact Git revisions, trees or nonmutating check output."""
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def unique_pairs(pairs):
    """Reject duplicate JSON keys so evidence cannot hide earlier values."""
    result = {}
    for key, value in pairs:
        assert key not in result, key
        result[key] = value
    return result


def anchors(path):
    """Compute local GitHub-style heading anchors including repeated headings."""
    counts, result = {}, set()
    content = re.sub(r'(?ms)^```.*?^```[^\n]*\n?', '', path.read_text())
    for line in content.splitlines():
        match = re.match(r'^#{1,6}\s+(.+?)\s*#*$', line)
        if not match:
            continue
        title = re.sub(r'[`*_]', '', match[1]).lower()
        slug = ''.join(c for c in title if c in '-_ ' or unicodedata.category(c)[0] in 'LN')
        slug = slug.replace(' ', '-')
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(slug + (f'-{count}' if count else ''))
    return result


def tasks(text):
    """Bind each checkbox ID to its complete task block for preservation checks."""
    matches = list(re.finditer(r'^- \[ \] \*\*([A-Z0-9-]+) —', text, re.M))
    result = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.start():end]
        block = re.split(r'(?m)^#{1,3} ', block, maxsplit=1)[0].rstrip()
        assert match[1] not in result, match[1]
        result[match[1]] = block
    return result


def tree(revision):
    """Read tree identity without touching authoring files or import caches."""
    rows = git('ls-tree', '-r', revision).splitlines()
    return {row.split('\t', 1)[1]: row.split('\t', 1)[0] for row in rows}


def main():
    """Verify examined history, task coverage, retention, links and declared profile support."""
    head, main_head = git('rev-parse', 'HEAD'), git('rev-parse', 'refs/heads/main')
    print(f'HEAD {head}; main {main_head}; examined EXCLUSIVE {PRIOR} .. INCLUSIVE {BASE}')
    assert main_head == BASE, 'Main advanced: delta audit/reconciliation/review required'
    for ancestor, descendant in [(PRIOR, BASE), (BASE, head)]:
        subprocess.run(['git', 'merge-base', '--is-ancestor', ancestor, descendant],
                       cwd=ROOT, check=True)
    assert not git('rev-list', '--merges', PRIOR + '..' + head)
    manifest = json.loads((EVIDENCE / 'audit-manifest.json').read_text(),
                          object_pairs_hook=unique_pairs)
    revisions = git('rev-list', '--reverse', PRIOR + '..' + BASE).splitlines()
    assert len(revisions) == manifest['accepted_commit_count'] == 13
    assert manifest['base'] == manifest['inclusive_watermark'] == BASE
    assert manifest['prior_exclusive'] == PRIOR
    assert revisions == [c['revision'] for c in manifest['commits']]
    for commit in manifest['commits']:
        assert commit['parents'] == git('show', '-s', '--format=%P', commit['revision']).split()
        assert commit['paths'] == git('diff-tree', '--no-commit-id', '--name-only', '-r',
                                     commit['revision']).splitlines()
    print('PASS actual 13-commit exclusive/inclusive range, parents/paths and linear ancestry')

    before = tasks(git('show', BASE + ':TODO.md'))
    after = tasks((ROOT / 'TODO.md').read_text())
    assert list(before) == manifest['base_task_ids'] and len(before) == 27
    assert len(after) == 28 and set(after) - set(before) == {'P0-DOC5'}
    assert not set(before) - set(after)
    assert not set(after) & {'P0-DOC1', 'P0-DOC2', 'P0-DOC3', 'P0-DOC4', 'S01', 'S03', 'P0-03'}
    rows = re.findall(r'^\| ([A-Z][A-Z0-9-]+) \|', (ROOT / RECORD).read_text(), re.M)
    assert sorted(rows) == sorted(after), 'Every task must have exactly one disposition'
    revised = {'P0-PROFILES', 'S03-R', 'S04', 'P0-GATE'}
    for key in set(before) - revised:
        assert before[key] == after[key], f'Unscoped task block change: {key}'
    assert 'P0-DOC5' in after['P0-GATE']
    print('PASS 27 base / 28 delivered tasks covered once; only DOC5 added, none removed')

    paths = {'TODO.md', INDEX, RECORD}
    paths.update(str(p.relative_to(ROOT)) for p in EVIDENCE.iterdir() if p.is_file())
    if (ROOT / REVIEW).exists():
        paths.add(REVIEW)
    changed = set(git('diff', '--name-only', BASE).splitlines())
    changed.update(git('ls-files', '--others', '--exclude-standard').splitlines())
    assert changed <= paths, changed - paths
    old_tree, new_tree = tree(BASE), tree(head)
    kept = 0
    for path, identity in old_tree.items():
        if path not in {'TODO.md', INDEX}:
            assert new_tree.get(path) == identity, path
            kept += 1
    for item in manifest['consulted_records']:
        raw = (ROOT / item['path']).read_bytes()
        assert len(raw) == item['bytes']
        assert hashlib.sha256(raw).hexdigest() == item['sha256'], item['path']
    print(f'PASS {kept} other base tree entries and all historical/source records retained')

    links, json_count = 0, 0
    for name in sorted(paths):
        path = ROOT / name
        raw = path.read_bytes()
        assert b'\r' not in raw and raw.endswith(b'\n'), name
        assert all(line == line.rstrip(b' \t') for line in raw.splitlines()), name
        if path.suffix == '.json':
            json.loads(raw, object_pairs_hook=unique_pairs)
            json_count += 1
        if path.suffix != '.md':
            continue
        content = re.sub(r'(?ms)^```.*?^```[^\n]*\n?', '', raw.decode())
        for match in re.finditer(r'!?\[[^\]]*\]\(([^)]+)\)', content):
            target = urlsplit(match[1].strip('<>'))
            if target.scheme:
                continue
            destination = (path.parent / unquote(target.path)).resolve() if target.path else path
            assert destination.exists(), (name, match[1])
            if target.fragment and destination.suffix == '.md':
                assert unquote(target.fragment) in anchors(destination), (name, match[1])
            links += 1
    assert BASE in (ROOT / INDEX).read_text()
    assert 'plan-check-2026-10-07-04.md' in (ROOT / INDEX).read_text()
    subprocess.run(['git', 'diff', '--check', BASE], cwd=ROOT, check=True)
    print(f'PASS scoped docs/evidence, {links} local links/anchors, {json_count} JSONs, LF/whitespace')

    discovery = json.loads((EVIDENCE / 'profile-discovery.json').read_text())
    assert discovery['profiles']['profiles'] == []
    models = {m['id']: m for m in discovery['models']['models']}
    declarations = {p['selectedModel']: p for p in discovery['inspections']}
    proposal = json.loads((ROOT / 'docs/workflows/p0-profiles-evidence/proposed.patch.json').read_text())
    profiles = proposal['agentProfiles']
    assert len(profiles) == len({p['id'] for p in profiles}) == 4
    assert [(p['model'], p['thinkingOptionId']) for p in profiles] == [
        ('gpt-6.1-sol', 'medium'), ('gpt-6.1-sol', 'high'),
        ('gpt-6-luna', 'high'), ('gpt-6-astra', 'high')]
    for profile in profiles:
        declaration = declarations[profile['model']]
        assert profile['thinkingOptionId'] in {o['id'] for o in models[profile['model']]['thinkingOptions']}
        assert profile['modeId'] == 'auto-review'
        assert profile['modeId'] in {m['id'] for m in declaration['modes']}
        assert set(profile['featureValues']) <= {f['id'] for f in declaration['features']}
        assert all(value is False for value in profile['featureValues'].values())
        assert profile['notes'].strip()
    installed = manifest['installed_declarations']
    for source in installed['source_hashes']:
        raw = (Path(installed['source_root']) / source['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == source['sha256'], source['path']
    print('PASS empty inventory; 4 inert proposals match fresh support declarations; 8 source hashes')
    print('No effective profile launch/capability, runtime/engine/network/device proof claimed')
    print('Status including untracked:', git('status', '--porcelain=v1', '-uall') or 'clean')


if __name__ == '__main__':
    main()
