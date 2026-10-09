"""Collect independent remaining identity, calibration, material and cost observations.

Does not rerun the stopped composite audits. Retains raw linear/sRGB comparisons.
"""
import hashlib,json,re,statistics,struct,subprocess,zlib
from pathlib import Path
ROOT=Path('/home/regner/.paseo/worktrees/0u71f39f/asset-register-production')
SNAP=Path('/tmp/batch02-final-10ddb64/snapshot'); OUT=Path(__file__).resolve().parent
E=SNAP/'docs/assets/production/batch_02-evidence'; T=E/'transport'
C='10ddb64d16e6cb2f137923a31d3ca14991468f7d'
def original(p): return subprocess.check_output(['git','show',C+':'+p],cwd=ROOT)
def lines(p): return [json.loads(x) for x in p.read_text().splitlines()]
def nested(row): return row['result'].get('result',{}).get('result',{})
def sha(data): return hashlib.sha256(data).hexdigest()
def linear(v): return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
observed=json.loads((OUT/'resource-query-audit.json').read_text())
materials=[]; imports=[]; dependency_uids=[]
for row in observed['rows']:
    path=row['model_source'].removeprefix('res://'); binary=original(path)
    length=struct.unpack_from('<I',binary,12)[0]; gltf=json.loads(binary[20:20+length])
    for mesh in row['envelope']['meshes']:
        node=next(n for n in gltf['nodes'] if n['name']==mesh['path'].split('/')[-1])
        for primitive,actual in zip(gltf['meshes'][node['mesh']]['primitives'],mesh['materials']):
            source=gltf['materials'][primitive['material']]; pbr=source['pbrMetallicRoughness']
            materials.append(dict(id=row['id'],node=mesh['path'],name=source['name'],
              gltf_linear_rgba=pbr['baseColorFactor'],godot_srgb_rgba=actual['albedo'],
              max_linear_rgb_difference=max(abs(linear(actual['albedo'][a])-pbr['baseColorFactor'][a]) for a in range(3)),
              alpha_difference=abs(actual['albedo'][3]-pbr['baseColorFactor'][3]),
              roughness_difference=abs(actual['roughness']-pbr['roughnessFactor']),
              metallic_difference=abs(actual['metallic']-pbr['metallicFactor']),
              gltf_double_sided=source.get('doubleSided',False),godot_cull_mode=actual['cull_mode'],
              godot_transparency=actual['transparency'],override=mesh['override']))
    sidecar=original(path+'.import').decode()
    imports.append(dict(path=path,source_file=re.search(r'source_file="([^"]+)"',sidecar).group(1),
      uid=re.search(r'uid="([^"]+)"',sidecar).group(1),root_scale_1='nodes/root_scale=1.0' in sidecar,
      generate_lods='meshes/generate_lods=true' in sidecar,
      unchanged_after_scratch_import=(SNAP/(path+'.import')).read_bytes()==original(path+'.import')))
before=json.loads((T/'roundtrip-before.json').read_text())
for p in before:
    for text in original(p).decode().splitlines():
        if not text.startswith('[ext_resource'): continue
        match=re.search(r'uid="([^"]+)" path="res://([^"]+)"',text)
        if not match: continue
        uid,path=match.groups()
        data=original(path+'.import' if path.endswith('.glb') else path+'.uid' if path.endswith('.gd') else path).decode()
        target=data.strip() if path.endswith('.gd') else re.search(r'uid="([^"]+)"',data).group(1)
        dependency_uids.append(dict(consumer=p,path=path,declared_uid=uid,target_uid=target,match=uid==target))
cost=[];native=[]
for name,file in [('baseline','final-native-probe-results.jsonl'),('repeat','repeat-final-probe-results.jsonl')]:
    res=nested(lines(T/file)[0]); samples=res['frame_samples']
    cost.append(dict(scenario=name,sample_count=len(samples),last60_medians={key:statistics.median(x[key] for x in samples[-60:]) for key in samples[0]},
      process_min_max=[min(x['process_s'] for x in samples),max(x['process_s'] for x in samples)],query_usec=res['query_batch_usec']))
    copy=dict(res); copy.pop('frame_samples',None);native.append(dict(scenario=name,result=copy))
processes=[]
for label in ['process_a','process_b']:
    command=json.loads((E/'processes'/f'{label}.execution.json').read_text())
    output=(E/'processes'/f'{label}.stdout.log').read_text()
    result=json.loads(output.split('BATCH02_PROCESS ')[1].splitlines()[0])
    processes.append(dict(command=command,result=result,stderr_bytes=(E/'processes'/f'{label}.stderr.log').stat().st_size))
images=[]
for p in [E/'gameplay.png',E/'mounting-close.png',E/'roof-close.png',E/'repetition.png',E/'calibration/tree-roof-metre-front-up-comparison.png']:
    data=p.read_bytes(); pos=8; valid=data[:8]==b'\x89PNG\r\n\x1a\n'; dims=None
    while pos<len(data):
        length=struct.unpack_from('>I',data,pos)[0]; kind=data[pos+4:pos+8]; chunk=data[pos+8:pos+8+length]
        crc=struct.unpack_from('>I',data,pos+8+length)[0]; valid=valid and zlib.crc32(kind+chunk)==crc
        if kind==b'IHDR': dims=list(struct.unpack_from('>II',chunk))
        pos+=length+12
    images.append(dict(path=str(p.relative_to(SNAP)),dimensions=dims,valid_crc=valid and pos==len(data),sha256=sha(data)))
cal=json.loads((OUT/'calibration-datums.json').read_text()); meta=json.loads((E/'calibration/tree-roof-measurements.json').read_text())
calibration=[]
for row in meta['assets']:
    actual=next(x for x in cal['instances'] if x['collection']==row['collection'])
    calibration.append(dict(collection=row['collection'],actual=actual,
      source_sha256=sha(original(row['source'])),retained_source_sha256=row['source_sha256_before'],
      glb_sha256=sha(original(row['glb'])),retained_glb_sha256=row['glb_sha256']))
results=dict(materials=materials,imports=imports,dependency_uids=dependency_uids,cost=cost,native=native,
 retained_processes=processes,images=images,calibration=calibration)
(OUT/'remaining-observations.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(dict(material_surfaces=len(materials),max_material_linear_rgb_delta=max(x['max_linear_rgb_difference'] for x in materials),
 roughness_max_delta=max(x['roughness_difference'] for x in materials),metallic_max_delta=max(x['metallic_difference'] for x in materials),
 uid_references=len(dependency_uids),uid_mismatches=[x for x in dependency_uids if not x['match']],imports=imports,cost=cost,images=images),indent=2))
