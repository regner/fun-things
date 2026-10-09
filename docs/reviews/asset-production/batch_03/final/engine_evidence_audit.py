import json,pathlib,re,hashlib,statistics,struct,subprocess
O=pathlib.Path(__file__).resolve().parent;E=pathlib.Path('docs/assets/production/batch_03-evidence');report={}
def rows(p):return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def body(r):return r['result']['result']
actual=rows(O/'editor_audit.stdout');glb={r['name']:r for r in json.load(open(O/'glb-audit.json'))};models=[]
for r in actual:
 v=body(r)['result'];ident=pathlib.Path(v['prefab']).stem;target=glb[ident];lo=[min(m['min'][a] for m in v['mesh_rows']) for a in range(3)];hi=[max(m['min'][a]+m['size'][a] for m in v['mesh_rows']) for a in range(3)]
 assert all(abs(x-y)<.00001 for x,y in zip(lo+hi,sum(target['bounds_godot'],[])))
 assert all(m['resource'].startswith(v['model']+'::') for m in v['mesh_rows']);assert all(s['cull_mode']==0 and s['transparency']==0 for m in v['mesh_rows'] for s in m['surfaces'])
 expected_model='res://art/models/environment/'+ident.removesuffix('_single').removesuffix('_double')+'/'+ident+'.glb';assert v['model']==expected_model
 models.append(dict(name=ident,source=v['model'],bounds=[lo,hi],surfaces=[s for m in v['mesh_rows'] for s in m['surfaces']]))
assert len(models)==9
for ident,mesh,mat in [('city_shop_fittings_02','fascia_artwork_carrier','fascia_artwork_face'),('city_shop_fittings_08','face_positive_x','blade_artwork_positive_x'),('city_shop_fittings_08','face_negative_x','blade_artwork_negative_x')]:
 v=next(body(r)['result'] for r in actual if pathlib.Path(body(r)['result']['prefab']).stem==ident);m=next(m for m in v['mesh_rows'] if m['node']==mesh);assert m['surfaces'][0]['name']==mat
report['live_models']=models
cached=json.loads(next(l.removeprefix('REVIEW_RESOURCE ') for l in (O/'imported_geometry.stdout').read_text().splitlines() if l.startswith('REVIEW_RESOURCE ')))
assert cached['passed'] and len(cached['rows'])==9
for r in cached['rows']:
 ident=pathlib.Path(r['path']).stem;assert sum(m['triangles'] for m in r['meshes'])==glb[ident]['triangles']
report['isolated_imported_geometry_matches_counts']=True
uidrows=[]
for r in rows(E/'transport/audit-results.jsonl'):
 b=body(r)
 if b.get('method')=='register_uids':uidrows=b['result']
assert len(uidrows)==25
for r in uidrows:
 p=pathlib.Path(r['path'].removeprefix('res://'));p=p if p.suffix=='.tscn' else pathlib.Path(str(p)+'.import');uid=re.search('uid="([^"]+)"',p.read_text()).group(1);assert uid==r['uid'] and r['was_registered'] and r['resolved']==r['path']
report['retained_identities_confirmed']=uidrows
before=json.load(open(O/'review-roundtrip-before.json'));rr=rows(O/'roundtrip.stdout');assert len(rr)==78
for path,digest in before.items():
 assert hashlib.sha256(pathlib.Path(path.removeprefix('res://')).read_bytes()).hexdigest()==digest
 matching=[r for r in rr if body(r).get('path')==path];assert [r['method'] for r in matching]==['scene.open','editor.save_scene','scene.close','scene.open','editor.save_scene'];assert all(body(r)['success'] for r in matching)
 assert not body(matching[2])['unsaved_changes_discarded']
report['live_roundtrip_byte_identical_scenes']=list(before)
processes=[]
for label in ['review_process_a','review_process_b']:
 r=json.loads(next(l.removeprefix('BATCH03_PROCESS ') for l in (O/(label+'.stdout')).read_text().splitlines() if l.startswith('BATCH03_PROCESS ')));assert r['passed'] and len(r['rows'])==6 and all(x['passed'] for x in r['rows']);processes.append(r)
assert processes[0]['pid']!=processes[1]['pid'] and processes[0]['rows']==processes[1]['rows'] and processes[0]['aim_hit']==processes[1]['aim_hit'];report['own_separate_physics_processes']=processes
obs=[]
for label in ['native-final-recapture','repeat-probe']:
 rs=rows(E/f'transport/{label}-results.jsonl');m=body(rs[0])['result'];a=body(rs[1])['result'];assert m['passed'] and a['passed'] and len(m['samples'])==120 and m['query_iterations']==300;assert m['entrance_structure_void'] and m['display_structure_void'];ss=m['samples'][-60:]
 obs.append(dict(label=label,motion=m['motion'],assembly=a,query_usec=m['query_usec'],last60_medians={k:statistics.median(s[k] for s in ss) for k in ss[0]}))
report['retained_native_observations']=obs
report['native_pngs']={}
for name in ['gameplay.png','frontage-close.png','repetition.png']:
 b=(E/name).read_bytes();dims=struct.unpack('>II',b[16:24]);assert dims==(1280,800);report['native_pngs'][name]=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),dimensions=dims)
# Retain diagnostic classifications and immutable full-stream references, never rewrite producer evidence.
streams=[]
for p in sorted(E.rglob('*')):
 if p.is_file() and p.suffix in ['.log','.jsonl']:
  text=p.read_text(errors='replace');diagnostics=[l for l in text.splitlines() if re.search(r'error|warning|failed|timeout|exception|invalid|Traceback',l,re.I)];streams.append(dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),empty=not text,diagnostic_lines=diagnostics))
report['retained_full_stream_references']=streams
receipts=[]
for p in sorted(E.rglob('*execution.json')):
 r=json.loads(p.read_text());receipts.append(dict(path=str(p),receipt=r))
report['execution_receipts']=receipts
report['all_project_owned_native_checks_represent_static_fixture_only']=True
(O/'engine-evidence-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(models=len(models),identities=len(uidrows),own_byte_stable_roundtrips=len(before),process_pids=[p['pid'] for p in processes],native_observations=len(obs),retained_streams=len(streams),execution_receipts=len(receipts))))
