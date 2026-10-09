"""Preserve a frozen log's complete append, then restart only its saved private editor."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
STATE = Path('/tmp/asset-register-production-editor')
CANDIDATE = '1031a3e1e66a404f67fa1a3857c4888d05f10d1e'
LOG = ROOT / 'docs/assets/production/batch_03-evidence/editor-restart.log'
launch = json.loads((STATE / 'launch.json').read_text())
pid = launch['pid']
assert pid == 254275 and os.readlink(f'/proc/{pid}/cwd') == str(ROOT)
assert os.readlink(f'/proc/{pid}/exe') == launch['argv'][0]
argv = Path(f'/proc/{pid}/cmdline').read_text().split('\0')
assert argv[:-1] == launch['argv']
fds = {str(fd): os.readlink(f'/proc/{pid}/fd/{fd}') for fd in (1, 2)}
assert all(path == str(LOG) for path in fds.values())
requests = OUT / 'pre-context-requests.json'
requests.write_text(json.dumps([{'method':'game.stop','params':{}},
    {'method':'scene.open','params':{'file_path':'res://tools/asset_production/integration/inspector.tscn'}},
    {'method':'node.call_method','params':{'node_path':'.','method_name':'context'}}], indent=2)+'\n')
context_argv = ['node', str(ROOT / 'tools/asset_production/integration/editor_client.mjs'), str(requests)]
with (OUT / 'pre-context.stdout.jsonl').open('w') as stdout, (OUT / 'pre-context.stderr.log').open('w') as stderr:
    result = subprocess.run(context_argv, cwd=ROOT, stdout=stdout, stderr=stderr)
(OUT / 'pre-context.execution.json').write_text(json.dumps({'argv':context_argv,
    'cwd':str(ROOT),'exit_code':result.returncode},indent=2)+'\n')
assert result.returncode == 0
rows = [json.loads(s) for s in (OUT/'pre-context.stdout.jsonl').read_text().splitlines()]
assert rows[0]['result']['result']['was_running'] is False
context = rows[-1]['result']['result']['result']
assert context['pid'] == pid and context['unsaved'] == 'PackedStringArray()'
assert context['project'].rstrip('/') == str(ROOT)
env_items = Path(f'/proc/{pid}/environ').read_bytes().split(b'\0')
parent_env = dict(s.decode().split('=',1) for s in env_items if b'=' in s)
overrides = {k:parent_env[k] for k in ['DISPLAY','WAYLAND_DISPLAY','XDG_RUNTIME_DIR'] if k in parent_env}
overrides.update({'XDG_DATA_HOME':str(STATE/'data'),'XDG_CONFIG_HOME':str(STATE/'config'),
    'XDG_CACHE_HOME':str(STATE/'cache'),'GODOT_MCP_EDITOR_PORT':'22650','GODOT_MCP_RUNTIME_PORT':'22651'})
os.kill(pid, signal.SIGTERM)
for _ in range(100):
    path = Path(f'/proc/{pid}/status')
    if not path.exists() or 'State:\tZ' in path.read_text():
        break
    time.sleep(.1)
else:
    raise RuntimeError('Owned editor did not stop; log not restored')
show_argv = ['git','show',CANDIDATE+':'+str(LOG.relative_to(ROOT))]
result = subprocess.run(show_argv, cwd=ROOT, capture_output=True)
(OUT/'git-show.stderr.log').write_bytes(result.stderr)
(OUT/'git-show.execution.json').write_text(json.dumps({'argv':show_argv,
    'exit_code':result.returncode},indent=2)+'\n')
assert result.returncode == 0
frozen = result.stdout
complete = LOG.read_bytes()
assert complete.startswith(frozen)
append = complete[len(frozen):]
reviewer = (ROOT/'docs/reviews/asset-production/batch_03/final/owned-editor-appended.log').read_bytes()
assert append.startswith(reviewer)
(OUT/'complete-editor-through-shutdown.log').write_bytes(complete)
(OUT/'append-after-frozen-prefix.log').write_bytes(append)
(OUT/'frozen-candidate-editor.log').write_bytes(frozen)
LOG.write_bytes(frozen)
assert LOG.read_bytes() == frozen
live_path = STATE/'f3/editor-live.log'
assert not live_path.exists(), 'Do not overwrite an existing private live log'
stream = live_path.open('w')
proc = subprocess.Popen(launch['argv'], cwd=ROOT, env=dict(os.environ,**overrides),
    stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
current = dict(launch, pid=proc.pid)
(STATE/'launch.json').write_text(json.dumps(current,indent=2)+'\n')
summary = {'frozen_candidate':CANDIDATE,'old_launch':launch,'old_fds':fds,
    'old_saved_context':context,'old_editor_stopped':True,
    'old_os_exit':'not observed; stopped/zombie PID verified after SIGTERM',
    'complete_bytes':len(complete),'complete_sha256':hashlib.sha256(complete).hexdigest(),
    'frozen_bytes':len(frozen),'frozen_sha256':hashlib.sha256(frozen).hexdigest(),
    'append_bytes':len(append),'append_sha256':hashlib.sha256(append).hexdigest(),
    'complete_equals_frozen_plus_append':complete == frozen+append,
    'reviewer_append_is_exact_prefix':append.startswith(reviewer),
    'reviewer_append_bytes':len(reviewer),'reviewer_append_sha256':hashlib.sha256(reviewer).hexdigest(),
    'current_launch':current,'live_log':str(live_path),'environment_overrides':overrides}
(OUT/'isolation.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'current_pid':proc.pid,'complete_bytes':len(complete),'append_bytes':len(append)}))
