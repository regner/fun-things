"""Independently decode glTF accessors without Blender or author/export imports."""
import json,struct,math,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'docs/assets/production/city_shop_fittings_02-evidence'
p=ROOT/'art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb'
b=p.read_bytes();magic,version,length=struct.unpack_from('<4sII',b);assert (magic,version,length)==(b'glTF',2,len(b))
n,kind=struct.unpack_from('<II',b,12);assert kind==0x4e4f534a
j=json.loads(b[20:20+n]);offset=20+n;bn,bt=struct.unpack_from('<II',b,offset);assert bt==0x004e4942
binary=b[offset+8:offset+8+bn]
def accessor(index):
    a=j['accessors'][index];v=j['bufferViews'][a['bufferView']]
    assert 'sparse' not in a and not a.get('normalized',False)
    fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']]
    count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    size=struct.calcsize('<'+fmt*count);stride=v.get('byteStride',size)
    start=v.get('byteOffset',0)+a.get('byteOffset',0)
    return [struct.unpack_from('<'+fmt*count,binary,start+i*stride) for i in range(a['count'])]
def sub(a,b):return [a[i]-b[i] for i in range(3)]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
expected={'city_shop_fittings_02','formed_fascia_frame','continuous_face_trim','folded_back_tray','artwork_reveal','fascia_artwork_carrier','wall_mount_rail_lower','wall_mount_rail_upper'}
assert {n['name'] for n in j['nodes']}==expected
assert len(j['nodes'])==8 and len(j['meshes'])==7
assert {m['name'] for m in j['materials']}=={'fascia_artwork_face','fascia_mount_metal','fascia_slate_petrol','fascia_recess','fascia_warm_trim'}
assert not any(k in j for k in ['animations','skins','cameras','images','textures'])
assert 'KHR_lights_punctual' not in j.get('extensions',{})
assert len(j['scenes'])==1
root_index=next(i for i,n in enumerate(j['nodes']) if n['name']=='city_shop_fittings_02')
assert j['scenes'][0]['nodes']==[root_index]
assert set(j['nodes'][root_index]['children'])==set(range(8))-{root_index}
coords=[];report=[];face_checks=0
for node in j['nodes']:
    assert not any(k in node for k in ['matrix','translation','rotation','scale'])
    if 'mesh' not in node:continue
    mesh=j['meshes'][node['mesh']];triangles=0;edges={};weld={};signed_volume=0
    for prim in mesh['primitives']:
        assert prim.get('mode',4)==4
        pos=accessor(prim['attributes']['POSITION']);norm=accessor(prim['attributes']['NORMAL']);idx=[v[0] for v in accessor(prim['indices'])]
        assert len(pos)==len(norm) and len(idx)%3==0
        assert all(math.isfinite(v) for p in pos for v in p)
        assert all(abs(dot(n,n)-1)<2e-5 for n in norm)
        coords.extend(pos);triangles+=len(idx)//3
        keys=[tuple(round(c,7) for c in v) for v in pos]
        for start in range(0,len(idx),3):
            ids=idx[start:start+3];a,bp,c=[pos[k] for k in ids]
            geometric=cross(sub(bp,a),sub(c,a));assert dot(geometric,geometric)>1e-20
            assert dot(geometric,[sum(norm[k][axis] for k in ids) for axis in range(3)])>0,(node['name'],ids)
            signed_volume+=dot(a,cross(bp,c))/6
            for u,v in [(ids[0],ids[1]),(ids[1],ids[2]),(ids[2],ids[0])]:
                ka,kb=keys[u],keys[v];key=tuple(sorted([ka,kb]));direction=1 if ka<kb else -1
                edges.setdefault(key,[]).append(direction)
        mat=j['materials'][prim['material']]['name']
        if mat=='fascia_artwork_face':
            assert node['name']=='fascia_artwork_carrier'
            uv=accessor(prim['attributes']['TEXCOORD_0'])
            assert len(pos)==len(uv)
            for point,normal,tex in zip(pos,norm,uv):
                assert abs(point[2]+.128)<1e-6 and normal[2]<-.99999
                # Explicit front-view landmark mapping, independent of Blender checker.
                assert -1e-6<=tex[0]<=1.000001 and -1e-6<=tex[1]<=1.000001
                assert abs(tex[0]-(.5-point[0]/3.0))<1e-6
                assert abs(tex[1]-(.5-point[1]/.6))<1e-6
                face_checks+=1
    assert all(len(v)==2 and sum(v)==0 for v in edges.values()),node['name']
    assert signed_volume>0,node['name']
    report.append(dict(name=node['name'],triangles=triangles,welded_edges=len(edges),nonmanifold_edges=0,degenerate_triangles=0,outward_winding=True,signed_volume_m3=signed_volume))
low=[min(p[i] for p in coords) for i in range(3)];high=[max(p[i] for p in coords) for i in range(3)]
assert all(abs(a-b)<1e-6 for a,b in zip(low,[-1.6,-.4,-.14]))
assert all(abs(a-b)<1e-6 for a,b in zip(high,[1.6,.4,0]))
assert face_checks==28
reexport=E/'reexport_city_shop_fittings_02.glb';assert reexport.read_bytes()==p.read_bytes()
result=dict(status='PASS',file=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),decoded_bounds_godot=[low,high],total_triangles=sum(o['triangles'] for o in report),objects=report,materials=j['materials'],uv_front_samples=face_checks,source_reexport_byte_identical=True,studio_excluded=True,no_external_dependencies=True)
(E/'glb_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
