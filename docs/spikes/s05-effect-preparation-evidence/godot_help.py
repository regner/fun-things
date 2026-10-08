"""Root-authorized <=5s nongraphical --help capability call; no editor or project arguments."""
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
private = Path(tempfile.mkdtemp(prefix='s05-godot-help-'))
private.chmod(0o700)
overrides = {}
for variable, name in (('XDG_DATA_HOME', 'data'), ('XDG_CONFIG_HOME', 'config'),
                       ('XDG_CACHE_HOME', 'cache')):
    directory = private / name
    directory.mkdir(mode=0o700)
    overrides[variable] = str(directory)
environment = os.environ.copy()
environment.update(overrides)
argv = ['/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot',
        '--help']
record = dict(argv=argv, cwd=str(private), env_overrides=overrides, timeout_s=5,
              termination=[], started_unix=time.time(), editor_launched=False, project_loaded=False)
with (HERE / 'godot-help.stdout').open('wb') as out, \
     (HERE / 'godot-help.stderr').open('wb') as err:
    child = subprocess.Popen(argv, cwd=private, env=environment, stdout=out, stderr=err)
    record['owned_pid'] = child.pid
    try:
        record['exit_code'] = child.wait(timeout=5)
    except subprocess.TimeoutExpired:
        record['termination'].append('owned-handle terminate after5s cap')
        child.terminate()
        try:
            record['exit_code'] = child.wait(timeout=1)
        except subprocess.TimeoutExpired:
            record['termination'].append('owned-handle kill after1s grace')
            child.kill()
            record['exit_code'] = child.wait(timeout=1)
record.update(reaped=child.poll() is not None, ended_unix=time.time(),
              private_files=[str(p.relative_to(private)) for p in sorted(private.rglob('*'))
                             if p.is_file()])
(HERE / 'godot-help-command.json').write_text(json.dumps(record, indent=2) + '\n')
assert record['exit_code'] == 0 and not record['termination']
print(json.dumps(record, sort_keys=True))
