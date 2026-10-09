"""Validate saved source islands and explicitly export each declared root."""
import bpy, bmesh, json, math, sys, hashlib
from pathlib import Path
import io_scene_gltf2
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_planting_05-evidence'
assert bpy.app.version[:3]==(5,2,2) and bpy.app.build_hash.decode()=='d13f752e3b9c'
assert io_scene_gltf2.bl_info['version']==(5,2,40)
assert bpy.context.scene.unit_settings.system=='METRIC'
assert bpy.context.scene.unit_settings.scale_length==1
scratch='--' in sys.argv
outdir=Path(sys.argv[sys.argv.index('--')+1]) if scratch else R/'art/models/environment/city_planting_05'
outdir.mkdir(parents=True,exist_ok=True)
fixture=bpy.data.objects['reference_one_metre_vertical']
assert abs(fixture.dimensions.z-1)<1e-7
assert fixture not in set(bpy.data.collections['export_city_planting_05'].all_objects)
reports=[]
for variant,dims,count in [('short_tuft',(.56,.42,.26),9),('spreading_clump',(1,.62,.20),15)]:
    col=bpy.data.collections['variant_'+variant]; col.hide_render=False
    root=col.objects['city_planting_05_'+variant]; assert root.parent is None
    assert len(col.objects)==2
    coords=[]; rows=[]
    bpy.context.view_layer.update()
    for o in col.objects:
        assert all(abs(o.matrix_world[i][j]-(i==j))<1e-7 for i in range(4) for j in range(4))
        if o.type!='MESH': assert o==root; continue
        assert o.parent==root and not o.modifiers
        o.data.calc_loop_triangles()
        bm=bmesh.new(); bm.from_mesh(o.data)
        bad=sum(not e.is_manifold or not e.is_contiguous for e in bm.edges)
        assert bad==0,(variant,bad)
        # Check each disconnected blade separately; positive total volume alone
        # could hide an inverted island. This also detects accidental duplicates.
        unseen=set(bm.verts); volumes=[]
        while unseen:
            seed=unseen.pop(); component={seed}; stack=[seed]
            while stack:
                v=stack.pop()
                for edge in v.link_edges:
                    n=edge.other_vert(v)
                    if n in unseen: unseen.remove(n); component.add(n); stack.append(n)
            faces={f for v in component for f in v.link_faces}
            vol=0
            for f in faces:
                a=f.verts[0].co
                for k in range(1,len(f.verts)-1):
                    vol+=a.dot(f.verts[k].co.cross(f.verts[k+1].co))/6
            assert vol>1e-9,(variant,vol)
            volumes.append(vol)
        assert len(volumes)==count
        min_area=min((o.data.vertices[t.vertices[1]].co-o.data.vertices[t.vertices[0]].co).cross(o.data.vertices[t.vertices[2]].co-o.data.vertices[t.vertices[0]].co).length/2 for t in o.data.loop_triangles)
        assert min_area>1e-10,(variant,min_area)
        assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
        assert all(abs(v.normal.length-1)<.002 for v in o.data.vertices)
        coords.extend(v.co.copy() for v in o.data.vertices)
        rows.append({'name':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'closed_blade_islands':len(volumes),'bad_edges':bad,'island_signed_volumes_m3':volumes,'minimum_triangle_area_m2':min_area,'materials':[m.name for m in o.data.materials]})
        bm.free()
    lo=[min(v[i] for v in coords) for i in range(3)]; hi=[max(v[i] for v in coords) for i in range(3)]
    expected_lo=[-dims[0]/2,-dims[1]/2,0]; expected_hi=[dims[0]/2,dims[1]/2,dims[2]]
    assert all(abs(a-b)<1e-6 for a,b in zip(lo,expected_lo))
    assert all(abs(a-b)<1e-6 for a,b in zip(hi,expected_hi))
    bpy.ops.object.select_all(action='DESELECT')
    for o in col.objects:o.select_set(True)
    settings=dict(export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=False,export_normals=True,export_tangents=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=False,export_animations=False)
    out=outdir/('city_planting_05_'+variant+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(out),**settings)
    reports.append({'variant':variant,'blender':bpy.app.version_string,'build':bpy.app.build_hash.decode(),'exporter':io_scene_gltf2.bl_info['version'],'source_collection':'export_city_planting_05/variant_'+variant,'root':root.name,'objects':rows,'blender_bounds':[lo,hi],'godot_bounds':[[lo[0],lo[2],-hi[1]],[hi[0],hi[2],-lo[1]]],'triangles':sum(r['triangles'] for r in rows),'one_metre_fixture_height_m':fixture.dimensions.z,'reference_excluded':True,'export_settings':settings,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
(E/('reexport_checks.json' if scratch else 'source_export_checks.json')).write_text(json.dumps(reports,indent=2)+'\n')
print('SOURCE_EXPORT_CHECKS_PASS',json.dumps(reports))
