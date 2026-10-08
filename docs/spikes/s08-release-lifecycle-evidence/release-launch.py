#!/usr/bin/env python3
"""Retain the second and final commissioned release diagnostic invocation, without retry."""
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
CONTROL = Path('/tmp/s08-lifecycle-control')
ARGV = ['python3', 'tools/s08/lifecycle_diagnostic.py', '--output',
        '/tmp/s08-lifecycle-release-set02', '--revision',
        'a5756b4b6126a5c9756de981b39fdadc35f3c8fe', '--author-project',
        '/tmp/s08-lifecycle-author/state/project', '--release-bundle',
        '/tmp/s08-lifecycle-release01', '--release-pck-sha256',
        '43cc8236fcb7a06f328c28cf45fed752d6630e1699ebea04e68e34d9aa40e3d7']


def main():
    """Capture complete supervisor streams and the stricter combined diagnostic elapsed cap."""
    started = time.monotonic()
    command = {'argv': ARGV, 'cwd': str(ROOT), 'start_monotonic': started}
    (CONTROL / 'release-supervisor.command.json').write_text(json.dumps(command) + '\n')
    with (CONTROL / 'release-supervisor.stdout').open('wb') as out:
        with (CONTROL / 'release-supervisor.stderr').open('wb') as err:
            result = subprocess.run(ARGV, cwd=ROOT, stdout=out, stderr=err)
    command.update(exit=result.returncode, end_monotonic=time.monotonic())
    command['aggregate_seconds'] = command['end_monotonic'] - started
    command['within_27s'] = command['aggregate_seconds'] <= 27
    command['combined_seconds'] = 2.630392014994868 + command['aggregate_seconds']
    command['combined_within_30s'] = command['combined_seconds'] <= 30
    (CONTROL / 'release-supervisor.command.json').write_text(json.dumps(command, indent=2) + '\n')
    print(json.dumps(command))
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
