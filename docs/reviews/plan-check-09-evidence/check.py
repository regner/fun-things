#!/usr/bin/env python3
"""Static checkpoint scope/range/task/link/JSON/source-reference checks; no runtime imports."""
import ast
import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path

BASE = '2d5457250701ebf93ef6e90f0e82ec9f384fd530'
LOWER = '122978243dba25b3fb5d8d90fc50ffb1a468ecf5'
EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[2]
RECORD = ROOT / 'docs/reviews/plan-check-2026-10-08-09.md'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, f'duplicate JSON key: {key}'
        result[key] = value
    return result


def parse(data):
    return json.loads(data, object_pairs_hook=unique)


def headings(path):
    text = path.read_text()
    result = set()
    counts = {}
    for heading in re.findall(r'^#{1,6}\s+(.+)$', text, re.M):
        heading = re.sub(r'<[^>]+>', '', heading).lower()
        heading = re.sub(r'[^\w\- ]', '', heading).replace(' ', '-')
        count = counts.get(heading, 0)
        counts[heading] = count + 1
        result.add(heading + (f'-{count}' if count else ''))
    return result


def main():
    assert git('rev-parse', 'HEAD').decode().strip() != LOWER
    subprocess.run(['git', 'merge-base', '--is-ancestor', LOWER, BASE], cwd=ROOT, check=True)
    ledger = parse(gzip.decompress((EVIDENCE / 'accepted-ledger.json.gz').read_bytes()))
    assert ledger['lower_exclusive'] == LOWER and ledger['upper_inclusive'] == BASE
    commits = git('rev-list', '--reverse', f'{LOWER}..{BASE}').decode().splitlines()
    assert len(commits) == ledger['linear_commit_count'] == 69
    previous = LOWER
    for commit, row in zip(commits, ledger['commits'], strict=True):
        assert commit == row['commit']
        assert row['parents'] == git('show', '-s', '--format=%P', commit).decode().split() == [previous]
        paths = git('diff-tree', '--no-commit-id', '--name-status', '-r', commit).decode().splitlines()
        assert paths == row['paths']
        previous = commit
    note_count = report_count = 0
    for row in ledger['consulted_notes']:
        assert not row.get('note_absent'), row
        blob = git('cat-file', 'blob', row['blob'])
        assert len(blob) == row['bytes'] and sha(blob) == row['sha256']
        # These immutable objects retain full reports, not a fresh decode of every runtime archive.
        note_count += 1
        report_count += len(row['reports'])
    references = parse((EVIDENCE / 'references.json').read_bytes())
    for row in references['selected_files']:
        blob = git('show', f"{row['revision']}:{row['path']}")
        assert len(blob) == row['bytes'] and sha(blob) == row['sha256']
    for row in references['extra_git_objects']:
        data = git('cat-file', 'blob', row['blob'])
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
    old = git('show', f'{BASE}:TODO.md').decode()
    todo = (ROOT / 'TODO.md').read_text()
    added = '- [ ] **P0-DOC14 — Reconcile current foundation evidence discovery.**\n'
    assert todo == old.replace('\n\n## First milestone', '\n' + added + '\n## First milestone', 1)
    ids = re.findall(r'^- \[ \] \*\*([A-Z0-9-]+) —', todo, re.M)
    assert len(ids) == len(set(ids)) == 28
    old_ids = re.findall(r'^- \[ \] \*\*([A-Z0-9-]+) —', old, re.M)
    assert len(old_ids) == 27 and set(ids) == set(old_ids) | {'P0-DOC14'}
    rows = re.findall(r'^\| ([A-Z][A-Z0-9-]*)(?: \(new\))? \|', RECORD.read_text(), re.M)
    assert len(rows) == 28 and set(rows) == set(ids)
    assert len(todo.splitlines()) == 64 and max(map(len, todo.splitlines())) <= 100
    index = (ROOT / 'docs/plans/task-requirements.md').read_text()
    for task in ids:
        assert f'**{task}:**' in index
    blocks = re.split(r'(?=^- \[ \] \*\*)', todo, flags=re.M)[1:]
    graph = {}
    for block in blocks:
        task = re.search(r'\*\*([A-Z0-9-]+) —', block).group(1)
        deps = re.search(r'After: ([A-Z0-9, -]+)[.;]', block)
        graph[task] = deps.group(1).split(', ') if deps else []
        assert all(dep in ids for dep in graph[task])
    def visit(task, active):
        assert task not in active, f'cycle: {active} -> {task}'
        for dep in graph[task]:
            visit(dep, active | {task})
    for task in ids:
        visit(task, set())
    assert graph['P0-GATE'] == ['S02', 'S03-S', 'S03-R', 'S04', 'S05', 'S06', 'S07', 'S08']
    assert 'P0-PROFILES' not in graph['P0-GATE'] and graph['M1-C2'] == []
    assert graph['M1-C4'] == ['M1-A2'] and 'All M1 tasks follow P0-GATE.' in todo
    changed = git('diff', '--name-only', BASE).decode().splitlines()
    new = git('ls-files', '--others', '--exclude-standard').decode().splitlines()
    permitted = {'TODO.md', 'docs/plans/task-requirements.md', 'docs/reviews/plan-checkpoints.md',
                 'docs/reviews/plan-check-2026-10-08-09.md'}
    assert all(path in permitted or path.startswith('docs/reviews/plan-check-09-evidence/')
               for path in changed + new), changed + new
    authored = [ROOT / p for p in permitted if (ROOT / p).exists()]
    authored += [p for p in EVIDENCE.iterdir() if p.suffix in {'.md', '.json', '.py'}]
    links = 0
    for path in authored:
        data = path.read_bytes()
        assert b'\r' not in data and data.endswith(b'\n'), path
        assert all(line == line.rstrip() for line in data.splitlines()), path
        if path.suffix == '.json':
            parse(data)
        elif path.suffix == '.py':
            ast.parse(data)
        elif path.suffix == '.md':
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', data.decode()):
                if re.match(r'[a-z]+:', target):
                    continue
                name, _, anchor = target.partition('#')
                dest = (path.parent / name).resolve() if name else path
                assert dest.exists(), (path, target)
                if anchor and dest.suffix == '.md':
                    assert anchor in headings(dest), (path, target, headings(dest))
                links += 1
    print(json.dumps({'result': 'PASS', 'range_commits': 69, 'immutable_notes': note_count,
                      'report_selectors_available': report_count,
                      'selected_files': len(references['selected_files']),
                      'tasks_before': 27, 'tasks_after': 28, 'todo_lines': 64,
                      'explicit_edges': sum(map(len, graph.values())), 'local_links': links,
                      'scope': changed + new, 'runtime_experiments': 0}, indent=2))


if __name__ == '__main__':
    main()
