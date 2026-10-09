"""Compare retained mounted scratch meshes with the exact current authoring sources."""
import bpy
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
FROZEN=Path('/tmp/batch03-independent/frozen')
def signature(o):
    m=o.data
    payload=dict(vertices=[list(v.co) for v in m.vertices],
      polygons=[dict(vertices=list(p.vertices),material=p.material_index,smooth=p.use_smooth) for p in m.polygons],
      normals=[list(n.vector) for n in m.corner_normals],
      uv=[[list(d.uv) for d in u.data] for u in m.uv_layers],
      materials=[dict(name=mat.name,backface_culling=mat.use_backface_culling,
        principled={k:list(v) if hasattr(v,'__len__') else v for k in ['Base Color','Metallic','Roughness','Alpha']
          for v in [mat.node_tree.nodes.get('Principled BSDF').inputs[k].default_value]}) for mat in m.materials])
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
sources={};source_meta={}
ids=['city_shop_fittings_'+i for i in ('01','02','03','05','06')]+['city_small_shop_shells_01']
for ident in ids:
    p=FROZEN/'art/source/models/environment'/ident/(ident+'.blend')
    bpy.ops.wm.open_mainfile(filepath=str(p))
    col=bpy.data.collections['export_'+ident]
    sources[ident]={o.name:signature(o) for o in col.all_objects if o.type=='MESH'}
    source_meta[ident]=dict(path=str(p),file_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mesh_signatures=sources[ident],materials=[dict(name=m.name,backface_culling=m.use_backface_culling) for m in bpy.data.materials])
assemblies=[]
for ident,filename,included in [
 ('city_small_shop_shells_01','mounted_frontage_scratch.blend',ids),
 ('city_shop_fittings_06','fitted_comparison.blend',['city_shop_fittings_03','city_shop_fittings_06'])]:
    p=FROZEN/f'docs/assets/production/{ident}-evidence'/filename
    bpy.ops.wm.open_mainfile(filepath=str(p))
    checks=[]
    for group in included:
        expected=sources[group]
        for name,sig in expected.items():
            if ident=='city_small_shop_shells_01' and (name.startswith('double_')):continue
            o=bpy.data.objects.get(name)
            checks.append(dict(source_id=group,name=name,present=bool(o),matches=bool(o) and signature(o)==sig,
                world_translation=list(o.matrix_world.translation) if o else None,
                root_parent=o.parent.name if o and o.parent else None))
    assemblies.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),checks=checks,
        scene_properties={k:str(v) for k,v in bpy.context.scene.items()},objects=[dict(name=o.name,type=o.type) for o in bpy.data.objects]))
result=dict(sources=source_meta,assemblies=assemblies)
(OUT/'scratch-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps([dict(path=a['path'],checked=len(a['checks']),mismatches=[c for c in a['checks'] if not c['matches']]) for a in assemblies],indent=2))
assert all(c['matches'] for a in assemblies for c in a['checks'])
