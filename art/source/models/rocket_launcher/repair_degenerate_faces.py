"""Narrow F1 repair of the saved source; run once, then measure and reexport.

Astra high, 9 October 2026. Preserve silhouette, materials, contacts and unit roots.
Weld bevel-collapse duplicates within 0.01 mm; dissolve collapsed faces/edges.
This edits existing source geometry, never the historical bootstrap or Godot cache.
"""
from pathlib import Path
import bpy
import bmesh

source = Path(__file__).resolve().parent / 'dock_thumper_a.blend'
assert Path(bpy.data.filepath).resolve() == source
for name in ('RearRecess', 'ExhaustRecess', 'RocketIvoryBand'):
    obj = bpy.data.objects[name]
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    before = len(bm.faces)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.00001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=0.00001)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(face.calc_area() > 1e-12 for face in bm.faces), name
    print('F1_REPAIR', name, before, '->', len(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
bpy.ops.wm.save_as_mainfile(filepath=str(source))
