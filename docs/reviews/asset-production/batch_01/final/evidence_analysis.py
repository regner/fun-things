import json,re,hashlib,statistics,subprocess
from pathlib import Path
R=Path('/tmp/six-engine-review-c4067ff');O=Path(__file__).resolve().parent;E=R/'docs/assets/production/batch_01-evidence';T=E/'transport'
C='c4067ff3abe1384301471d9a64e94e84201235e2';S='390377dc6530e101eddcbf38b2946a1b235137c7';B='66400c26a01bf917dfe631af4762c2b444d9c48f'
delta=[]
for line in subprocess.check_output(['git','diff','--name-status',S,C],text=True).splitlines():
 status,path=line.split('\t');p=R/path
 delta.append(dict(status=status,path=path,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),git_blob=subprocess.check_output(['git','rev-parse',C+':'+path],text=True).strip()))
(O/'actual-delta-file-index.json').write_text(json.dumps(dict(candidate=C,source=S,base=B,count=len(delta),files=delta),indent=2)+'\n')
logs=[]
for p in sorted(T.glob('*.log')):
 txt=p.read_text();diagnostics=[dict(line=i+1,text=line) for i,line in enumerate(txt.splitlines()) if re.search('ERROR|WARNING|invalid UID|SCRIPT ERROR|Assertion|Traceback|Error:',line)]
 logs.append(dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),diagnostics=diagnostics))
old=(T/'editor.log').read_text();new=(T/'editor-restarted.log').read_text();offset=json.loads((T/'final-log-offset.json').read_text())['offset'];tail=new[offset:]
uid_old=[dict(line=i+1,text=l) for i,l in enumerate(old.splitlines()) if 'invalid UID' in l]
uid_new=[dict(line=i+1,text=l) for i,l in enumerate(new.splitlines()) if 'invalid UID' in l]
recent=[dict(line=i+1,text=l) for i,l in enumerate(tail.splitlines()) if re.search('ERROR|WARNING|invalid UID|SCRIPT ERROR',l)]
(O/'retained-diagnostic-analysis.json').write_text(json.dumps(dict(logs=logs,old_uid_fallbacks=uid_old,restarted_uid_fallbacks=uid_new,final_offset=offset,final_tail_diagnostics=recent,offset_note='Producer offset starts inside a transport log line; full restarted log is also independently scanned, so no warning depends on an exact byte boundary.'),indent=2)+'\n')
scene=(R/'tests/fixtures/asset_production/batch_01_repeat.tscn').read_text();inst=re.findall(r'\[node name="Repeat_(city_[^"]+)_([0-7])"[^\n]*',scene);counts={}
for aid,i in inst:counts[aid]=counts.get(aid,0)+1
assert len(inst)==48 and all(n==8 for n in counts.values()) and len(counts)==6
observations=[]
for f in ['batch-final-styled-probe-results.jsonl','batch-repeat-probe-results.jsonl']:
 commands=[json.loads(l) for l in (T/f).read_text().splitlines()];obs=commands[0]['result']['result']['result'];frames=obs['render_samples'];assert len(frames)==120
 medians={k:statistics.median(x[k] for x in frames[-60:]) for k in frames[0]}
 observations.append(dict(file=f,raw_frame_count=len(frames),analysis_frame_indices=[60,119],medians=medians,first_frame=frames[0],last_frame=frames[-1],queries=obs['queries'],query_batch_usec=obs['query_batch_usec'],motion=obs['motion_outcomes'],outcomes=obs['outcomes'],passed=obs['passed']))
rounds=[json.loads(l) for l in (T/'batch-final-audit-results.jsonl').read_text().splitlines()];states=[]
for row in rounds:
 if row['method'] in ['scene.open','scene.close','editor.save_scene']:
  states.append(dict(method=row['method'],receipt=row['result']['result']))
assert all(x['receipt'].get('success') for x in states)
assert not any(x['receipt'].get('unsaved_changes_discarded',False) for x in states)
# Independent aggregate engine bounds, material and normal interface expectations.
interfaces=json.loads((O/'independent-engine-interfaces.json').read_text());prior=json.loads((O.parent/'independent-model-bounds.json').read_text())
assets=[]
for row in interfaces['prefabs']:
 meshes=[r for r in row['rows'] if r['type']=='mesh'];bounds=dict(min=[min(r['min'][a] for r in meshes) for a in range(3)],max=[max(r['max'][a] for r in meshes) for a in range(3)])
 materials=[]
 for mesh in meshes:
  for surface in mesh['surfaces']:
   assert surface['finite'] and surface['vertices']==surface['normals']
   assert abs(surface['normal_min']-1)<0.0001 and abs(surface['normal_max']-1)<0.0001
   materials.append(surface['material'])
 assert row['uid_registered'] and row['model_registered'] and row['uid_path']==row['path'] and row['model_uid_path']==row['model']
 assets.append(dict(prefab=row['path'],model=row['model'],bounds=bounds,surface_count=len(materials),materials=materials))
(O/'measured-evidence-analysis.json').write_text(json.dumps(dict(repeat_counts=counts,repeat_total=48,observations=observations,roundtrip_operations=states,roundtrip_operation_count=len(states),independent_imported_assets=assets),indent=2)+'\n')
# Retain our actual private editor raw log, with exact incremental offsets.
launch=Path('/tmp/asset-register-production-editor');guard=json.loads((O/'live-guard.json').read_text());fresh=[]
for info in guard['log_offsets']:
 p=Path(info['path']);
 if p.stat().st_size == info['offset']:continue
 target=O/('private-'+p.name);target.write_bytes(p.read_bytes());tail=target.read_bytes()[info['offset']:].decode(errors='replace')
 rows=[dict(line=i+1,text=l) for i,l in enumerate(tail.splitlines()) if re.search('ERROR|WARNING|invalid UID|SCRIPT ERROR',l)]
 fresh.append(dict(source=str(p),retained=target.name,start_byte_offset=info['offset'],end_byte_offset=target.stat().st_size,review_tail_diagnostics=rows))
(O/'fresh-diagnostic-analysis.json').write_text(json.dumps(fresh,indent=2)+'\n')
print('PASS exact delta',len(delta),'files;',len(logs),'retained raw logs read;',len(uid_old),'old UID warnings;',len(uid_new),'restarted UID warnings;',len(recent),'post-offset diagnostics; repeat48 and120-frame series independently analysed; saved operations',len(states))
print('Fresh diagnostic groups:',fresh)
