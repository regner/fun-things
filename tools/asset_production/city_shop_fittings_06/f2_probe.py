"""Compare corner normal treatments in memory without changing source."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_06-evidence/fix_f2'
o=bpy.data.objects['single_leaf_1_stiles_rails'];d=o.data

def audit():
    d.calc_loop_triangles();vals=[];bad=[]
    for t in d.loop_triangles:
        dots=[t.normal.dot(d.corner_normals[i].vector) for i in t.loops];vals.extend(dots)
        if min(dots)<0:bad.append(dict(triangle=t.index,polygon=t.polygon_index,dots=dots,positions=[list(d.vertices[i].co) for i in t.vertices]))
    return dict(minimum_dot=min(vals),opposing_triangles=bad)
r={'weighted_original':audit()}
d.normals_split_custom_set([(0,0,0)]*len(d.loops));d.update()
r['automatic_angle_normals']=audit()
(E/'normal_probe.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
