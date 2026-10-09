"""Independently decode GLB buffers and compare saved-source reexports byte-for-byte."""
import json,struct,math,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'docs/assets/production/city_lights_04-evidence'
EXPECTED={'CityLights04','mounting_backplate','mounting_gasket','mount_fastener_lower','mount_fastener_upper','curved_cast_arm','lower_shield','broad_recessed_diffuser','canopy_seal','broad_oval_canopy'}
reports=[]
for path in sorted((ROOT/'art/models/environment/city_lights_04').glob('*.glb')):
    blob=path.read_bytes();assert struct.unpack_from('<III',blob)==(0x46546c67,2,len(blob))
    size,kind=struct.unpack_from('<II',blob,12);assert kind==0x4e4f534a
    doc=json.loads(blob[20:20+size]);bin_size,bin_kind=struct.unpack_from('<II',blob,20+size)
    assert bin_kind==0x004e4942;binary=blob[28+size:];assert len(binary)==bin_size
    def accessor(i):
        a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']]
        fmt={5126:'f',5123:'H',5125:'I'}[a['componentType']]
        count={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']];step=struct.calcsize('<'+fmt*count)
        offset=v.get('byteOffset',0)+a.get('byteOffset',0)
        return [struct.unpack_from('<'+fmt*count,binary,offset+k*v.get('byteStride',step)) for k in range(a['count'])]
    assert {n['name'] for n in doc['nodes']}==EXPECTED
    roots=doc['scenes'][doc.get('scene',0)]['nodes'];assert len(roots)==1
    assert doc['nodes'][roots[0]]['name']=='CityLights04'
    assert len(doc['nodes'][roots[0]]['children'])==9
    positions=[];triangles=0;primitives=0;minimum_cross=float('inf')
    for node in doc['nodes']:
        assert not any(k in node for k in ['camera','skin','matrix','rotation','translation','scale'])
        if 'mesh' not in node:continue
        for p in doc['meshes'][node['mesh']]['primitives']:
            primitives+=1;assert p.get('mode',4)==4
            pos=accessor(p['attributes']['POSITION']);normals=accessor(p['attributes']['NORMAL'])
            assert all(math.isfinite(x) for v in pos for x in v)
            assert all(all(math.isfinite(x) for x in n) and abs(sum(x*x for x in n)-1)<.002 for n in normals)
            ids=[x[0] for x in accessor(p['indices'])];assert len(ids)%3==0
            assert all(0<=i<len(pos) for i in ids)
            for k in range(0,len(ids),3):
                a,b,c=[pos[ids[k+j]] for j in range(3)]
                u=[b[j]-a[j] for j in range(3)];v=[c[j]-a[j] for j in range(3)]
                cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
                area=math.sqrt(sum(x*x for x in cross))/2;assert area>1e-10
                minimum_cross=min(minimum_cross,area)
            triangles+=len(ids)//3;positions.extend(pos)
    low=[min(v[i] for v in positions) for i in range(3)];high=[max(v[i] for v in positions) for i in range(3)]
    assert all(abs(a-b)<.001 for a,b in zip(low,[-.32,-.23,-.71])),low
    assert all(abs(a-b)<.001 for a,b in zip(high,[.32,.305,0])),high
    assert triangles==4388 and primitives==9
    assert len(doc['materials'])==3
    variant='cool' if 'cool' in path.name else 'warm'
    assert {m['name'] for m in doc['materials']}=={'city_lights_04_petrol_metal','city_lights_04_recess_dark','city_lights_04_lens_'+variant}
    assert not any(doc.get(k) for k in ['cameras','images','textures','animations','skins'])
    assert 'KHR_lights_punctual' not in doc.get('extensionsUsed',[])
    reports.append({'path':str(path.relative_to(ROOT)),'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'godot_axis_aabb':[low,high],'triangles':triangles,'meshes':len(doc['meshes']),'primitives':primitives,'minimum_triangle_area_m2':minimum_cross,'nodes':doc['nodes'],'materials':doc['materials'],'pass':True})
(E/'glb_checks.json').write_text(json.dumps(reports,indent=2)+'\n')
if len(sys.argv)>1:
    scratch=Path(sys.argv[1]);comparison=[]
    for report in reports:
        a=ROOT/report['path'];b=scratch/a.name;assert a.read_bytes()==b.read_bytes(),a
        comparison.append({'production':str(a.relative_to(ROOT)),'scratch':str(b),'sha256':report['sha256'],'byte_identical':True})
    (E/'reproducibility.json').write_text(json.dumps(comparison,indent=2)+'\n')
print(json.dumps(reports,indent=2));print('CITY_LIGHTS_04_COMPLETE')
