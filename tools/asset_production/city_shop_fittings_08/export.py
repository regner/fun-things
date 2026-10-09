"""Saved-source topology audit and exact pinned selected-collection GLB export."""
import bpy,bmesh,json,math,sys,hashlib
from pathlib import Path
import io_scene_gltf2
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_shop_fittings_08-evidence'
assert bpy.app.version[:3]==(5,2,2) and bpy.app.build_hash.decode()=='d13f752e3b9c'
assert io_scene_gltf2.bl_info['version']==(5,2,40)
col=bpy.data.collections['export_city_shop_fittings_08']; bpy.context.view_layer.update()
expected={'city_shop_fittings_08','formed_blade_shell','wall_backplate'}
for side in ['positive_x','negative_x']:
    expected.update({'continuous_trim_'+side,'dark_reveal_'+side,'face_'+side})
for level in ['lower','upper']:
    expected.update({'cantilever_arm_'+level,'tapered_gusset_'+level})
    for side in ['left','right']:expected.add('captive_hex_'+side+'_'+level)
assert {o.name for o in col.objects}==expected
report={'blender':bpy.app.version_string,'build':bpy.app.build_hash.decode(),'exporter':io_scene_gltf2.bl_info['version'],'objects':[]}
coords=[]
for o in col.objects:
    assert all(abs(v)<1e-7 for v in o.location) and all(abs(v)<1e-7 for v in o.rotation_euler) and all(abs(v-1)<1e-7 for v in o.scale)
    if o.type!='MESH': continue
    assert not o.modifiers
    coords.extend(o.matrix_world@v.co for v in o.data.vertices)
    bm=bmesh.new(); bm.from_mesh(o.data); o.data.calc_loop_triangles()
    bad=sum(not e.is_manifold or not e.is_contiguous for e in bm.edges)
    assert bad==0,(o.name,bad)
    assert bm.calc_volume(signed=True)>0
    assert all(p.area>1e-10 for p in o.data.polygons)
    assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
    # Check each disconnected manufactured solid, not just total mesh volume.
    remaining=set(bm.verts); components=[]
    while remaining:
        seed=remaining.pop(); group={seed}; stack=[seed]
        while stack:
            for e in stack.pop().link_edges:
                for v in e.verts:
                    if v in remaining: remaining.remove(v); group.add(v); stack.append(v)
        faces={f for v in group for f in v.link_faces}
        volume=sum(f.calc_area()*f.normal.dot(f.calc_center_median())/3 for f in faces)
        assert volume>0,(o.name,volume); components.append(volume)
    report['objects'].append({'name':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'nonmanifold_or_inconsistent_edges':bad,'component_signed_volumes_m3':components,'material_slots':[m.name for m in o.data.materials]}); bm.free()
lo=[min(v[i] for v in coords) for i in range(3)]; hi=[max(v[i] for v in coords) for i in range(3)]
assert all(abs(a-b)<1e-5 for a,b in zip(lo,[-.1,0,-.58])); assert all(abs(a-b)<1e-5 for a,b in zip(hi,[.1,.88,.58]))
ref=bpy.data.objects['authoring_1m_reference']; assert all(abs(v-1)<1e-6 for v in ref.dimensions)
assert ref not in list(col.objects)
report.update(blender_bounds=[lo,hi],triangles=sum(o['triangles'] for o in report['objects']),authoring_reference_dimensions_m=list(ref.dimensions))
# Separate face contracts: full field, upright from both outward-facing sides.
uv_reports=[]
for sign,label in [(1,'positive_x'),(-1,'negative_x')]:
    o=bpy.data.objects['face_'+label]
    assert [m.name for m in o.data.materials]==['blade_artwork_'+label,'blade_mount_metal']
    assert o.data.uv_layers.active.name=='UV0'
    outward=[p for p in o.data.polygons if p.material_index==0]
    assert len(outward)==1 and outward[0].normal.x*sign>.999
    samples=[]
    for li in outward[0].loop_indices:
        p=o.data.vertices[o.data.loops[li].vertex_index].co
        uv=o.data.uv_layers.active.data[li].uv
        assert abs(p.x-sign*.067)<1e-6
        assert abs(uv.x-(.5+sign*(p.y-.54)/.58))<1e-6
        assert abs(uv.y-(.5+p.z/1.06))<1e-6
        samples.append([list(p),list(uv)])
    assert len(samples)==36
    for j in range(2):
        assert abs(min(v[1][j] for v in samples))<1e-6
        assert abs(max(v[1][j] for v in samples)-1)<1e-6
    uv_reports.append({'side':label,'normal':[sign,0,0],'outward_plane_x':sign*.067,'samples':samples})
report['artwork_interfaces']=uv_reports
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects: o.select_set(True)
settings=dict(export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=False,export_animations=False)
out=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else R/'art/models/environment/city_shop_fittings_08/city_shop_fittings_08.glb'
bpy.ops.export_scene.gltf(filepath=str(out),**settings)
report.update(export_settings=settings,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),bytes=out.stat().st_size)
(E/('reexport_checks.json' if '--' in sys.argv else 'source_export_checks.json')).write_text(json.dumps(report,indent=2)+'\n')
print('SOURCE_EXPORT_CHECKS_PASS',json.dumps(report))
