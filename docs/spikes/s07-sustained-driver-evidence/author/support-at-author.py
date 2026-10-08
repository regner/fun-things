"""Private staging and owned-handle receipts for the bounded S07 simulation driver."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
ENGINE = Path('/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot')
ENGINE_SHA = '6aea356032435e7af19dbfbf48dd20c5012a7dc1267eb8e92406f44e3584b5fd'


def save(path, value):
    """Persist complete JSON receipts before returning control."""
    path.write_text(json.dumps(value, indent=2) + '\n')


def identity(path):
    """Bind even empty streams to actual stored bytes."""
    data = path.read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def environment(output):
    """Create private XDG roots without changing HOME or inheriting Toolkit overrides."""
    env = {k: v for k, v in os.environ.items() if not k.startswith('GODOT_MCP_')}
    for key, name in [('XDG_CONFIG_HOME', 'config'), ('XDG_DATA_HOME', 'data'),
                      ('XDG_CACHE_HOME', 'cache'), ('XDG_RUNTIME_DIR', 'runtime'),
                      ('TMPDIR', 'tmp')]:
        target = output / name
        target.mkdir(parents=True, mode=0o700)
        env[key] = str(target)
    return env


def stage(project, editor=False):
    """Copy accepted dependencies, preserving resources and removing services only in the mirror."""
    project.mkdir()
    for spike in ['s02', 's03', 's04', 's06']:
        shutil.copytree(ROOT / 'tests/fixtures' / spike, project / 'tests/fixtures' / spike)
    for spike in ['s01', 's02', 's04', 's06']:
        shutil.copytree(ROOT / 'tools' / spike, project / 'tools' / spike)
    models = project / 'art/models/spikes'
    models.mkdir(parents=True)
    for spike in ['s02', 's04', 's06']:
        for path in (ROOT / 'art/models/spikes').glob(spike + '_*'):
            if path.is_file():
                shutil.copy2(path, models / path.name)
    settings = (ROOT / 'project.godot').read_text()
    settings = re.sub(r'(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)', '', settings)
    settings = re.sub(r'^config/icon=.*\n', '', settings, flags=re.M)
    if editor:
        shutil.copytree(ROOT / 'addons/godot_mcp_toolkit', project / 'addons/godot_mcp_toolkit')
        settings += '\n[editor_plugins]\nenabled=PackedStringArray("res://addons/godot_mcp_toolkit/plugin.cfg")\n'
    elif (ROOT / 'tests/fixtures/s07_driver').exists():
        shutil.copytree(ROOT / 'tests/fixtures/s07_driver', project / 'tests/fixtures/s07_driver')
    (project / 'project.godot').write_text(settings)
    return {str(p.relative_to(project)): identity(p) for p in project.rglob('*') if p.is_file()}


def stop(child):
    """Reap only the recorded child handle inside a six-second cleanup envelope."""
    if child.poll() is None:
        child.terminate()
        try:
            child.wait(timeout=2)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=4)
    else:
        child.wait()


def command(argv, cwd, env, output, timeout):
    """Run one owned command with separate complete streams and durable argv/exit/failure receipts."""
    output.mkdir()
    receipt = {'argv': list(map(str, argv)), 'cwd': str(cwd), 'timeout_seconds': timeout,
               'started_unix': time.time(), 'HOME': env.get('HOME'),
               'environment': {k: v for k, v in env.items() if k.startswith('XDG_')}}
    (output / 'engine.log').touch()
    child = None
    try:
        with (output / 'stdout.log').open('wb') as out, (output / 'stderr.log').open('wb') as err:
            child = subprocess.Popen(argv, cwd=cwd, env=env, stdout=out, stderr=err)
            receipt['owned_pid'] = child.pid
            save(output / 'command.json', receipt)
            try:
                child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                receipt['timeout'] = True
            finally:
                stop(child)
                receipt.update(exit=child.returncode, reaped=child.poll() is not None)
    except Exception as error:
        receipt['failure'] = repr(error)
    finally:
        receipt['ended_unix'] = time.time()
        save(output / 'command.json', receipt)
    return receipt


def verify_engine():
    """Reject a different executable without spending an engine launch."""
    if identity(ENGINE) != {'bytes': 151398728, 'sha256': ENGINE_SHA}:
        raise RuntimeError('pinned engine bytes differ')
