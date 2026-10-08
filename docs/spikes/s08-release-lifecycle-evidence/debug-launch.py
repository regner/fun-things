#!/usr/bin/env python3
"""Retain the sole commissioned debug diagnostic invocation and complete supervisor streams."""
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
CONTROL = Path('/tmp/s08-lifecycle-control')
ARGV = ['python3', 'tools/s08/lifecycle_diagnostic.py', '--output',
        '/tmp/s08-lifecycle-debug01', '--revision',
        'f178c70efb657ea9fba5951d9440c23c761aea31', '--author-project',
        '/tmp/s08-lifecycle-author/state/project']


def main():
    """Launch once, without retry, and bind the full aggregate elapsed time."""
    started = time.monotonic()
    command = {'argv': ARGV, 'cwd': str(ROOT), 'start_monotonic': started}
    (CONTROL / 'debug-supervisor.command.json').write_text(json.dumps(command) + '\n')
    with (CONTROL / 'debug-supervisor.stdout').open('wb') as out:
        with (CONTROL / 'debug-supervisor.stderr').open('wb') as err:
            result = subprocess.run(ARGV, cwd=ROOT, stdout=out, stderr=err)
    command.update(exit=result.returncode, end_monotonic=time.monotonic())
    command['aggregate_seconds'] = command['end_monotonic'] - started
    command['within_30s'] = command['aggregate_seconds'] <= 30
    (CONTROL / 'debug-supervisor.command.json').write_text(json.dumps(command, indent=2) + '\n')
    print(json.dumps(command))
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
