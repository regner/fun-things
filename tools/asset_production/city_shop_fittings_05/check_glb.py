"""Check exported GLB payload bounds, materials, normals and triangle count."""
import json, struct, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
reports=[]
for path in sorted((ROOT/'art/models/environment/city_shop_fittings_05').glob('*.glb')):
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
    assert len(doc['meshes'])==8
    assert len(doc['nodes'])==9
    assert {n['name'] for n in doc['nodes']}=={'city_shop_fittings_05','formed_perimeter','ivory_perimeter_inlay','left_glazing_gasket','right_glazing_gasket','left_opaque_glazing','right_opaque_glazing','centre_mullion','sloped_sill'}
    positions=[]; triangles=0
    for node in doc['nodes']:
        assert 'camera' not in node and 'skin' not in node
        assert 'matrix' not in node and 'rotation' not in node
        assert node.get('scale',[1,1,1])==[1,1,1]
        if 'mesh' not in node:continue
        shift=node.get('translation',[0,0,0]); assert all(abs(x)<1e-7 for x in shift)
        for p in doc['meshes'][node['mesh']]['primitives']:
            assert p.get('mode',4)==4
            pos=accessor(p['attributes']['POSITION'])
            normals=accessor(p['attributes']['NORMAL'])
            assert all(abs(sum(x*x for x in n)-1)<.002 for n in normals)
            ids=[x[0] for x in accessor(p['indices'])]
            assert len(ids)%3==0
            assert all(math.isfinite(c) for v in pos for c in v)
            assert p['material'] in range(5)
            for k in range(0,len(ids),3):
                a,b,c=[pos[ids[k+j]] for j in range(3)]
                u=[b[j]-a[j] for j in range(3)]; v=[c[j]-a[j] for j in range(3)]
                cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
                assert sum(x*x for x in cross)>1e-20
                mean=[sum(normals[ids[k+q]][j] for q in range(3)) for j in range(3)]
                assert sum(cross[j]*mean[j] for j in range(3))>0, (node["name"],k,"winding/normal disagreement")
            triangles+=len(ids)//3
            positions.extend(tuple(v[j]+shift[j] for j in range(3)) for v in pos)
    low=[min(v[i] for v in positions) for i in range(3)]; high=[max(v[i] for v in positions) for i in range(3)]
    assert all(abs(a-b)<.001 for a,b in zip(low,[-1.6,0,-.22])),low
    assert all(abs(a-b)<.001 for a,b in zip(high,[1.6,2.0,.18])),high
    assert triangles==json.loads((ROOT/'docs/assets/production/city_shop_fittings_05-evidence/source_export_checks.json').read_text())['triangles']
    assert not doc.get('animations') and not doc.get('images') and not doc.get('cameras')
    assert 'KHR_lights_punctual' not in doc.get('extensionsUsed',[])
    assert len(doc['materials'])==5
    assert {m['name'] for m in doc['materials']}=={'window_slate_petrol','window_warm_ivory','window_dark_gasket','window_opaque_tint','window_satin_sill'}
    assert not doc.get('textures') and not doc.get('skins')
    assert not any('KHR_materials_transmission' in m.get('extensions',{}) for m in doc['materials'])
    assert all(not m.get('doubleSided',False) and m.get('alphaMode','OPAQUE')=='OPAQUE' for m in doc['materials'])
    assert all(not any(m.get('emissiveFactor',[0,0,0])) for m in doc['materials'])
    reports.append({'file':str(path.relative_to(ROOT)),'godot_axis_aabb':[low,high],'triangles':triangles,'mesh_count':len(doc['meshes']),'materials':doc['materials'],'checks':'PASS: exact dimensions, unit transforms, finite unit normals, nondegenerate triangles, studio exclusion, no lights/animations/textures'})
(ROOT/'docs/assets/production/city_shop_fittings_05-evidence/glb_checks.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(reports,indent=2))
