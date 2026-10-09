"""Decode actual binary glTF independently of production tools and Blender importer."""
import hashlib
import json
import math
from pathlib import Path
import struct

OUT=Path(__file__).resolve().parent
FROZEN=Path('/tmp/batch03-final/frozen')
TOL=1e-5

def sub(a,b):return [x-y for x,y in zip(a,b)]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def length(a):return math.sqrt(dot(a,a))

def decode(path):
    raw=path.read_bytes()
    magic,version,size=struct.unpack_from('<III',raw)
    assert magic==0x46546c67 and version==2 and size==len(raw)
    offset=12;chunks={}
    while offset<size:
        n,t=struct.unpack_from('<II',raw,offset);offset+=8
        chunks[t]=raw[offset:offset+n];offset+=n
    doc=json.loads(chunks[0x4e4f534a]);binary=chunks[0x004e4942]
    def acc(i):
        a=doc['accessors'][i];b=doc['bufferViews'][a['bufferView']]
        assert not a.get('sparse') and not a.get('normalized')
        fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']]
        k={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        stride=b.get('byteStride',struct.calcsize('<'+fmt*k))
        start=b.get('byteOffset',0)+a.get('byteOffset',0)
        return [struct.unpack_from('<'+fmt*k,binary,start+j*stride) for j in range(a['count'])]
    return raw,doc,acc

expect={
 'city_shop_fittings_02':([-1.6,-.4,-.14],[1.6,.4,0],1656,7,5),
 'city_shop_fittings_03_single':([-.77,0,-.11],[.77,2.48,.52],2312,4,4),
 'city_shop_fittings_03_double':([-1.17,0,-.11],[1.17,2.48,.52],2312,4,4),
 'city_shop_fittings_05':([-1.6,0,-.22],[1.6,2,.18],1368,8,5),
 'city_shop_fittings_06_single':([-.512,.03,.352],[.512,2.232,.475],1512,3,3),
 'city_shop_fittings_06_double':([-.912,.03,.352],[.912,2.232,.475],3024,6,3),
 'city_shop_fittings_07':([-2.4,0,-.15],[2.4,1.6,.16],1760,11,5),
 'city_shop_fittings_08':([-.1,-.58,-.88],[.1,.58,0],3624,16,6),
 'city_small_shop_shells_01':([-3.2,0,-7.12],[3.2,5.05,7.22],4516,30,5)}
results=[]
for path in sorted((FROZEN/'art/models/environment').glob('*/*.glb')):
    name=path.stem
    if name not in expect:continue
    raw,doc,acc=decode(path)
    issues=[];points=[];mesh_reports=[];uv_reports=[]
    root_indices=doc['scenes'][doc.get('scene',0)]['nodes']
    nodes=doc['nodes'];root=nodes[root_indices[0]]
    if len(root_indices)!=1 or root['name']!=name or 'mesh' in root:issues.append('root membership')
    node_names={n['name'] for n in nodes}
    source_id=name.rsplit('_',1)[0] if name.endswith(('_single','_double')) else name
    source=json.loads((OUT/(source_id+'.source.json')).read_text())
    variant=next(v for v in source['variants'] if v['name']==name)
    if node_names!=set(variant['members']):issues.append('source/export member set')
    for node in nodes:
        if any(abs(x)>TOL for x in node.get('translation',[0,0,0])) and 'mesh' in node:issues.append(node['name']+': mesh translation')
        if node.get('scale',[1,1,1])!=[1,1,1] or node.get('rotation',[0,0,0,1])!=[0,0,0,1] or 'matrix' in node:issues.append(node['name']+': corrective transform')
    if any(doc.get(k) for k in ('animations','skins','images','textures','cameras','extensionsUsed','extensionsRequired')):issues.append('unexpected dependency/rig/studio/extension')
    for material in doc.get('materials',[]):
        if material.get('alphaMode','OPAQUE')!='OPAQUE' or material.get('doubleSided',False):issues.append(material['name']+': material scope')
    for node in nodes:
        if 'mesh' not in node:continue
        mesh=doc['meshes'][node['mesh']]
        mreport=dict(name=node['name'],primitives=[])
        for pi,prim in enumerate(mesh['primitives']):
            assert prim.get('mode',4)==4
            pos=acc(prim['attributes']['POSITION']);normal=acc(prim['attributes']['NORMAL']);ix=[x[0] for x in acc(prim['indices'])]
            points.extend(pos)
            material=doc['materials'][prim['material']]['name']
            bad_normals=[i for i,n in enumerate(normal) if not all(math.isfinite(v) for v in n) or abs(length(n)-1)>1e-4]
            bad_pos=[i for i,p in enumerate(pos) if not all(math.isfinite(v) for v in p)]
            degenerate=[];bad_corner=[];bad_average=[];all_dots=[];average_dots=[]
            for ti in range(0,len(ix),3):
                tri=ix[ti:ti+3];a,b,c=[pos[i] for i in tri]
                n=cross(sub(b,a),sub(c,a));area=length(n)/2
                if area<1e-10:degenerate.append(ti//3);continue
                n=[v/(2*area) for v in n]
                dots=[dot(n,normal[i]) for i in tri];all_dots.extend(dots)
                avg=sum(dots)/3;average_dots.append(avg)
                if min(dots)<-TOL:bad_corner.append(dict(triangle=ti//3,positions=[pos[i] for i in tri],normals=[normal[i] for i in tri],corner_dots=dots,average_dot=avg,area_m2=area))
                if avg<=0:bad_average.append(ti//3)
            pr=dict(material=material,vertices=len(pos),triangles=len(ix)//3,
                    attributes=list(prim['attributes']),invalid_normals=bad_normals,nonfinite_positions=bad_pos,
                    degenerate_triangles=degenerate,inward_average_normals=bad_average,
                    inward_corner_normals=bad_corner,minimum_corner_dot=min(all_dots),minimum_average_dot=min(average_dots))
            mreport['primitives'].append(pr)
            if bad_pos or bad_normals or degenerate or bad_average:issues.append(node['name']+': raw positions/normals/winding')
            if material in ('fascia_artwork_face','blade_artwork_positive_x','blade_artwork_negative_x'):
                uv=acc(prim['attributes']['TEXCOORD_0'])
                errors=[]
                for i,(p,t) in enumerate(zip(pos,uv)):
                    x,y,z=p
                    if material=='fascia_artwork_face': expected=(.5-x/3,.5-y/.6);axis=(0,0,-1);plane=z+.128
                    elif material=='blade_artwork_positive_x':expected=((-z-.25)/.58,.5-y/1.06);axis=(1,0,0);plane=x-.067
                    else:expected=((.83+z)/.58,.5-y/1.06);axis=(-1,0,0);plane=x+.067
                    if max(abs(t[j]-expected[j]) for j in (0,1))>2e-6 or abs(plane)>2e-6 or dot(normal[i],axis)<.999: errors.append(i)
                determinant=[]
                for j in range(0,len(ix),3):
                    a,b,c=[uv[i] for i in ix[j:j+3]]
                    determinant.append((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))
                uv_reports.append(dict(mesh=node['name'],material=material,vertices=len(pos),triangles=len(ix)//3,errors=errors,uv_bounds=[[min(t[i] for t in uv) for i in (0,1)],[max(t[i] for t in uv) for i in (0,1)]],determinant_min=min(determinant),determinant_max=max(determinant)))
                if errors:issues.append(node['name']+': artwork UV/plane/orientation')
        mesh_reports.append(mreport)
    lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
    elo,ehi,triangles,meshes,materials=expect[name]
    actual_triangles=sum(p['triangles'] for m in mesh_reports for p in m['primitives'])
    if any(abs(x-y)>1e-6 for x,y in zip(lo+hi,elo+ehi)):issues.append('brief bounds')
    if (actual_triangles,len(mesh_reports),len(doc['materials']))!=(triangles,meshes,materials):issues.append('brief count')
    results.append(dict(name=name,path=str(path),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
        bounds_godot=[lo,hi],triangles=actual_triangles,nodes=nodes,materials=doc['materials'],
        mesh_reports=mesh_reports,artwork_interfaces=uv_reports,issues=issues))
(OUT/'glb-audit.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps([dict(name=r['name'],bounds=r['bounds_godot'],triangles=r['triangles'],issues=r['issues'],
 inward_corner_triangles=sum(len(p['inward_corner_normals']) for m in r['mesh_reports'] for p in m['primitives']),artwork_interfaces=r['artwork_interfaces']) for r in results],indent=2))
assert not any(r['issues'] for r in results)
