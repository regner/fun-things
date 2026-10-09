"""Verify the selected opening, insertion envelope and source dependency scope."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_07-evidence'
col=bpy.data.collections['export_city_shop_fittings_07'];bpy.context.view_layer.update()
rear=[];report=[]
for o in col.objects:
    if o.type!='MESH':continue
    verts=[o.matrix_world@v.co for v in o.data.vertices]
    behind=[v for v in verts if v.y<0]
    for v in behind:
        assert -2.32-.00001<=v.x<=2.32+.00001,(o.name,list(v))
        assert .08-.00001<=v.z<=1.52+.00001,(o.name,list(v))
        assert v.y>=-.16-.00001
    rear.extend(behind)
    report.append(dict(name=o.name,bounds=[[min(v[i] for v in verts) for i in range(3)],[max(v[i] for v in verts) for i in range(3)]],rear_vertex_count=len(behind)))
assert rear
assert not bpy.data.libraries
assert not any(i.filepath for i in bpy.data.images)
assert {o.name for o in bpy.data.objects if o not in list(col.objects)}=={'authoring_1m_reference'}
assert not bpy.data.actions and not bpy.data.armatures
clearance=[min(v.x+2.34 for v in rear),min(2.34-v.x for v in rear),min(v.z-.06 for v in rear),min(1.54-v.z for v in rear)]
assert all(c>=.020-.00001 for c in clearance)
report=dict(checks='PASS',objects=report,opening_xz_m=[[-2.34,.06],[2.34,1.54]],insertion_clearance_left_right_bottom_top_m=clearance,rear_void_limit_y_m=-.18,minimum_rear_clearance_m=min(v.y+.18 for v in rear),source_external_dependencies=[],excluded_objects=['authoring_1m_reference'])
(E/'interface_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
