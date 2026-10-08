#!/usr/bin/env python3
"""Own one finite addon-free native Wayland host/live/settled-late S05 observation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import stat
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
ENGINE = '/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot'
ENGINE_SHA = '6aea356032435e7af19dbfbf48dd20c5012a7dc1267eb8e92406f44e3584b5fd'
SCENE = 'res://tests/fixtures/s05_draw/burst.tscn'
BUDGET_SECONDS = 30
MAX_COPY_BYTES = 8 * 1024 * 1024


def save(path, value):
    """Keep exact argv and process ownership receipts even on an unsuccessful phase."""
    path.write_text(json.dumps(value, indent=2) + '\n')


def rows(path):
    """Decode only complete actual fixture rows; an incomplete last write waits for polling."""
    if not path.exists():
        return []
    return [json.loads(line[4:]) for line in path.read_text().splitlines(keepends=True)
            if line.startswith('S05 ') and line.endswith('\n')]


def stage(author, output):
    """Copy only accepted runtime inputs, saved new resources and generated dependency caches."""
    project = output / 'project'
    project.mkdir()
    inputs = json.loads((author.parent / 'inputs.json').read_text())
    names = {r['path'] for r in inputs if not r['path'].startswith('addons/')
             and not r['path'].startswith('tests/fixtures/s05_effect/editor_')}
    names.update(p.relative_to(author).as_posix()
                 for p in (author / 'tests/fixtures/s05_draw').iterdir() if p.is_file())
    names.update(p.relative_to(author).as_posix()
                 for p in (author / '.godot/imported').iterdir() if p.is_file())
    names.update(['.godot/global_script_class_cache.cfg', '.godot/uid_cache.bin'])
    ledger = []
    total = 0
    for name in sorted(names):
        source = author / name
        data = source.read_bytes()
        if not name.startswith('.godot/'):
            current = ROOT / name
            if not current.exists() or data != current.read_bytes():
                raise RuntimeError('saved runtime input mismatch: ' + name)
        total += len(data)
        if total > MAX_COPY_BYTES:
            raise RuntimeError('runtime closure byte cap')
        target = project / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        ledger.append({'path': name, 'bytes': len(data),
                       'sha256': hashlib.sha256(data).hexdigest()})
    # The generated class cache still names the private editor helper. It remains
    # available as an unused @tool dependency; no editor or addon executes here.
    helper = 'tests/fixtures/s05_effect/editor_probe.gd'
    for name in [helper, helper + '.uid']:
        data = (author / name).read_bytes()
        target = project / name
        target.write_bytes(data)
        total += len(data)
        ledger.append({'path': name, 'bytes': len(data),
                       'sha256': hashlib.sha256(data).hexdigest()})
    if total > MAX_COPY_BYTES:
        raise RuntimeError('runtime closure byte cap')
    settings = (ROOT / 'project.godot').read_text()
    settings = re.sub(r'(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)', '', settings)
    settings = settings.replace('config/icon="res://icon.svg"\n', '')
    (project / 'project.godot').write_text(settings)
    save(output / 'copy-ledger.json', {'bytes': total, 'cap': MAX_COPY_BYTES,
                                     'files': ledger, 'project_settings_sha256':
                                     hashlib.sha256(settings.encode()).hexdigest()})
    return project, ledger


def main():
    """Own only three Popen handles, stop at first diagnostic, and retain unsuccessful groups."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--author-project', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(Path('/tmp')) or output.exists():
        parser.error('fresh /tmp output required')
    output.mkdir(mode=0o700)
    result = {'collection_ok': False, 'start_unix': time.time(),
              'budget_s': BUDGET_SECONDS, 'processes': {}, 'engine': ENGINE,
              'graphical_groups': 1, 'import_processes': 0}
    children, streams = {}, []
    project = None
    ledger = []
    try:
        with open(ENGINE, 'rb') as file:
            if hashlib.file_digest(file, 'sha256').hexdigest() != ENGINE_SHA:
                raise RuntimeError('pinned binary byte mismatch')
        socket_path = Path(os.environ['XDG_RUNTIME_DIR']) / os.environ['WAYLAND_DISPLAY']
        if not stat.S_ISSOCK(socket_path.stat().st_mode):
            raise RuntimeError('existing Wayland route unavailable')
        project, ledger = stage(args.author_project.resolve(), output)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]
        result.update(project=str(project), binary_sha256=ENGINE_SHA,
                      wayland_socket=str(socket_path), port=port)
        deadline = time.monotonic() + BUDGET_SECONDS

        def start(role):
            """Record one exact private role command before and immediately after spawn."""
            folder = output / role
            folder.mkdir()
            env = {k: v for k, v in os.environ.items() if not k.startswith('GODOT_MCP_')}
            for key, name in [('XDG_CONFIG_HOME', 'config'), ('XDG_DATA_HOME', 'data'),
                              ('XDG_CACHE_HOME', 'cache'), ('XDG_RUNTIME_DIR', 'runtime')]:
                target = folder / name
                target.mkdir(mode=0o700)
                env[key] = str(target)
            env['WAYLAND_DISPLAY'] = str(socket_path)
            command = [ENGINE, '--path', str(project), '--display-driver', 'wayland',
                       '--log-file', str(folder / 'engine.log'), SCENE, '--',
                       '--role=' + role, '--port=' + str(port)]
            record = {'argv': command, 'start_unix': time.time(),
                      'start_monotonic': time.monotonic(), 'environment': {k: env[k]
                      for k in ['XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_CACHE_HOME',
                                'XDG_RUNTIME_DIR', 'WAYLAND_DISPLAY']},
                      'home_unchanged': env.get('HOME') == os.environ.get('HOME')}
            result['processes'][role] = record
            save(output / 'lifecycle.json', result)
            out, err = (folder / 'stdout').open('wb'), (folder / 'stderr').open('wb')
            streams.extend([out, err])
            child = subprocess.Popen(command, cwd=project, env=env, stdout=out, stderr=err)
            children[role] = child
            record['owned_pid'] = child.pid
            save(output / 'lifecycle.json', result)

        start('host')
        while time.monotonic() < deadline:
            for role, child in children.items():
                actual = rows(output / role / 'stdout')
                if any(r['event'] == 'failure' for r in actual):
                    raise RuntimeError('fixture expectation failure: ' + role)
                for filename in ['stdout', 'stderr', 'engine.log']:
                    path = output / role / filename
                    if path.exists() and re.search(r'SCRIPT ERROR:|ERROR:|WARNING:',
                                                  path.read_text(errors='replace')):
                        raise RuntimeError('runtime diagnostic: ' + role + '/' + filename)
                if child.poll() is not None and child.returncode != 0:
                    raise RuntimeError('nonzero role exit: ' + role)
            host = rows(output / 'host/stdout')
            if any(r['event'] == 'ready' for r in host) and 'client' not in children:
                start('client')
            if any(r['event'] == 'settled' for r in host) and 'late' not in children:
                start('late')
            if len(children) == 3 and all(c.poll() is not None for c in children.values()):
                result['collection_ok'] = True
                break
            if children['host'].poll() is not None and 'late' not in children:
                raise RuntimeError('host left before settled-late launch')
            time.sleep(.01)
        else:
            raise RuntimeError('30s group deadline')
    except Exception as error:
        result['failure'] = repr(error)
    finally:
        for role, child in children.items():
            record = result['processes'][role]
            if child.poll() is None:
                record['cleanup_request'] = 'owned SIGINT; full2s grace before fallback'
                child.send_signal(signal.SIGINT)
                try:
                    child.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    record['terminate_fallback'] = True
                    child.terminate()
                    try:
                        child.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        record['kill_fallback'] = True
                        child.kill()
                        child.wait(timeout=2)
            else:
                child.wait()
            record.update(exit=child.returncode, end_unix=time.time(), reaped=True)
        for stream in streams:
            stream.close()
        unchanged = project is not None and all(hashlib.sha256((project / r['path']).read_bytes())
                                               .hexdigest() == r['sha256'] for r in ledger)
        result.update(end_unix=time.time(), streams_closed=True,
                      all_owned_children_reaped=all(c.poll() is not None for c in children.values()),
                      copy_bytes_preserved=unchanged)
        save(output / 'lifecycle.json', result)
    print(json.dumps(result, indent=2))
    return 0 if result['collection_ok'] and result['copy_bytes_preserved'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
