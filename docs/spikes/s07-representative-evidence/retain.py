#!/usr/bin/env python3
"""Retain new static receipts only, with a declared expected set and exact readback."""
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
DIR = ROOT / 'docs/spikes/s07-representative-evidence'
OUT = Path('/tmp/s07-representative-preparation')
BASE = '244089785b0d106451160acd89859c6977d30956'
REPO_SET = [
    'docs/spikes/s07-representative-preparation.md',
    'docs/spikes/s07.md', 'docs/plans/task-requirements.md',
    *[f'docs/spikes/s07-representative-evidence/{p}' for p in [
        '.gdignore', 'README.md', 'check.py', 'retain.py', 'references.json',
        'raw-requirements.md', 'launch.json']],
]
REVIEW_SET = ['report.md', 'check.py', 'commands.json', 'stdout', 'stderr', 'effective.json']
ATTEMPT_SET = ['source.py', 'command.json', 'stdout', 'stderr']


def fp(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def check(label):
    assert label.startswith('static-') and '/' not in label
    target = OUT / 'lead' / label
    target.mkdir(parents=True, exist_ok=False)
    source = DIR / 'check.py'
    (target / 'source.py').write_bytes(source.read_bytes())
    argv = ['python3', str(source.relative_to(ROOT))]
    result = subprocess.run(argv, cwd=ROOT, capture_output=True)
    (target / 'stdout').write_bytes(result.stdout)
    (target / 'stderr').write_bytes(result.stderr)
    (target / 'command.json').write_text(json.dumps({
        'argv': argv, 'cwd': str(ROOT), 'exit': result.returncode,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'source': fp(source.read_bytes()),
        'stdout': fp(result.stdout), 'stderr': fp(result.stderr)}, indent=2) + '\n')
    sys.stdout.buffer.write(result.stdout)
    sys.stderr.buffer.write(result.stderr)
    return result.returncode


def discovery():
    # Preserve actual combined tool outputs; never manufacture separate streams/exits.
    calls = {}
    failures = []
    for line in Path(os.environ['PI_SESSION_FILE']).read_text().splitlines():
        row = json.loads(line)
        msg = row.get('message', {})
        if msg.get('role') == 'assistant':
            for block in msg.get('content', []):
                if block.get('type') == 'toolCall':
                    calls[block['id']] = block
        if msg.get('role') == 'toolResult':
            text = '\n'.join(x.get('text', '') for x in msg.get('content', [])
                             if x.get('type') == 'text')
            if ('ENOENT' in text or 'Command exited with code 2' in text
                    or 'Script failed' in text or msg.get('isError')):
                failures.append({'request': calls.get(msg['toolCallId']),
                                 'actual_tool_result': msg,
                                 'timestamp': row.get('timestamp')})
    (OUT / 'discovery-errors.json').write_text(json.dumps({
        'cwd': str(ROOT), 'failures': failures,
        'scope': 'Actual new retrieval/check tool errors; combined streams as returned.'},
        indent=2) + '\n')
    print('retained actual retrieval/tool failure receipts:', len(failures))


def package(attempts, final_review):
    head = git('rev-parse', 'HEAD').decode().strip()
    assert git('status', '--porcelain=v1', '--untracked-files=all') == b'', 'candidate not clean'
    # Expected paths declared from contracts/attempt arguments BEFORE reading payloads.
    sources = {f'repo/{p}': ROOT / p for p in REPO_SET}
    for label in attempts:
        for name in ATTEMPT_SET:
            sources[f'lead/{label}/{name}'] = OUT / 'lead' / label / name
    for name in REVIEW_SET:
        sources[f'review/initial/{name}'] = OUT / 'review' / 'initial' / name
    if final_review:
        for name in REVIEW_SET:
            sources[f'review/final/{name}'] = OUT / 'review' / 'final' / name
    for name in ['discovery-errors.json', 'review-launch.json', 'review-settings-readback.json',
                 'handoff.json']:
        sources[name] = OUT / name
    for label in attempts:
        assert {p.name for p in (OUT / 'lead' / label).iterdir()} == set(ATTEMPT_SET)
    for phase in ['initial'] + (['final'] if final_review else []):
        assert {p.name for p in (OUT / 'review' / phase).iterdir()} == set(REVIEW_SET)
    expected = sorted(sources)
    payloads = {}
    required_empty = []
    for key in expected:
        data = sources[key].read_bytes()
        payloads[key] = {**fp(data), 'encoding': 'base64',
                         'data': base64.b64encode(data).decode()}
        if not data:
            required_empty.append(key)
    envelope = {'schema': 1, 'kind': 'S07 source-only representative preparation',
                'head': head, 'base': BASE, 'expected_paths': expected,
                'required_empty': required_empty,
                'expected_set_sha256': fp(('\n'.join(expected) + '\n').encode())['sha256'],
                'payloads': payloads,
                'historical_references': 'repo/docs/spikes/s07-representative-evidence/references.json',
                'limitations': 'Static planning only; S07/T/R/G/P0/M1 remain OPEN; no runtime/S08 grant.'}
    data = (json.dumps(envelope, indent=2) + '\n').encode()
    destination = OUT / 'envelope.json'
    destination.write_bytes(data)
    existing = subprocess.run(['git', 'notes', '--ref=paseo-orchestration', 'show', head],
                              cwd=ROOT, capture_output=True)
    assert existing.returncode != 0, 'existing candidate note must not be overwritten'
    subprocess.run(['git', 'notes', '--ref=paseo-orchestration', 'add', '-F',
                    str(destination), head], cwd=ROOT, check=True)
    blob = git('notes', '--ref=paseo-orchestration', 'list', head).decode().split()[0]
    stored = git('cat-file', 'blob', blob)
    assert stored == data, 'stored envelope differs from source'
    readback = json.loads(stored)
    assert readback['expected_paths'] == expected
    assert set(readback['payloads']) == set(expected)
    for key in expected:
        actual = base64.b64decode(readback['payloads'][key]['data'], validate=True)
        assert actual == sources[key].read_bytes(), ('source/readback differs', key)
        assert fp(actual) == {k: readback['payloads'][key][k] for k in ['bytes', 'sha256']}
    for key in required_empty:
        assert readback['payloads'][key]['bytes'] == 0
    receipt = {'result': 'PASS', 'head': head, 'base': BASE,
               'note_ref': 'refs/notes/paseo-orchestration', 'blob': blob,
               'envelope': fp(data), 'stored': fp(stored),
               'expected_set_sha256': envelope['expected_set_sha256'],
               'paths': len(expected), 'required_empty_streams': required_empty,
               'source/stored/decoded_readback': 'exact equality',
               'git_status': git('status', '--porcelain=v1', '--untracked-files=all').decode()}
    (OUT / 'readback.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    if sys.argv[1] == 'check':
        sys.exit(check(sys.argv[2]))
    elif sys.argv[1] == 'discovery':
        discovery()
    elif sys.argv[1] == 'package':
        package(sys.argv[2].split(','), sys.argv[3] == 'final-review')
    else:
        raise ValueError('check, discovery or package expected')
