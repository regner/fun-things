import bpy,json,sys,hashlib,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(sys.argv[sys.argv.index("--")+1]);manifest=json.loads((Path(bpy.data.filepath).parent/"source_manifest.json").read_text())
report={"blender":bpy.app.version_string,"build":bpy.app.build_hash.decode(),"unit_system":bpy.context.scene.unit_settings.system,"unit_scale":bpy.context.scene.unit_settings.scale_length,"libraries":[l.filepath for l in bpy.data.libraries],"images":[i.filepath for i in bpy.data.images],"collections":{},"contacts":{},"materials":{},"failures":[]}
def check(ok,msg):
 if not ok:report["failures"].append(msg)
check(report["unit_system"]=="METRIC" and report["unit_scale"]==1,"metres")
check(not report["libraries"] and not report["images"],"external dependencies")
for name,rows in manifest["collections"].items():
 col=bpy.data.collections[name];objects=[]
 check(set(o.name for o in col.all_objects)==set(x["name"] for x in rows),name+" membership")
 for o in col.all_objects:
  row={"name":o.name,"type":o.type,"location":list(o.location),"rotation":list(o.rotation_euler),"scale":list(o.scale),"matrix_world":[list(v) for v in o.matrix_world],"modifiers":[m.type for m in o.modifiers]}
  check(all(abs(s-1)<1e-6 for s in o.scale) and o.matrix_world.determinant()>0,o.name+" scale")
  check(max(abs(v) for v in o.rotation_euler)<1e-6,o.name+" unapplied rotation")
  expected=next(x for x in rows if x["name"]==o.name)
  if o.type=="MESH":
   vs=[o.matrix_world@v.co for v in o.data.vertices]; mapped=[(v.x,v.z,-v.y) for v in vs]
   lo=[min(v[i] for v in mapped) for i in range(3)];hi=[max(v[i] for v in mapped) for i in range(3)]
   row.update(min=lo,max=hi,triangles=sum(len(p.vertices)-2 for p in o.data.polygons),material=[m.name for m in o.data.materials],vertices=len(vs))
   check(row["triangles"]==expected["triangles"],o.name+" triangle manifest")
   check(all(abs(lo[i]-expected["aabb_godot_min"][i])<1e-6 and abs(hi[i]-expected["aabb_godot_max"][i])<1e-6 for i in range(3)),o.name+" bounds manifest")
   check(len(o.data.materials)==1 and row["material"][0]==expected["material"],o.name+" material manifest")
   bm=bmesh.new();bm.from_mesh(o.data)
   row["boundary_edges"]=sum(e.is_boundary for e in bm.edges);row["nonmanifold_edges"]=sum(not e.is_manifold for e in bm.edges);row["signed_volume"]=bm.calc_volume(signed=True)
   row["degenerate_faces"]=sum(f.calc_area()<1e-12 for f in bm.faces)
   check(not row["degenerate_faces"],o.name+" degenerate geometry")
   if not row["nonmanifold_edges"]:check(row["signed_volume"]>0,o.name+" inverted winding")
   bm.free()
  else:
   row["normal_blender"]=list(o["contact_normal_blender"]) if "contact_normal_blender" in o else None
  objects.append(row)
 report["collections"][name]=objects
for marker,objname in [("socket_support_hand","SupportIvoryBase"),("socket_shoulder","ShoulderPad")]:
 o=bpy.data.objects[objname];m=bpy.data.objects[marker]
 verts=[o.matrix_world@v.co for v in o.data.vertices];polys=[tuple(p.vertices) for p in o.data.polygons]
 tree=BVHTree.FromPolygons(verts,polys,all_triangles=True);pos,normal,index,distance=tree.find_nearest(m.matrix_world.translation)
 lo=[min(v[i] for v in verts) for i in range(3)];hi=[max(v[i] for v in verts) for i in range(3)]
 centre=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]));n=Vector(m["contact_normal_blender"])
 report["contacts"][marker]={"surface_object":objname,"marker_position":list(m.location),"nearest_position":list(pos),"distance":distance,"normal":list(normal),"stored_normal":list(n),"surface_centre":list(centre),"centre_error":(centre-m.location).length}
 check(distance<1e-6 and normal.dot(n)>.9999 and (centre-m.location).length<1e-6,marker+" surface centre/normal")
for m in bpy.data.materials:
 p=next((n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED"),None)
 report["materials"][m.name]={"base_color":list(p.inputs["Base Color"].default_value),"metallic":p.inputs["Metallic"].default_value,"roughness":p.inputs["Roughness"].default_value,"emission":list(p.inputs["Emission Color"].default_value),"emission_strength":p.inputs["Emission Strength"].default_value}
report["actions"]=[a.name for a in bpy.data.actions];report["armatures"]=[a.name for a in bpy.data.armatures]
out.write_text(json.dumps(report,indent=2)+"\n")
print("INDEPENDENT_SOURCE_REPORT",out,"failures",report["failures"])
assert not report["failures"]
