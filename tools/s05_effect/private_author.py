#!/usr/bin/env python3
"""Own the single commissioned S05 editor and normal installed MCP SDK transport."""
import hashlib
import json
import os
from pathlib import Path
import re
import select
import signal
import socket
import sys
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = 'ef730df936b5b159f0894033f5d01e2b7124386c'
RUN = Path('/tmp/s05-author-56eb6b28-run01')
CONTINUE = '--continue' in sys.argv
FINAL = '--final' in sys.argv
AFTER_CLEANUP = '--after-cleanup' in sys.argv
CONTINUE = CONTINUE or FINAL or AFTER_CLEANUP
LOG = Path('/tmp/s05-author-56eb6b28-run04' if AFTER_CLEANUP else
           '/tmp/s05-author-56eb6b28-run03' if FINAL else
           '/tmp/s05-author-56eb6b28-run02') if CONTINUE else RUN
ENGINE = '/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot'
PACKAGE = Path('/home/regner/.npm/_npx/ea3a09a27b3d1af0/node_modules')
PROBE = '''@tool
extends SceneTree
## Reports actual private editor context and initializes only the granted setting.

const BOOST: String = "mcp_toolkit/performance/keep_editor_responsive_unfocused"


## Waits until the editor singleton has been constructed by normal startup.
func _initialize() -> void:
\tcall_deferred("_probe")


## Saves an engine-generated private settings resource or reads it before authentication.
func _probe() -> void:
\tvar settings: EditorSettings = EditorInterface.get_editor_settings()
\tvar initialize: bool = "--initialize" in OS.get_cmdline_user_args()
\tvar error: int = OK
\tif initialize:
\t\tsettings.set_setting(BOOST, false)
\t\terror = ResourceSaver.save(settings, settings.get_path())

\tprint("S05_CONTEXT " + JSON.stringify({"editor_hint": Engine.is_editor_hint(),
\t\t"pid": OS.get_process_id(), "project": ProjectSettings.globalize_path("res://"),
\t\t"version": Engine.get_version_info(), "boost": settings.get_setting(BOOST),
\t\t"settings_path": settings.get_path(), "save_error": error}))
\tif initialize:
\t\tquit(error)
'''


def save(path, value):
    """Retain exact structured receipts without printing credentials."""
    path.write_text(json.dumps(value, indent=2) + '\n')


def stop(child):
    """Reap only an owned child with bounded graceful/signal escalation."""
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


def owned_entry(entry, project, pid):
    """Do not dial a stale startup entry; only the exact owned replacement can be ready."""
    return entry.get('_key') == str(project) and entry.get('pid') == pid


def stage():
    """Copy exact transitive fixture resources and unchanged toolkit, without native addons."""
    project = RUN / 'project'
    project.mkdir()
    tracked = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE],
                                      cwd=ROOT, text=True).splitlines()
    classes = {}
    for name in tracked:
        if name.startswith('tests/fixtures/') and name.endswith('.gd'):
            match = re.search(r'^class_name\s+(\w+)', (ROOT / name).read_text(), re.M)
            if match:
                classes[match[1]] = name
    paths = set()
    pending = ['tests/fixtures/s05/boot.tscn', 'tests/fixtures/s05/burst.tscn',
               'art/models/spikes/s05_explosion_carrier.glb']
    while pending:
        name = pending.pop()
        if name in paths:
            continue
        paths.add(name)
        data = (ROOT / name).read_bytes()
        if name.endswith(('.gd', '.tscn', '.tres', '.import')):
            source = data.decode()
            pending.extend(p for p in re.findall(r'res://([\w./-]+)', source)
                           if not p.startswith('.godot/'))
            pending.extend(path for symbol, path in classes.items()
                           if re.search(r'\b' + symbol + r'\b', source))
        for suffix in ['.uid', '.import']:
            if name + suffix in tracked:
                pending.append(name + suffix)
    paths.update(p for p in tracked if p.startswith('addons/godot_mcp_toolkit/'))
    rows = []
    for name in sorted(paths):
        data = (ROOT / name).read_bytes()
        expected = subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=ROOT)
        if data != expected:
            raise RuntimeError('non-base input: ' + name)
        target = project / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        rows.append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    save(RUN / 'inputs.json', rows)
    settings = (ROOT / 'project.godot').read_text()
    settings = re.sub(r'(?ms)^\[(?:autoload|editor_plugins)\]\n.*?(?=^\[|\Z)', '', settings)
    settings = settings.replace('config/icon="res://icon.svg"\n', '')
    settings += ('\n[autoload]\nMCPRuntimeServer="*res://addons/godot_mcp_toolkit/runtime/'
                 'mcp_runtime_server.gd"\n\n[editor_plugins]\n'
                 'enabled=PackedStringArray("res://addons/godot_mcp_toolkit/plugin.cfg")\n')
    (project / 'project.godot').write_text(settings)
    prep = RUN / 'prep'
    prep.mkdir()
    (prep / 'project.godot').write_text('config_version=5\n[application]\nconfig/name="S05 prep"\n')
    (RUN / 'context.gd').write_text(PROBE)
    return project, prep


