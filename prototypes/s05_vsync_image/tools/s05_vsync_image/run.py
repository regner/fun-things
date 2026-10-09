#!/usr/bin/env python3
"""Execute exactly one private Card I attempt; never offer a retry or fallback mode."""
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
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from incremental_log import appended_complete_lines, prefixed_json_records  # noqa: E402
from window_safety import capped_window_arguments, require_capped_window  # noqa: E402
BASE = '3f5fb4067c5ce5fca721f54d42165a833e4c884c'
ENGINE = '/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot'
ENGINE_SHA = '6aea356032435e7af19dbfbf48dd20c5012a7dc1267eb8e92406f44e3584b5fd'
SCENE = 'res://tests/fixtures/s05_draw/burst.tscn'
SOCKET = Path('/run/user/1000/wayland-0')
SOURCE_CAP = 8 * 1024 * 1024
TOTAL_SECONDS, PREP_SECONDS, COLLECTION_SECONDS = 120, 90, 20
CLEANUP_SECONDS, READBACK_SECONDS = 6, 4
DIAGNOSTIC = re.compile(r'SCRIPT ERROR:|ERROR:|WARNING:')
LOG_STATE = {}
DIAGNOSTIC_STATE = {}


def save(path, value):
    """Write a complete structured receipt in the owned output root."""
    path.write_text(json.dumps(value, indent=2) + '\n')


def digest(data):
    """Bind actual bytes with a stable cryptographic identity."""
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def before(deadline, phase):
    """Enforce absolute cutoffs before expensive operations and each spawn."""
    if time.monotonic() >= deadline:
        raise TimeoutError(phase + ' cutoff')


def closure():
    """Follow saved paths and fixture class references, without editor/native helpers."""
    tracked = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', 'HEAD'],
                                      cwd=ROOT, text=True).splitlines()
    classes = {}
    for name in tracked:
        if name.startswith('tests/fixtures/') and name.endswith('.gd'):
            match = re.search(r'^class_name\s+(\w+)', (ROOT / name).read_text(), re.M)
            if match:
                classes[match[1]] = name
    paths, pending = set(), [SCENE.removeprefix('res://')]
    while pending:
        name = pending.pop()
        if name in paths:
            continue
        if name not in tracked or name.startswith('addons/') or 'editor_' in name:
            raise RuntimeError('runtime dependency outside allowed closure: ' + name)
        paths.add(name)
        if name.endswith(('.gd', '.tscn', '.tres', '.import')):
            source = (ROOT / name).read_text()
            pending.extend(p for p in re.findall(r'res://([\w./-]+)', source)
                           if not p.startswith('.godot/'))
            pending.extend(path for symbol, path in classes.items()
                           if re.search(r'\b' + symbol + r'\b', source))
        for suffix in ['.uid', '.import']:
            if name + suffix in tracked:
                pending.append(name + suffix)
    # The icon is a saved project dependency, not a display/quality change.
    paths.update(['icon.svg', 'icon.svg.import'])
    return sorted(paths)


def socket_identity():
    """Inspect the authorized shared socket read-only; never change it or its service."""
    actual = SOCKET.lstat()
    if not stat.S_ISSOCK(actual.st_mode) or actual.st_uid != os.getuid():
        raise RuntimeError('Wayland socket type/owner mismatch')
    if str(SOCKET.resolve()) != str(SOCKET):
        raise RuntimeError('Wayland socket canonical path mismatch')
    return {'path': str(SOCKET), 'uid': actual.st_uid, 'gid': actual.st_gid,
            'mode': oct(stat.S_IMODE(actual.st_mode)), 'inode': actual.st_ino,
            'device': actual.st_dev, 'shared_read_only': True}


def stage(output, deadline):
    """Stage and hash only the frozen runtime closure inside the attempt clock."""
    project = output / 'project'
    project.mkdir(mode=0o700)
    ledger, total = [], 0
    for name in closure():
        before(deadline, 'preparation')
        data = (ROOT / name).read_bytes()
        expected = subprocess.check_output(['git', 'show', 'HEAD:' + name], cwd=ROOT)
        if data != expected:
            raise RuntimeError('unfrozen runtime source: ' + name)
        total += len(data)
        if total > SOURCE_CAP:
            raise RuntimeError('source-copy cap')
        target = project / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        ledger.append({'path': name, **digest(data)})
    settings = (ROOT / 'project.godot').read_text()
    settings = re.sub(r'(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)', '', settings)
    data = settings.encode()
    total += len(data)
    if total > SOURCE_CAP:
        raise RuntimeError('source-copy cap including private project settings')
    (project / 'project.godot').write_bytes(data)
    ledger.append({'path': 'project.godot', **digest(data)})
    save(output / 'copy-ledger.json', {'source_bytes': total, 'cap': SOURCE_CAP,
                                     'files': ledger, 'settings_change':
                                     'remove only autoload/editor_plugins sections'})
    return project, ledger


