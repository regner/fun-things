"""Audit saved editable source and export each explicit tree root in isolation.
Adapted read-only from city_planting_03 export method.
"""
import bpy,bmesh,json,math,sys,hashlib
from pathlib import Path
import io_scene_gltf2
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_planting_04-evidence'
assert bpy.app.version[:3]==(5,2,2) and bpy.app.build_hash.decode()=='d13f752e3b9c'
assert io_scene_gltf2.bl_info['version']==(5,2,40)
assert bpy.context.scene.unit_settings.scale_length==1
scratch='--' in sys.argv
outdir=Path(sys.argv[sys.argv.index('--')+1]) if scratch else R/'art/models/environment/city_planting_04'
outdir.mkdir(parents=True,exist_ok=True)
reports=[]
for variant in ['compact','broad']:
    col=bpy.data.collections['export_city_planting_04_'+variant]; col.hide_viewport=False; col.hide_render=False
    bpy.context.view_layer.update(); coords=[]; under=[]; crowns=[]; rows=[]
    assert len(col.objects)==7
    for o in col.objects:
        assert all(abs(v)<1e-7 for v in o.location) and all(abs(v)<1e-7 for v in o.rotation_euler) and all(abs(v-1)<1e-7 for v in o.scale)
        assert all(abs(o.matrix_world[i][j]-(1 if i==j else 0))<1e-7 for i in range(4) for j in range(4))
        if o.type!='MESH':assert o.name=='city_planting_04_'+variant; continue
        assert not o.modifiers and not o.data.has_custom_normals
        coords.extend(v.co.copy() for v in o.data.vertices)
        if '_crown_' in o.name:crowns.extend(v.co.copy() for v in o.data.vertices)
        bm=bmesh.new(); bm.from_mesh(o.data); o.data.calc_loop_triangles()
        bad=sum(not e.is_manifold or not e.is_contiguous for e in bm.edges)
        volume=bm.calc_volume(signed=True)
        assert bad==0,(o.name,bad)
        assert volume>0 and all(p.area>1e-10 for p in o.data.polygons)
        assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
        assert all(abs(v.normal.length-1)<.002 for v in o.data.vertices)
        # Clip every triangle edge to planter rim plane; radius bound is convex.
        under.extend(v.co.copy() for v in o.data.vertices if v.co.z<=.48)
        for tri in o.data.loop_triangles:
            for a,b in zip(tri.vertices,(*tri.vertices[1:],tri.vertices[0])):
                va=o.data.vertices[a].co; vb=o.data.vertices[b].co
                if (va.z-.48)*(vb.z-.48)<0:under.append(va.lerp(vb,(.48-va.z)/(vb.z-va.z)))
        rows.append({'name':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'bad_edges':bad,'signed_volume_m3':volume,'material_slots':[m.name for m in o.data.materials]}); bm.free()
    low=[min(v[i] for v in coords) for i in range(3)]; high=[max(v[i] for v in coords) for i in range(3)]
    crown_low=min(v.z for v in crowns); radius=max(math.hypot(v.x,v.y) for v in under)
    assert abs(low[2])<1e-7 and high[2]<=3.61
    assert crown_low>=2.1 and radius<.23
    assert max(math.hypot(v.x,v.y) for v in crowns)<(1.2 if variant=='compact' else 1.6)
    bpy.ops.object.select_all(action='DESELECT')
    for o in col.objects:o.select_set(True)
    settings=dict(export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=False,export_normals=True,export_tangents=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=False,export_animations=False)
    out=outdir/('city_planting_04_'+variant+'.glb'); bpy.ops.export_scene.gltf(filepath=str(out),**settings)
    reports.append({'variant':variant,'blender':bpy.app.version_string,'build':bpy.app.build_hash.decode(),'exporter':io_scene_gltf2.bl_info['version'],'objects':rows,'blender_bounds':[low,high],'godot_bounds':[[low[0],low[2],-high[1]],[high[0],high[2],-low[1]]],'triangles':sum(r['triangles'] for r in rows),'crown_min_height_m':crown_low,'below_surround_rim_max_radius_m':radius,'surround_radial_gap_min_m':1.2385/2-radius,'export_settings':settings,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
(E/('reexport_checks.json' if scratch else 'source_export_checks.json')).write_text(json.dumps(reports,indent=2)+'\n')
print('SOURCE_EXPORT_CHECKS_PASS',json.dumps(reports))
