"""Check saved-source exclusion, seating, UV/material scope and source/export agreement."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_02-evidence'
assert set(c.name for c in bpy.data.collections)=={'export_city_shop_fittings_02','authoring_excluded'}
assert len(bpy.data.objects)==9 and not bpy.data.cameras and not bpy.data.lights
assert not bpy.data.libraries
assert all(i.source=='VIEWER' and not i.filepath for i in bpy.data.images)
ref=bpy.data.objects['authoring_1m_reference'];assert ref.hide_render
carrier=bpy.data.objects['fascia_artwork_carrier'];tray=bpy.data.objects['folded_back_tray']
assert [m.name for m in carrier.data.materials]==['fascia_artwork_face','fascia_mount_metal']
assert len(carrier.data.uv_layers)==1 and carrier.data.uv_layers[0].name=='UV0'
front=[p for p in carrier.data.polygons if p.material_index==0]
assert len(front)==1 and abs(front[0].center.y-.128)<1e-6
assert all(abs(carrier.data.vertices[i].co.y-.128)<1e-6 for i in front[0].vertices)
back_y=min(v.co.y for v in carrier.data.vertices);tray_front=max(v.co.y for v in tray.data.vertices)
assert abs(back_y-.070)<1e-6 and abs(tray_front-.073)<1e-6 and tray_front>back_y
for m in bpy.data.materials:
    assert not any(n.type=='TEX_IMAGE' for n in m.node_tree.nodes)
    assert m.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value==1
    p=m.node_tree.nodes['Principled BSDF']
    assert p.inputs['Emission Strength'].default_value==0 or all(v==0 for v in p.inputs['Emission Color'].default_value[:3])
src=json.loads((E/'source_checks.json').read_text());glb=json.loads((E/'glb_checks.json').read_text())
lo,hi=src['bounds_blender'];expected=[(lo[0],lo[2],-hi[1]),(hi[0],hi[2],-lo[1])]
assert all(abs(a-b)<1e-7 for v,w in zip(expected,glb['decoded_bounds_godot']) for a,b in zip(v,w))
assert src['triangles']==glb['total_triangles']==1656
source=R/'art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend'
report=dict(status='PASS',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),export_sha256=glb['sha256'],source_bytes=source.stat().st_size,source_export_bounds_match=True,saved_source_studio_and_texture_images_absent=True,blender_internal_viewer_images=[i.name for i in bpy.data.images],retained_excluded_1m_reference=True,artwork_front_slot_only=True,insert_to_tray_seating_overlap_m=tray_front-back_y,export_material_count=len(glb['materials']),saved_materials=[m.name for m in bpy.data.materials],triangle_count=1656)
(E/'final_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
