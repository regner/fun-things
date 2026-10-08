#!/usr/bin/env python3
"""Independent offline buffering and coordination expectations; no engine or socket."""
import argparse
import contextlib
import json
from pathlib import Path
import subprocess
import tempfile
import time
from unittest.mock import patch

import observe

C_SOURCE = r'''
#include <stdarg.h>
#include <stdio.h>
#include <unistd.h>
static void log_record(const char *format, ...) {
    va_list args;
    va_start(args, format);
    vprintf(format, args);
    va_end(args);
}
int main(void) {
    log_record("S08 {\"ok\":true,\"padding\":\"");
    for (int i=0; i<22000; ++i) log_record("x");
    log_record("\"}\n");
    log_record("S03 {\"event\":\"ready\"}\n");
    usleep(700000);
    log_record("S03 {\"event\":\"result\",\"ok\":false}\n");
    return 1;
}
'''


def buffering(directory):
    """Require readiness while the child is live, independently of exit flushing."""
    source = directory/'logger.c'
    source.write_text(C_SOURCE)
    compile_argv = ['/usr/bin/cc', '-Wall', '-Wextra', '-Werror', str(source),
                    '-o', str(directory/'logger')]
    compiled = subprocess.run(compile_argv, capture_output=True, timeout=5)
    (directory/'compile.stdout').write_bytes(compiled.stdout)
    (directory/'compile.stderr').write_bytes(compiled.stderr)
    assert compiled.returncode == 0
    rows = []
    for name, prefix in [('regular', []), ('line-buffered', ['/usr/bin/stdbuf', '-oL'])]:
        argv = prefix+[str(directory/'logger')]
        start = time.monotonic()
        with (directory/(name+'.stdout')).open('wb') as out, \
                (directory/(name+'.stderr')).open('wb') as err:
            child = subprocess.Popen(argv, stdout=out, stderr=err)
            try:
                time.sleep(0.15)
                early = (directory/(name+'.stdout')).read_bytes()
                live = child.poll() is None
                assert live
                ready = b'S03 {"event":"ready"}\n' in early
                assert ready == (name == 'line-buffered')
                assert b'"event":"result"' not in early
                assert child.wait(timeout=2) == 1
            finally:
                if child.poll() is None:
                    child.terminate()
                    child.wait(timeout=2)
        final = (directory/(name+'.stdout')).read_bytes()
        assert b'S03 {"event":"ready"}\n' in final
        assert b'"event":"result"' in final
        rows.append({'name':name, 'argv':argv, 'exit':child.returncode,
                     'early_bytes':len(early), 'ready_at_150ms':ready, 'child_live':live,
                     'duration_seconds':time.monotonic()-start})
    return {'compile_argv':compile_argv, 'compile_exit':compiled.returncode, 'runs':rows}


def coordination(directory):
    """Exercise the actual file consumer against partial, coalesced and silent streams."""
    rows = []
    for case in ['partial', 'coalesced-failure', 'silent-deadline']:
        task = directory/case
        task.mkdir()
        calls = []
        state = {'polls':0}
        ready = b'S03 {"event":"ready","role":"host"}\n'
        failure = b'S03 {"event":"result","ok":false}\n'

        class Child:
            """Owned fake handle; deliberately stays live through stream injection."""
            pid = 123
            returncode = None

            def poll(self):
                """Expose the controlled process state."""
                return self.returncode

            def wait(self, timeout):
                """Complete only during final cleanup, without operating a process."""
                self.returncode = 1
                return 1

        class Proxy:
            """Inject file fragments without opening a socket."""
            count = 0
            events = []

            def __init__(self, *_args):
                """Supply only the socket-close contract used by the consumer."""
                self.socket = self

            def close(self):
                """Close the fake endpoint."""
                pass

            def poll(self):
                """Advance independent stream scenarios once per consumer poll."""
                state['polls'] += 1
                if case == 'silent-deadline':
                    return
                path = task/'enet/host/stdout.log'
                if state['polls'] == 1:
                    path.write_bytes(ready[:-1] if case == 'partial' else ready+failure)
                elif state['polls'] == 2:
                    assert len(calls) == 1, 'partial readiness must not launch a client'
                    path.write_bytes(ready+failure)

        def launch(argv, **_kwargs):
            """Record only simulated child requests; prohibit any real launcher."""
            calls.append(argv)
            assert len(calls) == 1, 'failed or incomplete host must not launch client'
            return Child()

        def env(directory):
            """Avoid even creating runtime environment directories in this test."""
            return {}

        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(observe, 'Proxy', Proxy))
            stack.enter_context(patch.object(observe.subprocess, 'Popen', launch))
            try:
                observe.network(task, env_factory=env, readiness_seconds=0.04)
            except RuntimeError:
                pass
            else:
                raise AssertionError('scenario must fail')
        result = json.loads((task/'enet/result.json').read_text())
        assert len(calls) == 1 and not result['host_ready_before_client']
        assert result['all_children_reaped'] and result['streams_closed'] and result['proxy_closed']
        if case == 'silent-deadline':
            assert 'readiness deadline' in result['failure']
            assert 'ready' not in result
        else:
            assert 'S03 assertion failed' in result['failure']
            assert result['ready']['event'] == 'ready'
        rows.append({'case':case, 'launcher_calls':len(calls), 'result':result})
    return rows


def main():
    """Retain complete actual offline streams and independently checked receipts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir()
    result = {'buffering':buffering(args.output), 'coordination':coordination(args.output)}
    observe.write_json(args.output/'result.json', result)
    print(json.dumps({'ok':True, 'buffering_runs':2, 'coordination_cases':3}))


if __name__ == '__main__':
    main()
