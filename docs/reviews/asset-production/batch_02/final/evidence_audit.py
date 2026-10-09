"""Assert retained request/result meaning and independent importer measurements."""
import hashlib,json,re,statistics,struct,subprocess,zlib
from pathlib import Path
ROOT=Path('/home/regner/.paseo/worktrees/0u71f39f/asset-register-production')
SNAP=Path('/tmp/batch02-final-10ddb64/snapshot')
OUT=Path(__file__).resolve().parent
E=SNAP/'docs/assets/production/batch_02-evidence'; T=E/'transport'
C='10ddb64d16e6cb2f137923a31d3ca14991468f7d'
def original(p): return subprocess.check_output(['git','show',C+':'+p],cwd=ROOT)
def readlines(p): return [json.loads(line) for line in p.read_text().splitlines()]
def nested(row): return row['result'].get('result',{}).get('result',{})
def sha(data): return hashlib.sha256(data).hexdigest()
commands=json.loads((T/'commands.json').read_text()); transport=[]
for command in commands:
    result=SNAP/command['result']; rows=readlines(result)
    assert len(rows)==command['completed_response_count'],command['result']
    if 'retained_request' in command:
        requests=json.loads((SNAP/command['retained_request']).read_text())
        assert len(rows)<=len(requests)
        assert [r['method'] for r in rows]==[r['method'] for r in requests[:len(rows)]]
    transport.append(dict(path=command['result'],response_count=len(rows),exit=command['observed_client_exit_code']))
audit=readlines(T/'audit-results.jsonl'); requests=json.loads((T/'audit-requests.json').read_text())
before=json.loads((T/'roundtrip-before.json').read_text()); roundtrips=[]
for p,digest in before.items():
    assert sha(original(p))==digest,p
    indices=[i for i,r in enumerate(requests) if r['method']=='scene.close' and r.get('params',{}).get('file_path')=='res://'+p]
    assert len(indices)==1,p
    i=indices[0]
    assert [requests[j]['method'] for j in [i-2,i-1,i,i+1,i+2]]==['scene.open','editor.save_scene','scene.close','scene.open','editor.save_scene']
    for j in [i-2,i-1,i,i+1,i+2]:
        receipt=audit[j]['result']['result']
        assert receipt.get('success') is True
        assert receipt.get('path')=='res://'+p
    assert audit[i]['result']['result']['unsaved_changes_discarded'] is False
    roundtrips.append(dict(path=p,before_and_candidate_sha256=digest,request_indices=list(range(i-2,i+3))))
assert len(roundtrips)==13
paths=json.loads((T/'source-paths.json').read_text())
source_retention=[]
for p in paths:
    source=subprocess.check_output(['git','show','5e94cc0ea4155219285db49c64b5728e0882b093:'+p],cwd=ROOT)
    assert source==original(p),p
    source_retention.append(dict(path=p,bytes=len(source),sha256=sha(source)))
(OUT/'all-retained-source-payloads.json').write_text(json.dumps(source_retention,indent=2)+'\n')
# Compare imported runtime AABBs with earlier independently decoded source GLBs.
initial=json.loads((SNAP/'docs/reviews/asset-production/batch_02/initial/binary-audit.json').read_text())
observed=json.loads((OUT/'resource-query-audit.json').read_text())
row_map={x['id']:x for x in observed['rows']}; imports=[]; dependency_uids=[]
for row in initial:
    id=row['root']; runtime=row_map[id]
    assert runtime['model_source']=='res://'+row['committed_path']
    assert runtime['model_transform_identity'] and runtime['root_transform_identity'] and runtime['visual_transform_identity']
    for label,expected in zip(['min','max'],row['godot_bounds']):
        assert max(abs(x-y) for x,y in zip(runtime['envelope'][label],expected))<2e-5
    glb=original(row['committed_path']); length=struct.unpack_from('<I',glb,12)[0]
    gltf=json.loads(glb[20:20+length]); materials=gltf.get('materials',[])
    for mesh in runtime['envelope']['meshes']:
        assert mesh['source'].startswith('res://'+row['committed_path']+'::ArrayMesh_')
        assert mesh['override'] is False
        leaf=mesh['path'].split('/')[-1]
        gnode=next(n for n in gltf['nodes'] if n['name']==leaf)
        primitives=gltf['meshes'][gnode['mesh']]['primitives']
        assert len(primitives)==len(mesh['materials'])
        for primitive,actual in zip(primitives,mesh['materials']):
            material=materials[primitive['material']]; pbr=material['pbrMetallicRoughness']
            assert max(abs(a-b) for a,b in zip(actual['albedo'],pbr['baseColorFactor']))<1e-5
            assert abs(actual['roughness']-pbr['roughnessFactor'])<1e-5
            assert abs(actual['metallic']-pbr['metallicFactor'])<1e-5
            assert actual['transparency']==0 and actual['cull_mode']==(2 if material.get('doubleSided') else 0)
    sidecar=original(row['committed_path']+'.import').decode()
    assert 'nodes/root_scale=1.0' in sidecar and 'meshes/generate_lods=true' in sidecar
    assert re.search(r'uid="(uid://[^"]+)"',sidecar)
    assert (SNAP/(row['committed_path']+'.import')).read_bytes()==original(row['committed_path']+'.import')
    imports.append(dict(id=id,source=row['committed_path'],uid=runtime['uid'],bounds=runtime['envelope']['size'],
      linked_material_surfaces=sum(len(m['materials']) for m in runtime['envelope']['meshes']),collision_bodies=runtime['bodies']))
