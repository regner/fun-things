"""Evaluate local corner diagonal changes on copies of the original ring."""
import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_06-evidence/fix_f2'
o=bpy.data.objects['single_leaf_1_stiles_rails'];original=o.data;original.calc_loop_triangles()
bad={t.polygon_index for t in original.loop_triangles if min(t.normal.dot(original.corner_normals[i].vector) for i in t.loops)<0}
rows=[]
for method in ['ALTERNATE','SHORT_EDGE','LONG_EDGE']:
    d=original.copy();o.data=d;bm=bmesh.new();bm.from_mesh(d);bm.faces.ensure_lookup_table()
    bmesh.ops.triangulate(bm,faces=[bm.faces[i] for i in bad],quad_method=method);bm.to_mesh(d);bm.free()
    bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
    m=o.modifiers.new('broad_face_normals','WEIGHTED_NORMAL');m.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=m.name)
    d.calc_loop_triangles();dots=[t.normal.dot(d.corner_normals[i].vector) for t in d.loop_triangles for i in t.loops]
    rows.append(dict(method=method,polygons=sorted(bad),minimum_corner_dot=min(dots),opposing_corners=sum(x<0 for x in dots)))
o.data=original
(E/'triangulation_probe.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