def private_environment(folder):
    """Keep HOME unchanged and isolate every writable XDG root with mode0700."""
    env = {key: os.environ[key] for key in
           ['HOME', 'PATH', 'USER', 'LOGNAME', 'LANG', 'LC_ALL', 'LC_CTYPE'] if key in os.environ}
    for key, name in [('XDG_CONFIG_HOME', 'config'), ('XDG_DATA_HOME', 'data'),
                      ('XDG_CACHE_HOME', 'cache'), ('XDG_RUNTIME_DIR', 'runtime')]:
        path = folder / name
        path.mkdir(mode=0o700)
        if stat.S_IMODE(path.stat().st_mode) != 0o700:
            raise RuntimeError('private XDG mode mismatch')
        env[key] = str(path)
    env['WAYLAND_DISPLAY'] = str(SOCKET)
    return env


def identity(child):
    """Bind the exact owned Popen handle to live proc start/argv/fd metadata."""
    proc = Path('/proc') / str(child.pid)
    return {'pid': child.pid, 'proc_stat': (proc / 'stat').read_text(),
            'proc_cmdline': (proc / 'cmdline').read_bytes().split(b'\0')[:-1]
            and (proc / 'cmdline').read_bytes().decode().split('\0')[:-1],
            'proc_exe': str((proc / 'exe').resolve()),
            'popen_handle_owned': True}


def bound_endpoint(child, port, receipt_path):
    """Retain owned lookup inputs and prove an IPv4 or IPv4-mapped loopback UDP fd."""
    proc = Path('/proc') / str(child.pid)
    lookup = {'owned_pid': child.pid, 'port': port, 'handles': {}, 'tables': {},
              'matches': [], 'failures': []}
    # Kernel table lookup is observation, not a second network owner. Retain failures
    # before raising; IPv4-mapped UDP6 is not an external/all-interface listener.
    try:
        for path in (proc / 'fd').iterdir():
            try:
                lookup['handles'][path.name] = os.readlink(path)
            except FileNotFoundError:
                lookup['failures'].append('fd disappeared during lookup: ' + path.name)
        addresses = {'udp': '0100007F', 'udp6': '0000000000000000FFFF00000100007F'}
        for table, address in addresses.items():
            source = (proc / 'net' / table).read_text()
            lookup['tables'][table] = source
            for line in source.splitlines()[1:]:
                fields = line.split()
                if len(fields) < 10:
                    continue
                handle = f'socket:[{fields[9]}]'
                if fields[1] == f'{address}:{port:04X}' and handle in lookup['handles'].values():
                    lookup['matches'].append({'table': table, 'raw_udp_row': line,
                        'inode': fields[9], 'owned_fd': handle, 'address': '127.0.0.1', 'port': port})
    except OSError as error:
        lookup['failures'].append(repr(error))
    save(receipt_path, lookup)
    if len(lookup['matches']) != 1:
        raise RuntimeError('owned host loopback endpoint not proven; raw lookup retained')
    return lookup['matches'][0]


def production_rows(path):
    """Read only appended complete fixture rows while retaining prior observations."""
    return prefixed_json_records(path, b"S05 ", LOG_STATE)


def diagnostics(folder):
    """Reject diagnostics while scanning only newly appended complete log lines."""
    for name in ['stdout', 'stderr', 'engine.log']:
        path = folder / name
        if any(DIAGNOSTIC.search(line)
               for line in appended_complete_lines(path, DIAGNOSTIC_STATE)):
            raise RuntimeError('engine/script diagnostic: ' + str(path))


def cleanup(children, records, deadline):
    """Share2s interrupt/terminate/kill-reap deadlines across all failed owned handles."""
    phases = []
    for action in ['interrupt', 'terminate', 'kill']:
        active = [(role, child) for role, child in children.items() if child.poll() is None]
        if not active:
            break
        start = time.monotonic()
        cutoff = min(start + 2, deadline)
        for role, child in active:
            records[role].setdefault('cleanup_actions', []).append(action)
            try:
                if action == 'interrupt':
                    child.send_signal(signal.SIGINT)
                elif action == 'terminate':
                    child.terminate()
                else:
                    child.kill()
            except ProcessLookupError:
                pass
        for role, child in active:
            try:
                child.wait(timeout=max(0, cutoff - time.monotonic()))
            except subprocess.TimeoutExpired:
                pass
        phases.append({'action': action, 'start': start, 'cutoff': cutoff,
                       'end': time.monotonic()})
    for role, child in children.items():
        if child.poll() is not None:
            child.wait(timeout=0)
            records[role].update(exit=child.returncode, reaped=True)
        else:
            records[role].update(reaped=False, cleanup_failure='unreaped owned handle')
    return phases


