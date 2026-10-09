"""Retain exact private editor batch argv, requests, responses and exit status."""
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/assets/production/batch_03-evidence/transport'
label = sys.argv[1]
requests = Path(sys.argv[2]).resolve()
retained = OUT / f'{label}-requests.json'
retained.write_bytes(requests.read_bytes())
argv = ['node', str(ROOT / 'tools/asset_production/integration/editor_client.mjs'), str(requests)]
if '--runtime' in sys.argv:
    argv.append('--runtime')
started = time.time()
with (OUT / f'{label}-results.jsonl').open('w') as stdout, (OUT / f'{label}-stderr.log').open('w') as stderr:
    result = subprocess.run(argv, cwd=ROOT, stdout=stdout, stderr=stderr)
(OUT / f'{label}-execution.json').write_text(json.dumps({'argv': argv, 'cwd': str(ROOT),
    'exit_code': result.returncode, 'elapsed_s': time.time() - started}, indent=2) + '\n')
sys.exit(result.returncode)
