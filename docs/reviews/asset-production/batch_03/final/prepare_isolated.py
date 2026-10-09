import subprocess,pathlib,hashlib,json,shutil
O=pathlib.Path(__file__).resolve().parent;R=pathlib.Path('/tmp/batch03-final/project');R.mkdir(exist_ok=True);C='1031a3e1e66a404f67fa1a3857c4888d05f10d1e';rows=[]
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',C]).decode().splitlines()
for p in paths:
 if p.startswith(('docs/','tools/','.agents/','.codex/','art/source/')) or not (p.startswith(('addons/','art/','scenes/','scripts/','tests/','resources/','shaders/')) or p in ['project.godot','icon.svg']):continue
 if p.startswith('tests/fixtures/asset_production/batch_03_upper_wall/') and p.endswith('.blend'):continue
 if p.endswith(('.png.import','.glb.import')) or not p.endswith(('.md','.py','.log','.json','.blend','.blend1','.png')) or p.startswith(('art/','scenes/','scripts/','addons/','resources/','shaders/')):
  b=subprocess.check_output(['git','show',C+':'+p]);t=R/p;t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(b);rows.append(dict(path=p,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
# Only copy existing importer cache, never source evidence packs; read-only reference, rechecked runtime.
if pathlib.Path('.godot').exists():
 shutil.copytree('.godot',R/'.godot',dirs_exist_ok=True)
(O/'isolated-input-index.json').write_text(json.dumps(dict(candidate=C,files=rows,cache='Read-only copy of existing .godot; no fresh import/whole-project validity claim'),indent=2)+'\n');print(json.dumps(dict(files=len(rows),bytes=sum(r['bytes'] for r in rows),scratch=str(R))))