def main():
    """Run exactly one initialization and authoring session; stop on readiness failure."""
    os.umask(0o077)
    if CONTINUE:
        LOG.mkdir()
    else:
        RUN.mkdir()
    streams = []
    editor = connector = init = None
    result = {'ok': False, 'base': BASE, 'start_unix': time.time()}
    registry = None
    try:
        with open(ENGINE, 'rb') as source:
            if hashlib.file_digest(source, 'sha256').hexdigest() != (
                    '6aea356032435e7af19dbfbf48dd20c5012a7dc1267eb8e92406f44e3584b5fd'):
                raise RuntimeError('engine SHA mismatch')
        if CONTINUE:
            project, prep = RUN / 'project', RUN / 'prep'
            for row in json.loads((RUN / 'inputs.json').read_text()):
                actual = hashlib.sha256((project / row['path']).read_bytes()).hexdigest()
                if actual != row['sha256']:
                    raise RuntimeError('changed mirror input: ' + row['path'])
            (LOG / 'context.gd').write_bytes((RUN / 'context.gd').read_bytes())
        else:
            project, prep = stage()
        env = {k: v for k, v in os.environ.items() if not k.startswith('GODOT_MCP_')}
        for key, folder in [('XDG_DATA_HOME', 'data'), ('XDG_CONFIG_HOME', 'config'),
                            ('XDG_CACHE_HOME', 'cache'), ('XDG_RUNTIME_DIR', 'runtime')]:
            path = RUN / folder
            path.mkdir(mode=0o700, exist_ok=CONTINUE)
            env[key] = str(path)
        env.update(GODOT_MCP_PROJECT_PATH=str(project), GODOT_MCP_CONFIG_VERSION='1')
        ports = []
        sockets = []
        try:
            for _ in range(3):
                sock = socket.socket()
                sock.bind(('127.0.0.1', 0))
                sockets.append(sock)
                ports.append(sock.getsockname()[1])
        finally:
            for sock in sockets:
                sock.close()
        flags = ['--lsp-port', str(ports[0]), '--dap-port', str(ports[1]),
                 '--debug-server', 'tcp://127.0.0.1:' + str(ports[2])]
        env['GODOT_MCP_LSP_PORT'] = str(ports[0])
        env['GODOT_MCP_LSP_HOST'] = '127.0.0.1'
        argv = lambda path, mode: [ENGINE, '--headless', '--editor', '--path', str(path),
                '--script', str(LOG / 'context.gd'), *flags,
                '--log-file', str(LOG / (mode + '.engine.log')), '--', '--' + mode]
        result.update(environment={k: v for k, v in env.items()
                                   if k.startswith(('XDG_', 'GODOT_MCP_'))},
                      init_argv=None if CONTINUE else argv(prep, 'initialize'), editor_argv=argv(project, 'observe'),
                      home_unchanged=env.get('HOME') == os.environ.get('HOME'))
        save(LOG / 'commands-before-engine.json', result)
        for mode, path in ([('observe', project)] if CONTINUE else [('initialize', prep), ('observe', project)]):
            out = (LOG / (mode + '.stdout')).open('wb')
            err = (LOG / (mode + '.stderr')).open('wb')
            streams.extend([out, err])
            child = subprocess.Popen(argv(path, mode), env=env, cwd=path, stdout=out, stderr=err)
            result[mode + '_process'] = {'pid': child.pid, 'start_unix': time.time(),
                                        'argv': argv(path, mode)}
            save(LOG / 'lifecycle.json', result)
            if mode == 'initialize':
                init = child
                init.wait(timeout=15)
                if init.returncode != 0:
                    raise RuntimeError('private initialization exit')
            else:
                editor = child
        deadline = time.monotonic() + 60
        key = hashlib.sha256(str(project).encode()).hexdigest()[:12]
        registry = RUN / 'data/godot-mcp-toolkit/entries' / (key + '.json')
        while time.monotonic() < deadline:
            if editor.poll() is not None:
                raise RuntimeError('authoring editor exited before readiness')
            rows = [json.loads(line[12:]) for line in (LOG / 'observe.stdout').read_text().splitlines()
                    if line.startswith('S05_CONTEXT ')]
            if registry.exists() and len(rows) == 1:
                context = rows[0]
                entry = json.loads(registry.read_text())
                if not owned_entry(entry, project, editor.pid):
                    # Registration happens after editor initialization and transport
                    # startup. A known old record is not permission to authenticate.
                    time.sleep(.1)
                    continue
                token = Path(entry['token_path'])
                if not token.is_relative_to(RUN / 'data') or not token.is_file():
                    raise RuntimeError('token path outside owned private data')
                if not context['editor_hint'] or context['pid'] != editor.pid or (
                        context['project'] != str(project) + '/' or context['boost'] is not False):
                    raise RuntimeError('actual editor context mismatch')
                if context['version']['hash'] != 'c971f93e7e76b0ef919bf6009e7b868bea04db7f':
                    raise RuntimeError('actual engine revision mismatch')
                result.update(context=context, registry=entry)
                break
            time.sleep(.1)
        else:
            raise RuntimeError('private readiness60s timeout')
        client = LOG / 'client.mjs'
        client.write_text('''import {Client} from "'''+str(PACKAGE)+'''/@modelcontextprotocol/sdk/dist/esm/client/index.js";
import {StdioClientTransport} from "'''+str(PACKAGE)+'''/@modelcontextprotocol/sdk/dist/esm/client/stdio.js";
import readline from "node:readline";
const transport=new StdioClientTransport({command:"/usr/bin/node",args:["'''+str(PACKAGE)+'''/@npgamedev/godot-mcp-server/dist/index.js"],cwd:process.cwd(),env:process.env,stderr:"inherit"});
const client=new Client({name:"S05 owned author",version:"1"});
await client.connect(transport);
for await(const line of readline.createInterface({input:process.stdin,crlfDelay:Infinity})) {
 const req=JSON.parse(line);
 try {const response=req.list?await client.listTools():await client.callTool({name:req.name,arguments:req.args??{}},undefined,{timeout:30000});process.stdout.write(JSON.stringify(response)+"\\n");}
 catch(e){process.stdout.write(JSON.stringify({isError:true,error:String(e)})+"\\n");}
}
await client.close();
''')
        err = (LOG / 'connector.stderr').open('wb')
        streams.append(err)
        connector = subprocess.Popen(['/usr/bin/node', str(client)], env=env, cwd=project,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=err, text=True, bufsize=1)
        sequence = 0

        def call(request):
            """Preserve complete SDK request/response wire lines and handler diagnostics."""
            nonlocal sequence
            sequence += 1
            name = 'call-%03d' % sequence
            save(LOG / (name + '.request.json'), request)
            connector.stdin.write(json.dumps(request) + '\n')
            connector.stdin.flush()
            if not select.select([connector.stdout], [], [], 35)[0]:
                raise RuntimeError('SDK response35s timeout')
            line = connector.stdout.readline()
            (LOG / (name + '.response.json')).write_text(line)
            response = json.loads(line)
            return response

        for request in [
                {'name': 'project_get_settings', 'args': {'prefix': 'application/'}},
                {'name': 'editor_get_console', 'args': {'source': 'buffer', 'limit': 100}}]:
            if call(request).get('isError'):
                raise RuntimeError('authenticated readiness handler failed')
        diagnostics = (LOG / 'observe.stderr').read_text()
        if re.search(r'SCRIPT ERROR:|ERROR:', diagnostics):
            raise RuntimeError('readiness engine diagnostics')
        save(LOG / 'tool-inventory.json', call({'list': True}))
        result.update(ready_unix=time.time(), editor_pid=editor.pid)
        save(LOG / 'lifecycle.json', result)
        print(json.dumps({'ready': True, 'pid': editor.pid, 'project': str(project),
                          'editor_port': entry['port'], 'boost_disabled': True}), flush=True)
        (LOG / 'requests').mkdir()
        (LOG / 'responses').mkdir()
        author_deadline = time.monotonic() + 1200
        next_request = 1
        while time.monotonic() < author_deadline:
            request_path = LOG / 'requests' / ('%03d.json' % next_request)
            if not request_path.exists():
                time.sleep(.05)
                continue
            request = json.loads(request_path.read_text())
            if request.get('finish'):
                result['ok'] = True
                break
            response = call(request)
            save(LOG / 'responses' / request_path.name, response)
            # A handler rejection is evidence for the lead to inspect. It is not a
            # readiness failure and must never trigger teardown of unsaved work.
            next_request += 1
        else:
            raise RuntimeError('authoring20min budget')
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
        stop(editor)
        stop(init)
        for stream in streams:
            stream.close()
        result.update(end_unix=time.time(), init_exit=None if init is None else init.returncode,
                      editor_exit=None if editor is None else editor.returncode,
                      connector_exit=None if connector is None else connector.returncode,
                      registry_entry_gone=registry is None or not registry.exists(),
                      all_owned_children_reaped=True, streams_closed=True)
        save(LOG / 'lifecycle.json', result)
        print(json.dumps({'finished': result}), flush=True)


if __name__ == '__main__':
    main()
