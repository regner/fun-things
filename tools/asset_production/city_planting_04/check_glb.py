"""Check exported GLB payload bounds, materials, normals and triangle count."""
import json, struct, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
reports=[]
source=json.loads((ROOT/'docs/assets/production/city_planting_04-evidence/source_export_checks.json').read_text())
for path in sorted((ROOT/'art/models/environment/city_planting_04').glob('*.glb')):
    blob=path.read_bytes()
    assert struct.unpack_from('<III',blob)==(0x46546c67,2,len(blob))
    size,kind=struct.unpack_from('<II',blob,12); assert kind==0x4e4f534a
    doc=json.loads(blob[20:20+size]); binary=blob[28+size:]
    def accessor(i):
        a=doc['accessors'][i]; v=doc['bufferViews'][a['bufferView']]
        fmt={5126:'f',5123:'H',5125:'I'}[a['componentType']]
        n={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']]; step=struct.calcsize('<'+fmt*n)
        offset=v.get('byteOffset',0)+a.get('byteOffset',0)
        return [struct.unpack_from('<'+fmt*n,binary,offset+k*v.get('byteStride',step)) for k in range(a['count'])]
    assert len(doc['meshes'])==6
    positions=[]; triangles=0
    for node in doc['nodes']:
        assert 'camera' not in node and 'skin' not in node
        assert 'matrix' not in node and 'rotation' not in node
        assert node.get('scale',[1,1,1])==[1,1,1]
        if 'mesh' not in node:continue
        shift=node.get('translation',[0,0,0])
        for p in doc['meshes'][node['mesh']]['primitives']:
            assert p.get('mode',4)==4
            pos=accessor(p['attributes']['POSITION'])
            normals=accessor(p['attributes']['NORMAL'])
            assert all(abs(sum(x*x for x in n)-1)<.002 for n in normals)
            ids=[x[0] for x in accessor(p['indices'])]
            assert len(ids)%3==0
            for k in range(0,len(ids),3):
                a,b,c=[pos[ids[k+j]] for j in range(3)]
                u=[b[j]-a[j] for j in range(3)]; v=[c[j]-a[j] for j in range(3)]
                cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
                assert sum(x*x for x in cross)>1e-20
            triangles+=len(ids)//3
            positions.extend(tuple(v[j]+shift[j] for j in range(3)) for v in pos)
    low=[min(v[i] for v in positions) for i in range(3)]; high=[max(v[i] for v in positions) for i in range(3)]
    variant=path.stem.split('_')[-1]
    expected=next(r for r in source if r['variant']==variant)
    assert all(abs(a-b)<.00001 for a,b in zip(low,expected['godot_bounds'][0]))
    assert all(abs(a-b)<.00001 for a,b in zip(high,expected['godot_bounds'][1]))
    assert abs(low[1])<1e-7 and 3.2<high[1]<3.61
    assert high[0]-low[0] < (2.3 if variant=='compact' else 3.1)
    assert high[2]-low[2] < (2.2 if variant=='compact' else 2.8)
    assert triangles==expected['triangles']
    assert len(doc['nodes'])==7
    assert {n['name'] for n in doc['nodes']}=={'city_planting_04_'+variant,variant+'_sculpted_trunk',*(variant+'_crown_'+x for x in ['leader','west','east','front','back'])}
    assert all(n.get('translation',[0,0,0])==[0,0,0] for n in doc['nodes'])
    assert all(m.get('alphaMode','OPAQUE')=='OPAQUE' and not m.get('doubleSided',False) for m in doc['materials'])
    assert all(m['pbrMetallicRoughness'].get('metallicFactor',1)==0 for m in doc['materials'])
    assert all(math.isfinite(x) for v in positions for x in v)
    assert not doc.get('animations') and not doc.get('images') and not doc.get('cameras')
    assert 'KHR_lights_punctual' not in doc.get('extensionsUsed',[])
    assert len(doc['materials'])==3
    reports.append({'file':str(path.relative_to(ROOT)),'godot_axis_aabb':[low,high],'triangles':triangles,'mesh_count':len(doc['meshes']),'materials':doc['materials'],'checks':'PASS: exact dimensions, unit transforms, finite unit normals, nondegenerate triangles, studio exclusion, no lights/animations/textures'})
(ROOT/'docs/assets/production/city_planting_04-evidence/glb_checks.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(reports,indent=2))
