"""Launch one owned native comparison at physical1280x800; retain argv/PID ownership."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
STATE = Path('/tmp/asset-register-production-editor')
label = sys.argv[1]
launch = json.loads((STATE/'launch.json').read_text())
assert os.readlink(f"/proc/{launch['pid']}/cwd") == str(ROOT)
penv = dict(s.decode().split('=',1) for s in Path(f"/proc/{launch['pid']}/environ").read_bytes().split(b'\0') if b'=' in s)
overrides = {k:penv[k] for k in ['DISPLAY','WAYLAND_DISPLAY','XDG_RUNTIME_DIR'] if k in penv}
overrides.update({'XDG_DATA_HOME':str(STATE/'data'),'XDG_CONFIG_HOME':str(STATE/'config'),
    'XDG_CACHE_HOME':str(STATE/'cache'),'GODOT_MCP_RUNTIME_PORT':'22651'})
argv=[launch['argv'][0],'--path',str(ROOT),'--resolution','1280x800',
      f'res://tests/assets/asset_production/batch_03_{label}.tscn']
log=ROOT/f'docs/assets/production/batch_03-evidence/native-{label}.log'
stream=log.open('w')
proc=subprocess.Popen(argv,env=dict(os.environ,**overrides),stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
row={'pid':proc.pid,'argv':argv,'cwd':str(ROOT),'environment_overrides':overrides,
     'editor_pid':launch['pid'],'runtime_port':22651}
(STATE/'batch03/native-launch.json').write_text(json.dumps(row,indent=2)+'\n')
(ROOT/f'docs/assets/production/batch_03-evidence/native-{label}-launch.json').write_text(json.dumps(row,indent=2)+'\n')
print(proc.pid)
