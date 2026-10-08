import json,subprocess,time,os
from pathlib import Path
root=Path('/tmp/s06-operations')
cmd=['node',str(root/'client.mjs'),str(root/'main-state.json'),'/home/regner/Development/fun-things']
p=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
(root/'fresh-main-state.jsonl').write_text(p.stdout);(root/'fresh-main-state.stderr').write_text(p.stderr)
assert p.returncode==0
s=json.loads(p.stdout)['response']['result']['result'];assert s['project']=='/home/regner/Development/fun-things/' and s['unsaved']=='PackedStringArray()'
assert Path('/proc/325756').exists()
(root/'saved-tabs.json').write_text(json.dumps(s,indent=2)+'\n')
q=subprocess.run(['node',str(root/'client.mjs'),str(root/'quit.json'),s['project'].rstrip('/')],capture_output=True,text=True,timeout=30)
(root/'quit-result.jsonl').write_text(q.stdout);(root/'quit.stderr').write_text(q.stderr)
for _ in range(40):
 if not Path('/proc/325756').exists(): break
 time.sleep(.1)
assert not Path('/proc/325756').exists(),'known editor did not exit'
subprocess.run(['python3',str(root/'host_inventory.py')],check=True)
(root/'host-after-quit.json').write_bytes((root/'host-before.json').read_bytes())
assert not json.loads((root/'host-after-quit.json').read_text())['host_processes']
print('S06_MAIN_SAVED_QUIT_HOST_ABSENCE')
