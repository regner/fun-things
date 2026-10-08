#!/usr/bin/env python3
"""Package selected source evidence without fetching or repeating earlier experiments."""
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
from extract import ROOT, SCRATCH, PRIOR

# Original line numbers in immutable public headers, or reproducibly extracted doc text.
RANGES = {
    'sockets.h': [(91, 168), (193, 219), (361, 384), (489, 582), (818, 825), (983, 1053)],
    'types.h': [(660, 725), (737, 833), (956, 1029), (1153, 1198), (1200, 1233), (1280, 1303), (1539, 1576)],
    'sdk-api.text': [(14, 112), (169, 183)],
    'matchmaking.text': [(62, 73), (205, 220), (229, 255), (325, 340), (351, 405), (429, 464), (471, 477)],
    'steam-utils.text': [(28, 57), (234, 243), (391, 397), (430, 438)],
    'friends.text': [(12, 18), (356, 366), (961, 977)],
    'sdr.text': [(1, 25)],
    'sockets.text': [(1, 10)],
    'messages.text': [(1, 67)],
    'utils.text': [(1, 20)],
    'types.text': [(1, 5)],
}


def sha(data):
    """Return the exact-byte SHA-256 digest."""
    return hashlib.sha256(data).hexdigest()


def excerpt(data, ranges):
    """Number original lines, preserving their text and endings exactly."""
    lines = data.splitlines(keepends=True)
    assert all(1 <= a <= b <= len(lines) for a, b in ranges)
    return b''.join(f'{i}: '.encode() + lines[i - 1]
                    for a, b in ranges for i in range(a, b + 1))


def main():
    """Save immutable files and numbered excerpts with raw and stored hashes separated."""
    (ROOT / 'sources').mkdir(exist_ok=True)
    retrieval = {r['name']: r for r in json.loads((ROOT / 'retrieval.json').read_text())}
    records = []
    for name in ('api-common.h', 'messages.h', 'utils.h', 'gns-readme.md', 'license', *RANGES):
        if name in ('sockets.h', 'types.h'):
            filename = {'sockets.h': 'isteamnetworkingsockets.h', 'types.h': 'steamnetworkingtypes.h'}[name]
            data = (PRIOR / filename).read_bytes()
            old = json.loads((ROOT.parent / 's03-s-upstream-peer-evidence/sources.json').read_text())
            record = next(r.copy() for r in old['files'] if r['candidate'] == 'valve' and r['path'].endswith(filename))
            assert len(data) == record['bytes'] and sha(data) == record['sha256']
            record = {k: record[k] for k in ('url', 'bytes', 'sha256')}
            record['origin'] = 'Accepted evidence 57d337312bb6f98a22e8d94a41eace3b9e7cc50b; original 2026-10-08 retrieval, local verified source readback; no refetch'
        else:
            raw_name = name.replace('.text', '.html')
            record = retrieval[raw_name].copy()
            assert record['exit'] == 0
            raw = (SCRATCH / raw_name).read_bytes()
            assert len(raw) == record['bytes'] and sha(raw) == record['sha256']
            data = (SCRATCH / name).read_bytes()
            if name.endswith('.text'):
                record.update(extraction='extract.py DocText; not original HTML bytes',
                              extracted_bytes=len(data), extracted_sha256=sha(data))
        saved = excerpt(data, RANGES[name]) if name in RANGES else data
        path = 'sources/' + name + '.txt'
        (ROOT / path).write_bytes(saved)
        record.update(key=name, stored_path=path, stored_bytes=len(saved), stored_sha256=sha(saved),
                      stored_kind='numbered excerpts' if name in RANGES else 'complete exact bytes')
        if name in RANGES:
            record['line_ranges'] = RANGES[name]
        records.append(record)
    (ROOT / 'sources.json').write_text(json.dumps(records, indent=2) + '\n')
    print('Packaged', len(records), 'source records')


if __name__ == '__main__':
    main()
