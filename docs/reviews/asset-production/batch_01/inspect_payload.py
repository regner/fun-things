"""Independent expected-set/hash and GLB binary geometry/material/UV checks."""
import hashlib,json,math,re,struct
from pathlib import Path
ROOT=Path('/tmp/six-asset-review-390377d');OUT=Path(__file__).resolve().parent
readback=json.loads((ROOT/'docs/assets/production/batch_01-evidence/source-readback.json').read_text())
manifest_reports=[];glb_reports=[]
for row in readback:
    aid=row['id'];mp=ROOT/row['manifest'];manifest=json.loads(mp.read_text());entries=manifest if isinstance(manifest,list) else manifest.get('files',manifest.get('artifacts',manifest))
    if isinstance(entries,dict):entries=[dict(path=p,**v) for p,v in entries.items()]
    declared={e['path'] for e in entries};actual=set()
    for p in ['art/source/models/environment/'+aid,'art/models/environment/'+aid,'tools/asset_production/'+aid,'docs/assets/production/'+aid+'-evidence']:
        actual.update(str(x.relative_to(ROOT)) for x in (ROOT/p).rglob('*') if x.is_file() and x.name!='manifest.json')
    actual.add('docs/assets/production/'+aid+'.md')
    mismatches=[]
    for e in entries:
        f=ROOT/e['path'];b=f.read_bytes() if f.exists() else b''
        if not f.exists() or len(b)!=e['bytes'] or hashlib.sha256(b).hexdigest()!=e['sha256']:mismatches.append(e['path'])
    manifest_reports.append(dict(asset=aid,producer_manifest_supplied=row['producer_manifest_supplied'],manifest=row['manifest'],declared_count=len(declared),actual_count=len(actual),hash_byte_mismatches=mismatches,uncovered_candidate_paths=sorted(actual-declared),declared_missing_paths=sorted(declared-actual),readback_manifest_hash_matches=hashlib.sha256(mp.read_bytes()).hexdigest()==row['manifest_sha256'],readback_count_matches=len(declared)==row['count'],manifest_metadata={k:v for k,v in manifest.items() if k not in ['files','artifacts'] and not isinstance(v,dict)} if isinstance(manifest,dict) else {}))
    for path in sorted((ROOT/'art/models/environment'/aid).glob('*.glb')):
        data=path.read_bytes();magic,version,length=struct.unpack_from('<III',data);assert magic==0x46546c67 and version==2 and length==len(data)
        at=12;chunks={}
        while at<len(data):n,t=struct.unpack_from('<II',data,at);chunks[t]=data[at+8:at+8+n];at+=8+n
        doc=json.loads(chunks[0x4e4f534a]);binary=chunks[0x004e4942]
        def accessor(index):
            a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']];comp={5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'}[a['componentType']];num={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];fmt='<'+comp*num;size=struct.calcsize(fmt);start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size)
            return [struct.unpack_from(fmt,binary,start+i*stride) for i in range(a['count'])]
        def sub(a,b):return tuple(x-y for x,y in zip(a,b))
        def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
        points=[];meshes=[]
        for mesh in doc['meshes']:
            prims=[]
            for p in mesh['primitives']:
                assert p.get('mode',4)==4
                pos=accessor(p['attributes']['POSITION']);norm=accessor(p['attributes']['NORMAL']);inds=[i[0] for i in accessor(p['indices'])] if 'indices' in p else list(range(len(pos)));points+=pos
                deg=0;inward=0;min_alignment=1;volume=0
                for i in range(0,len(inds),3):
                    ids=inds[i:i+3];a,b,c=[pos[j] for j in ids];n=cross(sub(b,a),sub(c,a));mag=math.sqrt(sum(x*x for x in n));deg+=mag<1e-10
                    for j in ids:
                        align=sum(n[k]*norm[j][k] for k in range(3))/mag if mag else 0;min_alignment=min(min_alignment,align);inward+=align< -1e-6
                    volume+=sum(a[k]*cross(b,c)[k] for k in range(3))/6
                uv=accessor(p['attributes']['TEXCOORD_0']) if 'TEXCOORD_0' in p['attributes'] else []
                mat=doc['materials'][p['material']]['name']
                uv_error=None
                if aid=='city_sign_supports_01' and mat=='sign_face':
                    uv_error=max(max(abs(u-(.610-v[0])/1.22),abs(w-(.410-v[1])/.82)) for v,(u,w) in zip(pos,uv))
                prims.append(dict(material=mat,vertices=len(pos),triangles=len(inds)//3,degenerate_triangles=deg,nonfinite_positions=sum(not math.isfinite(x) for v in pos for x in v),bad_normals=sum(not all(math.isfinite(x) for x in n) or abs(math.sqrt(sum(x*x for x in n))-1)>1e-5 for n in norm),normal_winding_negative_corners=inward,min_normal_face_dot=min_alignment,signed_volume=volume,attributes=list(p['attributes']),uv_count=len(uv),sign_face_uv_max_error=uv_error))
            meshes.append(dict(name=mesh.get('name'),primitives=prims))
        glb_reports.append(dict(path=str(path.relative_to(ROOT)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),bounds_raw_godot=[[min(v[i] for v in points) for i in range(3)],[max(v[i] for v in points) for i in range(3)]],nodes=doc['nodes'],meshes=meshes,materials=doc['materials'],unexpected_features={k:doc[k] for k in ['cameras','images','textures','animations','skins'] if k in doc},extensions_used=doc.get('extensionsUsed',[]),generator=doc['asset'].get('generator')))
(OUT/'independent-manifest-check.json').write_text(json.dumps(manifest_reports,indent=2)+'\n')
(OUT/'independent-glb-check.json').write_text(json.dumps(glb_reports,indent=2)+'\n')
print('MANIFESTS',json.dumps(manifest_reports,indent=2))
print('GLBS',len(glb_reports),'TRIANGLES',[(x['path'],sum(p['triangles'] for m in x['meshes'] for p in m['primitives'])) for x in glb_reports])
