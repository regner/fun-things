import os,signal,time,json
from pathlib import Path
expected={380695:'blender --background --python tools/s06/create_source.py ',382718:'blender --background art/source/models/spikes/s06_intersection.blend --python tools/s06/export.py -- art/models/spikes '}
rows=[]
for pid,cmd in expected.items():
 p=Path('/proc')/str(pid)
 if not p.exists():continue
 actual=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode()
 assert actual==cmd and os.readlink(p/'cwd')=='/home/regner/.paseo/worktrees/0u71f39f/s06-provisional-turn-seam'
 os.kill(pid,signal.SIGTERM);rows.append({'pid':pid,'command':actual,'signal':'SIGTERM','reason':'owned CLI hung in audio teardown after confirmed source save/export'})
for _ in range(30):
 if all(not (Path('/proc')/str(pid)).exists() for pid in expected):break
 time.sleep(.1)
for pid in expected:
 if (Path('/proc')/str(pid)).exists():
  os.kill(pid,signal.SIGKILL);rows.append({'pid':pid,'signal':'SIGKILL','reason':'owned teardown timeout'})
Path('/tmp/s06-operations/blender-owned-stop.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
