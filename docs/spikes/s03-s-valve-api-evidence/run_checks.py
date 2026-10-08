#!/usr/bin/env python3
"""Run the fixed static delivery checks once, preserving complete streams and exits."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
BASE = '233493abc7d2e3c106fb620105cfb766f542813b'
PLAN = [
    ('source-readback', ['python3', str(ROOT.relative_to(REPO) / 'check.py'), '--source-readback']),
    ('offline-static', ['python3', str(ROOT.relative_to(REPO) / 'check.py')]),
    ('whitespace', ['git', 'diff', '--check', BASE]),
]


def main():
    """Predeclare expected output paths, then record each unfiltered subprocess."""
    directory = ROOT / 'checks'
    directory.mkdir(exist_ok=True)
    assert not (directory / 'commands.json').exists(), 'Never overwrite an earlier run'
    for name, _ in PLAN:
        for suffix in ('stdout', 'stderr'):
            (directory / (name + '.' + suffix)).write_bytes(b'')
    records = []
    (directory / 'commands.json').write_text('[]\n')
    for name, argv in PLAN:
        result = subprocess.run(argv, cwd=REPO, capture_output=True)
        (directory / (name + '.stdout')).write_bytes(result.stdout)
        (directory / (name + '.stderr')).write_bytes(result.stderr)
        records.append({'name': name, 'argv': argv, 'cwd': str(REPO),
                        'utc': datetime.now(timezone.utc).isoformat(), 'exit': result.returncode,
                        'stdout': name + '.stdout', 'stderr': name + '.stderr'})
        (directory / 'commands.json').write_text(json.dumps(records, indent=2) + '\n')
        print(name, 'exit', result.returncode)
    assert all(r['exit'] == 0 for r in records), 'Retained failures require correction'


if __name__ == '__main__':
    main()
