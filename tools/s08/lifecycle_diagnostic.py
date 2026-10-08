#!/usr/bin/env python3
"""One log-only debug ENet diagnostic, with one absolute setup/runtime/cleanup deadline."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools/s08'))
from run_s03 import Proxy
from handoff_cleanup import cleanup
from observe import environment

ENGINE = Path('/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot')
ENGINE_SHA = '6aea356032435e7af19dbfbf48dd20c5012a7dc1267eb8e92406f44e3584b5fd'
TOTAL_SECONDS = 30.0
WORK_SECONDS = 20.0


def save(path, value):
    """Retain complete structured receipts, not just successful events."""
    path.write_text(json.dumps(value, indent=2) + '\n')


class ObservedSocket:
    """Observe actual UDP receive/send sizes without changing the existing fault schedule."""

    def __init__(self, owned, stream):
        self.owned, self.stream = owned, stream
        self.counts = {'recv_datagrams': 0, 'recv_bytes': 0, 'send_datagrams': 0, 'send_bytes': 0}

    def record(self, direction, data, endpoint):
        """Retain one actual transport observation in the supervisor monotonic clock."""
        self.counts[direction + '_datagrams'] += 1
        self.counts[direction + '_bytes'] += len(data)
        self.stream.write(json.dumps({'event': direction, 'monotonic': time.monotonic(),
            'clock_domain': 'supervisor_python_monotonic', 'endpoint': endpoint,
            'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}) + '\n')
        self.stream.flush()

    def recvfrom(self, limit):
        """Observe packets returned by the owned socket, including nonscheduled traffic."""
        data, source = self.owned.recvfrom(limit)
        self.record('recv', data, source)
        return data, source

    def sendto(self, data, target):
        """Count only actual successful OS sends, preserving every transmitted byte."""
        sent = self.owned.sendto(data, target)
        if sent != len(data):
            raise RuntimeError('partial UDP send')
        self.record('send', data, target)
        return sent

    def close(self):
        """Close only this set's owned endpoint."""
        self.owned.close()


