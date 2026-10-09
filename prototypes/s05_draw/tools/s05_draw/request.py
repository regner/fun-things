#!/usr/bin/env python3
"""Send one sequenced request to the owned private SDK supervisor."""
import argparse
import json
from pathlib import Path
import time


def main():
    """Write an atomic request and retain the full response, including tool errors."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument('name')
    parser.add_argument('args', nargs='?', default='{}')
    args = parser.parse_args()
    requests = args.log / 'requests'
    index = len(list(requests.glob('*.json'))) + 1
    target = requests / f'{index:03d}.json'
    temporary = requests / f'{index:03d}.tmp'
    request = {'finish': True} if args.name == 'finish' else {
        'name': args.name, 'args': json.loads(args.args)}
    temporary.write_text(json.dumps(request) + '\n')
    temporary.rename(target)
    if args.name == 'finish':
        return 0
    deadline = time.monotonic() + 40
    response = args.log / 'responses' / target.name
    while time.monotonic() < deadline:
        if response.exists():
            value = json.loads(response.read_text())
            print(json.dumps(value))
            return 1 if value.get('isError') else 0
        time.sleep(.05)
    raise TimeoutError('owned SDK response40s deadline')


if __name__ == '__main__':
    raise SystemExit(main())
