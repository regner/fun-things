"""Decode binary buffers independently and compare frozen GLBs with fresh source exports."""
import hashlib
import json
import math
from pathlib import Path
import struct

OUT = Path(__file__).resolve().parent
SNAPSHOT = Path('/tmp/batch02-review-5e94cc0/snapshot')
IDS = ['city_planting_03','city_planting_04','city_planting_05',
       'city_roof_details_01','city_roof_details_02','city_shop_fittings_01']


def subtract(a,b):
    return [x-y for x,y in zip(a,b)]


def cross(a,b):
    return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def decode(path):
    data = path.read_bytes()
    magic,version,size = struct.unpack_from('<III',data)
    assert (magic,version,size)==(0x46546C67,2,len(data))
    offset=12
    chunks={}
    while offset<len(data):
        length,kind=struct.unpack_from('<II',data,offset)
        assert kind not in chunks
        chunks[kind]=data[offset+8:offset+8+length]
        offset+=8+length
    assert offset==len(data)
    model=json.loads(chunks[0x4E4F534A])
    binary=chunks[0x004E4942]
    assert not any(b.get('uri') for b in model['buffers'])

    def accessor(n):
        a=model['accessors'][n]
        assert not a.get('sparse')
        v=model['bufferViews'][a['bufferView']]
        assert v.get('buffer',0)==0
        fmt,sz={5126:('f',4),5125:('I',4),5123:('H',2),5121:('B',1)}[a['componentType']]
        width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        start=v.get('byteOffset',0)+a.get('byteOffset',0)
        stride=v.get('byteStride',sz*width)
        assert a['count']==0 or start+(a['count']-1)*stride+sz*width<=v.get('byteOffset',0)+v['byteLength']<=len(binary)
        values=[struct.unpack_from('<'+fmt*width,binary,start+i*stride) for i in range(a['count'])]
        return [x[0] for x in values] if width==1 else values

    return data,model,accessor


def clip_below(triangle,height):
    """Clip a triangle at a horizontal interface; extrema lie on clipped vertices."""
    clipped=[]
    for a,b in zip(triangle,triangle[1:]+triangle[:1]):
        if a[1]<=height:
            clipped.append(a)
        if (a[1]-height)*(b[1]-height)<0:
            t=(height-a[1])/(b[1]-a[1])
            clipped.append(tuple(x+(y-x)*t for x,y in zip(a,b)))
    return clipped


def bounds(points):
    return [[min(p[i] for p in points) for i in range(3)],
            [max(p[i] for p in points) for i in range(3)]]


