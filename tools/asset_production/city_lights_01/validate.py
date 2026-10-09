"""Measure saved Blender geometry and actual GLB accessors; retain complete evidence."""
import bpy, bmesh, json, math, struct, hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'docs/assets/production/city_lights_01-evidence'
S=ROOT/'art/source/models/environment/city_lights_01/city_lights_01.blend'
bpy.ops.wm.open_mainfile(filepath=str(S))
c=bpy.data.collections['export_city_lights_01']
assert set(o.name for o in c.objects)=={'CityLights01','CityLights01_Mesh'}
o=bpy.data.objects['CityLights01_Mesh']; mesh=o.data
assert all(abs(v-1)<1e-6 for v in o.scale)
assert all(abs(v)<1e-6 for v in o.rotation_euler)
assert all(abs(v)<1e-6 for v in o.location)
assert bpy.context.scene.unit_settings.scale_length==1
assert not o.modifiers
assert all(abs(n.vector.length-1)<1e-4 for n in mesh.corner_normals)
mesh.calc_loop_triangles()
bm=bmesh.new(); bm.from_mesh(mesh)
nonmanifold=sum(not e.is_manifold for e in bm.edges)
assert nonmanifold==0, nonmanifold
assert all(math.isfinite(v) for vert in mesh.vertices for v in vert.co)
small_faces=[(p.index,p.area) for p in mesh.polygons if p.area<=1e-10]
print("SMALL_FACES",small_faces,flush=True)
assert not small_faces, small_faces
coords=[o.matrix_world@v.co for v in mesh.vertices]
lo=[min(v[i] for v in coords) for i in range(3)]
hi=[max(v[i] for v in coords) for i in range(3)]
assert abs(lo[2])<.001
assert abs(hi[2]-6.2)<.001
assert abs(hi[0]-.36)<.001 and abs(hi[1]-1.40)<.001
report={'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),
 'source_bounds_blender':{'min':lo,'max':hi},
 'expected_godot_bounds':{'min':[lo[0],lo[2],-hi[1]],'max':[hi[0],hi[2],-lo[1]]},
 'pivot':[0,0,0],'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),
 'small_faces':small_faces,'nonmanifold_edges':nonmanifold,'mesh_objects':1,'source_material_slots':[m.name for m in mesh.materials],
 'exports':{}}
for variant in ('warm','cool'):
    p=ROOT/f'art/models/environment/city_lights_01/city_lights_01_{variant}.glb'
    raw=p.read_bytes(); magic,version,length=struct.unpack_from('<4sII',raw)
    assert magic==b'glTF' and version==2 and length==len(raw)
    n,kind=struct.unpack_from('<II',raw,12); doc=json.loads(raw[20:20+n])
    assert not doc.get('animations') and not doc.get('cameras') and not doc.get('skins')
    assert not doc.get('images') and not doc.get('textures')
    assert len(doc['nodes'])==2 and len(doc['meshes'])==1
    assert all(node.get('scale',[1,1,1])==[1,1,1] for node in doc['nodes'])
    assert all('rotation' not in node for node in doc['nodes'])
    bounds=[doc['accessors'][pr['attributes']['POSITION']] for pr in doc['meshes'][0]['primitives']]
    gmin=[min(a['min'][i] for a in bounds) for i in range(3)]
    gmax=[max(a['max'][i] for a in bounds) for i in range(3)]
    for a,b in zip(gmin+gmax,report['expected_godot_bounds']['min']+report['expected_godot_bounds']['max']): assert abs(a-b)<1e-5
    assert {m['name'] for m in doc['materials']}=={'pole_petrol','fixture_rim','service_recess','lens_'+variant}
    report['exports'][variant]={'file':str(p.relative_to(ROOT)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
        'actual_godot_axis_bounds':{'min':gmin,'max':gmax},'triangles':sum(doc['accessors'][pr['indices']]['count']//3 for pr in doc['meshes'][0]['primitives']),
        'surfaces':len(doc['meshes'][0]['primitives']),'materials':doc['materials'],'nodes':doc['nodes']}
report['status']='PASS: source topology/transforms/dimensions and actual GLB structure/axis bounds; engine acceptance pending'
(E/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
