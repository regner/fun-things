"""Read saved sources, verify canonical binding/weights and measure skinned clip bounds."""
from pathlib import Path
import hashlib
import json
import bpy

ROOT=Path(__file__).resolve().parents[2]


def main():
    """Audit actual saved skin and action data without reconstructing or saving source."""
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art/source/models/player_character/coral_courier.blend'))
    rig=bpy.data.objects['Rig'];mesh=bpy.data.objects['Skin']
    rest=[]
    for bone in rig.data.bones:
        rest.append({'name':bone.name,'parent':bone.parent.name if bone.parent else None,
                     'head_blender_m':list(bone.head_local),'tail_blender_m':list(bone.tail_local),
                     'matrix_blender_armature':[list(row) for row in bone.matrix_local]})
    fingerprint=hashlib.sha256(json.dumps(rest,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    canonical=json.loads((ROOT/'art/source/models/shared_humanoid/shared_humanoid_v1.json').read_text())
    assert fingerprint==canonical['rest_sha256']
    max_weights=max(len(v.groups) for v in mesh.data.vertices)
    assert max_weights<=4
    assert all(v.groups and abs(sum(g.weight for g in v.groups)-1)<1e-5 for v in mesh.data.vertices)
    assert all(g.name in rig.data.bones for g in mesh.vertex_groups)
    mesh.data.calc_loop_triangles()
    degenerate=sum(1 for tri in mesh.data.loop_triangles if tri.area<1e-10)
    assert degenerate==0,degenerate
    assert mesh.data.uv_layers.active is not None
    motion=ROOT/'art/source/models/shared_humanoid/shared_humanoid_player_motion_v1.blend'
    manifest=json.loads(motion.with_suffix('.json').read_text())
    with bpy.data.libraries.load(str(motion),link=False) as (source,target):
        target.actions=[c['name'] for c in manifest['clips']]
    actions={a.name:a for a in target.actions}
    rig.animation_data_create()
    bounds={}
    for spec in manifest['clips']:
        action=actions[spec['name']];rig.animation_data.action=action
        rig.animation_data.action_slot=action.slots[0]
        frames=range(spec['frames'][0],spec['frames'][1]+1,3)
        samples=[]
        for frame in list(frames)+[spec['frames'][1]]:
            bpy.context.scene.frame_set(frame)
            deps=bpy.context.evaluated_depsgraph_get();evaluated=mesh.evaluated_get(deps)
            points=[evaluated.matrix_world @ v.co for v in evaluated.data.vertices]
            samples.append({'frame':frame,'min':[min(p[i] for p in points) for i in range(3)],
                            'max':[max(p[i] for p in points) for i in range(3)]})
        bounds[spec['name']]=samples
    report={'rest_sha256':fingerprint,'vertices':len(mesh.data.vertices),'triangles':len(mesh.data.loop_triangles),
            'degenerate_triangles':degenerate,'max_weights':max_weights,'materials':len(mesh.data.materials),
            'clips':bounds,'death_final_ground_min_z':bounds['death'][-1]['min'][2]}
    assert 0 <= report['death_final_ground_min_z'] <= .01
    path=ROOT/'docs/assets/player_character/evidence/source_audit.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
    print('SOURCE_AUDIT',fingerprint,'death minimum',report['death_final_ground_min_z'])


if __name__=='__main__':main()