def main():
    """Own one import plus at most three graphical children, including all preparation time."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--candidate', required=True)
    args = parser.parse_args()
    LOG_STATE.clear()
    DIAGNOSTIC_STATE.clear()
    output = args.output.resolve()
    if output.exists() or not output.name.startswith('p0-image-') or output.parent != Path('/tmp'):
        parser.error('fresh direct /tmp/p0-image-<worker>-<attempt> required')
    os.umask(0o077)
    # No closure staging/hashing or engine invocation occurs before this clock.
    start = time.monotonic()
    absolute, prep = start + TOTAL_SECONDS, start + PREP_SECONDS
    output.mkdir(mode=0o700)
    result = {'candidate': args.candidate, 'base': BASE, 'attempt': 1,
              'start_unix': time.time(), 'start_monotonic': start,
              'absolute_deadline': absolute, 'prep_deadline': prep,
              'collection_ok': False, 'processes': {}, 'engine': ENGINE,
              'phase_budgets_s': [90, 20, 6, 4]}
    children, streams, ledger = {}, [], []
    project = None
    try:
        actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        if actual != args.candidate or subprocess.check_output(
                ['git', 'status', '--porcelain'], cwd=ROOT):
            raise RuntimeError('exact clean frozen candidate required')
        result['wayland_socket_before'] = socket_identity()
        before(prep, 'preparation')
        result['binary'] = digest(Path(ENGINE).read_bytes())
        if result['binary']['sha256'] != ENGINE_SHA:
            raise RuntimeError('pinned binary mismatch')
        project, ledger = stage(output, prep)
        result['project'] = str(project)
        result['source_ancestry'] = {str(p.relative_to(ROOT)): digest(p.read_bytes())
            for p in (ROOT / 'art').rglob('*.blend') if p.name in
            ['s04_kit.blend', 's05_explosion_carrier.blend']}
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]
        result['endpoint_request'] = {'address': '127.0.0.1', 'port': port,
                                      'allocation': 'OS-selected; released before ENet bind'}
        def spawn(role, command, deadline):
            """Save exact argv/env before spawning and ownership immediately afterward."""
            before(deadline, 'spawn')
            folder = output / role
            folder.mkdir(mode=0o700)
            env = private_environment(folder)
            record = {'argv': command, 'environment': env, 'cwd': str(project),
                      'start_unix': time.time(), 'start_monotonic': time.monotonic(),
                      'home_unchanged': env.get('HOME') == os.environ.get('HOME')}
            result['processes'][role] = record
            save(output / 'lifecycle.json', result)
            out, err = (folder / 'stdout').open('wb'), (folder / 'stderr').open('wb')
            streams.extend([out, err])
            before(deadline, 'spawn')
            child = subprocess.Popen(command, cwd=project, env=env, stdout=out, stderr=err)
            children[role] = child
            record['owned_pid'] = child.pid
            record['identity'] = identity(child)
            save(output / 'lifecycle.json', result)
            return child
        # One minimal-closure headless import creates only this new private project's cache.
        importer = spawn('import', [ENGINE, '--headless', '--path', str(project), '--import',
                                   '--log-file', str(output / 'import/engine.log')], prep)
        importer.wait(timeout=max(0, prep - time.monotonic()))
        diagnostics(output / 'import')
        if importer.returncode != 0:
            raise RuntimeError('minimal import nonzero exit')
        before(prep, 'preparation')
        generated = []
        for path in (project / '.godot').rglob('*'):
            before(prep, 'generated import accounting')
            if path.is_file():
                generated.append({'path': str(path.relative_to(project)), **digest(path.read_bytes())})
                before(prep, 'completed generated import hash')
        save(output / 'generated-imports.json', {'files': generated,
             'bytes': sum(r['bytes'] for r in generated), 'separate_from_source_cap': True})
        before(prep, 'completed preparation')
        result['prep_end_monotonic'] = time.monotonic()
        result['preparation_within_budget'] = True
        collect = min(start + PREP_SECONDS + COLLECTION_SECONDS,
                      time.monotonic() + COLLECTION_SECONDS)
        result['collection_deadline'] = collect
        def graphical(role):
            """Launch only the exact Card I argv with disabled VSync and fresh private paths."""
            result['wayland_socket_prelaunch'] = socket_identity()
            if result['wayland_socket_prelaunch'] != result['wayland_socket_before']:
                raise RuntimeError('shared socket identity changed')
            command = [ENGINE, '--audio-driver', 'Dummy', '--disable-vsync',
                *capped_window_arguments(), '--path', str(project), '--display-driver',
                'wayland', '--log-file', str(output / role / 'engine.log'), SCENE, '--',
                '--role=' + role, '--port=' + str(port)]
            require_capped_window(command)
            return spawn(role, command, min(prep, collect) if role == 'host' else collect)
        graphical('host')
        while time.monotonic() < collect:
            for role, child in list(children.items()):
                diagnostics(output / role)
                rows = production_rows(output / role / 'stdout')
                if any(r['event'] == 'failure' for r in rows):
                    raise RuntimeError('fixture expectation failure: ' + role)
                if child.poll() is not None and child.returncode != 0:
                    raise RuntimeError('nonzero exit: ' + role)
            host = production_rows(output / 'host/stdout')
            if any(r['event'] == 'ready' for r in host) and 'client' not in children:
                result['bound_endpoint'] = bound_endpoint(
                    children['host'], port, output / 'endpoint-lookup.json')
                graphical('client')
            if any(r['event'] == 'settled' for r in host) and 'late' not in children:
                result['settled_before_late'] = next(r for r in host if r['event'] == 'settled')
                graphical('late')
            if len(children) == 4 and all(c.poll() is not None for c in children.values()):
                result['collection_ok'] = True
                break
            if children['host'].poll() is not None and 'late' not in children:
                raise RuntimeError('host left before late launch')
            time.sleep(min(.01, max(0, collect - time.monotonic())))
        else:
            raise TimeoutError('collection cutoff')
    except Exception as error:
        result['failure'] = repr(error)
    finally:
        phase_end = time.monotonic()
        result['collection_within_budget'] = result.get('collection_ok', False) and (
            phase_end <= result.get('collection_deadline', start))
        cleanup_start = time.monotonic()
        cleanup_cutoff = min(cleanup_start + CLEANUP_SECONDS, absolute - READBACK_SECONDS)
        result['cleanup_phases'] = cleanup(children, result['processes'], cleanup_cutoff)
        result['cleanup_within_budget'] = time.monotonic() <= cleanup_cutoff
        for stream in streams:
            stream.close()
        result['streams_closed'] = True
        preserved = project is not None and bool(ledger)
        readback_start = time.monotonic()
        cutoff = min(readback_start + READBACK_SECONDS, absolute)
        try:
            for row in ledger:
                before(cutoff, 'readback')
                preserved &= digest((project / row['path']).read_bytes()) == {
                    'bytes': row['bytes'], 'sha256': row['sha256']}
                if row['path'] != 'project.godot':
                    preserved &= digest((ROOT / row['path']).read_bytes()) == {
                        'bytes': row['bytes'], 'sha256': row['sha256']}
            before(cutoff, 'completed readback')
        except Exception as error:
            preserved = False
            result['readback_failure'] = repr(error)
        result.update(source_preserved=preserved,
                      all_owned_children_reaped=all(c.poll() is not None for c in children.values()),
                      end_monotonic=time.monotonic(), end_unix=time.time())
        result['elapsed_s'] = result['end_monotonic'] - start
        result['within_budget'] = result['end_monotonic'] <= absolute
        result['readback_elapsed_s'] = result['end_monotonic'] - readback_start
        result['readback_within_budget'] = result['end_monotonic'] <= cutoff
        result.setdefault('preparation_within_budget', False)
        result['normal_exits'] = bool(children) and all(c.returncode == 0 for c in children.values())
        result['absent_outputs'] = {role: [stage + '.png' for stage in stages
            if not list((output / role).rglob(stage + '.png'))] for role, stages in
            [('host', ['baseline', 'burst', 'expired']),
             ('client', ['baseline', 'burst', 'expired']), ('late', ['hydrated'])]}
        save(output / 'lifecycle.json', result)
    print(json.dumps(result, indent=2))
    return 0 if all(result.get(k) for k in ['collection_ok', 'source_preserved',
        'all_owned_children_reaped', 'within_budget', 'normal_exits', 'preparation_within_budget',
        'collection_within_budget', 'cleanup_within_budget', 'readback_within_budget']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
