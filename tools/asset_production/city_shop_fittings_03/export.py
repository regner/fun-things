"""Audit both saved variant collections and export each independently."""
import bpy,bmesh,json,math,sys,hashlib
from pathlib import Path
import io_scene_gltf2
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_shop_fittings_03-evidence'
assert bpy.app.version[:3]==(5,2,2) and bpy.app.build_hash.decode()=='d13f752e3b9c'
assert io_scene_gltf2.bl_info['version']==(5,2,40)
bpy.context.view_layer.update()
reports=[]
for variant,w in [('single',1.04),('double',1.84)]:
    col=bpy.data.collections['variant_'+variant]
    expected={'city_shop_fittings_03_'+variant} | {variant+'_'+n for n in ['recessed_reveal','rounded_face_casing','rear_stop','sloped_threshold']}
    assert {o.name for o in col.objects}==expected
    report={'blender':bpy.app.version_string,'build':bpy.app.build_hash.decode(),'exporter':io_scene_gltf2.bl_info['version'],'variant':variant,'objects':[]}
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
    assert all(abs(a-b)<1e-5 for a,b in zip(lo,[-(w+.5)/2,-.520,0]))
    assert all(abs(a-b)<1e-5 for a,b in zip(hi,[(w+.5)/2,.110,2.48]))
    ref=bpy.data.objects['authoring_1m_reference']; assert all(abs(v-1)<1e-6 for v in ref.dimensions)
    assert ref not in list(col.objects)
    report.update(blender_bounds=[lo,hi],triangles=sum(o['triangles'] for o in report['objects']),authoring_reference_dimensions_m=list(ref.dimensions))
    bpy.ops.object.select_all(action='DESELECT')
    for o in col.objects: o.select_set(True)
    settings=dict(export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=False,export_normals=True,export_tangents=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=False,export_animations=False)
    outdir=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else R/'art/models/environment/city_shop_fittings_03'
    outdir.mkdir(exist_ok=True)
    out=outdir/('city_shop_fittings_03_'+variant+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(out),**settings)
    report.update(export_settings=settings,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),bytes=out.stat().st_size)
    reports.append(report)
(E/('reexport_checks.json' if '--' in sys.argv else 'source_export_checks.json')).write_text(json.dumps(reports,indent=2)+'\n')
print('SOURCE_EXPORT_CHECKS_PASS',json.dumps(reports))
