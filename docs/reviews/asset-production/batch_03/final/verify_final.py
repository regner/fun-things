import hashlib,json,pathlib,subprocess
O=pathlib.Path(__file__).resolve().parent
C='1031a3e1e66a404f67fa1a3857c4888d05f10d1e';P='4f11c54d4abf4aa77813a1cf8bcf885fd040b7c9';I='028775618c4493ca672646e6e37fdc3c83e0e313';B='66400c26a01bf917dfe631af4762c2b444d9c48f'
def git(*a):return subprocess.check_output(['git',*a])
def blob(p,c=C):return git('show',c+':'+p)
def sha(b):return hashlib.sha256(b).hexdigest()
def entry(p,e=None):
 b=blob(p);w=pathlib.Path(p).read_bytes();r=dict(path=p,bytes=len(b),sha256=sha(b),working_matches=b==w)
 if e:r['expected_matches']=len(b)==e['bytes'] and sha(b)==e['sha256']
 return r
paths=set(git('ls-tree','-r','--name-only',C).decode().splitlines());src=json.loads(blob('docs/assets/production/batch_03-evidence/source-readback.json'));idx={};records=[]
for rec in src['records']:
 ident=rec['id'];mp=f'docs/assets/production/{ident}-evidence/manifest.json';raw=json.loads(blob(mp));es=raw if isinstance(raw,list) else raw['files'];expected={e['path'] for e in es}|{mp};observed={p for p in paths if any(p.startswith(r) for r in [f'art/source/models/environment/{ident}/',f'art/models/environment/{ident}/',f'tools/asset_production/{ident}/',f'docs/assets/production/{ident}-evidence/']) and not p.endswith('.import')}|{f'docs/assets/production/{ident}.md'}
 for e in es:idx[e['path']]=entry(e['path'],e)
 idx[mp]=entry(mp);idx[mp]['historical_source_readback_manifest_sha256']=rec['manifest_sha256'];correction=json.loads(blob('docs/assets/production/batch_03-evidence/correction-readback.json'));current=next((r for r in correction['records'] if r['id']==ident),rec);idx[mp]['expected_matches']=sha(blob(mp))==current['manifest_sha256']
 records.append(dict(id=ident,count=len(es),manifest_sha256=sha(blob(mp)),missing=sorted(expected-observed),extra=sorted(observed-expected)))
 for p in expected:
  if p.startswith('art/') or p.endswith(('mounted_frontage_scratch.blend','fitted_comparison.blend')):
   t=pathlib.Path('/tmp/batch03-final/frozen')/p;t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(blob(p))
ep='docs/assets/production/batch_03-evidence/engine-artifact-index.json';engine=json.loads(blob(ep));ei=[entry(e['path'],e) for e in engine['files']]+[entry(ep)];enginepaths={e['path'] for e in ei};actual=set(git('diff','--name-only',P,C).decode().splitlines())
deltas={}
for label,a,z in [('source_correction',I,P),('engine',P,C),('original_base',B,C)]:
 lines=git('diff','--name-status',a,z).decode().splitlines();rs=[]
 for line in lines:
  status,p=line.split('\t');r=dict(status=status,path=p)
  for key,rev in [('before',a),('after',z)]:
   if (key=='before' and status!='A') or (key=='after' and status!='D'):
    b=blob(p,rev);r[key]=dict(bytes=len(b),sha256=sha(b))
  rs.append(r)
 deltas[label]=rs
initial=[entry(p) for p in sorted(paths) if p.startswith('docs/reviews/asset-production/batch_03/initial/')];immutable=[dict(path=r['path'],bytes=r['bytes'],sha256=r['sha256']) for r in initial]
ref=[]
for ext,prefix in [('blend','art/source/models/environment'),('glb','art/models/environment')]:
 p=f'{prefix}/city_shop_fittings_01/city_shop_fittings_01.{ext}';ref.append(entry(p));t=pathlib.Path('/tmp/batch03-final/frozen')/p;t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(blob(p))
wall='art/source/models/spikes/batch_03_upper_wall/batch_03_upper_wall.blend';t=pathlib.Path('/tmp/batch03-final/frozen')/wall;t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(blob(wall))
result=dict(candidate=C,parent=P,initial=I,original_base=B,actual_head=git('rev-parse','HEAD').decode().strip(),actual_parent=git('rev-parse',C+'^').decode().strip(),producer_records=records,producer_payload_count=len(idx)-7,producer_expected_paths=sorted(idx),producer_files=[idx[p] for p in sorted(idx)],engine_expected_paths=sorted(enginepaths),engine_files=ei,engine_index_self_exclusion=ep,engine_delta_missing=sorted(actual-enginepaths),engine_delta_extra=sorted(enginepaths-actual),actual_deltas=deltas,initial_immutable_references=immutable,reference_interfaces=ref,untracked_excluded=git('ls-files','--others','--exclude-standard').decode().splitlines())
(O/'candidate-file-index.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(producer_payload_count=len(idx)-7,records=records,engine_payload_count=len(ei)-1,engine_delta_missing=result['engine_delta_missing'],engine_delta_extra=result['engine_delta_extra'],delta_counts={k:len(v) for k,v in deltas.items()},initial_pack_count=len(initial)),indent=2))
assert result['actual_head']==C and result['actual_parent']==P
assert all(r['working_matches'] and r.get('expected_matches',True) for r in list(idx.values())+ei+initial+ref)
assert not result['engine_delta_missing'];assert set(result['engine_delta_extra'])=={f'docs/assets/production/batch_03-evidence/{n}.json' for n in ['correction-readback','review-retention-readback','source-readback']};assert all(blob(p,P)==blob(p) for p in result['engine_delta_extra'])
assert all(not r['missing'] and not r['extra'] for r in records)
assert len(idx)-7==594 and len(ei)==300
assert set(src['exact_frozen_paths'])==set(idx)
