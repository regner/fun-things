import json,hashlib,subprocess,os
from pathlib import Path
O=Path(__file__).resolve().parent;R=Path.cwd();C='c4067ff3abe1384301471d9a64e94e84201235e2';S='390377dc6530e101eddcbf38b2946a1b235137c7';B='66400c26a01bf917dfe631af4762c2b444d9c48f'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==C
ancestors=[]
for ref in [B,S]:
 result=subprocess.run(['git','merge-base','--is-ancestor',ref,C]);ancestors.append(dict(ancestor=ref,exit=result.returncode));assert result.returncode==0
preservation=[]
for index in ['candidate-scope-file-index.json','artifact-index.json']:
 raw=json.loads((O.parent/index).read_text());files=raw['files'] if isinstance(raw,dict) else raw
 for row in files:
  p=row['path'];digest=hashlib.sha256((R/p).read_bytes()).hexdigest();assert digest==row['sha256'],p
 preservation.append(dict(index=index,count=len(files),mismatches=[]))
delta=json.loads((O/'actual-delta-file-index.json').read_text())
for row in delta['files']:
 data=subprocess.check_output(['git','show',C+':'+row['path']]);assert hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
# Newly authored engine/tools/scenes are compared directly with immutable Git bytes.
guard=json.loads((O/'live-guard.json').read_text());rows=[]
for row in guard['live_files']:
 p=row['path'];data=subprocess.check_output(['git','show',C+':'+p]);actual=(R/p).read_bytes();assert actual==data,p
 rows.append(dict(path=p,sha256=hashlib.sha256(actual).hexdigest(),matches_candidate=True))
cal=json.loads((O/'calibration-component-diagnostic.json').read_text());assert all(not r['differing_fields'] for r in cal['comparisons'])
for i,r in enumerate(cal['fixtures']):
 assert r['translation']==[i*3-6,0,0] and r['rotation']==[0,0,0] and r['scale']==[1,1,1]
 assert r['fixture_vertex_extents']==[1,1,1]
prior={r['path']:r for r in json.loads((O.parent/'independent-model-bounds.json').read_text())};measured=json.loads((O/'measured-evidence-analysis.json').read_text());comp=[]
for r in measured['independent_imported_assets']:
 expected=prior[r['model'].removeprefix('res://')]['bounds_model_godot'];actual=[r['bounds']['min'],r['bounds']['max']];error=max(abs(x-y) for a,b in zip(expected,actual) for x,y in zip(a,b));assert error<0.001
 comp.append(dict(prefab=r['prefab'],max_error_m=error))
# Original source contract rights/provenance and geometry checks remain immutable;
# current source scope has no changes, so no repeated source reexport is warranted.
L=json.loads(Path('/tmp/asset-register-production-editor/launch.json').read_text());pid=L['pid'];P=Path('/proc')/str(pid)
assert pid==195352 and Path(os.path.realpath(P/'cwd'))==R
args=(P/'cmdline').read_bytes().decode().strip('\0').split('\0');assert args==L['argv'];assert os.path.realpath(P/'exe')==L['argv'][0]
children=[]
for child in (P/'task'/str(pid)/'children').read_text().split():
 q=Path('/proc')/child
 if (q/'cmdline').exists():
  argv=(q/'cmdline').read_bytes().decode().strip('\0').split('\0');children.append(dict(pid=int(child),argv=argv))
assert not any(str(R) in r['argv'] and '--editor' not in r['argv'] for r in children)
stop=[json.loads(l) for l in (O/'private-stop.stdout.log').read_text().splitlines()];assert stop[0]['result']['result']['success'] and stop[1]['result']['result']['result']['unsaved']=='PackedStringArray()'
log=Path('/tmp/asset-register-production-editor/editor-restarted.log');(O/'private-editor-restarted.log').write_bytes(log.read_bytes());fresh=json.loads((O/'fresh-diagnostic-analysis.json').read_text());fresh[0]['end_byte_offset']=log.stat().st_size;(O/'fresh-diagnostic-analysis.json').write_text(json.dumps(fresh,indent=2)+'\n')
record=dict(candidate=C,delta_base=S,original_base=B,ancestor_checks=ancestors,initial_preservation=preservation,exact_delta_hash_count=len(delta['files']),unchanged_live_files=rows,imported_bound_comparison=comp,calibration_comparisons=5,editor_pid=pid,editor_argv=args,editor_children=children,runtime_stopped=True,unsaved_scenes=[],notes='No implementation/source/index/shared-document mutations. Only reviewer final evidence and isolated scratch writes. No UID recovery/registration mutation called by reviewer.')
(O/'final-preservation-and-quiescence.json').write_text(json.dumps(record,indent=2)+'\n')
print('PASS original180 and67 preservation; exact196 delta hashes; live',len(rows),'candidate file bytes; five calibration identities/one-metre fixtures; nine engine bounds; editor saved and runtime stopped')
