import bpy,bmesh,json
for o in bpy.data.objects:
 if o.type=='MESH' and 'trunk' in o.name:
  b=bmesh.new();b.from_mesh(o.data)
  print(o.name, len(b.verts), len(b.faces))
  for e in b.edges:
   if not e.is_manifold or not e.is_contiguous:print('BAD_EDGE',e.index,'faces',len(e.link_faces),'length',e.calc_length(),'coords',[list(v.co) for v in e.verts])
  b.free()
