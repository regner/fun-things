"""Independently assess final delta, old evidence preservation and indexed integrity."""
import hashlib,json,re,subprocess
from pathlib import Path
O=Path(__file__).resolve().parent;R=Path('/tmp/six-engine-review-c4067ff');C='c4067ff3abe1384301471d9a64e94e84201235e2';S='390377dc6530e101eddcbf38b2946a1b235137c7';B='66400c26a01bf917dfe631af4762c2b444d9c48f'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify_index(path):
 data=json.loads((R/path).read_text());rows=data.get('files',data) if isinstance(data,dict) else data
 if isinstance(rows,dict):rows=[dict(path=k,**v) for k,v in rows.items()]
 return dict(index=path,count=len(rows),mismatches=[x['path'] for x in rows if not (R/x['path']).exists() or (R/x['path']).stat().st_size!=x['bytes'] or digest(R/x['path'])!=x['sha256']])
indices=[verify_index(x) for x in ['docs/reviews/asset-production/batch_01/candidate-scope-file-index.json','docs/reviews/asset-production/batch_01/artifact-index.json','docs/assets/production/batch_01-evidence/integration-artifact-index.json']]
old=json.loads((R/'docs/reviews/asset-production/batch_01/artifact-index.json').read_text())['files'];local=[]
for x in old:
 p=Path(x['path']);local.append(dict(path=x['path'],matches_current_local=p.exists() and digest(p)==x['sha256']))
paths=subprocess.run(['git','diff','--name-status',S,C],capture_output=True,text=True,check=True);(O/'actual-delta.stdout.log').write_text(paths.stdout);(O/'actual-delta.stderr.log').write_text(paths.stderr)
changed=[line.split('\t') for line in paths.stdout.splitlines()]
ids=['city_lights_01','city_lights_02','city_lights_04','city_sign_supports_01','city_planting_01','city_planting_02']
source_changes=[p for status,p in changed if any(p.startswith(f'{pre}/{a}/') for a in ids for pre in ['art/source/models/environment','tools/asset_production']) or (p.endswith('.glb') and any(a in p for a in ids))]
prefabs=sorted(p for p in (R/'scenes/prefabs/environment').glob('*.tscn') if any(p.stem==a or p.stem==a+'_cool' for a in ids));scene_rows=[]
for path in prefabs:
 text=path.read_text();refs=[]
 for line in text.splitlines():
  if line.startswith('[ext_resource'):
   source=re.search(r'path="res://([^"\n]+)"',line).group(1);uid=re.search(r'uid="([^"]+)"',line).group(1);ip=R/(source+'.import');actual=re.search(r'uid="([^"]+)"',ip.read_text()).group(1) if ip.exists() else None
   refs.append(dict(path=source,scene_uid=uid,import_uid=actual,uid_matches=uid==actual))
 scene_rows.append(dict(path=str(path.relative_to(R)),sha256=digest(path),references=refs,embedded_render_mesh=bool(re.search(r'ArrayMesh|BoxMesh|SphereMesh|CylinderMesh|CSG',text)),editable_imported_children='[editable' in text,script_attached='type="Script"' in text,node_id_count=len(re.findall(r'unique_id=',text)),collision_shapes=len(re.findall(r'type="CollisionShape3D"',text))))
roundtrip=json.loads((R/'docs/assets/production/batch_01-evidence/transport/final-before-roundtrip.json').read_text());stable=[dict(path=k,sha256=v,matches_candidate=digest(R/k)==v) for k,v in roundtrip.items()]
initial=[]
for name in ['city_lights_01','city_lights_01_cool','city_lights_02','city_lights_02_cool']:
 p='scenes/prefabs/environment/'+name+'.tscn';before=subprocess.run(['git','show',S+':'+p],capture_output=True,text=True,check=True).stdout;after=(R/p).read_text()
 initial.append(dict(path=p,uids_same=re.findall(r'uid="[^"]+"',before)==re.findall(r'uid="[^"]+"',after),node_ids_same=re.findall(r'unique_id=\d+',before)==re.findall(r'unique_id=\d+',after),byte_identical=before==after,delta=subprocess.run(['git','diff',S,C,'--',p],capture_output=True,text=True,check=True).stdout))
indexed=json.loads((R/'docs/assets/production/batch_01-evidence/integration-artifact-index.json').read_text())['files'];declared={x['path'] for x in indexed}
new_engine=[p for s,p in changed if not p.startswith('docs/reviews/') and not p.startswith('docs/assets/production/city_lights_02-evidence/')]
results=dict(candidate=C,source_candidate=S,base=B,indices=indices,local_original_review_preservation=local,source_geometry_or_tool_changes=source_changes,delta_count=len(changed),delta=changed,prefabs=scene_rows,roundtrip_hashes=stable,initial_uid_node_identity=initial,unindexed_delta_paths=sorted(set(new_engine)-declared-{'docs/assets/production/batch_01-evidence/integration-artifact-index.json'}))
(O/'static-audit.json').write_text(json.dumps(results,indent=2)+'\n');assert not source_changes
assert all(not x['mismatches'] for x in indices) and all(x['matches_current_local'] for x in local)
assert len(scene_rows)==9 and all(not x['embedded_render_mesh'] and not x['editable_imported_children'] and all(r['uid_matches'] for r in x['references']) for x in scene_rows)
assert all(x['matches_candidate'] for x in stable) and all(x['uids_same'] and x['node_ids_same'] for x in initial)
print(json.dumps({k:v for k,v in results.items() if k not in ['delta','local_original_review_preservation','initial_uid_node_identity','roundtrip_hashes']},indent=2))
