import bpy,json,re,hashlib
from pathlib import Path
R=Path('/tmp/six-engine-review-c4067ff');O=Path(__file__).resolve().parent
ids=['city_lights_01','city_lights_02','city_sign_supports_01','city_planting_01','city_planting_02']
def name(n):return re.sub(r'(\.\d{3})+$','',n)
def payload(o):
 d=dict(type=o.type,matrix=[list(x) for x in o.matrix_local],world=[list(x) for x in o.matrix_world],parent=name(o.parent.name) if o.parent else None)
 if o.type=='MESH':
  m=o.data;d.update(vertices=[list(v.co) for v in m.vertices],faces=[list(p.vertices) for p in m.polygons],materials=[name(m.name) for m in m.materials],slots=[p.material_index for p in m.polygons],normals=[list(n.vector) for n in m.corner_normals],uvs=[[list(x.uv) for x in u.data] for u in m.uv_layers])
 return d
bpy.ops.wm.open_mainfile(filepath=str(R/'docs/assets/production/batch_01-evidence/calibration/five-source-metre-comparison.blend'))
bpy.context.view_layer.update()
cal={};fixtures=[]
for i,aid in enumerate(ids):
 inst=next(o for o in bpy.data.objects if o.instance_type=='COLLECTION' and o.instance_collection and o.instance_collection.name=='export_'+aid)
 col=inst.instance_collection;cal[aid]={name(o.name):payload(o) for o in col.all_objects}
 f=bpy.data.objects[aid+'_reference_1m'];coords=[f.matrix_world@v.co for v in f.data.vertices]
 points=[o.matrix_world@v.co for o in col.all_objects if o.type=='MESH' for v in o.data.vertices]
 fixtures.append(dict(asset=aid,instance=inst.name,translation=list(inst.location),rotation=list(inst.rotation_euler),scale=list(inst.scale),fixture_vertex_extents=[max(v[a] for v in coords)-min(v[a] for v in coords) for a in range(3)],source_bounds=[[min(v[a] for v in points) for a in range(3)],[max(v[a] for v in points) for a in range(3)]],members=list(cal[aid])))
rows=[]
def diff(a,b,path=''):
 if type(a)!=type(b):return [dict(path=path,a=a,b=b)]
 if isinstance(a,dict):return sum([diff(a.get(k),b.get(k),path+'/'+k) for k in set(a)|set(b)],[])
 if isinstance(a,list):
  if len(a)!=len(b):return [dict(path=path,lengths=[len(a),len(b)])]
  return sum([diff(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))],[])
 if a==b:return []
 if isinstance(a,(int,float)) and abs(a-b)<1e-6:return []
 return [dict(path=path,a=a,b=b)]
for aid in ids:
 src=R/'art/source/models/environment'/aid/(aid+'.blend');bpy.ops.wm.open_mainfile(filepath=str(src));bpy.context.view_layer.update()
 original={name(o.name):payload(o) for o in bpy.data.collections['export_'+aid].all_objects};delta=diff(cal[aid],original)
 rows.append(dict(asset=aid,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),differing_fields=delta,saved_source_member_count=len(cal[aid]),original_member_count=len(original)))
out=dict(method='separate actual source mainfile reads, updated evaluated transforms, suffix-independent member identity, numeric tolerance 1e-6',fixtures=fixtures,comparisons=rows)
(O/'calibration-component-diagnostic.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
