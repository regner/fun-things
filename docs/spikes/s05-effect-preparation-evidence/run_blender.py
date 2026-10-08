"""Bounded source preparation; record and reap only subprocess handles we create."""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'art/source/models/spikes/s05_explosion_carrier.blend'
EXPORT = ROOT / 'art/models/spikes/s05_explosion_carrier.glb'
assert not SOURCE.exists() and not EXPORT.exists(), 'Bootstrap is new-only'
binary = Path(shutil.which('blender')).resolve()
scratch = Path(tempfile.mkdtemp(prefix='s05-source-preparation-'))
commands = []
environment = os.environ.copy()
private = {'ALSOFT_DRIVERS': 'null', 'XDG_CACHE_HOME': str(scratch / 'cache'),
           'BLENDER_USER_CONFIG': str(scratch / 'config')}
environment.update(private)
for folder in ('cache', 'config'):
    (scratch / folder).mkdir()


def run(label, arguments):
    """Retain raw streams and termination details for this exact owned child."""
    argv = [str(binary), *arguments]
    record = dict(label=label, argv=argv, cwd=str(ROOT), env_overrides=private,
                  timeout_s=45, termination=[], started_unix=time.time())
    with (HERE / (label + '.stdout')).open('wb') as stdout, \
         (HERE / (label + '.stderr')).open('wb') as stderr:
        process = subprocess.Popen(argv, cwd=ROOT, env=environment, stdout=stdout, stderr=stderr)
        record['owned_pid'] = process.pid
        try:
            record['exit_code'] = process.wait(timeout=45)
        except subprocess.TimeoutExpired:
            record['termination'].append('owned-handle terminate after45s')
            process.terminate()
            try:
                record['exit_code'] = process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                record['termination'].append('owned-handle kill after5s grace')
                process.kill()
                record['exit_code'] = process.wait(timeout=5)
    record['reaped'] = process.poll() is not None
    record['ended_unix'] = time.time()
    commands.append(record)
    (HERE / 'commands.json').write_text(json.dumps(dict(scratch=str(scratch), commands=commands),
                                                indent=2) + '\n')
    print(label, record['exit_code'], record['termination'], flush=True)
    assert record['exit_code'] == 0 and not record['termination'], record


run('version', ['--version'])
base = ['--background', '--factory-startup', '--python-exit-code', '1']
run('author', [*base, '--python', str(HERE / 'author.py')])
run('source-probe', [*base, str(SOURCE), '--python', str(HERE / 'source_probe.py'),
                     '--', str(HERE / 'source-probe.json')])
first = scratch / 'first.glb'
run('export', [*base, str(SOURCE), '--python', str(HERE / 'export.py'), '--', str(first)])
second = scratch / 'reopen.glb'
run('reopen-export', [*base, str(SOURCE), '--python', str(HERE / 'export.py'), '--', str(second)])
run('reopen-probe', [*base, str(SOURCE), '--python', str(HERE / 'source_probe.py'),
                     '--', str(HERE / 'reopen-probe.json')])
assert (HERE / 'source-probe.json').read_bytes() == (HERE / 'reopen-probe.json').read_bytes()
assert first.read_bytes() == second.read_bytes(), 'Saved-source reexport must be byte-identical'
shutil.copyfile(first, EXPORT)
receipt = dict(source=str(SOURCE.relative_to(ROOT)), export=str(EXPORT.relative_to(ROOT)),
               source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               export_sha256=hashlib.sha256(EXPORT.read_bytes()).hexdigest(),
               source_bytes=SOURCE.stat().st_size, export_bytes=EXPORT.stat().st_size,
               reopened_source_equal=True, reexport_byte_equal=True,
               binary=str(binary), binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
               all_owned_children_reaped=all(c['reaped'] for c in commands), checks='PASS')
(HERE / 'fingerprints.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, sort_keys=True))
