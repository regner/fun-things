"""Check all rear fitting geometry fits shell aperture with specified installation gaps."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_05-evidence'
col=bpy.data.collections['export_city_shop_fittings_05'];errors=[];rear=[]
for o in col.objects:
    if o.type!='MESH':continue
    for v in o.data.vertices:
        if v.co.y<0:
            rear.append(tuple(v.co))
            if not (-1.52+.0199 <= v.co.x <= 1.52-.0199 and .06+.0199 <= v.co.z <= 1.94-.0199):
                errors.append(dict(object=o.name,vertex=v.index,position=list(v.co)))
report=dict(check='Rear geometry within shell opening with nominal >=20mm side/head/bottom gaps',opening_blender_xz_m=[[-1.52,.06],[1.52,1.94]],rear_bounds_m=[[min(v[i] for v in rear) for i in range(3)],[max(v[i] for v in rear) for i in range(3)]],violations=errors,passed=not errors)
(E/'interface_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report));assert not errors,'Shell opening intrusion'
