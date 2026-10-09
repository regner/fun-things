"""Audit the saved editable source, then export only declared game members."""
import bpy,bmesh,math,json,sys,hashlib
from pathlib import Path
import io_scene_gltf2
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_small_shop_shells_01-evidence'
assert bpy.app.version[:3]==(5,2,2) and bpy.app.build_hash.decode()=='d13f752e3b9c'
assert io_scene_gltf2.bl_info['version']==(5,2,40)
col=bpy.data.collections['export_city_small_shop_shells_01']; bpy.context.view_layer.update()
report={'pin':[bpy.app.version_string,bpy.app.build_hash.decode(),io_scene_gltf2.bl_info['version']],'objects':[],'markers':{}}
coords=[]
for o in col.objects:
    assert all(abs(v)<1e-7 for v in o.rotation_euler) and all(abs(v-1)<1e-7 for v in o.scale)
    if o.type=='EMPTY':
        report['markers'][o.name]=list(o.location); continue
    assert o.type=='MESH' and not o.modifiers
    assert all(abs(v)<1e-7 for v in o.location)
    bm=bmesh.new(); bm.from_mesh(o.data); o.data.calc_loop_triangles()
    assert all(e.is_manifold and e.is_contiguous for e in bm.edges),o.name
    assert all(p.area>1e-10 for p in o.data.polygons),o.name
    assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
    remaining=set(bm.verts); volumes=[]
    while remaining:
        seed=remaining.pop(); group={seed}; stack=[seed]
        while stack:
            for edge in stack.pop().link_edges:
                for v in edge.verts:
                    if v in remaining: remaining.remove(v); group.add(v); stack.append(v)
        fs={f for v in group for f in v.link_faces}
        volume=sum(f.calc_area()*f.normal.dot(f.calc_center_median())/3 for f in fs)
        assert volume>0,(o.name,volume); volumes.append(volume)
    bm.free(); vs=[o.matrix_world@v.co for v in o.data.vertices]; coords.extend(vs)
    report['objects'].append({'name':o.name,'vertices':len(vs),'triangles':len(o.data.loop_triangles),'bounds':[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],'component_volumes_m3':volumes,'material_slots':[m.name for m in o.data.materials]})
lo=[min(v[i] for v in coords) for i in range(3)]; hi=[max(v[i] for v in coords) for i in range(3)]
assert all(abs(a-b)<1e-5 for a,b in zip(lo,[-3.2,-7.22,0]))
assert all(abs(a-b)<1e-5 for a,b in zip(hi,[3.2,7.12,5.05]))
ref=bpy.data.objects['authoring_1m_reference']; assert all(abs(v-1)<1e-6 for v in ref.dimensions)
assert ref not in list(col.objects)
assert len(report['markers'])==9 and len(report['objects'])==30,(len(report['markers']),len(report['objects']))
# Rear cap and side caps butt without a coplanar overlap rectangle.
rear=next(o for o in report['objects'] if o['name']=='rear_coping')
joints=[]
for name in ['party_coping_left','party_coping_right']:
    side=next(o for o in report['objects'] if o['name']==name)
    gap=side['bounds'][0][1]-rear['bounds'][1][1]
    assert abs(gap)<1e-5 and gap>=-1e-6
    joints.append({'side':name,'rear_max_y':rear['bounds'][1][1],'side_min_y':side['bounds'][0][1],'gap_m':gap})
report['rear_coping_butt_joints']=joints
report.update(bounds_blender=[lo,hi],triangles=sum(x['triangles'] for x in report['objects']),reference_dimensions_m=list(ref.dimensions),reference_ratios=[6.4,14,5.05],checks='PASS: finite, positive closed consistently wound solids, nondegenerate faces, applied transforms, excluded studio/reference, measured bounds')
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects: o.select_set(True)
settings=dict(export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=False,export_normals=True,export_tangents=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=False,export_animations=False)
out=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else R/'art/models/environment/city_small_shop_shells_01/city_small_shop_shells_01.glb'
bpy.ops.export_scene.gltf(filepath=str(out),**settings)
report.update(export_settings=settings,bytes=out.stat().st_size,sha256=hashlib.sha256(out.read_bytes()).hexdigest())
(E/('reexport_checks.json' if '--' in sys.argv else 'source_export_checks.json')).write_text(json.dumps(report,indent=2)+'\n')
print('SOURCE_EXPORT_PASS',report['triangles'],report['bounds_blender'])
