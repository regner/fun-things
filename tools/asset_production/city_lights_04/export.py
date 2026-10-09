"""Validate and export only the declared source collection; accepts a scratch output folder."""
import bpy,bmesh,io_scene_gltf2,json,math,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'docs/assets/production/city_lights_04-evidence'
MEMBERS=['CityLights04','mounting_backplate','mounting_gasket','mount_fastener_lower','mount_fastener_upper','curved_cast_arm','lower_shield','broad_recessed_diffuser','canopy_seal','broad_oval_canopy']
SETTINGS=dict(export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_texcoords=False,export_normals=True,export_tangents=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=False,export_animations=False,export_skins=False,export_morph=False)
def perform(output,report_path):
    assert bpy.app.version[:3]==(5,2,2)
    assert io_scene_gltf2.bl_info['version']==(5,2,40)
    col=bpy.data.collections['export_city_lights_04'];assert sorted(o.name for o in col.all_objects)==sorted(MEMBERS)
    root=bpy.data.objects['CityLights04'];assert root.parent is None
    report={'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'exporter':io_scene_gltf2.bl_info['version'],'collection':col.name,'root':root.name,'members':MEMBERS,'settings':SETTINGS,'objects':[]}
    bpy.context.view_layer.update();coords=[]
    for obj in col.objects:
        assert all(abs(v)<1e-7 for v in obj.location) and all(abs(v)<1e-7 for v in obj.rotation_euler)
        assert all(abs(v-1)<1e-7 for v in obj.scale) and len(obj.modifiers)==0
        if obj.type=='EMPTY':continue
        assert obj.type=='MESH' and obj.parent==root
        mesh=obj.data;bm=bmesh.new();bm.from_mesh(mesh)
        assert all(e.is_manifold for e in bm.edges),obj.name
        assert bm.calc_volume(signed=True)>0,obj.name
        assert all(p.area>1e-10 for p in mesh.polygons),obj.name
        assert all(math.isfinite(v) for vert in mesh.vertices for v in vert.co),obj.name
        assert all(math.isfinite(v) for p in mesh.polygons for v in p.normal),obj.name
        mesh.calc_loop_triangles()
        assert all((mesh.vertices[t.vertices[1]].co-mesh.vertices[t.vertices[0]].co).cross(mesh.vertices[t.vertices[2]].co-mesh.vertices[t.vertices[0]].co).length>1e-10 for t in mesh.loop_triangles),obj.name
        coords.extend(obj.matrix_world@v.co for v in mesh.vertices)
        report['objects'].append({'name':obj.name,'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'volume_m3':bm.calc_volume(signed=True),'slot_0':mesh.materials[0].name,'nonmanifold_edges':0});bm.free()
    low=[min(v[i] for v in coords) for i in range(3)];high=[max(v[i] for v in coords) for i in range(3)]
    assert all(abs(a-b)<.001 for a,b in zip(low,[-.32,0,-.23])),low
    assert all(abs(a-b)<.001 for a,b in zip(high,[.32,.71,.305])),high
    report['bounds_blender']=[low,high];report['triangles']=sum(o['triangles'] for o in report['objects'])
    bpy.ops.object.select_all(action='DESELECT')
    for o in col.objects:o.select_set(True)
    output.mkdir(parents=True,exist_ok=True);report['outputs']=[]
    lens=bpy.data.objects['broad_recessed_diffuser'];original=lens.data.materials[0]
    for variant in ['warm','cool']:
        lens.data.materials[0]=bpy.data.materials['city_lights_04_lens_'+variant]
        path=output/('city_lights_04_'+variant+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),**SETTINGS)
        report['outputs'].append({'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    lens.data.materials[0]=original
    report_path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    output=Path(args[0]) if args else ROOT/'art/models/environment/city_lights_04'
    perform(output,E/'reexport_source_checks.json');print('CITY_LIGHTS_04_COMPLETE',flush=True)
