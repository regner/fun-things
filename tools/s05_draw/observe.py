#!/usr/bin/env python3
"""Own one finite addon-free native Wayland host/live/settled-late S05 observation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
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
CLEANUP_PHASE_SECONDS = 2
PRESERVATION_RESERVE_SECONDS = 4
COLLECTION_SECONDS = BUDGET_SECONDS - 3 * CLEANUP_PHASE_SECONDS - PRESERVATION_RESERVE_SECONDS
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


def require_before(deadline, phase):
    """Stop work before its reserved monotonic phase budget has been consumed."""
    if time.monotonic() >= deadline:
        raise TimeoutError(phase + ' deadline')


def stage(author, output, deadline):
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
        require_before(deadline, 'preparation/collection')
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
        require_before(deadline, 'preparation/collection')
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


def cleanup_owned(children, records, deadline):
    """Request all owned exits first, then share each actual grace/fallback deadline."""
    phases = []
    for action in ['interrupt', 'terminate', 'kill']:
        active = [(role, child) for role, child in children.items() if child.poll() is None]
        if not active:
            break
        start = time.monotonic()
        phase_deadline = min(start + CLEANUP_PHASE_SECONDS, deadline)
        for role, child in active:
            record = records[role]
            if action == 'interrupt':
                record['cleanup_request'] = 'owned SIGINT; shared2s grace before fallback'
                child.send_signal(signal.SIGINT)
            elif action == 'terminate':
                record['terminate_fallback'] = True
                child.terminate()
            else:
                record['kill_fallback'] = True
                child.kill()
        for role, child in active:
            try:
                child.wait(timeout=max(0, phase_deadline - time.monotonic()))
                records[role]['reaped'] = True
            except subprocess.TimeoutExpired:
                pass
        phases.append({'action': action, 'start_monotonic': start,
                       'deadline_monotonic': phase_deadline, 'end_monotonic': time.monotonic()})
    for role, child in children.items():
        if child.poll() is not None:
            child.wait(timeout=0)
            records[role].update(exit=child.returncode, end_unix=time.time(), reaped=True)
        else:
            records[role]['reaped'] = False
            records[role]['cleanup_failure'] = 'owned child did not reap within reserved deadline'
    return phases


def main():
    """Own only three Popen handles, stop at first diagnostic, and retain unsuccessful groups."""
    start_monotonic = time.monotonic()
    group_deadline = start_monotonic + BUDGET_SECONDS
    collection_deadline = start_monotonic + COLLECTION_SECONDS
    cleanup_deadline = group_deadline - PRESERVATION_RESERVE_SECONDS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--author-project', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--group', type=int, choices=[1, 2], required=True)
    parser.add_argument('--audio-driver', choices=['Dummy'])
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(Path('/tmp')) or output.exists():
        parser.error('fresh /tmp output required')
    output.mkdir(mode=0o700)
    result = {'collection_ok': False, 'start_unix': time.time(),
              'budget_s': BUDGET_SECONDS, 'processes': {}, 'engine': ENGINE,
              'graphical_group': args.group, 'import_processes': 0}
    result.update(start_monotonic=start_monotonic, deadline_monotonic=group_deadline,
                  collection_deadline_monotonic=collection_deadline,
                  cleanup_deadline_monotonic=cleanup_deadline,
                  phase_budgets_s={'preparation_collection': COLLECTION_SECONDS,
                                   'cleanup': 3 * CLEANUP_PHASE_SECONDS,
                                   'preservation': PRESERVATION_RESERVE_SECONDS})
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
        require_before(collection_deadline, 'preparation/collection')
        project, ledger = stage(args.author_project.resolve(), output, collection_deadline)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]
        result.update(project=str(project), binary_sha256=ENGINE_SHA,
                      wayland_socket=str(socket_path), port=port)

        def start(role):
            """Record one exact private role command before and immediately after spawn."""
            require_before(collection_deadline, 'spawn')
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
            if args.audio_driver:
                command[1:1] = ['--audio-driver', args.audio_driver]
            record = {'argv': command, 'start_unix': time.time(),
                      'start_monotonic': time.monotonic(), 'environment': {k: env[k]
                      for k in ['XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_CACHE_HOME',
                                'XDG_RUNTIME_DIR', 'WAYLAND_DISPLAY']},
                      'home_unchanged': env.get('HOME') == os.environ.get('HOME')}
            result['processes'][role] = record
            save(output / 'lifecycle.json', result)
            out, err = (folder / 'stdout').open('wb'), (folder / 'stderr').open('wb')
            streams.extend([out, err])
            require_before(collection_deadline, 'spawn')
            child = subprocess.Popen(command, cwd=project, env=env, stdout=out, stderr=err)
            children[role] = child
            record['owned_pid'] = child.pid
            save(output / 'lifecycle.json', result)

        start('host')
        while time.monotonic() < collection_deadline:
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
            time.sleep(min(.01, max(0, collection_deadline - time.monotonic())))
        else:
            raise RuntimeError('collection cutoff; cleanup/preservation reserve retained')
    except Exception as error:
        result['failure'] = repr(error)
    finally:
        result['cleanup_phases'] = cleanup_owned(children, result['processes'], cleanup_deadline)
        for stream in streams:
            stream.close()
        unchanged = project is not None
        preservation_start = time.monotonic()
        try:
            for row in ledger:
                require_before(group_deadline, 'preservation')
                unchanged &= hashlib.sha256((project / row['path']).read_bytes()).hexdigest() == (
                    row['sha256'])
        except Exception as error:
            unchanged = False
            result['preservation_failure'] = repr(error)
        result.update(end_unix=time.time(), streams_closed=True,
                      all_owned_children_reaped=all(c.poll() is not None for c in children.values()),
                      copy_bytes_preserved=unchanged)
        end_monotonic = time.monotonic()
        result.update(end_monotonic=end_monotonic, elapsed_s=end_monotonic - start_monotonic,
                      preservation_start_monotonic=preservation_start,
                      within_supervisor_budget=end_monotonic <= group_deadline)
        save(output / 'lifecycle.json', result)
    print(json.dumps(result, indent=2))
    return 0 if all(result[key] for key in ['collection_ok', 'copy_bytes_preserved',
                                           'all_owned_children_reaped',
                                           'within_supervisor_budget']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
