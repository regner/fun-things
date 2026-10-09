"""Independently decode game GLB payload and compare with saved-source measurements."""
import json,struct,math
from pathlib import Path
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_small_shop_shells_01-evidence'
p=R/'art/models/environment/city_small_shop_shells_01/city_small_shop_shells_01.glb'
b=p.read_bytes(); assert struct.unpack_from('<III',b)==(0x46546c67,2,len(b))
n,t=struct.unpack_from('<II',b,12); assert t==0x4e4f534a
d=json.loads(b[20:20+n]); raw=b[28+n:]; source=json.loads((E/'source_export_checks.json').read_text())
def accessor(i):
    a=d['accessors'][i]; v=d['bufferViews'][a['bufferView']]
    fmt={5126:'f',5123:'H',5125:'I'}[a['componentType']]*{'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']]
    step=struct.calcsize('<'+fmt); offset=v.get('byteOffset',0)+a.get('byteOffset',0)
    return [struct.unpack_from('<'+fmt,raw,offset+k*v.get('byteStride',step)) for k in range(a['count'])]
expected={o['name'] for o in source['objects']}|set(source['markers'])
assert {o['name'] for o in d['nodes']}==expected
assert not any(d.get(k) for k in ['animations','images','cameras','skins','textures'])
assert 'KHR_lights_punctual' not in d.get('extensionsUsed',[])
assert len(d['materials'])==5 and len(d['meshes'])==30
assert all(not m.get('doubleSided',False) and m.get('alphaMode','OPAQUE')=='OPAQUE' for m in d['materials'])
positions=[]; count=0; markers={}; material_names={m['name'] for m in d['materials']}
assert material_names=={name for o in source['objects'] for name in o['material_slots']}
for node in d['nodes']:
    assert 'matrix' not in node and 'rotation' not in node and node.get('scale',[1,1,1])==[1,1,1]
    shift=node.get('translation',[0,0,0]); name=node['name']
    if name in source['markers']:
        x,y,z=source['markers'][name]; expect=[x,z,-y]
        assert all(abs(a-b)<1e-6 for a,b in zip(shift,expect)),(name,shift,expect)
        markers[name]=shift; assert 'mesh' not in node; continue
    assert shift==[0,0,0]; points=[]; triangles=0
    for prim in d['meshes'][node['mesh']]['primitives']:
        assert prim.get('mode',4)==4
        pos=accessor(prim['attributes']['POSITION']); normals=accessor(prim['attributes']['NORMAL']); ids=[v[0] for v in accessor(prim['indices'])]
        assert len(ids)%3==0 and all(math.isfinite(c) for v in pos+normals for c in v)
        assert all(abs(sum(c*c for c in v)-1)<.002 for v in normals)
        for k in range(0,len(ids),3):
            a,b,c=[pos[ids[k+j]] for j in range(3)]; u=[b[j]-a[j] for j in range(3)]; v=[c[j]-a[j] for j in range(3)]
            cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
            assert sum(x*x for x in cross)>1e-20,(name,k)
            mean=[sum(normals[ids[k+q]][j] for q in range(3)) for j in range(3)]
            assert sum(cross[j]*mean[j] for j in range(3))>0,(name,k,'normal/winding')
        points.extend(pos); triangles+=len(ids)//3
    rec=next(o for o in source['objects'] if o['name']==name)
    assert triangles==rec['triangles']; count+=triangles; positions.extend(points)
    lo,hi=rec['bounds']; converted=[[lo[0],lo[2],-hi[1]],[hi[0],hi[2],-lo[1]]]
    measured=[[min(v[i] for v in points) for i in range(3)],[max(v[i] for v in points) for i in range(3)]]
    assert all(abs(a-b)<1e-5 for aa,bb in zip(converted,measured) for a,b in zip(aa,bb)),name
assert count==source['triangles']
report={'triangles':count,'meshes':30,'materials':d['materials'],'markers_godot_axes':markers,'bounds_godot':[[min(v[i] for v in positions) for i in range(3)],[max(v[i] for v in positions) for i in range(3)]],'checks':'PASS exact members, transforms, all per-mesh source/export bounds and counts, finite unit normals, winding agreement, no degenerate triangles, opaque materials, studio exclusion'}
(E/'glb_checks.json').write_text(json.dumps(report,indent=2)+'\n'); print(report['checks'],count)