def main():
    """Capture lifecycle ordering through the actual S03 APIs without outcome repair."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--author-project', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    absolute = started + TOTAL_SECONDS
    work = started + WORK_SECONDS
    directory = args.output.resolve()
    if directory.exists() or not directory.is_relative_to(Path('/tmp')):
        parser.error('fresh private /tmp evidence directory required')
    directory.mkdir(mode=0o700, parents=True)
    children, streams, commands, offsets, results = [], [], {}, {}, {}
    proxy = None
    record = {'ok': False, 'diagnostic_only': True, 'revision': args.revision,
        'started_monotonic': started, 'absolute_deadline': absolute,
        'work_deadline': work, 'observations': [], 'commands': commands,
        'clock_contract': 'Godot ticks_usec is per-engine elapsed, not cross-process; '
                          'Python monotonic timestamps/exit observations share one parent domain.'}
    try:
        with ENGINE.open('rb') as source:
            if hashlib.file_digest(source, 'sha256').hexdigest() != ENGINE_SHA:
                raise RuntimeError('pinned DEBUG engine hash differs')
        project = directory / 'project'
        project.mkdir()
        paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', args.revision,
            'tests/fixtures/s03'], cwd=ROOT, text=True).splitlines()
        manifest = []
        for name in paths:
            data = subprocess.check_output(['git', 'show', args.revision + ':' + name], cwd=ROOT)
            if (args.author_project / name).read_bytes() != data:
                raise RuntimeError('saved private author input differs: ' + name)
            target = project / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            manifest.append({'path': name, 'bytes': len(data),
                             'sha256': hashlib.sha256(data).hexdigest()})
        source = subprocess.check_output(['git', 'show', args.revision + ':project.godot'],
                                         cwd=ROOT).decode()
        import re
        source = re.sub(r'(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)', '', source)
        source = source.replace('config/icon="res://icon.svg"\n', '')
        source = source.replace('[application]\n', '[application]\n'
            'run/main_scene="res://tests/fixtures/s03/boot.tscn"\n')
        (project / 'project.godot').write_text(source)
        cache = project / '.godot'
        cache.mkdir()
        # Reuse only owned initial-editor discovery. No fresh import or shared cache.
        class_data = (args.author_project / '.godot/global_script_class_cache.cfg').read_text()
        blocks = re.findall(r'\{.*?\}', class_data, re.S)
        selected = [block for block in blocks if 'res://tests/fixtures/s03/' in block]
        if len(selected) != 7:
            raise RuntimeError('private S03 class discovery differs')
        (cache / 'global_script_class_cache.cfg').write_text('list=Array[Dictionary]([' +
            ', '.join(selected) + '])\n')
        (cache / 'uid_cache.bin').write_bytes((args.author_project / '.godot/uid_cache.bin').read_bytes())
        save(directory / 'staged-input.json', manifest)
        readiness_deadline = started + 4.0
        proxy_log = (directory / 'proxy.jsonl').open('w')
        traffic = (directory / 'traffic.jsonl').open('w')
        streams.extend([proxy_log, traffic])
        # At most one owned socket at a time. A bind race fails, never steals a port.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.bind(('127.0.0.1', 0))
            host_port = probe.getsockname()[1]
        proxy = Proxy(host_port, 0, proxy_log)
        proxy_port = proxy.socket.getsockname()[1]
        if proxy_port == host_port:
            raise RuntimeError('ephemeral host/proxy endpoints coincide')
        observed = ObservedSocket(proxy.socket, traffic)
        proxy.socket = observed
        record['ports'] = {'host': host_port, 'proxy': proxy_port}

        def start(role, port):
            """Launch one actual owned child with separate XDG/log paths and command receipt."""
            logs = directory / role
            logs.mkdir()
            (logs / 'engine.log').touch()
            env = environment(logs / 'user')
            argv = ['/usr/bin/stdbuf', '-oL', str(ENGINE), '--headless', '--path', str(project),
                '--log-file', str(logs / 'engine.log'), '--', '--role=' + role, '--port=' + str(port)]
            out, err = (logs / 'stdout.log').open('wb'), (logs / 'stderr.log').open('wb')
            streams.extend([out, err])
            if role == 'client' and time.monotonic() >= readiness_deadline:
                raise RuntimeError('client handoff expired before Popen')
            command = {'argv': argv, 'cwd': str(project), 'start_monotonic': time.monotonic(),
                'environment': {key: env[key] for key in env if key.startswith('XDG_')},
                'home_unchanged': env.get('HOME') == os.environ.get('HOME')}
            child = subprocess.Popen(argv, cwd=project, env=env, stdout=out, stderr=err)
            children.append(child)
            command['pid'] = child.pid
            commands[role] = command
            offsets[role] = 0
            save(logs / 'command.json', command)
            return child

        host = start('host', host_port)
        client = None
        ready = False
        observed_exits = set()
        while time.monotonic() < work:
            proxy.poll()
            failed = False
            for role, command in list(commands.items()):
                child = children[0 if role == 'host' else 1]
                polled = child.poll()
                if polled is not None and role not in observed_exits:
                    observed_exits.add(role)
                    record['observations'].append({'event': 'exit_observed', 'role': role,
                        'exit': polled, 'monotonic': time.monotonic()})
                with (directory / role / 'stdout.log').open() as output:
                    output.seek(offsets[role])
                    while True:
                        position = output.tell()
                        line = output.readline()
                        if not line.endswith('\n'):
                            offsets[role] = position
                            break
                        offsets[role] = output.tell()
                        if not line.startswith('S03 '):
                            continue
                        event = json.loads(line[4:])
                        record['observations'].append({'role': role, 'monotonic': time.monotonic(),
                            'host_poll': host.poll(), 'child_poll': child.poll(), 'record': event})
                        if event['event'] == 'ready' and role == 'host':
                            ready = True
                        elif event['event'] == 'snapshots' and role == 'host':
                            proxy.armed = True
                            proxy.record('armed')
                        elif event['event'] == 'result':
                            results[role] = event
                            failed |= event.get('ok') is not True
            if failed:
                record['failure'] = 'actual S03 failed result; full streams retained'
                break
            if client is None:
                if time.monotonic() >= readiness_deadline:
                    raise RuntimeError('readiness expired')
                if ready:
                    if host.poll() is not None:
                        raise RuntimeError('host not live at handoff')
                    client = start('client', proxy_port)
            if len(results) == 2 and all(child.poll() is not None for child in children):
                record['ok'] = all(event['ok'] for event in results.values())
                break
            if any(child.poll() is not None for child in children):
                if any(role not in results for role in observed_exits):
                    raise RuntimeError('child exit before result')
            time.sleep(0.01)
        else:
            record['failure'] = '20s aggregate work deadline'
        record.update(results=results, traffic=observed.counts, proxy_count=proxy.count,
                      proxy_events=proxy.events)
    except Exception as error:
        record['failure'] = repr(error)
        traceback.print_exc()
    finally:
        details = cleanup(children, streams, proxy, None, absolute)
        record['cleanup'] = details
        for role, command in commands.items():
            index = 0 if role == 'host' else 1
            command.update(exit=children[index].returncode, reaped=details['children_reaped'][index])
            save(directory / role / 'command.json', command)
        record['end_monotonic'] = time.monotonic()
        record['duration_seconds'] = record['end_monotonic'] - started
        record['within_30s'] = record['end_monotonic'] <= absolute
        if (details['errors'] or not details['all_children_reaped']
                or not details['streams_closed'] or not details['proxy_closed']
                or not record['within_30s']):
            record['ok'] = False
        save(directory / 'result.json', record)
        print(json.dumps({'ok': record['ok'], 'duration': record['duration_seconds'],
                          'failure': record.get('failure')}))
    return 0 if record['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
