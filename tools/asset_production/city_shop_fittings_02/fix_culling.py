"""F1 only: save explicit material culling, preserve source data and refresh owned scratch copy."""
import bpy,hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_02-evidence/f1_culling'
sys.path.insert(0,str(Path(__file__).parent));sys.dont_write_bytecode=True
import export
export.verify_pin()
source=R/'art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def signature(o,culling=False):
    m=o.data
    data=dict(vertices=[list(v.co) for v in m.vertices],polygons=[dict(vertices=list(p.vertices),material=p.material_index,smooth=p.use_smooth) for p in m.polygons],normals=[list(n.vector) for n in m.corner_normals],uv=[dict(name=u.name,values=[list(v.uv) for v in u.data]) for u in m.uv_layers],materials=[dict(name=mat.name,principled={k:list(v) if hasattr(v,'__len__') else v for k in ['Base Color','Metallic','Roughness','Alpha','Emission Color','Emission Strength'] for v in [mat.node_tree.nodes['Principled BSDF'].inputs[k].default_value]},**({'backface_culling':mat.use_backface_culling} if culling else {})) for mat in m.materials])
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
def snapshot():
    return {o.name:dict(type=o.type,parent=o.parent.name if o.parent else None,matrix=[list(row) for row in o.matrix_world],mesh=signature(o) if o.type=='MESH' else None) for o in bpy.data.objects}
old_sha=sha(source);before=snapshot()
materials={m.name:m for o in bpy.data.collections['export_city_shop_fittings_02'].all_objects if o.type=='MESH' for m in o.data.materials}
assert len(materials)==5 and all(not m.use_backface_culling for m in materials.values())
old_flags={n:m.use_backface_culling for n,m in materials.items()}
for m in materials.values():m.use_backface_culling=True
assert before==snapshot()
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.wm.open_mainfile(filepath=str(source))
assert before==snapshot()
assert all(bpy.data.materials[n].use_backface_culling for n in old_flags)
current={o.name:signature(o,True) for o in bpy.data.collections['export_city_shop_fittings_02'].all_objects if o.type=='MESH'}
export.perform(R/'art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb',E/'source_checks.json')
report=dict(finding='F1 P2',frozen_candidate='028775618c4493ca672646e6e37fdc3c83e0e313',source_sha256_before=old_sha,source_sha256_after=sha(source),before_flags=old_flags,after_flags={n:True for n in old_flags},unchanged_geometry_uv_normals_slots_transforms=before,source_material_mesh_signatures=current)
# Original shell evidence stays immutable. Patch ONLY corresponding fascia materials
# in an additive owned copy, verifying every mesh and transform remains unchanged.
scratch=R/'docs/assets/production/city_small_shop_shells_01-evidence/mounted_frontage_scratch.blend'
scratch_sha=sha(scratch);bpy.ops.wm.open_mainfile(filepath=str(scratch));baseline=snapshot()
for name in old_flags:
    m=bpy.data.materials[name];assert not m.use_backface_culling;m.use_backface_culling=True
assert baseline==snapshot()
assert all(signature(bpy.data.objects[n],True)==sig for n,sig in current.items())
output=E/'mounted_frontage_fascia_culling_scratch.blend'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(output));bpy.ops.wm.open_mainfile(filepath=str(output))
assert baseline==snapshot()
assert all(signature(bpy.data.objects[n],True)==sig for n,sig in current.items())
assert sha(scratch)==scratch_sha
report['scratch']=dict(original_path=str(scratch.relative_to(R)),original_sha256=scratch_sha,original_unchanged=True,owned_copy_path=str(output.relative_to(R)),owned_copy_sha256=sha(output),all_original_mesh_geometry_and_transforms_unchanged=True,fascia_current_source_matches=7,fascia_signatures={n:signature(bpy.data.objects[n],True) for n in current},scope='Fascia material correction only; other fittings remain frozen scratch versions, not validation of concurrent F2 changes')
(E/'correction_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
