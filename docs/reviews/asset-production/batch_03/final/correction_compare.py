import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent

def read(path,ident):
 bpy.ops.wm.open_mainfile(filepath=str(path));result={}
 for o in bpy.data.collections['export_'+ident].all_objects:
  if o.type!='MESH':continue
  m=o.data;result[o.name]=dict(vertices=[list(v.co) for v in m.vertices],polygons=[dict(vertices=list(p.vertices),material=p.material_index,smooth=p.use_smooth) for p in m.polygons],normals=[list(n.vector) for n in m.corner_normals],uv=[[list(d.uv) for d in u.data] for u in m.uv_layers],materials=[dict(name=mat.name,backface_culling=mat.use_backface_culling,principled={k:list(v) if hasattr(v,'__len__') else v for k in ['Base Color','Metallic','Roughness','Alpha'] for v in [mat.node_tree.nodes.get('Principled BSDF').inputs[k].default_value]}) for mat in m.materials],matrix=[list(r) for r in o.matrix_world])
 return result
results=[]
for ident in ['city_shop_fittings_02','city_shop_fittings_06']:
 suffix=Path('art/source/models/environment')/ident/(ident+'.blend');a=read(Path('/tmp/batch03-final/historical')/suffix,ident);b=read(Path('/tmp/batch03-final/frozen')/suffix,ident);assert a.keys()==b.keys();changed=[];changes=[]
 for name in a:
  if a[name]!=b[name]:changed.append(name)
  keys=[k for k in a[name] if a[name][k]!=b[name][k]];changes.append(dict(name=name,changed_fields=keys,old_vertices=len(a[name]['vertices']),new_vertices=len(b[name]['vertices'])))
  if ident.endswith('_02'):
   assert keys==['materials'];assert all(m['backface_culling'] for m in b[name]['materials'])
   for aa,bb in zip(a[name]['materials'],b[name]['materials']):assert dict(aa,backface_culling=True)==bb
  elif name.endswith('_stiles_rails'):
   assert set(keys)<=set(['vertices','polygons','normals']);assert a[name]['materials']==b[name]['materials'] and a[name]['matrix']==b[name]['matrix']
  else:assert not keys
 if ident.endswith('_06'):assert set(changed)=={'single_leaf_1_stiles_rails','double_leaf_1_stiles_rails','double_leaf_2_stiles_rails'}
 results.append(dict(id=ident,changed_objects=changed,fields=changes))
(O/'correction-compare.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
