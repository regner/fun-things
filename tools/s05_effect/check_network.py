#!/usr/bin/env python3
"""Run the one commissioned finite host/live/settled-late saved-effect ENet set."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path('/tmp/s05-author-56eb6b28-run01/project')
OUT = Path('/tmp/s05-effect-network-56eb6b28-run01')
ENGINE = '/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot'
SCENE = 'res://tests/fixtures/s05_effect/burst.tscn'


def rows(path):
    """Decode actual production-proof receipts without treating exit status as evidence."""
    if not path.exists():
        return []
    return [json.loads(line[4:]) for line in path.read_text().splitlines()
            if line.startswith('S05 ')]


def main():
    """Own at most three real processes under the declared30s/10s-ready budgets."""
    OUT.mkdir()
    project = OUT / 'project'
    shutil.copytree(SOURCE, project)
    settings = (project / 'project.godot').read_text()
    settings = re.sub(r'(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)', '', settings)
    (project / 'project.godot').write_text(settings)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    children, streams, record, ready_times = {}, [], {}, {}
    result = {'ok': False, 'start_unix': time.time(), 'supervisor_budget_s': 30,
              'per_process_after_ready_s': 10, 'processes': record}
    deadline = time.monotonic() + 30

    def save():
        """Keep complete lifecycle/argv/environment facts before and after each spawn."""
        (OUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n')

    def start(role):
        """Launch one owned role with three private XDG roots and separate raw streams."""
        folder = OUT / role
        folder.mkdir()
        env = {k: v for k, v in os.environ.items() if not k.startswith('GODOT_MCP_')}
        for key, name in [('XDG_DATA_HOME', 'data'), ('XDG_CONFIG_HOME', 'config'),
                          ('XDG_CACHE_HOME', 'cache')]:
            target = folder / name
            target.mkdir()
            env[key] = str(target)
        command = [ENGINE, '--headless', '--path', str(project), '--log-file',
                   str(folder / 'engine.log'), SCENE, '--', '--role=' + role,
                   '--port=' + str(port)]
        record[role] = {'argv': command, 'start_unix': time.time(),
                        'environment': {k: env[k] for k in ['XDG_DATA_HOME',
                            'XDG_CONFIG_HOME', 'XDG_CACHE_HOME']}, 'home_unchanged': True}
        save()
        stdout = (folder / 'stdout').open('wb')
        stderr = (folder / 'stderr').open('wb')
        streams.extend([stdout, stderr])
        child = subprocess.Popen(command, env=env, cwd=project, stdout=stdout, stderr=stderr)
        children[role] = child
        record[role]['owned_pid'] = child.pid
        save()

    try:
        start('host')
        while time.monotonic() < deadline:
            for role, child in list(children.items()):
                receipts = rows(OUT / role / 'stdout')
                if any(row['event'] == 'failure' for row in receipts):
                    raise RuntimeError('first production expectation failure: ' + role)
                if (OUT / role / 'stderr').read_text():
                    raise RuntimeError('runtime stderr diagnostic: ' + role)
                if child.poll() is not None and child.returncode != 0:
                    raise RuntimeError('nonzero process exit: ' + role)
                if any(row['event'] in ['ready', 'hydrate', 'fire'] for row in receipts):
                    ready_times.setdefault(role, time.monotonic())
                if child.poll() is None and role in ready_times and (
                        time.monotonic() - ready_times[role] > 10):
                    raise RuntimeError('10s after-ready deadline: ' + role)
            host = rows(OUT / 'host/stdout')
            if any(row['event'] == 'ready' for row in host) and 'client' not in children:
                start('client')
            if any(row['event'] == 'settled' for row in host) and 'late' not in children:
                start('late')
            if len(children) == 3 and all(child.poll() is not None for child in children.values()):
                break
            time.sleep(.01)
        else:
            raise RuntimeError('combined30s deadline')
        decoded = {role: rows(OUT / role / 'stdout') for role in children}
        host = next(row for row in decoded['host'] if row['event'] == 'network')
        live = next(row for row in decoded['client'] if row['event'] == 'client_state')
        late = next(row for row in decoded['late'] if row['event'] == 'hydrate')
        checks = {
            'host_health_literal_twelve_zero': [r['health'] for r in host['cut']['rows']] == [0]*12,
            'live_health_literal_twelve_zero': [r['health'] for r in live['cut']['rows']] == [0]*12,
            'settled_late_health_literal_twelve_zero': [r['health'] for r in late['cut']['rows']] == [0]*12,
            'all_outcomes_and_visits': host['damage'] == 12 and host['visits'] == 144,
            'eight_slots_four_drops': host['effects'] == 8 and host['effect_drops'] == 4,
            'actual_saved_instance_peak': host['saved_effects']['instances'] == 8 and
                                           host['saved_effects']['visual_peak'] == 8,
            'actual_live_dedup': live['live'] == 12 and live['duplicates'] == 12,
            'settled_hydration_no_history': late['effects'] == 0 and not late['input_enabled'],
            'three_distinct_native_processes': len({c.pid for c in children.values()}) == 3,
        }
        for role, receipts in decoded.items():
            final = [r for r in receipts if r['event'] == 'result']
            checks[role + '_result'] = len(final) == 1 and final[0]['ok']
            engine = (OUT / role / 'engine.log').read_text()
            checks[role + '_engine_diagnostics_absent'] = not re.search(r'ERROR:|WARNING:', engine)
        result.update(checks=checks, host=host, live=live, late=late, ok=all(checks.values()))
    except Exception as error:
        result['failure'] = repr(error)
    finally:
        for role, child in children.items():
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=2)
            else:
                child.wait()
            record[role].update(exit=child.returncode, end_unix=time.time())
        for stream in streams:
            stream.close()
        result.update(end_unix=time.time(), all_owned_children_reaped=True, streams_closed=True)
        save()
    print(json.dumps({'ok': result['ok'], 'failure': result.get('failure'),
                      'checks': result.get('checks'), 'directory': str(OUT)}))
    raise SystemExit(0 if result['ok'] else 1)


if __name__ == '__main__':
    main()
