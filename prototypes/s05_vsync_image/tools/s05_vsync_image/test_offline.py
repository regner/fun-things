#!/usr/bin/env python3
"""Finite source/fake-clock checks of Card I's actual supervisor; no engine/socket executes."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
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
            if name == 'slow-generated':
                (project / '.godot').mkdir()
                (project / '.godot/last-generated').write_bytes(b'fake-generated')
            return project, [{'path': 'project.godot', **real_digest(b'fake-settings')}]
        def read(path):
            return pin if path.as_posix() == module.ENGINE else real_read(path)
        def digest(data):
            if data == b'fake-generated':
                clock.sleep(100)
            if data == b'fake-settings':
                clock.sleep(5 if name == 'slow-readback' else 3)
            return real_digest(data)
        def popen(command, **_kwargs):
            role = 'import' if '--import' in command else next(
                arg.removeprefix('--role=') for arg in command if arg.startswith('--role='))
            cutoff = 190 if role == 'import' else min(210, 100 + prep_seconds + 20)
            assert clock.now < cutoff, 'post-cutoff spawn'
            spawn_times.append((role, clock.now))
            normal = name in ['normal', 'slow-generated', 'slow-readback'] or (
                role == 'import' and name != 'import-timeout')
            child = Child(clock, len(children) + 1, role, normal)
            children.append(child)
            if name == 'live-spawn-cutoff' and role == 'client':
                clock.sleep(20)
            return child
        def rows(path):
            return [{'event': 'ready'}, {'event': 'settled'}] if path.parent.name == 'host' else []
        def git(command, **_kwargs):
            return 'candidate\n' if command[1] == 'rev-parse' else b''
        fake_output = Path('/tmp') / ('p0-image-' + Path(temporary).name + '-attempt01')
        real_resolve = Path.resolve
        private_environment = (module.private_environment if os.name != 'nt'
                               else lambda _folder: os.environ.copy())
        def resolve(path, *args, **kwargs):
            return path if path == fake_output else real_resolve(path, *args, **kwargs)
        with patch.object(module, 'time', clock), patch.object(module, 'stage', stage), \
             patch.object(module, 'digest', digest), patch.object(Path, 'read_bytes', read), \
             patch.object(Path, 'resolve', resolve), \
             patch.object(module, 'ENGINE_SHA', real_digest(pin)['sha256']), \
             patch.object(module, 'socket_identity', lambda: {'owned': True}), \
             patch.object(module, 'identity', lambda c: {'pid': c.pid}), \
             patch.object(module, 'bound_endpoint', lambda c, p, r: {'port': p, 'address': '127.0.0.1'}), \
             patch.object(module, 'production_rows', rows), \
             patch.object(module, 'private_environment', private_environment), \
             patch.object(module.subprocess, 'check_output', git), \
             patch.object(module.subprocess, 'Popen', popen), \
             patch.object(module.socket, 'socket', lambda *_args: Socket()), \
             redirect_stdout(io.StringIO()):
            # A fresh direct-/tmp fake output exercises the real production path gate.
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
        assert receipt['streams_closed']
        assert receipt['source_preserved'] == (name != 'slow-readback'), receipt
        assert receipt['all_owned_children_reaped'] and all(c.reaped for c in children)
        assert receipt['start_monotonic'] == 100 and receipt['absolute_deadline'] == 220
        assert receipt['readback_elapsed_s'] == (5 if name == 'slow-readback' else 3)
        if name == 'slow-generated':
            assert exit_code == 1 and len(children) == 1 and children[0].role == 'import'
            assert not receipt['preparation_within_budget'] and 'host' not in receipt['processes']
            assert receipt['elapsed_s'] == 106
        elif name == 'slow-readback':
            assert exit_code == 1 and len(children) == 4 and not receipt['readback_within_budget']
            assert math.isclose(receipt['elapsed_s'], 17, abs_tol=.01)
        elif name == 'normal':
            assert exit_code == 0 and len(children) == 4 and not receipt['cleanup_phases'], (
                receipt, children)
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
    # Scalar telemetry tests create no PNG/callback/effect and grant no image credit.
    sizes = {'viewport': [1280, 800], 'window_size': [2112, 1320],
             'requested_project_size': [1280, 800]}
    check.validate_sizes([2112, 1320], [2112, 1320], sizes)
    try:
        check.validate_sizes([2112, 1320], [1280, 800], sizes)
    except AssertionError:
        pass
    else:
        raise AssertionError('PNG header versus receipt mismatch was accepted')
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


def endpoint_cases():
    """Test corrected lookup against literal SYNTHETIC proc inputs, never post-exit evidence."""
    from types import SimpleNamespace
    module = load_runner()
    results = []
    for name, table, address, inode, duplicate in [
            ('ipv4', 'udp', '0100007F', '77', False),
            ('ipv4-mapped', 'udp6', '0000000000000000FFFF00000100007F', '77', False),
            ('external-bind', 'udp', '00000000', '77', False),
            ('wrong-owner', 'udp', '0100007F', '88', False),
            ('ambiguous', 'udp', '0100007F', '77', True)]:
        with TemporaryDirectory(prefix='s05-synthetic-proc-') as temporary:
            root = Path(temporary)
            proc = root / 'proc/123'
            (proc / 'fd').mkdir(parents=True)
            (proc / 'net').mkdir()
            (proc / 'fd/10').touch()
            for filename in ['udp', 'udp6']:
                (proc / 'net' / filename).write_text('header\n')
            row = f'0: {address}:D903 00000000:0000 07 0:0 0:0 0 1000 0 {inode} 2\n'
            (proc / 'net' / table).write_text('header\n' + row + (row if duplicate else ''))
            actual_path = Path
            with patch.object(module, 'Path', lambda p: root / 'proc' if str(p) == '/proc'
                              else actual_path(p)), \
                 patch.object(module.os, 'readlink', lambda _path: 'socket:[77]'):
                try:
                    result = module.bound_endpoint(SimpleNamespace(pid=123), 55555, root / 'lookup.json')
                    accepted = True
                    assert result['address'] == '127.0.0.1' and result['inode'] == '77'
                except RuntimeError:
                    accepted = False
            assert accepted == (name in ['ipv4', 'ipv4-mapped'])
            lookup = json.loads((root / 'lookup.json').read_text())
            assert table in lookup['tables'] and lookup['handles']['10'] == 'socket:[77]'
            results.append({'case': name, 'accepted': accepted, 'synthetic_inputs': lookup})
    return results


class OfflineChecks(unittest.TestCase):
    """Expose the standalone offline checks to repository-wide unittest discovery."""

    def test_supervisor_failure_paths(self):
        """Exercise aggregate bounds and shared cleanup grace across supervisor outcomes."""
        for name, prep_seconds in [('normal', 3), ('three-stubborn', 3),
                                   ('preparation-cutoff', 90), ('import-timeout', 3),
                                   ('live-spawn-cutoff', 3), ('slow-generated', 3),
                                   ('slow-readback', 3)]:
            with self.subTest(name=name):
                scenario(name, prep_seconds)

    def test_evaluator_rejects_historical_streams(self):
        """Reject historical streams that omit current image and lifecycle evidence."""
        evaluator_negatives()

    def test_endpoint_probe_cases(self):
        """Accept only uniquely owned loopback endpoints in the synthetic proc table."""
        endpoint_cases()


def main():
    """Assert literal aggregate bounds and shared grace for the actual runner's failure paths."""
    results = [scenario('normal'), scenario('three-stubborn'),
               scenario('preparation-cutoff', 90), scenario('import-timeout'),
               scenario('live-spawn-cutoff'), scenario('slow-generated'), scenario('slow-readback')]
    print(json.dumps({'engine_executed': False, 'real_socket_opened': False,
                      'cases': results, 'evaluator_negatives': evaluator_negatives(),
                      'corrected_probe_synthetic_cases': endpoint_cases()}, indent=2))


if __name__ == '__main__':
    main()