for p in before:
    text=original(p).decode()
    for line in text.splitlines():
        if not line.startswith('[ext_resource'): continue
        match=re.search(r'uid="([^"]+)" path="res://([^"]+)"',line)
        if not match: continue
        uid,path=match.groups(); data=original(path+'.import' if path.endswith('.glb') else path+'.uid' if path.endswith('.gd') else path).decode()
        target_uid=data.strip() if path.endswith('.gd') else re.search(r'uid="([^"]+)"',data).group(1)
        assert uid==target_uid,(p,path,uid,target_uid)
        dependency_uids.append(dict(consumer=p,path=path,uid=uid))
def probe(name): return nested(readlines(T/name)[0])
baseline=probe('final-native-probe-results.jsonl'); repeated=probe('repeat-final-probe-results.jsonl')
cost=[]
for name,result in [('baseline',baseline),('repeat',repeated)]:
    samples=result['frame_samples']; assert len(samples)==120
    summary={key:statistics.median(x[key] for x in samples[-60:]) for key in samples[0]}
    summary['max_process_s_all_samples']=max(x['process_s'] for x in samples)
    summary['scenario']=name; summary['sample_count']=len(samples); summary['query_batch_usec']=result['query_batch_usec']
    cost.append(summary)
    assert result['aim_hit'].endswith('/BroadTree/Collision/PoleBody')
    assert all(v['hit']==v['expected'] for v in result['overlaps'].values())
    assert all(v['passed'] for v in result['motion'].values())
# Raw distinct retained process results, not blanket multiplayer acceptance.
processes=[]
for label in ['process_a','process_b']:
    receipt=json.loads((E/'processes'/f'{label}.execution.json').read_text())
    raw=(E/'processes'/f'{label}.stdout.log').read_text()
    outcome=json.loads(raw.split('BATCH02_PROCESS ')[1].splitlines()[0])
    assert receipt['pid']==outcome['pid'] and receipt['exit_code']==0
    assert (E/'processes'/f'{label}.stderr.log').read_bytes()==b''
    assert len(outcome['rows'])==3
    processes.append(dict(execution=receipt,outcome=outcome))
assert processes[0]['execution']['pid']!=processes[1]['execution']['pid']
assert processes[0]['outcome']['rows']==processes[1]['outcome']['rows']
# PNG integrity: check every chunk CRC and actual IHDR dimensions without Pillow.
images=[]
for p in [E/'gameplay.png',E/'mounting-close.png',E/'roof-close.png',E/'repetition.png',E/'calibration/tree-roof-metre-front-up-comparison.png']:
    raw=p.read_bytes(); assert raw[:8]==b'\x89PNG\r\n\x1a\n'; pos=8; dimensions=None
    while pos<len(raw):
        size=struct.unpack_from('>I',raw,pos)[0]; kind=raw[pos+4:pos+8]; content=raw[pos+8:pos+8+size]
        crc=struct.unpack_from('>I',raw,pos+8+size)[0]
        assert zlib.crc32(kind+content)==crc
        if kind==b'IHDR': dimensions=list(struct.unpack_from('>II',content))
        pos+=size+12
    assert pos==len(raw)
    images.append(dict(path=str(p.relative_to(SNAP)),dimensions=dimensions,sha256=sha(raw)))
result=dict(retained_transport=transport,source_payload_count=len(source_retention),roundtrips=roundtrips,
 imports=imports,dependency_uids=dependency_uids,desktop_counter_summaries=cost,retained_processes=processes,images=images,
 independent_canopy_travel=observed['canopy_travel'],independent_queries=observed['query_samples'])
(OUT/'evidence-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(passed=True,imports=len(imports),roundtrips=len(roundtrips),unchanged_source_payloads=len(source_retention),
 dependencies=len(dependency_uids),cost=cost,images=images),indent=2))
