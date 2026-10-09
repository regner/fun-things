"""Audit and explicitly export the saved source collection; optional scratch output."""
import bpy,bmesh,json,math,sys,hashlib
from pathlib import Path
import io_scene_gltf2
ROOT=Path(__file__).resolve().parents[3]; E=ROOT/'docs/assets/production/city_planting_03-evidence'
assert bpy.app.version[:3]==(5,2,2)
assert bpy.app.build_hash.decode()=='d13f752e3b9c'
assert io_scene_gltf2.bl_info['version']==(5,2,40)
col=bpy.data.collections['export_city_planting_03']; bpy.context.view_layer.update()
report={'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'exporter':io_scene_gltf2.bl_info['version'],'objects':[]}
coords=[]
for o in col.objects:
    assert all(abs(v)<1e-7 for v in o.location) and all(abs(v)<1e-7 for v in o.rotation_euler) and all(abs(v-1)<1e-7 for v in o.scale)
    if o.type!='MESH': continue
    coords.extend(o.matrix_world@v.co for v in o.data.vertices)
    bm=bmesh.new(); bm.from_mesh(o.data); o.data.calc_loop_triangles()
    bad=sum(not e.is_manifold or not e.is_contiguous for e in bm.edges)
    assert bad==0,(o.name,bad)
    assert bm.calc_volume(signed=True)>0
    if o.name == 'three_recessed_stems':
        assert all(abs(v.co.x)<.35 and abs(v.co.y)<.09 for v in o.data.vertices)
    else:
        assert min(v.co.z for v in o.data.vertices) >= .03499
        assert all(abs(v.co.x)<.46 and abs(v.co.y)<.18 for v in o.data.vertices if v.co.z<=.20)
    assert all(p.area>1e-10 for p in o.data.polygons)
    assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
    report['objects'].append({'name':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'nonmanifold_or_inconsistent_edges':bad,'signed_volume_m3':bm.calc_volume(signed=True),'material_slots':[m.name for m in o.data.materials]}); bm.free()
lo=[min(v[i] for v in coords) for i in range(3)]; hi=[max(v[i] for v in coords) for i in range(3)]
assert -.60 < lo[0] < -.50 and .50 < hi[0] < .60
assert -.36 < lo[1] and hi[1] < .38
assert abs(lo[2])<1e-7 and abs(hi[2]-.67)<1e-5
assert all(math.hypot(v.x,v.y)<.60 for v in coords)
assert len(col.objects)==7
report['interface_checks']='PASS: below rectangular rim shrub inside .92 x .36m; full shrub inside radius .60m'
# Include edge intersections with the rim plane, not only vertices below it.
under=[]
for o in col.objects:
    if o.type!='MESH': continue
    under.extend(v.co.copy() for v in o.data.vertices if v.co.z<=.20)
    o.data.calc_loop_triangles()
    for tri in o.data.loop_triangles:
        for a,b in zip(tri.vertices,(*tri.vertices[1:],tri.vertices[0])):
            va=o.data.vertices[a].co; vb=o.data.vertices[b].co
            if (va.z-.20)*(vb.z-.20)<0:
                under.append(va.lerp(vb,(.20-va.z)/(vb.z-va.z)))
assert all(abs(v.x)<.46 and abs(v.y)<.18 for v in under)
report['below_rectangular_rim_bounds']=[[min(v[i] for v in under) for i in range(3)],[max(v[i] for v in under) for i in range(3)]]
report['blender_bounds']=[lo,hi]; report['triangles']=sum(o['triangles'] for o in report['objects'])
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects: o.select_set(True)
settings=dict(export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=False,export_normals=True,export_tangents=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=False,export_animations=False)
out=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else ROOT/'art/models/environment/city_planting_03/city_planting_03.glb'
bpy.ops.export_scene.gltf(filepath=str(out),**settings)
report['export_settings']=settings; report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest(); report['bytes']=out.stat().st_size
(E/('reexport_checks.json' if '--' in sys.argv else 'source_export_checks.json')).write_text(json.dumps(report,indent=2)+'\n')
print('SOURCE_EXPORT_CHECKS_PASS',json.dumps(report))
