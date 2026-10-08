#!/usr/bin/env python3
"""Independent fake-clock/handle/pipe expectations for S08 review boundaries; no engine."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace
from unittest.mock import patch

import observe
from handoff_cleanup import cleanup


class Clock:
    """Advance only by declared fixture events and simulated waits."""
    def __init__(self, now=0.0):
        """Start at an independent, specified elapsed time."""
        self.value = now

    def now(self):
        """Read the controlled time without an implicit tick."""
        return self.value

    def sleep(self, seconds):
        """Consume only the requested nonnegative interval."""
        assert seconds >= 0
        self.value += seconds


class Handle:
    """Owned fake process which may resist waits/signals and inject failures."""
    def __init__(self, clock, index, resistant=False, faults=(), reap_delay=1.9):
        """Assign independent resistance and error expectations."""
        self.clock, self.index, self.resistant = clock, index, resistant
        self.faults, self.reap_delay = set(faults), reap_delay
        self.pid, self.returncode, self.killed_at = 9000+index, None, None
        self.calls = []

    def poll(self):
        """Expose only completion that the fixture has actually made observable."""
        if 'poll' in self.faults:
            raise OSError('injected poll error')
        if self.killed_at is not None and self.reap_delay is not None:
            if self.clock.now() >= self.killed_at+self.reap_delay:
                self.returncode = -9
        return self.returncode

    def wait(self, timeout):
        """Consume a bounded timeout or the remaining concurrent kill-to-reap interval."""
        assert timeout >= 0
        self.calls.append({'operation':'wait', 'at':self.clock.now(), 'timeout':timeout})
        if 'wait' in self.faults:
            raise OSError('injected wait error')
        if not self.resistant:
            self.returncode = 1
            return 1
        if self.killed_at is not None and self.reap_delay is not None:
            remaining=max(0.0, self.killed_at+self.reap_delay-self.clock.now())
            if remaining <= timeout:
                self.clock.sleep(remaining)
                self.returncode = -9
                return -9
        self.clock.sleep(timeout)
        raise subprocess.TimeoutExpired('fake-owned-handle', timeout)

    def send_signal(self, _signal):
        """Record an owned interrupt, optionally failing without touching a process."""
        self.calls.append({'operation':'interrupt', 'at':self.clock.now()})
        if 'signal' in self.faults:
            raise OSError('injected signal error')

    def terminate(self):
        """Record an owned terminate, independently of previous failures."""
        self.calls.append({'operation':'terminate', 'at':self.clock.now()})
        if 'terminate' in self.faults:
            raise OSError('injected terminate error')

    def kill(self):
        """Start concurrent fake final completion or inject a final signal failure."""
        self.calls.append({'operation':'kill', 'at':self.clock.now()})
        if 'kill' in self.faults:
            raise OSError('injected kill error')
        self.killed_at = self.clock.now()


class Stream:
    """Independent stream-close expectation, including an explicit close failure."""
    def __init__(self, fail=False):
        """Start with an open fake stream."""
        self.closed, self.attempted, self.fail = False, False, fail

    def close(self):
        """Retain the attempted close even if it raises."""
        self.attempted = True
        if self.fail:
            raise OSError('injected close error')
        self.closed = True


def readiness(task, scenario, chunks, expected_launches, setup_expiry=False):
    """Feed real pipe fragments into the actual file consumer at independent times."""
    task.mkdir()
    clock = Clock()
    handles = []
    read_fd, write_fd = os.pipe()
    os.set_blocking(read_fd, False)
    pipe_closed = False
    polls = 0
    socket = Stream()

    class Proxy:
        """Inject producer fragments without a socket or engine process."""
        events = []
        count = 0

        def __init__(self, *_args):
            """Use a fake endpoint whose closure is independently observable."""
            self.socket = socket

        def poll(self):
            """Publish a scheduled fragment then stop the fake run after observation."""
            nonlocal polls
            if polls >= len(chunks):
                raise RuntimeError('fixture end; no actual gameplay simulated')
            when, data = chunks[polls]
            clock.value = when
            os.write(write_fd, data)
            received = os.read(read_fd, len(data))
            assert received == data
            with (task/'enet/host/stdout.log').open('ab') as log:
                log.write(received)
            polls += 1

    def launch(argv, **_kwargs):
        """Count actual mock Popen requests independently of consumer flags."""
        assert argv[-2].startswith('--role=')
        handle = Handle(clock, len(handles))
        handles.append(handle)
        return handle

    def environment(_directory):
        """Expire client preparation independently of the earlier loop-level check."""
        if setup_expiry and len(handles) == 1:
            clock.sleep(0.002)
        return {}

    fake_time = SimpleNamespace(monotonic=clock.now, time=lambda:1000+clock.now(), sleep=lambda _:None)
    try:
        with patch.object(observe, 'time', fake_time), patch.object(observe, 'Proxy', Proxy), \
                patch.object(observe.subprocess, 'Popen', launch):
            try:
                observe.network(task, env_factory=environment)
            except RuntimeError:
                pass
            else:
                raise AssertionError('fake run must end without gameplay acceptance')
    finally:
        os.close(read_fd)
        os.close(write_fd)
        pipe_closed = True
    result=json.loads((task/'enet/result.json').read_text())
    assert len(handles) == expected_launches
    assert result['host_ready_before_client'] == (expected_launches == 2)
    assert result['all_children_reaped'] and result['streams_closed']
    assert result['proxy_closed'] and result['proxy_log_closed'] and socket.closed
    if expected_launches == 2:
        assert result['handoff_seconds'] < 4.0
    if 'coalesced' in scenario:
        assert 'S03 assertion failed' in result['failure']
    elif expected_launches == 1:
        assert 'readiness deadline' in result['failure']
    return {'scenario':scenario, 'launch_requests':len(handles), 'pipe_closed':pipe_closed,
            'result':result}


def cleanup_cases():
    """Verify independent 30s cap and every later cleanup after injected errors."""
    rows=[]
    cases=[('two-resistant', (), 1.9), ('signal-error', ('signal',), 1.9),
           ('wait-error', ('wait',), 1.9), ('poll-error', ('poll',), 1.9),
           ('terminate-error', ('terminate',), 1.9), ('kill-error', ('kill',), 1.9),
           ('final-reap-timeout', (), None)]
    for name, faults, delay in cases:
        clock=Clock(20.0)
        first=Handle(clock, 0, resistant=True, faults=faults, reap_delay=delay)
        second=Handle(clock, 1, resistant=True, reap_delay=1.9)
        streams=[Stream(fail=True), Stream()] if name == 'signal-error' else [Stream(), Stream()]
        socket, log=Stream(), Stream()
        result=cleanup([first,second], streams, SimpleNamespace(socket=socket), log, 30.0,
                       now=clock.now)
        assert clock.now() <= 30.0, 'independent absolute set cap'
        assert all(s.attempted for s in streams) and socket.closed and log.closed
        assert any(x['operation']=='kill' for x in second.calls), 'later child still escalated'
        assert result['children_reaped'][1], 'later child independently reaped'
        assert first.calls[0]['operation']=='wait' and first.calls[0]['at']==20.0
        if name == 'two-resistant':
            assert result['all_children_reaped'] and not result['errors']
            assert clock.now() == 27.9
            assert [x['at'] for x in first.calls if x['operation']=='kill'] == [26.0]
            assert [x['at'] for x in second.calls if x['operation']=='kill'] == [26.0]
        else:
            assert result['errors']
        if name in ['wait-error','kill-error','final-reap-timeout','poll-error']:
            assert not result['children_reaped'][0] and not result['all_children_reaped']
        if name == 'signal-error':
            assert not result['streams_closed']
        rows.append({'case':name, 'clock_end':clock.now(), 'first':first.calls,
                     'second':second.calls, 'cleanup':result})
    return rows


def receipt_after_errors(task):
    """Exercise the network finally path: errors cannot skip other handles or receipt."""
    task.mkdir()
    clock=Clock()
    handles=[]
    socket=Stream()
    polls=0

    class Proxy:
        """Publish readiness then inject a work failure with two handles owned."""
        events=[]
        count=0

        def __init__(self, *_args):
            """Attach only the fake close contract."""
            self.socket=socket

        def poll(self):
            """Ensure the network path reaches cleanup with both handles."""
            nonlocal polls
            if polls:
                clock.value=20.0
                raise RuntimeError('injected work failure')
            (task/'enet/host/stdout.log').write_bytes(b'S03 {"event":"ready"}\n')
            polls+=1

    def launch(_argv, **_kwargs):
        """Inject first-handle signal/wait errors and second-handle resistance."""
        faults=('signal','wait') if not handles else ()
        h=Handle(clock,len(handles),resistant=True,faults=faults)
        handles.append(h)
        return h

    fake_time=SimpleNamespace(monotonic=clock.now,time=lambda:1000+clock.now(),sleep=lambda _:None)
    with patch.object(observe,'time',fake_time), patch.object(observe,'Proxy',Proxy), \
            patch.object(observe.subprocess,'Popen',launch):
        try:
            observe.network(task,env_factory=lambda _: {})
        except RuntimeError:
            pass
        else:
            raise AssertionError('cleanup errors must not be reported as success')
    result=json.loads((task/'enet/result.json').read_text())
    assert not result['ok'] and not result['all_children_reaped']
    assert result['cleanup']['children_reaped']==[False,True]
    assert result['cleanup']['errors'] and result['streams_closed']
    assert result['proxy_closed'] and result['proxy_log_closed'] and socket.closed
    assert (task/'enet/client/command.json').is_file()
    assert json.loads((task/'enet/host/command.json').read_text())['child_reaped'] is False
    assert json.loads((task/'enet/client/command.json').read_text())['child_reaped'] is True
    assert clock.now() <= 30.0
    return result


def main():
    """Retain every original boundary scenario and complete result without runtime."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    args.output.mkdir()
    ready=b'S03 {"event":"ready"}\n'
    failure=b'S03 {"event":"result","ok":false}\n'
    scenarios=[('before',[(3.999,ready)],2,False), ('at',[(4.0,ready)],1,False),
               ('after',[(4.001,ready)],1,False),
               ('fragment-late',[(3.99,ready[:-1]),(4.001,b'\n')],1,False),
               ('coalesced-before',[(3.999,ready+failure)],1,False),
               ('coalesced-after',[(4.001,ready+failure)],1,False),
               ('setup-expiry',[(3.999,ready)],1,True)]
    result={'readiness':[readiness(args.output/name,name,chunks,count,setup)
                        for name,chunks,count,setup in scenarios],
            'cleanup':cleanup_cases(), 'network_receipt':receipt_after_errors(args.output/'errors')}
    observe.write_json(args.output/'result.json', result)
    print(json.dumps({'ok':True,'readiness_cases':7,'cleanup_cases':7,
                      'network_receipt_after_errors':True,'engine_network_operations':0}))


if __name__ == '__main__':
    main()
