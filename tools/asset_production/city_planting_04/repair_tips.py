"""Remove diagnosed isolated tiny remesh quads inside crowns; retain exact source."""
import bpy,bmesh
from pathlib import Path
R=Path(__file__).resolve().parents[3]
for o in bpy.data.objects:
 if o.type!='MESH' or 'sculpted_trunk' not in o.name:continue
 bm=bmesh.new(); bm.from_mesh(o.data); boundary=[e for e in bm.edges if e.is_boundary]
 print(o.name,'boundary_before',len(boundary))
 # Inspection identifies a disconnected tiny quad island, not a hole in the trunk.
 if boundary:
  faces={f for e in boundary for f in e.link_faces}
  assert len(faces)==1 and all(e.is_boundary for f in faces for e in f.edges)
  verts={v for f in faces for v in f.verts}
  assert all(v.co.z>2.5 for v in verts)
  assert sum(f.calc_area() for f in faces)<.0001
  bmesh.ops.delete(bm,geom=list(verts),context='VERTS')
 bmesh.ops.dissolve_degenerate(bm,dist=.000001,edges=list(bm.edges))
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 assert all(e.is_manifold and e.is_contiguous for e in bm.edges)
 bm.to_mesh(o.data); bm.free(); o.data.update()
 print(o.name,'closed')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
