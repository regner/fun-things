#!/usr/bin/env python3
"""Call the installed standard Godot bridge for this private worktree only.

Usage: python tools/brackett_greybox/editor_call.py requests.json
Requires the private editor/registry under /tmp/brackett-greybox, never shared config.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SESSION = Path('/tmp/brackett-greybox')


def main():
    """Verify project/process binding before passing a finite request batch to MCP."""
    entries = list((SESSION/'data/godot-mcp-toolkit/entries').glob('*.json'))
    entry = next(json.loads(p.read_text()) for p in entries if json.loads(p.read_text())['_key'] == str(ROOT))
    pid = int(entry['pid'])
    command = Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
    assert str(ROOT).encode() in command and b'--editor' in command
    assert entry['port'] == 16650 and entry['token_path'].startswith(str(SESSION/'data')+'/')
    binding = SESSION/'binding.json'
    binding.write_text(json.dumps(entry))
    env = os.environ.copy()
    for key in list(env):
        if key.startswith('GODOT_MCP_'):
            del env[key]
    env.update(XDG_CONFIG_HOME=str(SESSION/'config'), XDG_DATA_HOME=str(SESSION/'data'),
               XDG_CACHE_HOME=str(SESSION/'cache'), GODOT_MCP_PROJECT_PATH=str(ROOT))
    requests = json.loads(Path(sys.argv[1]).read_text())
    result = subprocess.run(['/usr/bin/node', str(ROOT/'tools/s08/standard_bridge.mjs'), str(binding)],
                            input=''.join(json.dumps(r)+'\n' for r in requests), text=True,
                            cwd=ROOT, env=env, capture_output=True, timeout=180)
    print(result.stdout)
    print(result.stderr, file=sys.stderr)
    result.check_returncode()
    for line in result.stdout.splitlines()[1:]:
        response = json.loads(line)
        assert 'error' not in response and response.get('result', {}).get('success') is not False, response


if __name__ == '__main__':
    main()
