"""Validate the saved Blender source and export only its declared member set."""
import bpy, bmesh, io_scene_gltf2, json, math, sys, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
MEMBERS=['CitySignSupports01','rounded_frame','rear_shell','face_gasket','artwork_carrier','mount_rail_lower','mount_rail_upper','wall_pad_lower_left','wall_pad_lower_right','wall_pad_upper_left','wall_pad_upper_right','release_tab_left','release_tab_right']
SETTINGS=dict(export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_texcoords=True,export_normals=True,export_tangents=False,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=False,export_animations=False,export_skins=False,export_morph=False)

def perform(output, report_path):
    assert bpy.app.version[:3]==(5,2,2)
    assert bpy.app.build_hash.decode()=='d13f752e3b9c'
    assert io_scene_gltf2.bl_info['version']==(5,2,40)
    assert bpy.context.scene.unit_settings.system=='METRIC' and bpy.context.scene.unit_settings.scale_length==1
    col=bpy.data.collections['export_city_sign_supports_01']
    assert sorted(o.name for o in col.all_objects)==sorted(MEMBERS)
    root=bpy.data.objects['CitySignSupports01']; assert root.parent is None
    report=dict(blender=bpy.app.version_string,build_hash=bpy.app.build_hash.decode(),gltf_exporter=io_scene_gltf2.bl_info['version'],members=MEMBERS,export_settings=SETTINGS,objects=[])
    coords=[]
    for obj in col.all_objects:
        assert all(abs(v)<1e-7 for v in obj.location) and all(abs(v)<1e-7 for v in obj.rotation_euler),obj.name
        assert all(abs(v-1)<1e-7 for v in obj.scale) and len(obj.modifiers)==0,obj.name
        if obj.type=='EMPTY': continue
        assert obj.type=='MESH' and obj.parent==root
        mesh=obj.data; bm=bmesh.new(); bm.from_mesh(mesh)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges),obj.name
        assert bm.calc_volume(signed=True)>0,obj.name
        assert not any(len(v.link_faces)==0 for v in bm.verts)
        assert all(p.area>1e-10 for p in mesh.polygons),obj.name
        assert all(math.isfinite(c) for v in mesh.vertices for c in v.co)
        assert all(abs(n.vector.length-1)<1e-5 for n in mesh.corner_normals)
        mesh.calc_loop_triangles()
        for tri in mesh.loop_triangles:
            a,b,c=[mesh.vertices[i].co for i in tri.vertices]
            assert (b-a).cross(c-a).length>1e-10,obj.name
        coords.extend(obj.matrix_world@v.co for v in mesh.vertices)
        report['objects'].append(dict(name=obj.name,vertices=len(mesh.vertices),triangles=len(mesh.loop_triangles),volume_m3=bm.calc_volume(signed=True),material_slots=[m.name for m in mesh.materials],nonmanifold_edges=0,inconsistent_winding_edges=0,degenerate_triangles=0,applied_transforms=True))
        bm.free()
    low=[min(v[i] for v in coords) for i in range(3)]; high=[max(v[i] for v in coords) for i in range(3)]
    assert all(abs(a-b)<1e-6 for a,b in zip(low,[-.70,0,-.50])),low
    assert all(abs(a-b)<1e-6 for a,b in zip(high,[.70,.10,.50])),high
    carrier=bpy.data.objects['artwork_carrier'].data
    front=[p for p in carrier.polygons if p.material_index==0]
    assert len(front)==1 and front[0].normal.y>.999
    for li in front[0].loop_indices:
        v=carrier.vertices[carrier.loops[li].vertex_index].co; u,t=carrier.uv_layers[0].data[li].uv
        assert abs(u-(.610-v.x)/1.22)<1e-6 and abs(t-(v.z+.410)/.82)<1e-6
    report.update(bounds_blender=[low,high],triangles=sum(o['triangles'] for o in report['objects']),artwork_front_y=.088,artwork_uv_orientation='U increases toward Blender -X; V toward +Z; glTF V storage flips',artwork_material='sign_face')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in col.all_objects: obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(output),**SETTINGS)
    report.update(output_bytes=output.stat().st_size,output_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    report_path.write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report),flush=True)
if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    perform(Path(args[0]),Path(args[1])); print('CITY_SIGN_SUPPORTS_01_COMPLETE',flush=True)
