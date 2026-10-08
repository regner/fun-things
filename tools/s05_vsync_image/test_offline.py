#!/usr/bin/env python3
"""Finite source/fake-clock checks of Card I's actual supervisor; no engine/socket executes."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def load_runner():
    """Load source without invoking its engine entrypoint."""
    spec = importlib.util.spec_from_file_location('card_i_runner', ROOT / 'tools/s05_vsync_image/run.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Clock:
    """Advance time only at declared blocking operations."""
    def __init__(self):
        self.now = 100.0

    def monotonic(self):
        return self.now

    def time(self):
        return self.now + 1000

    def sleep(self, duration):
        assert duration >= 0
        self.now += duration


class Child:
    """Represent one owned handle with normal or stubborn cleanup behavior."""
    def __init__(self, clock, pid, role, normal):
        self.clock, self.pid, self.role, self.normal = clock, pid, role, normal
        self.returncode, self.kill_time = None, None
        self.actions, self.waits = [], []
        self.reaped = False

    def poll(self):
        if self.role == 'import' and self.normal:
            self.returncode = 0
        if self.role != 'import' and self.normal and self.clock.now >= 112:
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
        assert timeout is not None and timeout >= 0
        self.waits.append((self.clock.now, timeout))
        if self.poll() is None:
            self.clock.sleep(timeout)
        if self.poll() is None:
            raise subprocess.TimeoutExpired('fake', timeout)
        self.reaped = True
        return self.returncode


class Socket:
    """Supply an OS-allocation-shaped receipt without opening any endpoint."""
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def bind(self, address):
        assert address == ('127.0.0.1', 0)

    def getsockname(self):
        return ('127.0.0.1', 55555)


def scenario(name, prep_seconds=3):
    """Drive the real main through normal/cutoff/failed-import/shared-cleanup branches."""
    module, clock = load_runner(), Clock()
    children, spawn_times = [], []
    real_read = Path.read_bytes
    real_digest = module.digest
    pin = b'fake-pin'
    with TemporaryDirectory(prefix='p0-image-offline-') as temporary:
        output = Path(temporary) / 'p0-image-fake-attempt01'
        def stage(target, _deadline):
            clock.sleep(prep_seconds)
            project = target / 'project'
            project.mkdir()
            (project / 'project.godot').write_bytes(b'fake-settings')
            return project, [{'path': 'project.godot', **real_digest(b'fake-settings')}]
        def read(path):
            return pin if str(path) == module.ENGINE else real_read(path)
        def digest(data):
            if data == b'fake-settings':
                clock.sleep(3)
            return real_digest(data)
        def popen(command, **_kwargs):
            role = 'import' if '--import' in command else next(
                arg.removeprefix('--role=') for arg in command if arg.startswith('--role='))
            cutoff = 190 if role == 'import' else min(210, 100 + prep_seconds + 20)
            assert clock.now < cutoff, 'post-cutoff spawn'
            spawn_times.append((role, clock.now))
            normal = name == 'normal' or role == 'import' and name != 'import-timeout'
            child = Child(clock, len(children) + 1, role, normal)
            children.append(child)
            if name == 'live-spawn-cutoff' and role == 'client':
                clock.sleep(20)
            return child
        def rows(path):
            return [{'event': 'ready'}, {'event': 'settled'}] if path.parent.name == 'host' else []
        def git(command, **_kwargs):
            return 'candidate\n' if command[1] == 'rev-parse' else b''
        with patch.object(module, 'time', clock), patch.object(module, 'stage', stage), \
             patch.object(module, 'digest', digest), patch.object(Path, 'read_bytes', read), \
             patch.object(module, 'ENGINE_SHA', real_digest(pin)['sha256']), \
             patch.object(module, 'socket_identity', lambda: {'owned': True}), \
             patch.object(module, 'identity', lambda c: {'pid': c.pid}), \
             patch.object(module, 'bound_endpoint', lambda c, p: {'port': p, 'address': '127.0.0.1'}), \
             patch.object(module, 'production_rows', rows), \
             patch.object(module.subprocess, 'check_output', git), \
             patch.object(module.subprocess, 'Popen', popen), \
             patch.object(module.socket, 'socket', lambda *_args: Socket()), \
             redirect_stdout(io.StringIO()):
            # A fresh direct-/tmp fake output exercises the real production path gate.
            fake_output = Path('/tmp') / (Path(temporary).name + '-attempt01')
            with patch.object(sys, 'argv', ['run.py', '--output', str(fake_output),
                                           '--candidate', 'candidate']):
                try:
                    exit_code = module.main()
                    receipt = json.loads((fake_output / 'lifecycle.json').read_text())
                finally:
                    import shutil
                    if fake_output.exists():
                        shutil.rmtree(fake_output)
        assert receipt['within_budget'] and receipt['elapsed_s'] <= 120
        assert receipt['streams_closed'] and receipt['source_preserved']
        assert receipt['all_owned_children_reaped'] and all(c.reaped for c in children)
        assert receipt['start_monotonic'] == 100 and receipt['absolute_deadline'] == 220
        assert receipt['readback_elapsed_s'] == 3
        if name == 'normal':
            assert exit_code == 0 and len(children) == 4 and not receipt['cleanup_phases']
        elif name == 'preparation-cutoff':
            assert exit_code == 1 and not children
        elif name == 'import-timeout':
            assert exit_code == 1 and len(children) == 1 and children[0].role == 'import'
            assert children[0].actions == [('interrupt', 190), ('terminate', 192), ('kill', 194)]
        elif name == 'live-spawn-cutoff':
            assert exit_code == 1 and len(children) == 3 and 'late' not in receipt['processes']
        else:
            assert exit_code == 1 and len(children) == 4
            assert receipt['elapsed_s'] == 32
            for child in children[1:]:
                assert child.actions == [('interrupt', 123), ('terminate', 125), ('kill', 127)]
        return {'name': name, 'exit': exit_code, 'spawns': spawn_times,
                'receipt': receipt, 'children': [{'role': c.role, 'actions': c.actions,
                    'waits': c.waits, 'reaped': c.reaped} for c in children]}


def evaluator_negatives():
    """Use immutable old streams as offline negative inputs, never as a new runtime receipt."""
    import gzip
    spec = importlib.util.spec_from_file_location('card_i_check', ROOT / 'tools/s05_vsync_image/check.py')
    check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(check)
    old = ROOT / 'docs/spikes/s05-render-observation-evidence/payloads/group02'
    with TemporaryDirectory(prefix='s05-offline-negative-') as temporary:
        group = Path(temporary)
        life = {'processes': {r: {} for r in ['import', 'host', 'client', 'late']},
                'collection_ok': True, 'source_preserved': True, 'streams_closed': True,
                'all_owned_children_reaped': True, 'within_budget': True, 'normal_exits': True,
                'bound_endpoint': {'address': '127.0.0.1'}, 'cleanup_phases': []}
        (group / 'lifecycle.json').write_text(json.dumps(life))
        for role in ['host', 'client', 'late']:
            folder = group / role
            (folder / 'data').mkdir(parents=True)
            (folder / 'stdout').write_bytes(gzip.decompress((old / role / 'stdout.gz').read_bytes()))
            (folder / 'data/draw.jsonl').write_bytes(
                gzip.decompress((old / role / 'draw.jsonl.gz').read_bytes()))
        result = check.evaluate(group)
        assert not result['receipt_checks_ok'] and not result['images']
        assert all(not result['checks'][r + '_required_stages'] for r in ['host', 'client', 'late'])
        assert all(not result['checks'][r + '_effective_vsync_disabled']
                   for r in ['host', 'client', 'late'])
        assert result['checks']['twelve_outcomes_144_visits'] and result['checks']['live_dedup']
        return {'input': 'historical group02 decoded offline ONLY', 'no_runtime': True,
                'missing_stages_rejected': True, 'unavailable_vsync_rejected': True,
                'old_gameplay_does_not_pass_new_images': True}


def main():
    """Assert literal aggregate bounds and shared grace for the actual runner's failure paths."""
    results = [scenario('normal'), scenario('three-stubborn'),
               scenario('preparation-cutoff', 90), scenario('import-timeout'),
               scenario('live-spawn-cutoff')]
    print(json.dumps({'engine_executed': False, 'real_socket_opened': False,
                      'cases': results, 'evaluator_negatives': evaluator_negatives()}, indent=2))


if __name__ == '__main__':
    main()
