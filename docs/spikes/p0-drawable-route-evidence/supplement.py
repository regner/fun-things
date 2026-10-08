"""Bind the installed binary and already accepted receipts without launching an engine."""
import gzip
import hashlib
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
BINARY = Path('/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot')


def identity(data):
    """Return exact byte count and content hash for a retained or immutable source."""
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def main():
    """Inspect only the declared binary and three reachable historical evidence payloads."""
    data = BINARY.read_bytes()
    record = {'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
              'binary': {'path': str(BINARY), **identity(data),
                         'strings_present': {flag: flag.encode() in data for flag in
                                             ['--disable-vsync', '--write-movie',
                                              'DisplayServerWayland']}},
              'exposed_tool_search': {'query': 'display Godot screenshot computer browser',
                                      'result': [], 'all_tools_surface_name_filter': []},
              'historical_refs': []}
    for name in ['group02/host/engine.log', 'group02/lifecycle.json',
                 'group02/client/engine.log']:
        source = 'docs/spikes/s05-render-observation-evidence/payloads/' + name + '.gz'
        stored = (REPO / source).read_bytes()
        decoded = gzip.decompress(stored)
        record['historical_refs'].append({'revision':
            '233493abc7d2e3c106fb620105cfb766f542813b', 'path': source,
            'stored': identity(stored), 'decoded': identity(decoded)})
    (ROOT / 'supplement.json').write_text(json.dumps(record, indent=2) + '\n')


if __name__ == '__main__':
    main()
