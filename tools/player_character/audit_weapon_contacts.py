"""Measure fixed weapon surface contacts against the actual deformed Courier skin."""
from pathlib import Path
import json
import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[2]


def main():
    """Inspect source poses and mesh surfaces; leave the saved source untouched."""
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art/source/models/characters/coral_courier/coral_courier.blend'))
    rig=bpy.data.objects['Rig'];skin=bpy.data.objects['Skin']
    source=ROOT/'art/source/models/characters/shared_humanoid/shared_humanoid_player_motion_v1.blend'
    profiles=json.loads((ROOT/'art/source/models/characters/coral_courier/weapon_profiles.json').read_text())['profiles']
    with bpy.data.libraries.load(str(source),link=False) as (src,dst):
        dst.actions=['pistol_hold','smg_hold','launcher_hold']
    actions={a.name:a for a in dst.actions};rig.animation_data_create()
    results={}
    for weapon in ['pistol','smg','launcher']:
        rig.animation_data.action=actions[weapon+'_hold']
        rig.animation_data.action_slot=rig.animation_data.action.slots[0]
        bpy.context.scene.frame_set(0)
        evaluated=skin.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh=evaluated.data;mesh.calc_loop_triangles()
        verts=[evaluated.matrix_world @ v.co for v in mesh.vertices]
        garment=[];left_hand=[]
        for tri in mesh.loop_triangles:
            if mesh.materials[tri.material_index].name in ['ivory_yoke','coral_shell']:
                garment.append(list(tri.vertices))
            groups={skin.vertex_groups[g.group].name for vi in tri.vertices for g in skin.data.vertices[vi].groups}
            if groups and all(g in ['hand_l','thumb_l','index_l','fingers_l'] for g in groups):
                left_hand.append(list(tri.vertices))
        cloth=BVHTree.FromPolygons(verts,garment,all_triangles=True)
        hand=BVHTree.FromPolygons(verts,left_hand,all_triangles=True)
        grip=Vector(profiles[weapon]['hold_grip_blender'])
        result={'grip_blender':list(grip)}
        if weapon!='pistol':
            contact=grip+Vector((0,-.280,.128 if weapon=='smg' else .085))
            normal=Vector((0,1,0)) if weapon=='smg' else Vector((0,0,1))
            point,hit_normal,index,distance=cloth.ray_cast(contact+normal, -normal,2)
            result['shoulder']={'contact':list(contact),'surface':list(point) if point else None,
                                'signed_surface_gap_m':(contact-point).dot(normal) if point else None}
            support=grip+Vector((0,.310,.055)) if weapon=='smg' else grip+Vector((0,.430,-.0825))
            point,normal,index,distance=hand.find_nearest(support)
            result['support']={'contact':list(support),'nearest_hand':list(point),'distance_m':distance}
            assert abs(result['shoulder']['signed_surface_gap_m']) < .005, result
            assert result['support']['distance_m'] < .005, result
        if weapon=='launcher':
            head_points=[verts[v.index] for v in skin.data.vertices if any(
                skin.vertex_groups[g.group].name=='head' for g in v.groups)]
            result['head_lateral_clearance_m']=grip.x-.203-max(v.x for v in head_points)
            assert result['head_lateral_clearance_m'] > .005, result
        results[weapon]=result
    (ROOT/'docs/assets/player_character/evidence/weapon_contacts.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results))


if __name__=='__main__':main()
