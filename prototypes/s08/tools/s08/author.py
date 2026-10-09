#!/usr/bin/env python3
"""Single commissioned private editor, standard discovery and raw stream supervision."""
import hashlib
import json
import os
from pathlib import Path
import re
import select
import signal
import socket
import subprocess
import sys
import time

from request_file import read_request

ROOT = Path(__file__).resolve().parents[2]
BASE = 'ef730df936b5b159f0894033f5d01e2b7124386c'
ORIGINAL = Path('/tmp/s08-standard-555e0330')
SECOND = '--scan-complete-preparation' in sys.argv
ACTUAL04 = '--file-author-run04' in sys.argv
ACTUAL03 = '--cleaned-author-run03' in sys.argv or ACTUAL04
ACTUAL02 = '--corrected-author-run02' in sys.argv or ACTUAL03
ACTUAL = '--author-existing-settings' in sys.argv or ACTUAL02
TASK = ORIGINAL / ('actual-editor-run04' if ACTUAL04 else 'actual-editor-run03' if ACTUAL03 else 'actual-editor-run02' if ACTUAL02 else 'actual-editor-attempt' if ACTUAL else 'scan-complete-attempt') if (SECOND or ACTUAL) else ORIGINAL
PROJECT = ORIGINAL / 'project'
ENGINE = '/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot'
ENGINE_SHA = '6aea356032435e7af19dbfbf48dd20c5012a7dc1267eb8e92406f44e3584b5fd'
DIAGNOSTIC = re.compile(r'(?i)(?:SCRIPT ERROR:|ERROR:|WARNING:)')
KNOWN_WARNING = 'latest tested version'


def save(path, value):
    """Retain complete structured receipts with a terminating newline."""
    path.write_text(json.dumps(value, indent=2) + '\n')


def identity(path):
    """Bind actual bytes, including empty streams."""
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    return {'bytes': path.stat().st_size, 'sha256': digest}


def blob(path):
    """Read immutable accepted sources without current checkout ambiguity."""
    return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT)


def stop(child):
    """Reap only an actual owned handle, with a two-second graceful window."""
    if child is None:
        return
    if child.poll() is None:
        child.send_signal(signal.SIGINT)
        try:
            child.wait(timeout=2)
        except subprocess.TimeoutExpired:
            child.terminate()
            try:
                child.wait(timeout=2)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=2)
    else:
        child.wait()


def listeners():
    """Choose isolated ports only for engine servers that startup actually creates."""
    probes = []
    try:
        for _ in range(3):
            probe = socket.socket()
            probes.append(probe)
            probe.bind(('127.0.0.1', 0))
        ports = [probe.getsockname()[1] for probe in probes]
        return ['--lsp-port', str(ports[0]), '--dap-port', str(ports[1]),
                '--debug-server', 'tcp://127.0.0.1:' + str(ports[2])]
    finally:
        for probe in probes:
            probe.close()


def clean_streams(directory, known_warning=False):
    """Reject new errors; retain and explicitly identify the unchanged version warning."""
    for name in ['stdout.log', 'stderr.log', 'engine.log']:
        text = (directory / name).read_text(errors='replace')
        for line in text.splitlines():
            if DIAGNOSTIC.search(line):
                if known_warning and '4.7' in line and ('4.8' in line or 'tested' in line):
                    continue
                raise RuntimeError(str(directory / name) + ': ' + line)


