import json,os,hashlib,subprocess
from pathlib import Path
R=Path.cwd();S=Path('/tmp/six-engine-review-c4067ff');L=json.loads(Path('/tmp/asset-register-production-editor/launch.json').read_text());pid=L['pid'];P=Path('/proc')/str(pid)
assert pid==195352 and Path(os.path.realpath(P/'cwd'))==R
args=(P/'cmdline').read_bytes().decode().strip('\0').split('\0');assert args==L['argv']
exe=os.path.realpath(P/'exe');assert exe==L['argv'][0]
paths=set()
for prefix in ['scenes/prefabs/environment','tests/fixtures/asset_production','tools/asset_production/integration']:
 for p in (S/prefix).rglob('*'):
  if p.is_file() and ('city_lights' in p.name or 'city_sign_supports_01' in p.name or 'city_planting_0' in p.name or prefix!='scenes/prefabs/environment'):paths.add(p.relative_to(S))
for aid in ['city_lights_01','city_lights_02','city_lights_04','city_sign_supports_01','city_planting_01','city_planting_02']:
 for prefix in ['art/models/environment','art/source/models/environment']:
  paths.update(p.relative_to(S) for p in (S/prefix/aid).rglob('*') if p.is_file())
rows=[dict(path=str(p),sha256=hashlib.sha256((R/p).read_bytes()).hexdigest(),matches_candidate=(R/p).read_bytes()==(S/p).read_bytes()) for p in sorted(paths)]
assert all(r['matches_candidate'] for r in rows)
log=Path('/tmp/asset-register-production-editor/editor-restarted.log')
logs=[dict(path=str(p),offset=p.stat().st_size) for p in Path('/tmp/asset-register-production-editor').glob('*.log')]
out=dict(pid=pid,cwd=str(R),argv=args,exe=exe,ports=[L['editor_port'],L['runtime_port'],L['lsp_port']],live_files=rows,log_offsets=logs)
(R/'docs/reviews/asset-production/batch_01/final/live-guard.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS exact private process and',len(rows),'live source/engine/tool file bytes; log offsets recorded')
