#!/usr/bin/env python3
"""Verify declared source evidence, links and exact research/TODO scope offline."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
sys.dont_write_bytecode = True
from extract import DocText, ROOT, SCRATCH, PRIOR
from snapshot import RANGES, excerpt

BASE = '3f5fb4067c5ce5fca721f54d42165a833e4c884c'
REPO = ROOT.parents[2]
DOC = ROOT.parent / 's03-s-valve-api-interface.md'
SOURCE_KEYS = {'api-common.h', 'messages.h', 'utils.h', 'gns-readme.md', 'license',
               'sockets.h', 'types.h', 'sdk-api.text', 'matchmaking.text',
               'steam-utils.text', 'friends.text', 'sdr.text', 'sockets.text',
               'messages.text', 'utils.text', 'types.text'}


def sha(data):
    """Compute exact stored-byte hash."""
    return hashlib.sha256(data).hexdigest()


def git(*args):
    """Read repository facts with checked Git subprocess output."""
    return subprocess.check_output(['git', *args], cwd=REPO)


def outside_task(data):
    """Remove just the owned S03-S block for byte-exact unrelated TODO comparison."""
    start = data.index(b'- [ ] **S03-S ')
    end = data.index(b'- [ ] **S03-R ', start)
    return data[:start] + data[end:]


def check(source_readback):
    """Check the independently declared path set and every original/stored identity."""
    expected = set(json.loads((ROOT / 'expected-set.json').read_text()))
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()}
    assert actual == expected, {'missing': sorted(expected - actual), 'extra': sorted(actual - expected)}
    records = json.loads((ROOT / 'sources.json').read_text())
    assert {r['key'] for r in records} == SOURCE_KEYS
    assert len(records) == len(SOURCE_KEYS)
    for record in records:
        saved = (ROOT / record['stored_path']).read_bytes()
        assert len(saved) == record['stored_bytes']
        assert sha(saved) == record['stored_sha256'], record['key']
        if not source_readback:
            continue
        key = record['key']
        if key in ('sockets.h', 'types.h'):
            filename = {'sockets.h': 'isteamnetworkingsockets.h', 'types.h': 'steamnetworkingtypes.h'}[key]
            original = (PRIOR / filename).read_bytes()
            content = original
        else:
            original = (SCRATCH / key.replace('.text', '.html')).read_bytes()
            content = original
            if key.endswith('.text'):
                parser = DocText()
                parser.feed(original.decode())
                content = parser.result().encode()
                assert len(content) == record['extracted_bytes']
                assert sha(content) == record['extracted_sha256']
        assert len(original) == record['bytes'] and sha(original) == record['sha256'], key
        assert (excerpt(content, RANGES[key]) if key in RANGES else content) == saved, key
    retrieval = json.loads((ROOT / 'retrieval.json').read_text())
    assert len(retrieval) == 14 and len({r['name'] for r in retrieval}) == 14
    assert all(r['exit'] == 0 for r in retrieval)
    for path in ROOT.rglob('*.json'):
        json.loads(path.read_text())
    for path in ROOT.glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    for path in (DOC, ROOT / 'README.md', REPO / 'TODO.md'):
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            if '://' in target or target.startswith('#'):
                continue
            assert (path.parent / target.split('#')[0]).exists(), (path, target)
    old = git('show', BASE + ':TODO.md')
    new = (REPO / 'TODO.md').read_bytes()
    old_phrase = b'S03-S upstream compatibility evidence; '
    new_phrase = (b'S03-S [public API/interface record](docs/spikes/s03-s-valve-api-interface.md), '
                  b'then separately commissioned native prerequisites; ')
    assert new.count(new_phrase) == old.count(old_phrase) == 1
    assert outside_task(new).replace(new_phrase, old_phrase) == outside_task(old)
    allowed_doc = str(DOC.relative_to(REPO))
    allowed_prefix = str(ROOT.relative_to(REPO)) + '/'
    changed = set(git('diff', '--name-only', BASE).decode().splitlines())
    changed.update(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
    assert all(p == 'TODO.md' or p == allowed_doc or p.startswith(allowed_prefix) for p in changed), changed
    assert git('rev-parse', '--abbrev-ref', 'HEAD').decode().strip() == 's03-s-valve-api-interface-research'
    git('merge-base', '--is-ancestor', BASE, 'HEAD')
    # Earlier headers are reference evidence, not SDK call-result declarations.
    assert b"it's a stub" in (ROOT / 'sources/api-common.h.txt').read_bytes()
    print(f'PASS: {len(expected)} expected paths; 16 source identities; 14 public retrieval records; '
          f'JSON/Python/links; exact scope and unrelated TODO preservation; '
          f'original-source readback={source_readback}')


def main():
    """Select optional scratch readback without network or native execution."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-readback', action='store_true')
    args = parser.parse_args()
    check(args.source_readback)


if __name__ == '__main__':
    main()
