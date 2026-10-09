#!/usr/bin/env python3
"""One bounded S05 API/three-process ENet chain experiment in an isolated saved copy."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import tempfile
import time

from incremental_log import prefixed_json_records
from run_s03 import stop_children
from run_s04 import stage as stage_dependencies
from script_checks import ROOT, DIAGNOSTIC, checked_command, engine_version, environment

LOG_STATE = {}


def stage(directory):
    """Reuse the existing S04 dependency staging and add only the new saved S05 fixture."""
    project = stage_dependencies(directory)
    shutil.copytree(ROOT / 'tests/fixtures/s05', project / 'tests/fixtures/s05',
                    ignore=shutil.ignore_patterns('editor_harness.tscn', 'editor_probe.gd*'))
    return project


def records(path):
    """Read only complete appended S05 rows and retain prior records per log."""
    return prefixed_json_records(path, b"S05 ", LOG_STATE)


def inspect_logs(directory, roles):
    for role in roles:
        for name in ['stdout.log', 'engine.log']:
            path = directory / role / name
            if not path.exists() or DIAGNOSTIC.search(path.read_text(errors='replace')):
                raise RuntimeError(f'missing log or runtime diagnostic: {role}/{name}')
        result = [row for row in records(directory / role / 'stdout.log')
                  if row['event'] == 'result']
        if len(result) != 1 or not result[0]['ok']:
            raise RuntimeError(f'{role} incomplete or failed result')


def network(args, project, directory, scene, port):
    """Launch a host, live client and post-chain joiner as actual separate ENet processes."""
    children, logs, commands, observed = {}, {}, {}, set()
    deadline = time.monotonic() + args.deadline
    directory.mkdir()

    def start(role):
        folder = directory / role
        folder.mkdir()
        command = [args.godot, '--headless', '--path', str(project),
                   '--log-file', str(folder / 'engine.log'), scene, '--',
                   '--role=' + role, '--port=' + str(port)]
        commands[role] = command
        logs[role] = (folder / 'stdout.log').open('w')
        children[role] = subprocess.Popen(command, stdout=logs[role],
                                          stderr=subprocess.STDOUT,
                                          env=environment(folder / 'user'))

    try:
        start('host')
        while time.monotonic() < deadline:
            for row in records(directory / 'host/stdout.log'):
                observed.add(row['event'])
            if 'ready' in observed and 'client' not in children:
                start('client')
            if 'settled' in observed and 'late' not in children:
                start('late')
            if len(children) == 3 and all(child.poll() is not None
                                          for child in children.values()):
                break
            if children['host'].poll() is not None and 'late' not in children:
                raise RuntimeError('host exited before late-join launch')
            time.sleep(0.01)
        else:
            raise RuntimeError('three-process wall-clock deadline')
        if any(child.returncode != 0 for child in children.values()):
            raise RuntimeError('nonzero actual process exit')
        inspect_logs(directory, children)
        rows = {role: records(directory / role / 'stdout.log') for role in children}
        host = next(row for row in rows['host'] if row['event'] == 'network')
        live = next(row for row in rows['client'] if row['event'] == 'client_state')
        late = next(row for row in rows['late'] if row['event'] == 'hydrate')
        expected = 12 if scene.endswith('burst.tscn') else 2
        literal = [0] * 12 if expected == 12 else [0, 0, 100]
        health = [row['health'] for row in host['cut']['rows']]
        checks = {
            'literal_host_health': health == literal,
            'live_current_health': [row['health'] for row in live['cut']['rows']] == literal,
            'late_current_health': [row['health'] for row in late['cut']['rows']] == literal,
            'late_no_historical_effects': late['effects'] == 0 and not late['input_enabled'],
            'live_event_once': live['live'] == expected and live['duplicates'] == expected,
            'independent_gameplay_cosmetic_counts': host['damage'] == expected and
                host['effects'] == expected and host['effect_drops'] == 0,
            'finite_work': host['visits'] == (144 if expected == 12 else 6) and
                host['target_peak'] <= 4 and host['queue_peak'] <= 12 and host['active_jobs'] == 0,
            'off_camera_burst': expected != 12 or host['hidden'],
            'separate_native_processes': len({child.pid for child in children.values()}) == 3,
        }
        result = {'ok': all(checks.values()), 'checks': checks, 'host': host,
                  'live': live, 'late': late, 'commands': commands,
                  'pids': {role: child.pid for role, child in children.items()},
                  'exits': {role: child.returncode for role, child in children.items()}}
        (directory / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        if not result['ok']:
            raise RuntimeError('independent network outcomes failed')
        return result
    finally:
        stop_children(list(children.values()))
        for log in logs.values():
            log.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot', required=True)
    parser.add_argument('--gdstyle', required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--port', type=int, default=25040)
    parser.add_argument('--deadline', type=float, default=18)
    parser.add_argument('--api-only', action='store_true')
    parser.add_argument('--queue-only', action='store_true')
    args = parser.parse_args()
    LOG_STATE.clear()
    if not 1 <= args.port <= 65534 or not 1 <= args.deadline <= 30:
        parser.error('port 1..65534 and deadline 1..30 seconds required')
    directory = (args.output or Path(tempfile.mkdtemp(prefix='s05-'))).resolve()
    if directory.is_relative_to(ROOT) or (directory.exists() and any(directory.iterdir())):
        parser.error('fresh empty external output required')
    directory.mkdir(parents=True, exist_ok=True)
    print('S05 evidence:', directory, flush=True)
    report = {'ok': False, 'platform': platform.platform(), 'api': {}, 'network': {}}
    previous = signal.signal(signal.SIGTERM, lambda *_args: (_ for _ in ()).throw(KeyboardInterrupt()))
    try:
        report['engine'] = engine_version(args.godot)
        project = stage(directory)
        before = {str(p.relative_to(project)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in project.rglob('*') if p.is_file()}
        env = environment(directory / 'check-user')
        commands = [[args.godot, '--headless', '--editor', '--path', str(project), '--import', '--quit']]
        if not checked_command(commands[0], directory / 'import.log', env):
            raise RuntimeError('isolated saved dependency import failed')
        report['compilation'] = {}
        for source in sorted((ROOT / 'tests/fixtures/s05').glob('*.gd')):
            if source.name == 'editor_probe.gd':
                continue
            relative = source.relative_to(ROOT).as_posix()
            command = [args.godot, '--headless', '--path', str(project),
                       '--check-only', '--script', 'res://' + relative]
            commands.append(command)
            report['compilation'][source.name] = checked_command(
                command, directory / ('compile-' + source.name + '.log'), env)
        scripts = [str(p) for p in sorted((ROOT / 'tests/fixtures/s05').glob('*.gd'))]
        report['formatting'] = checked_command([args.gdstyle, 'fmt', '--check', *scripts],
                                               directory / 'formatting.log', env)
        report['lint'] = checked_command([args.gdstyle, '--max-warnings', '0', *scripts],
                                         directory / 'lint.log', env)
        if not all(report['compilation'].values()) or not report['formatting'] or not report['lint']:
            raise RuntimeError('explicit compilation or pinned style failed')
        if not args.queue_only:
            for name in ['boot', 'burst']:
                api = directory / ('api-' + name)
                api.mkdir()
                scene = 'res://tests/fixtures/s05/' + name + '.tscn'
                command = [args.godot, '--headless', '--path', str(project),
                           '--log-file', str(api / 'engine.log'), scene, '--', '--role=api']
                commands.append(command)
                if not checked_command(command, api / 'stdout.log', environment(api / 'user'), timeout=12):
                    raise RuntimeError('public API check failed: ' + name)
                entries = records(api / 'stdout.log')
                result = next((row for row in entries if row['event'] == 'result'), {})
                if not result.get('ok'):
                    raise RuntimeError('public API result missing/failed: ' + name)
                report['api'][name] = next(row for row in entries if row['event'] == 'api')
                if not args.api_only:
                    report['network'][name] = network(args, project, directory / ('enet-' + name),
                                                      scene, args.port + (name == 'burst'))
        queue = directory / 'queue'
        queue.mkdir()
        command = [args.godot, '--headless', '--path', str(project),
                   '--log-file', str(queue / 'engine.log'),
                   'res://tests/fixtures/s05/burst.tscn', '--', '--role=queue']
        commands.append(command)
        if not checked_command(command, queue / 'stdout.log', environment(queue / 'user'), timeout=12):
            raise RuntimeError('finite reserved queue row failed')
        rows = records(queue / 'stdout.log')
        result = next((row for row in rows if row['event'] == 'result'), {})
        metrics = next((row for row in rows if row['event'] == 'queue'), {})
        if not result.get('ok') or not (metrics.get('queue_peak') == 12 and
                metrics.get('visits') == 144 and metrics.get('effects') == 12 and
                metrics.get('effect_drops') == 0 and metrics.get('active_jobs') == 0):
            raise RuntimeError('independent queue pressure outcomes failed')
        report['queue'] = metrics
        report['source_sha256'] = before
        report['saved_source_unchanged'] = all(
            hashlib.sha256((project / p).read_bytes()).hexdigest() == digest
            for p, digest in before.items())
        report['commands'] = commands
        report['ok'] = report['saved_source_unchanged']
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, KeyboardInterrupt) as error:
        report['failure'] = str(error) or 'runner interrupted; owned children stopped'
    finally:
        signal.signal(signal.SIGTERM, previous)
    (directory / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'ok': report['ok'], 'failure': report.get('failure')}), flush=True)
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
