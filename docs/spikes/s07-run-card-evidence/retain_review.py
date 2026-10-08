#!/usr/bin/env python3
"""Retain a complete reviewer package and verify every archived byte against its source."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

FOLDER = Path(__file__).resolve().parent


def main():
    """Require explicit source set/hash equality, then archive and decode/read back all files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('name')
    args = parser.parse_args()
    assert args.name in ('review-initial', 'review-final')
    source = args.source.resolve()
    expected = json.loads((source / 'expected-set.json').read_text())
    manifest = json.loads((source / 'manifest.json').read_text())
    assert len(expected) == len(set(expected))
    assert set(manifest['payloads']) == set(expected)
    actual = {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()}
    assert actual == set(expected) | {'manifest.json'}, ('review set mismatch', actual)
    data = {}
    for path in sorted(actual):
        assert not Path(path).is_absolute() and '..' not in Path(path).parts
        data[path] = (source / path).read_bytes()
        if path != 'manifest.json':
            row = manifest['payloads'][path]
            assert len(data[path]) == row['bytes'], path
            assert hashlib.sha256(data[path]).hexdigest() == row['sha256'], path
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w') as archive:
        for path, content in data.items():
            info = tarfile.TarInfo(path)
            info.size = len(content)
            info.mode = 0o644
            archive.addfile(info, io.BytesIO(content))
    output = FOLDER / (args.name + '.tar.gz')
    assert not output.exists(), 'preserve prior review archives'
    output.write_bytes(gzip.compress(stream.getvalue(), mtime=0))
    decoded = gzip.decompress(output.read_bytes())
    with tarfile.open(fileobj=io.BytesIO(decoded), mode='r:') as archive:
        members = archive.getmembers()
        assert len(members) == len(actual) and {m.name for m in members} == actual
        for member in members:
            assert archive.extractfile(member).read() == data[member.name], member.name
    receipt = {'source_directory': str(source), 'payloads': len(expected),
               'archived_files_including_source_manifest': len(actual),
               'complete_expected_set_hash_source_decode_readback': True,
               'archive_bytes': output.stat().st_size,
               'archive_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
               'source_files': {p: {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}
                                for p, b in data.items()}}
    (FOLDER / (args.name + '-package.json')).write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(f'PASS {args.name}: {len(expected)} payloads plus original manifest; '
          'complete source/set/hash/archive decode/readback')


if __name__ == '__main__':
    main()