reports=[]
for asset in IDS:
    source=json.loads((OUT/(asset+'-source.json')).read_text())
    for variant in source['variants']:
        root=variant['root']
        committed=SNAPSHOT/f'art/models/environment/{asset}/{root}.glb'
        data,model,accessor=decode(committed)
        fresh=OUT/(root+'-fresh.glb')
        assert data==fresh.read_bytes(), root
        nodes=model['nodes']
        expected={root}|{r['name'] for r in variant['objects']}
        assert {n['name'] for n in nodes}==expected
        root_index=next(i for i,n in enumerate(nodes) if n['name']==root)
        assert model['scenes'][model.get('scene',0)]['nodes']==[root_index]
        assert set(nodes[root_index]['children'])==set(range(len(nodes)))-{root_index}
        for n in nodes:
            assert n.get('translation',[0,0,0])==[0,0,0]
            assert n.get('rotation',[0,0,0,1])==[0,0,0,1]
            assert n.get('scale',[1,1,1])==[1,1,1]
            assert not n.get('matrix') and not n.get('skin')
        assert not any(model.get(k) for k in ('animations','skins','cameras','images','textures','extensionsRequired','extensionsUsed'))
        points=[]
        triangles=[]
        surfaces=[]
        source_mats={m['name']:m for m in variant['materials']}
        for material in model['materials']:
            sm=source_mats[material['name']]
            pbr=material['pbrMetallicRoughness']
            for key,expected_value in [('baseColorFactor',sm['base_color']),
                                       ('metallicFactor',sm['metallic']),
                                       ('roughnessFactor',sm['roughness'])]:
                actual=pbr.get(key,1)
                assert max(abs(a-b) for a,b in zip(actual,expected_value))<1e-6 if isinstance(actual,list) else abs(actual-expected_value)<1e-6
            assert material.get('alphaMode','OPAQUE')=='OPAQUE'
            assert material.get('doubleSided',False)==(not sm['backface_culling'])
        for node in nodes:
            if 'mesh' not in node:
                continue
            for primitive in model['meshes'][node['mesh']]['primitives']:
                assert primitive.get('mode',4)==4
                assert set(primitive['attributes'])=={'POSITION','NORMAL'}
                positions=accessor(primitive['attributes']['POSITION'])
                normals=accessor(primitive['attributes']['NORMAL'])
                indices=accessor(primitive['indices'])
                assert len(indices)%3==0 and len(positions)==len(normals)
                assert all(math.isfinite(x) for a in positions+normals for x in a)
                assert all(abs(math.sqrt(dot(n,n))-1)<.002 for n in normals)
                assert all(0<=n<len(positions) for n in indices)
                points.extend(positions)
                areas=[]
                normal_agreement=[]
                for i in range(0,len(indices),3):
                    ids=indices[i:i+3]
                    tri=[positions[j] for j in ids]
                    triangles.append((node['name'],tri))
                    face=cross(subtract(tri[1],tri[0]),subtract(tri[2],tri[0]))
                    twice_area=math.sqrt(dot(face,face))
                    assert twice_area>2e-12
                    areas.append(twice_area/2)
                    avg=[sum(normals[j][k] for j in ids)/3 for k in range(3)]
                    normal_agreement.append(dot(face,avg)/twice_area)
                surfaces.append({'node':node['name'],'triangles':len(areas),
                    'minimum_triangle_area_m2':min(areas),
                    'minimum_face_normal_dot':min(normal_agreement),
                    'opposed_shading_normal_faces':sum(d< -1e-5 for d in normal_agreement),
                    'material':model['materials'][primitive['material']]['name']})
                assert not surfaces[-1]['opposed_shading_normal_faces'], surfaces[-1]
        actual_bounds=bounds(points)
        assert max(abs(a-b) for aa,bb in zip(actual_bounds,variant['godot_bounds']) for a,b in zip(aa,bb))<1e-5
        assert sum(s['triangles'] for s in surfaces)==sum(o['triangles'] for o in variant['objects'])
        interfaces={}
        if asset in ('city_planting_03','city_planting_04'):
            heights=[.20,.48] if asset=='city_planting_03' else [.48]
            for height in heights:
                below=[p for name,tri in triangles for p in clip_below(tri,height)]
                interfaces[str(height)]={'bounds':bounds(below),'max_radius_m':max(math.hypot(p[0],p[2]) for p in below)}
            if asset=='city_planting_03':
                lo,hi=interfaces['0.2']['bounds']
                # Trough's immutable reserved rectangle is 1.90 x 0.40m.
                assert max(abs(lo[0]-.48),abs(hi[0]+.48))<=.95
                assert max(abs(lo[2]),abs(hi[2]))<=.20
                assert max(math.hypot(p[0],p[2]) for p in points)<.60
            else:
                assert interfaces['0.48']['max_radius_m']<.60
        if asset.startswith('city_roof_details'):
            contact=[p for name,tri in triangles if name=='flashing_and_curb' for p in tri if abs(p[1])<1e-7]
            interfaces['contact_plane']={'godot_y':0,'contact_vertices':len(contact),'bounds':bounds(contact)}
            assert abs(actual_bounds[0][1])<1e-6
        if asset=='city_shop_fittings_01':
            wall=[p for name,tri in triangles if name=='wall_mount_rail' for p in tri if abs(p[2])<1e-7]
            interfaces['wall_contact']={'godot_z':0,'contact_vertices':len(wall),'bounds':bounds(wall)}
            assert abs(actual_bounds[1][2])<1e-6
        reports.append({'asset':asset,'root':root,'committed_path':str(committed.relative_to(SNAPSHOT)),
            'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'fresh_byte_identical':True,
            'nodes':[n['name'] for n in nodes],'godot_bounds':actual_bounds,
            'triangles':sum(s['triangles'] for s in surfaces),'surfaces':surfaces,
            'materials':model['materials'],'interfaces':interfaces})
(OUT/'binary-audit.json').write_text(json.dumps(reports,indent=2)+'\n')
print('INDEPENDENT_BINARY_AUDIT_COMPLETE',len(reports),'outputs')
