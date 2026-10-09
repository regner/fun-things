import bpy,json,math
from pathlib import Path
from mathutils import Vector
rig=bpy.data.objects['Rig'];mesh=bpy.data.objects['WorkerMesh'];scene=bpy.context.scene
rows={}
for action in bpy.data.actions:
 rig.animation_data.action=action; rig.animation_data.action_slot=action.slots[0]
 points=[];roots=[];poses={}
 for frame in range(int(action.frame_range[0]),int(action.frame_range[1])+1):
  scene.frame_set(frame);bpy.context.view_layer.update()
  evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
  pts=[v.co.copy() for v in evaluated.data.vertices];points.extend(pts)
  roots.append(max(abs(v) for v in rig.pose.bones['root'].location))
  poses[frame]=[tuple(p.matrix_basis[i]) for p in rig.pose.bones for i in range(4)]
 first=min(poses);last=max(poses)
 seam=max(abs(a-b) for va,vb in zip(poses[first],poses[last]) for a,b in zip(va,vb))
 hold=max(abs(a-b) for va,vb in zip(poses.get(40,poses[last]),poses[last]) for a,b in zip(va,vb))
 rows[action.name]={'seconds':(last-first)/30,'min':[min(v[i] for v in points) for i in range(3)],'max':[max(v[i] for v in points) for i in range(3)],'root_translation_max':max(roots),'endpoint_basis_error':seam,'final_hold_basis_error':hold}
 assert max(roots)<1e-8
 assert rows[action.name]['min'][2]>-.006,rows[action.name]
 if action.name!='death': assert seam<1e-5
 else: assert hold<1e-6
out=Path('docs/assets/pedestrian_worker_a-evidence/motion.json');out.write_text(json.dumps(rows,indent=2)+'\n');print('MOTION_CHECK',json.dumps(rows))
