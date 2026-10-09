"""Ray-measure the saved final aperture and analytic future-leaf envelope gaps."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_shop_fittings_03-evidence'
reports=[]
def hit(o,origin,direction):
    ok,loc,normal,index=o.ray_cast(Vector(origin),Vector(direction))
    assert ok,(o.name,origin,direction)
    return list(loc)
for variant,w in [('single',1.04),('double',1.84)]:
    reveal=bpy.data.objects[variant+'_recessed_reveal']; stop=bpy.data.objects[variant+'_rear_stop']
    sill=bpy.data.objects[variant+'_sloped_threshold']
    side=[]; head=[]
    for y in (-.475,-.4525,-.430):
        for z in (.05,.4,1.2,2.20):
            l=hit(reveal,(0,y,z),(-1,0,0)); r=hit(reveal,(0,y,z),(1,0,0))
            assert abs(l[0]+w/2)<1e-5 and abs(r[0]-w/2)<1e-5
            side.append(dict(y=y,z=z,left=l[0],right=r[0],width=r[0]-l[0]))
        for x in (-w/2+.04,0,w/2-.04):
            h=hit(reveal,(x,y,1.2),(0,0,1))[2]; assert abs(h-2.24)<1e-5
            head.append(dict(x=x,y=y,head_z=h))
    floor=hit(sill,(0,-.4525,1.2),(0,0,-1))[2]; assert abs(floor-.020)<1e-6
    back=hit(stop,(w/2-.012,-.475,1.2),(0,-1,0))[1]; assert abs(back+.481)<1e-6
    leaf_x=[[-.512,.512]] if variant=='single' else [[-.912,-.004],[.004,.912]]
    gaps=dict(side_m=.008,head_m=min(h['head_z'] for h in head)-2.232,bottom_m=.030-floor,rear_stop_m=-.475-back,meeting_m=.008 if variant=='double' else None)
    assert all(v is None or v>=.00599 for v in gaps.values())
    reports.append(dict(variant=variant,aperture_samples=side,head_samples=head,threshold_top_z_m=floor,rear_stop_front_y_m=back,planned_leaf_bounds_blender_m=[[[a,-.475,.030],[b,-.430,2.232]] for a,b in leaf_x],measured_gaps=gaps,scope='Saved-mesh ray probes plus arithmetic envelope comparison; no door leaves authored, no collision/runtime acceptance.'))
(E/'interface_checks.json').write_text(json.dumps(reports,indent=2)+'\n')
print('INTERFACE_CHECKS_PASS',json.dumps(reports))
