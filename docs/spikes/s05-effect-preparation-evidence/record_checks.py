"""Retain exact non-editor check argv, full raw streams and exits."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
records = []
for script in ('check_glb.py', 'inspect_isolation.py'):
    label = script.removesuffix('.py')
    argv = [sys.executable, str(HERE / script)]
    with (HERE / (label + '.stdout')).open('wb') as out, \
         (HERE / (label + '.stderr')).open('wb') as err:
        result = subprocess.run(argv, cwd=ROOT, stdout=out, stderr=err, timeout=30, check=False)
    records.append(dict(argv=argv, cwd=str(ROOT), timeout_s=30, exit_code=result.returncode))
    (HERE / 'check-commands.json').write_text(json.dumps(records, indent=2) + '\n')
    assert result.returncode == 0, label
    print(label, 'PASS')
