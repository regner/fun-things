"""Evaluate hardened bevel normals, preserving original sharp-miter geometry."""
from pathlib import Path
import json
T=Path(__file__).resolve().parent;R=T.parents[2];E=R/'docs/assets/production/city_shop_fittings_06-evidence/fix_f2'
code=(E/'before/author.py').read_text().replace("m=o.modifiers.new('soft_manufactured_edges','BEVEL'); m.width=bevel; m.segments=4", "for p in d.polygons: p.use_smooth=True\n    m=o.modifiers.new('soft_manufactured_edges','BEVEL'); m.width=bevel; m.segments=4\n    if name.endswith('_stiles_rails'): m.harden_normals=True; m.miter_inner='MITER_ARC'; m.spread=.004")
code=code.replace("m=o.modifiers.new('broad_face_normals','WEIGHTED_NORMAL'); m.keep_sharp=True", "if name.endswith('_stiles_rails'): return o\n    m=o.modifiers.new('broad_face_normals','WEIGHTED_NORMAL'); m.keep_sharp=True")
code=code.replace("str(R/'art/source/models/environment/city_shop_fittings_06/city_shop_fittings_06.blend')","str(E/'arc_harden_probe.blend')")
exec(compile(code,str(T/'author.py'),'exec'))
rows=[]
for o in bpy.data.objects:
    if o.type!='MESH':continue
    d=o.data;d.calc_loop_triangles();dots=[t.normal.dot(d.corner_normals[i].vector) for t in d.loop_triangles for i in t.loops]
    rows.append(dict(name=o.name,triangles=len(d.loop_triangles),minimum_corner_dot=min(dots),opposing_corners=sum(x<0 for x in dots)))
(E/'arc_harden_probe.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
