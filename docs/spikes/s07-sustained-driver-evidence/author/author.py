"""One private editor; installed standard discovery/authentication and saved inherited authoring."""
import argparse
import hashlib
import json
from pathlib import Path
import select
import shutil
import socket
import subprocess
import time

from support import ROOT, ENGINE, environment, identity, save, stage, stop, verify_engine

SEED = Path('/tmp/s05-author-56eb6b28-run01/config/godot/editor_settings-4.8.tres')


def listener_args():
    """Allocate private engine ancillary listeners without pinning the Toolkit editor endpoint."""
    probes = []
    try:
        for _ in range(3):
            probe = socket.socket()
            probes.append(probe)
            probe.bind(('127.0.0.1', 0))
        ports = [p.getsockname()[1] for p in probes]
        return ['--lsp-port', str(ports[0]), '--dap-port', str(ports[1]),
                '--debug-server', 'tcp://127.0.0.1:' + str(ports[2])]
    finally:
        for probe in probes:
            probe.close()


def main():
    """Discover a bound private route, author through Toolkit tools, save/reopen and reap owned handles."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or output.is_relative_to(ROOT):
        raise ValueError('fresh external output required')
    verify_engine()
    seed = SEED.read_bytes()
    if b'mcp_toolkit/performance/keep_editor_responsive_unfocused = false' not in seed:
        raise RuntimeError('authorized seed missing effective false setting')
    output.mkdir(mode=0o700)
    env = environment(output / 'private')
    target = Path(env['XDG_CONFIG_HOME']) / 'godot/editor_settings-4.8.tres'
    target.parent.mkdir()
    target.write_bytes(seed)
    save(output / 'settings-seed.json', {'source': str(SEED), 'copy': str(target),
                                       'source_identity': identity(SEED), 'copy_identity': identity(target)})
    project = output / 'project'
    before = stage(project, editor=True)
    save(output / 'staged-inputs.json', before)
    env['GODOT_MCP_PROJECT_PATH'] = str(project)
    deadline = time.monotonic() + 1500
    result = {'ok': False, 'commands': []}
    editor = bridge = None
    streams = []
    try:
        for name in ['editor', 'connector']:
            for suffix in ['stdout', 'stderr']:
                streams.append((output / f'{name}.{suffix}.log').open('wb'))
        (output / 'editor.engine.log').touch()
        argv = [str(ENGINE), '--headless', '--editor', '--path', str(project),
                *listener_args(), '--log-file', str(output / 'editor.engine.log'),
                '--script', str(ROOT / 'tools/s08/editor_context.gd')]
        editor = subprocess.Popen(argv, cwd=project, env=env, stdout=streams[0], stderr=streams[1])
        result['commands'].append({'argv': argv, 'cwd': str(project), 'owned_pid': editor.pid,
                                   'started_unix': time.time(), 'HOME': env.get('HOME'),
                                   'environment': {k:v for k,v in env.items() if k.startswith(('XDG_', 'GODOT_MCP_'))}})
        save(output / 'lifecycle.json', result)
        key = hashlib.sha256(str(project).encode()).hexdigest()[:12]
        registry = Path(env['XDG_DATA_HOME']) / 'godot-mcp-toolkit/entries' / (key + '.json')
        ready_deadline = min(deadline, time.monotonic() + 90)
        while time.monotonic() < ready_deadline:
            if editor.poll() is not None:
                raise RuntimeError('editor exited before readiness')
            contexts = [json.loads(line[19:]) for line in (output / 'editor.stdout.log').read_text().splitlines()
                        if line.startswith('S08_EDITOR_CONTEXT ')]
            if registry.exists() and len(contexts) == 1:
                entry = json.loads(registry.read_text())
                context = contexts[0]
                if entry.get('pid') == editor.pid and context.get('boost') is False:
                    break
            time.sleep(.1)
        else:
            raise RuntimeError('private startup deadline')
        if context['project'] != str(project) + '/' or context['pid'] != editor.pid:
            raise RuntimeError('private editor context mismatch')
        if context['settings_path'] != str(target) or not context['editor_hint']:
            raise RuntimeError('private settings context mismatch')
        if entry.get('_key') != str(project) or not Path(entry['token_path']).is_relative_to(Path(env['XDG_DATA_HOME'])):
            raise RuntimeError('private canonical endpoint/token binding mismatch')
        result['context'] = context
        save(output / 'registry-binding.json', entry)
        bargv = ['/usr/bin/node', str(ROOT / 'tools/s08/standard_bridge.mjs'), str(output / 'registry-binding.json')]
        bridge = subprocess.Popen(bargv, cwd=project, env=env, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=streams[3])
        result['commands'].append({'argv': bargv, 'cwd': str(project), 'owned_pid': bridge.pid,
                                   'started_unix': time.time()})

        def receive():
            """Retain exact response bytes with a bounded request deadline."""
            timeout = min(25, max(0, deadline - time.monotonic()))
            if not select.select([bridge.stdout], [], [], timeout)[0]:
                raise RuntimeError('owned bridge request deadline')
            raw = bridge.stdout.readline()
            streams[2].write(raw)
            streams[2].flush()
            return json.loads(raw)

        result['discovery'] = receive()
        sequence = 0

        def call(method, params=None):
            """Invoke a supported editor tool and retain its complete request/result before assertions."""
            nonlocal sequence
            sequence += 1
            request = {'method': method, 'params': params or {}}
            save(output / f'call-{sequence:03}.json', {'request': request})
            bridge.stdin.write((json.dumps(request) + '\n').encode())
            bridge.stdin.flush()
            response = receive()
            save(output / f'call-{sequence:03}.json', {'request': request, 'response': response})
            if response.get('error') or response.get('headless') is not True:
                raise RuntimeError('owned tool transport failed: ' + str(response))
            if response.get('result', {}).get('success') is not True:
                raise RuntimeError('owned editor tool failed: ' + str(response))
            return response['result']

        call('project.get_settings', {'prefix': 'application/'})
        call('editor.wait_for_idle', {'timeout_ms': 15000})
        call('scene.open', {'file_path': 'res://tests/fixtures/s06/intersection.tscn'})
        call('scene.get_tree', {'max_depth': -1})
        for name in ['fixture', 'run', 'guards']:
            content = (ROOT / f'tools/s07_driver/{name}.gd.txt').read_text()
            response = call('script.write', {'file_path': f'res://tests/fixtures/s07_driver/{name}.gd', 'content': content})
            if response.get('valid') is False:
                raise RuntimeError('authored script invalid: ' + name)
        scene = 'res://tests/fixtures/s07_driver/intersection.tscn'
        call('scene.create_inherited', {'file_path': scene, 'base_scene': 'res://tests/fixtures/s06/intersection.tscn'})
        call('scene.open', {'file_path': scene})
        call('node.set_script', {'node_path': '.', 'script_path': 'res://tests/fixtures/s07_driver/fixture.gd'})
        call('editor.save_scene')
        fixture_path = project / 'tests/fixtures/s07_driver/intersection.tscn'
        roundtrip_before = identity(fixture_path)
        call('scene.open', {'file_path': 'res://tests/fixtures/s06/intersection.tscn'})
        call('scene.close', {'file_path': scene})
        call('scene.open', {'file_path': scene})
        call('scene.get_tree', {'max_depth': -1})
        call('editor.save_scene')
        result['roundtrip'] = {'before': roundtrip_before, 'after': identity(fixture_path)}
        if result['roundtrip']['before'] != result['roundtrip']['after']:
            raise RuntimeError('inherited scene changed in roundtrip')
        call('editor.get_console', {'source': 'buffer', 'limit': 200})
        changed = [name for name, expected in before.items() if identity(project / name) != expected]
        if changed:
            raise RuntimeError('unowned staging bytes changed: ' + str(changed))
        destination = ROOT / 'tests/fixtures/s07_driver'
        if destination.exists():
            raise RuntimeError('new fixture destination already exists')
        shutil.copytree(project / 'tests/fixtures/s07_driver', destination)
        result['ok'] = True
    except Exception as error:
        result['failure'] = repr(error)
    finally:
        if bridge is not None:
            if bridge.poll() is None:
                bridge.stdin.close()
                try:
                    bridge.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    stop(bridge)
        if editor is not None:
            stop(editor)
        for child, receipt in zip([editor, bridge], result['commands']):
            receipt.update(exit=child.returncode, reaped=child.poll() is not None, ended_unix=time.time())
        for stream in streams:
            stream.close()
        result['quiescent'] = all(c is None or c.poll() is not None for c in [editor, bridge])
        save(output / 'lifecycle.json', result)
    print(json.dumps(result))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
