"""Compare refreshed fitted scratch with actual saved source mesh/material data."""
import bpy,json,hashlib,os
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=Path(os.environ['ASSET_EVIDENCE_DIR'])
def signature(o):
    d=o.data;d.calc_loop_triangles()
    mats=[]
    for m in d.materials:
        p=m.node_tree.nodes.get('Principled BSDF')
        mats.append(dict(name=m.name,color=list(p.inputs['Base Color'].default_value),metallic=p.inputs['Metallic'].default_value,roughness=p.inputs['Roughness'].default_value,culling=m.use_backface_culling))
    payload=dict(vertices=[list(v.co) for v in d.vertices],polygons=[list(p.vertices) for p in d.polygons],smooth=[p.use_smooth for p in d.polygons],slots=[p.material_index for p in d.polygons],normals=[list(n.vector) for n in d.corner_normals],materials=mats)
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
expected={}
for asset in ['03','06']:
    bpy.ops.wm.open_mainfile(filepath=str(R/('art/source/models/environment/city_shop_fittings_'+asset+'/city_shop_fittings_'+asset+'.blend')))
    expected.update({o.name:signature(o) for o in bpy.data.objects if o.type=='MESH' and o.name!='authoring_1m_reference'})
bpy.ops.wm.open_mainfile(filepath=str(E/'fitted_comparison.blend'))
actual={name:signature(bpy.data.objects[name]) for name in expected}
assert expected==actual
(E/'scratch_correspondence.json').write_text(json.dumps(dict(mesh_count=len(expected),expected=expected,actual=actual,all_match=True),indent=2)+'\n')
print('ALL_17_FITTED_SCRATCH_MESH_MATERIAL_NORMAL_SIGNATURES_MATCH_CURRENT_SOURCES')
