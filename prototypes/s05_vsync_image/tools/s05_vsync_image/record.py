#!/usr/bin/env python3
"""Retain complete command receipts and separate streams, including unsuccessful checks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def main():
    """Capture one explicit command without filtering diagnostics or inventing empty streams."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    args.directory.mkdir(parents=True, exist_ok=True)
    prefix = args.directory / args.name
    assert not prefix.with_suffix('.command.json').exists(), 'receipt names are immutable'
    start = time.time()
    with Path(str(prefix) + '.stdout').open('wb') as out, Path(str(prefix) + '.stderr').open('wb') as err:
        child = subprocess.Popen(command, stdout=out, stderr=err)
        pid = child.pid
        exit_code = child.wait()
    receipt = {'argv': command, 'cwd': os.getcwd(), 'wrapper_pid': os.getpid(),
               'owned_command_pid': pid, 'start_unix': start, 'end_unix': time.time(),
               'exit': exit_code, 'streams_closed': True, 'owned_command_reaped': True}
    receipt['sources'] = {arg: {'bytes': len(Path(arg).read_bytes()),
        'sha256': hashlib.sha256(Path(arg).read_bytes()).hexdigest()} for arg in command
        if Path(arg).is_file()}
    Path(str(prefix) + '.command.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
