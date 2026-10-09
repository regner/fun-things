"""Inspect actual saved calibration contents against unchanged source collections."""
import bpy,hashlib,json,re,struct
from pathlib import Path
from mathutils import Vector
import io_scene_gltf2
R=Path('/tmp/six-engine-review-c4067ff');O=Path(__file__).resolve().parent
assert bpy.app.version_string=='5.2.2 LTS' and bpy.app.build_hash.decode()=='d13f752e3b9c' and io_scene_gltf2.bl_info['version']==(5,2,40)
path=R/'docs/assets/production/batch_01-evidence/calibration/five-source-metre-comparison.blend';bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene
assert scene.unit_settings.system=='METRIC' and scene.unit_settings.scale_length==1
ids=['city_lights_01','city_lights_02','city_sign_supports_01','city_planting_01','city_planting_02']
def basename(name):return re.sub(r'\.\d{3}$','',name)
def signature(obj):
 row=dict(type=obj.type,matrix=[list(v) for v in obj.matrix_local],parent=basename(obj.parent.name) if obj.parent else None)
 if obj.type=='MESH':
  m=obj.data;row.update(vertices=[list(v.co) for v in m.vertices],faces=[list(p.vertices) for p in m.polygons],materials=[basename(x.name) for x in m.materials],face_slots=[p.material_index for p in m.polygons],normals=[list(n.vector) for n in m.corner_normals],uvs=[[list(x.uv) for x in u.data] for u in m.uv_layers])
 return hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest()
rows=[]
for index,aid in enumerate(ids):
 inst=next(o for o in bpy.data.objects if o.instance_type=='COLLECTION' and o.instance_collection and o.instance_collection.name=='export_'+aid);col=inst.instance_collection;fixture=bpy.data.objects[aid+'_reference_1m'];assert inst.instance_type=='COLLECTION' and col.name=='export_'+aid
 original={basename(o.name):signature(o) for o in col.all_objects}
 assert list(inst.scale)==[1,1,1] and all(abs(x)<1e-7 for x in inst.rotation_euler)
 assert all(abs(x-y)<1e-6 for x,y in zip(inst.location,[index*3-6,0,0]))
 assert all(abs(x-1)<1e-6 for x in fixture.dimensions)
 # Decode fixture vertices, rather than trusting its dimensions field alone.
 coords=[fixture.matrix_world@v.co for v in fixture.data.vertices];fmin=[min(v[i] for v in coords) for i in range(3)];fmax=[max(v[i] for v in coords) for i in range(3)];assert all(abs(y-x-1)<1e-6 for x,y in zip(fmin,fmax))
 pts=[o.matrix_world@v.co for o in col.all_objects if o.type=='MESH' for v in o.data.vertices];lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
 source=R/'art/source/models/environment'/aid/(aid+'.blend')
 with bpy.data.libraries.load(str(source),link=False) as (available,requested):requested.collections=['export_'+aid]
 source_col=requested.collections[0];now={basename(o.name):signature(o) for o in source_col.all_objects};assert original==now,aid
 rows.append(dict(asset=aid,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),saved_collection=col.name,source_member_signatures=original,matches_actual_source_members=True,instance_translation=list(inst.location),instance_rotation=list(inst.rotation_euler),instance_scale=list(inst.scale),fixture_world_bounds=[fmin,fmax],source_bounds_blender=[lo,hi],source_bounds_godot=[[lo[0],lo[2],-hi[1]],[hi[0],hi[2],-lo[1]]],export_member_count=len(original)))
result=dict(blender=bpy.app.version_string,build=bpy.app.build_hash.decode(),exporter=io_scene_gltf2.bl_info['version'],calibration_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),units=scene.unit_settings.system,unit_scale=scene.unit_settings.scale_length,camera_position=list(scene.camera.location),camera_rotation=list(scene.camera.rotation_euler),render_resolution=[scene.render.resolution_x,scene.render.resolution_y],assets=rows)
(O/'independent-calibration.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS actual saved five-source collection signatures, translation-only placements, one-metre vertex extents, source hashes/axes/bounds')