def main():
    """Initialize one new private scope, verify readiness, then serve authorized mutations."""
    TASK.mkdir(mode=0o700)
    if not (SECOND or ACTUAL):
        PROJECT.mkdir()
    shared = (ORIGINAL / 'scan-complete-attempt/private') if ACTUAL else (TASK / 'private')
    if not ACTUAL:
        shared.mkdir(mode=0o700)
    env = os.environ.copy()
    for key in list(env):
        if key.startswith('GODOT_MCP_'):
            del env[key]
    for key, folder in [('XDG_CONFIG_HOME', 'config'), ('XDG_DATA_HOME', 'data'),
                        ('XDG_CACHE_HOME', 'cache'), ('XDG_RUNTIME_DIR', 'runtime'),
                        ('TMPDIR', 'tmp')]:
        target = shared / folder
        if not ACTUAL:
            target.mkdir(mode=0o700)
        elif not target.is_dir():
            raise RuntimeError('private scope missing')
        env[key] = str(target)
    env['GODOT_MCP_PROJECT_PATH'] = str(PROJECT)
    children, streams = [], []
    editor = connector = None
    result = {'ok': False, 'base': BASE, 'started_unix': time.time(), 'commands': []}
    sequence = 0
    try:
        if SECOND or ACTUAL:
            original = json.loads((ORIGINAL / 'lifecycle.json').read_text())
            if original['ok'] or len(original['commands']) != 1 or original['commands'][0]['phase'] != 'prepare':
                raise RuntimeError('original STOP/never-started editor boundary differs')
            result['original_stop'] = str(ORIGINAL / 'lifecycle.json')
            result['distinct_grant'] = 'ROOT source-qualified scan completion/deferred shutdown, one additional prep'
        if ACTUAL:
            binding = json.loads((ORIGINAL / ('settings-before-run04.json' if ACTUAL04 else 'settings-before-actual-editor.json')).read_text())
            if identity(Path(binding['path'])) != {k: binding[k] for k in ['bytes', 'sha256']}:
                raise RuntimeError('private setting artifact changed since phase declaration')
            result['settings_artifact'] = binding
            result['distinct_grant'] = 'ROOT independent actual authoring readiness phase; both prep STOPs preserved'
        if identity(Path(ENGINE)) != {'bytes': 151398728, 'sha256': ENGINE_SHA}:
            raise RuntimeError('pinned engine identity differs')
        paths = [row['path'] for row in json.loads(
            (ROOT / 'docs/spikes/s08-linux-evidence/staged-input.json').read_text())]
        toolkit = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE,
            'addons/godot_mcp_toolkit'], cwd=ROOT, text=True).splitlines()
        if len(paths) != 31 or len(set(paths)) != 31:
            raise RuntimeError('accepted 31-file closure differs')
        manifest = []
        for name in paths + toolkit:
            target = PROJECT / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if SECOND or ACTUAL:
                expected = blob(name)
                if ACTUAL04 and name == 'tests/fixtures/s03/replication.gd':
                    expected = expected.replace(
                        b'\tassert(match_state.apply_journal(participant, 70, match_state.durable_revision + 1))',
                        b'\tvar journal_applied: bool = match_state.apply_journal(\n\t\tparticipant, 70, match_state.durable_revision + 1\n\t)\n\tassert(journal_applied)')
                if target.read_bytes() != expected:
                    raise RuntimeError('original mirror bytes changed: ' + name)
            else:
                target.write_bytes(blob(name))
            manifest.append({'path': name, **identity(target)})
        save(TASK / 'mirror-inputs.json', manifest)
        settings = blob('project.godot').decode()
        settings = re.sub(r'(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)', '', settings)
        settings = settings.replace('config/icon="res://icon.svg"\n', '')
        (PROJECT / 'project.godot').write_text(settings + '\n[autoload]\n'
            'MCPRuntimeServer="*res://addons/godot_mcp_toolkit/runtime/mcp_runtime_server.gd"\n'
            '\n[editor_plugins]\nenabled=PackedStringArray("res://addons/godot_mcp_toolkit/plugin.cfg")\n')
        prep = TASK / 'prepare-project'
        prep.mkdir()
        (prep / 'project.godot').write_text('config_version=5\n[application]\nconfig/name="S08 Settings Preparation"\n')
        (prep / 'initialize_settings.gd').write_bytes((ROOT / ('tools/s08/initialize_settings_scan.gd' if SECOND else 'tools/s08/initialize_settings.gd')).read_bytes())
        phases = [('editor', PROJECT, ['--script', str(ROOT / 'tools/s08/editor_context.gd')], 60)]
        if not ACTUAL:
            phases.insert(0, ('prepare', prep, ['--script', 'res://initialize_settings.gd'], 15))
        for phase, project, extra, budget in phases:
            logs = TASK / phase
            logs.mkdir()
            (logs / 'engine.log').touch()
            out, err = (logs / 'stdout.log').open('wb'), (logs / 'stderr.log').open('wb')
            streams.extend([out, err])
            argv = [ENGINE, '--headless', '--editor', '--path', str(project), *listeners(),
                    '--log-file', str(logs / 'engine.log'), *extra]
            command = {'phase': phase, 'argv': argv, 'cwd': str(project),
                       'budget_seconds': budget, 'started_unix': time.time(),
                       'environment': {k: v for k, v in env.items()
                                       if k.startswith(('XDG_', 'GODOT_MCP_')) or k == 'TMPDIR'}}
            child = subprocess.Popen(argv, cwd=project, env=env, stdout=out, stderr=err)
            children.append(child)
            command['owned_pid'] = child.pid
            result['commands'].append(command)
            save(logs / 'command.json', command)
            if phase == 'prepare':
                try:
                    command['exit'] = child.wait(timeout=budget)
                except subprocess.TimeoutExpired:
                    command['timeout'] = True
                    raise
                finally:
                    stop(child)
                    command.update(exit=child.returncode, reaped=child.poll() is not None,
                                   ended_unix=time.time())
                    save(logs / 'command.json', command)
                if command['exit'] != 0:
                    raise RuntimeError('private settings preparation failed')
                clean_streams(logs)
                receipts = [json.loads(line[13:]) for line in (logs / 'stdout.log').read_text().splitlines()
                            if line.startswith('S08_SETTINGS ')]
                if len(receipts) != 1 or receipts[0].get('ok') is not True:
                    raise RuntimeError('private settings readback missing/failed')
                result['settings_receipt'] = receipts[0]
                save(TASK / 'settings-file.json', identity(Path(receipts[0]['path'])))
                continue
            editor = child
        deadline = time.monotonic() + max(0, 60 - (time.time() - command['started_unix']))
        key = hashlib.sha256(str(PROJECT).encode()).hexdigest()[:12]
        registry = shared / 'data/godot-mcp-toolkit/entries' / (key + '.json')
        while time.monotonic() < deadline:
            if editor.poll() is not None:
                raise RuntimeError('editor exited before readiness')
            contexts = [json.loads(line[19:]) for line in (TASK / 'editor/stdout.log').read_text().splitlines()
                        if line.startswith('S08_EDITOR_CONTEXT ')]
            if registry.exists() and len(contexts) == 1:
                entry = json.loads(registry.read_text())
                token_path = Path(entry['token_path'])
                if (entry['_key'] != str(PROJECT) or entry['pid'] != editor.pid
                        or not 6550 <= entry['port'] <= 6560
                        or not token_path.is_relative_to(shared / 'data')):
                    time.sleep(0.1)
                    continue
                projection_path = shared / 'data/godot-mcp-toolkit/projects.json'
                try:
                    projected = json.loads(projection_path.read_text()).get('by_path', {}).get(str(PROJECT))
                except (FileNotFoundError, json.JSONDecodeError):
                    projected = None
                expected = {k: v for k, v in entry.items() if k != '_key'}
                if projected != expected:
                    time.sleep(0.1)
                    continue
                save(TASK / 'projection-binding.json', {'by_path': {str(PROJECT): projected}})
                if token_path.is_file():
                    context = contexts[0]
                    if (context['editor_hint'] is not True or context['pid'] != editor.pid
                            or context['project'] != str(PROJECT) + '/' or context['boost'] is not False
                            or context['settings_path'] != str(shared / 'config/godot/editor_settings-4.8.tres')
                            or context['version']['hash'] != 'c971f93e7e76b0ef919bf6009e7b868bea04db7f'):
                        raise RuntimeError('actual private editor startup context differs')
                    result['startup_context'] = context
                    result['registry_entry'] = entry
                    save(TASK / 'registry-binding.json', entry)
                    break
            time.sleep(0.1)
        else:
            raise RuntimeError('editor readiness60s expired')
        cerr = (TASK / 'editor/connector.stderr.log').open('wb')
        raw = (TASK / 'editor/connector.stdout.log').open('wb')
        streams.extend([cerr, raw])
        cargv = ['/usr/bin/node', str(ROOT / 'tools/s08/standard_bridge.mjs'), str(TASK / 'registry-binding.json')]
        connector = subprocess.Popen(cargv, env=env, cwd=PROJECT, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=cerr)
        children.append(connector)
        ccommand = {'phase': 'connector', 'argv': cargv, 'cwd': str(PROJECT),
                    'owned_pid': connector.pid, 'started_unix': time.time()}
        result['commands'].append(ccommand)

        def receive():
            """Store original connector line bytes before decoding the additional receipt."""
            if not select.select([connector.stdout], [], [], min(20, max(0.01, deadline-time.monotonic())))[0]:
                raise RuntimeError('standard connector response timeout')
            line = connector.stdout.readline()
            raw.write(line)
            raw.flush()
            if not line:
                raise RuntimeError('standard connector exited')
            return json.loads(line)

        discovery = receive()
        result['discovery'] = discovery
        if discovery.get('registry') != {k: v for k, v in result['registry_entry'].items() if k != '_key'}:
            raise RuntimeError('standard discovered entry differs')

        def call(request, critical=False):
            """Issue one supported private handler call and retain original response bytes."""
            nonlocal sequence
            sequence += 1
            record = {'request': request, 'started_unix': time.time()}
            save(TASK / f'call-{sequence:03}.json', record)
            connector.stdin.write((json.dumps(request) + '\n').encode())
            connector.stdin.flush()
            response = receive()
            record.update(response=response, ended_unix=time.time())
            save(TASK / f'call-{sequence:03}.json', record)
            if response.get('error') or response.get('headless') is not True:
                raise RuntimeError('standard connector/auth failed: ' + json.dumps(response))
            if critical and response.get('result', {}).get('success') is not True:
                raise RuntimeError('private handler failed: ' + json.dumps(response))
            return response['result']

        context = call({'method': 'project.get_settings', 'params': {'prefix': 'application/'}}, critical=True)
        call({'method': 'editor.get_console', 'params': {'source': 'buffer', 'limit': 100}}, critical=True)
        call({'method': 'editor.wait_for_idle', 'params': {'timeout_ms': 15000}}, critical=True)
        call({'method': 'scene.open', 'params': {'file_path': 'res://tests/fixtures/s03/boot.tscn'}}, critical=True)
        tree = call({'method': 'scene.get_tree', 'params': {'max_depth': -1}}, critical=True)
        path = call({'method': 'node.get_property', 'params': {'node_path': '.', 'property': 'scene_file_path'}}, critical=True)
        if path.get('value') != 'res://tests/fixtures/s03/boot.tscn':
            raise RuntimeError('actual saved editor scene mismatch')
        clean_streams(TASK / 'editor', known_warning=True)
        if any(identity(PROJECT / row['path']) != {k: row[k] for k in ['bytes', 'sha256']}
               for row in manifest):
            raise RuntimeError('source bytes changed before authoring')
        result.update(ready=True, editor_context=context, scene_tree=tree, ready_unix=time.time())
        save(TASK / 'lifecycle.json', result)
        print(json.dumps({'ready': True, 'pid': editor.pid, 'project': str(PROJECT),
                          'port': entry['port'], 'boost_enabled': False}), flush=True)
        deadline = time.monotonic() + 1200
        while time.monotonic() < deadline:
            if not select.select([sys.stdin], [], [], min(15, deadline-time.monotonic()))[0]:
                continue
            line = sys.stdin.readline()
            if not line:
                raise RuntimeError('authoring command input closed before finish')
            request = json.loads(line)
            if 'request_file' in request:
                request, request_raw = read_request(request, ORIGINAL)
                (TASK / f'request-{sequence + 1:03}.json').write_bytes(request_raw)
            if request.get('finish'):
                result['ok'] = True
                break
            response = call(request)
            print(json.dumps(response), flush=True)
        else:
            raise RuntimeError('owned authoring20min expired')
    except Exception as error:
        result['failure'] = repr(error)
        print(json.dumps({'STOP': result['failure']}), flush=True)
    finally:
        if connector is not None and connector.poll() is None:
            connector.stdin.close()
            try:
                connector.wait(timeout=2)
            except subprocess.TimeoutExpired:
                stop(connector)
        for child in children:
            stop(child)
        for child, command in zip(children, result['commands']):
            command.update(exit=child.returncode, reaped=child.poll() is not None,
                           ended_unix=time.time())
        for stream in streams:
            stream.close()
        result.update(ended_unix=time.time(), all_children_reaped=all(
            child.poll() is not None for child in children), streams_closed=True)
        save(TASK / 'lifecycle.json', result)
        print(json.dumps({'finished': result}), flush=True)
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
