"""Recheck saved source/export with every Blender user path private; keep initial logs."""
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
source = ROOT / 'art/source/models/spikes/s05_explosion_carrier.blend'
scratch = Path(tempfile.mkdtemp(prefix='s05-private-blender-check-'))
overrides = {'ALSOFT_DRIVERS': 'null'}
for key in ('BLENDER_USER_RESOURCES', 'BLENDER_USER_CONFIG', 'BLENDER_USER_EXTENSIONS',
            'BLENDER_USER_SCRIPTS', 'BLENDER_USER_DATAFILES',
            'XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_CACHE_HOME'):
    directory = scratch / key.lower()
    directory.mkdir()
    overrides[key] = str(directory)
env = os.environ.copy()
env.update(overrides)
commands = []
base = ['/usr/bin/blender', '--background', '--factory-startup', '--python-exit-code', '1']
operations = [
    ('private-help', ['/usr/bin/blender', '--help']),
    ('private-probe', [*base, str(source), '--python', str(HERE / 'source_probe.py'),
                       '--', str(HERE / 'private-probe.json')]),
    ('private-export', [*base, str(source), '--python', str(HERE / 'export.py'),
                        '--', str(scratch / 'private.glb')]),
]
for label, argv in operations:
    record = dict(label=label, argv=argv, env_overrides=overrides, timeout_s=45, termination=[])
    with (HERE / (label + '.stdout')).open('wb') as out, \
         (HERE / (label + '.stderr')).open('wb') as err:
        child = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=out, stderr=err)
        record['owned_pid'] = child.pid
        try:
            record['exit_code'] = child.wait(timeout=45)
        except subprocess.TimeoutExpired:
            child.terminate()
            record['termination'].append('owned-handle terminate after45s')
            try:
                record['exit_code'] = child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                record['termination'].append('owned-handle kill after5s grace')
                record['exit_code'] = child.wait(timeout=5)
    record['reaped'] = child.poll() is not None
    commands.append(record)
    (HERE / 'private-commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    assert record['exit_code'] == 0 and not record['termination']
    assert b'writing cache failed' not in (HERE / (label + '.stdout')).read_bytes()
assert (HERE / 'private-probe.json').read_bytes() == (HERE / 'source-probe.json').read_bytes()
assert (scratch / 'private.glb').read_bytes() == \
       (ROOT / 'art/models/spikes/s05_explosion_carrier.glb').read_bytes()
receipt = dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
               export_sha256=hashlib.sha256((scratch / 'private.glb').read_bytes()).hexdigest(),
               probe_byte_equal=True, export_byte_equal=True,
               all_owned_children_reaped=all(c['reaped'] for c in commands), checks='PASS')
(HERE / 'private-check.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, sort_keys=True))
