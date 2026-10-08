import subprocess,json,os
from pathlib import Path
root=Path('/tmp/s06-operations');subprocess.run(['python3',str(root/'host_inventory.py')],check=True)
receipt=json.loads((root/'host-before.json').read_text());assert not receipt['host_processes']
(root/'host-before-worktree-launch.json').write_text(json.dumps(receipt,indent=2)+'\n')
binary='/home/regner/.local/share/mise/installs/github-godotengine-godot-builds/4.8-dev7/godot'
project='/home/regner/.paseo/worktrees/0u71f39f/s06-provisional-turn-seam'
command=[binary,'--editor','--path',project,'res://tests/fixtures/s04/editor_harness.tscn']
log=open(root/'editor.log','wb')
p=subprocess.Popen(command,cwd=project,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(root/'editor-launch.json').write_text(json.dumps({'pid':p.pid,'command':command},indent=2)+'\n');print('S06_EDITOR',p.pid)
