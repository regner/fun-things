import bpy,bmesh
for o in bpy.data.objects:
 if o.type!='MESH' or ('sculpted_trunk' not in o.name and '_crown_' not in o.name):continue
 b=bmesh.new(); b.from_mesh(o.data)
 print(o.name,'volume',b.calc_volume(signed=True),'minarea',min(f.calc_area() for f in b.faces),'badfaces',[(f.index,f.calc_area()) for f in b.faces if f.calc_area()<=1e-10])
 b.free()
