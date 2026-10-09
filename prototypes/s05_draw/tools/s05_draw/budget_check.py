#!/usr/bin/env python3
"""Exercise supervisor time and owned cleanup using only fake clocks/children; never run Godot."""
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def load_runner():
    """Read the actual runner implementation without invoking its entrypoint."""
    spec = importlib.util.spec_from_file_location('s05_budget_runner', ROOT / 'tools/s05_draw/observe.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Clock:
    """Advance deterministically; timeout assertions cannot depend on a fast real machine."""
    def __init__(self):
        self.now = 100.0

    def monotonic(self):
        return self.now

    def time(self):
        return 1000.0 + self.now

    def sleep(self, duration):
        assert duration >= 0
        self.now += duration


class OwnedChild:
    """Represent only the fake Popen handle; three survivors share each fallback interval."""
    def __init__(self, clock, pid, normal_exit):
        self.clock, self.pid, self.normal_exit = clock, pid, normal_exit
        self.returncode = None
        self.actions = []
        self.waits = []
        self.kill_time = None
        self.reaped = False

    def poll(self):
        if self.normal_exit and self.clock.now >= 108:
            self.returncode = 0
        if self.kill_time is not None and self.clock.now >= self.kill_time + 2:
            self.returncode = -9
        return self.returncode

    def send_signal(self, value):
        assert value == signal.SIGINT
        self.actions.append(('interrupt', self.clock.now))

    def terminate(self):
        self.actions.append(('terminate', self.clock.now))

    def kill(self):
        self.actions.append(('kill', self.clock.now))
        self.kill_time = self.clock.now

    def wait(self, timeout=None):
        assert timeout is not None, 'no unbounded wait permitted'
        self.waits.append((self.clock.now, timeout))
        if self.poll() is None:
            self.clock.sleep(timeout)
        if self.poll() is None:
            raise subprocess.TimeoutExpired('fake-owned-child', timeout)
        self.reaped = True
        return self.returncode


class Socket:
    """Supply an owned fake loopback port without opening any real socket."""
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def bind(self, address):
        assert address == ('127.0.0.1', 0)

    def getsockname(self):
        return ('127.0.0.1', 55555)


def scenario(name, preparation_seconds, normal_exit=False, late_cutoff=False):
    """Check the full real main path with fake staging/Popen/time and actual private test receipts."""
    module = load_runner()
    clock = Clock()
    children, spawn_times = [], []
    copy_bytes = b'budgetcopy'
    expected_sha = hashlib.sha256(copy_bytes).hexdigest()
    real_sha = hashlib.sha256
    pin = b'fake-pinned-byte-read'
    with TemporaryDirectory(prefix='s05-budget-check-') as temporary:
        folder = Path(temporary)
        output = folder / 'group'
        route = folder / 'fake-wayland-socket'
        route.touch()

        def stage(_author, target, deadline):
            clock.sleep(preparation_seconds)
            project = target / 'project'
            project.mkdir()
            (project / 'input').write_bytes(copy_bytes)
            return project, [{'path': 'input', 'sha256': expected_sha}]

        def sha(data):
            if data == copy_bytes:
                clock.sleep(3)  # Explicitly exercise reserved preservation time.
            return real_sha(data)

        def popen(_command, **_kwargs):
            assert clock.now < 120, 'post-cutoff owned spawn'
            spawn_times.append(clock.now)
            child = OwnedChild(clock, len(children) + 1, normal_exit)
            children.append(child)
            if late_cutoff and len(children) == 2:
                clock.sleep(20)  # Spawn returns at cutoff before late is attempted.
            return child

        def rows(path):
            if path.parent.name == 'host':
                return [{'event': 'ready'}, {'event': 'settled'}]
            return []

        environment = {'HOME': os.environ['HOME'], 'XDG_RUNTIME_DIR': str(folder),
                       'WAYLAND_DISPLAY': route.name}
        stream = io.StringIO()
        with patch.object(module, 'time', clock), patch.object(module, 'stage', stage), \
             patch.object(module, 'rows', rows), patch.object(module, 'os',
                 SimpleNamespace(environ=environment)), \
             patch.object(module, 'stat', SimpleNamespace(S_ISSOCK=lambda _mode: True)), \
             patch.object(module, 'socket', SimpleNamespace(AF_INET=2, SOCK_DGRAM=2,
                                                          socket=lambda *_args: Socket())), \
             patch.object(module, 'open', lambda *_args, **_kwargs: io.BytesIO(pin), create=True), \
             patch.object(module, 'ENGINE_SHA', real_sha(pin).hexdigest()), \
             patch.object(module.subprocess, 'Popen', popen), \
             patch.object(module.hashlib, 'sha256', sha), \
             patch.object(sys, 'argv', ['observe.py', '--author-project', str(folder),
                                       '--output', str(output), '--group', '2']), \
             redirect_stdout(stream):
            exit_code = module.main()
        receipt = json.loads((output / 'lifecycle.json').read_text())
        assert receipt['elapsed_s'] <= 30 and receipt['within_supervisor_budget']
        assert receipt['copy_bytes_preserved'] and receipt['streams_closed']
        assert receipt['all_owned_children_reaped'] and all(child.reaped for child in children)
        assert receipt['start_monotonic'] == 100 and receipt['deadline_monotonic'] == 130
        assert all(t < 120 for t in spawn_times)
        if name == 'three-child-timeout':
            assert len(children) == 3 and exit_code == 1 and not receipt['collection_ok']
            assert receipt['elapsed_s'] == 29
            for child in children:
                assert child.actions == [('interrupt', 120), ('terminate', 122), ('kill', 124)]
                assert child.waits and child.reaped
            assert all(record['terminate_fallback'] and record['kill_fallback'] and record['reaped']
                       for record in receipt['processes'].values())
        elif name == 'preparation-cutoff':
            assert not children and exit_code == 1
        elif name == 'late-spawn-cutoff':
            assert len(children) == 2 and 'late' not in receipt['processes'] and exit_code == 1
            for child in children:
                assert child.actions[1][1] - child.actions[0][1] == 2
        else:
            assert len(children) == 3 and exit_code == 0 and receipt['collection_ok']
            assert all(not child.actions for child in children)
        return {'name': name, 'exit': exit_code, 'spawns': spawn_times,
                'children': [{'pid': c.pid, 'actions': c.actions, 'waits': c.waits,
                              'reaped': c.reaped} for c in children], 'receipt': receipt}


def main():
    """Assert literal aggregate bounds, preserved copies, no late spawn and full shared grace."""
    results = [scenario('three-child-timeout', 3), scenario('preparation-cutoff', 20),
               scenario('normal-completion', 3, normal_exit=True),
               scenario('late-spawn-cutoff', 0, late_cutoff=True)]
    print(json.dumps({'engine_executed': False, 'cases': results}, indent=2))


if __name__ == '__main__':
    main()
