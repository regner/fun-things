"""Original baked player motion on shared_humanoid/1.0.0; Astra spatial authoring.

Root stays fixed. These are presentation clips, never gameplay movement/events.
The separate saved player source library retain the canonical rest matrices.
"""
from pathlib import Path
import json
import math
import bpy
from mathutils import Vector, Matrix, Quaternion

ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/'art/source/models/characters/shared_humanoid/shared_humanoid_v1.blend'
FPS=30


def rotation(axis, angle):
    """Return an armature-space rotation matrix."""
    return Matrix.Rotation(angle,4,axis)


def orient(rig, name, origin, direction, normal=None):
    """Transport a rest bone orientation onto a segment; optionally lock palm normal."""
    bone=rig.data.bones[name]
    d=(bone.tail_local-bone.head_local).normalized();v=Vector(direction).normalized()
    if normal is None:
        r=d.rotation_difference(v).to_matrix()
    else:
        n=Vector((0,1,0));n=(n-d*n.dot(d)).normalized()
        target=Vector(normal);target=(target-v*target.dot(v)).normalized()
        a=Matrix((d.cross(n),d,n)).transposed()
        b=Matrix((v.cross(target),v,target)).transposed()
        r=b @ a.transposed()
    return Matrix.Translation(origin) @ (r @ bone.matrix_local.to_3x3()).to_4x4()


def two_bone(start, target, first_length, second_length, pole):
    """Solve a bounded two-segment anatomical chain without changing bone lengths."""
    delta=target-start;distance=delta.length
    direction=delta.normalized()
    distance=min(max(distance,abs(first_length-second_length)+.001),first_length+second_length-.001)
    target=start+direction*distance
    along=(first_length**2-second_length**2+distance**2)/(2*distance)
    height=math.sqrt(max(0,first_length**2-along**2))
    bend=Vector(pole)-direction*Vector(pole).dot(direction)
    if bend.length<.0001:bend=Vector((1,0,0)).cross(direction)
    return start+direction*along+bend.normalized()*height,target


def base_matrices(rig, body):
    """Move the deforming body while preserving the ground root and fixed rest hierarchy."""
    return {b.name:(b.matrix_local.copy() if b.name=='root' else body @ b.matrix_local)
            for b in rig.data.bones}


def pose(rig, clip, t, duration, kind):
    """Author one full pose from gait phase, measured hold contacts and clip intent."""
    phase=2*math.pi*t/duration
    running='run' in clip;walking='walk' in clip
    moving=running or walking
    stride=.26 if running else .17
    lift=.125 if running else .065
    bob=(-.052+(.014 if running else .008)*math.cos(phase*2)) if moving else -.025+.003*math.sin(phase)
    pelvis=Matrix.Translation((0,0,bob))
    desired=base_matrices(rig,pelvis)
    if clip=='death':
        k=min(1,t/duration);ease=k*k*(3-2*k)
        centre=Vector((0,0,.92))
        fallen=Matrix.Translation((.035*ease,.04*ease,-.72*ease)) @ Matrix.Translation(centre) @ rotation('X',-math.pi*.5*ease) @ Matrix.Translation(-centre)
        desired=pose(rig,'idle',0,2,kind)
        desired={name:(matrix if name=='root' else fallen @ matrix) for name,matrix in desired.items()}
        # Prone fall: keep shoe soles oriented to the floor and bend knees as legs settle.
        for side in ['r','l']:
            thigh,shin,foot,toe=[prefix+'_'+side for prefix in ['thigh','shin','foot','toe']]
            hip=desired[thigh].translation
            ankle=desired[foot].translation.copy();ankle.z=max(.12,ankle.z*(1-ease)+.12*ease)
            knee,ankle=two_bone(hip,ankle,rig.data.bones[thigh].length,
                               rig.data.bones[shin].length,(0,1-ease,ease))
            desired[thigh]=orient(rig,thigh,hip,knee-hip)
            desired[shin]=orient(rig,shin,knee,ankle-knee)
            delta=Matrix.Translation(ankle-rig.data.bones[foot].head_local)
            desired[foot]=delta @ rig.data.bones[foot].matrix_local
            desired[toe]=delta @ rig.data.bones[toe].matrix_local
        return desired
    # Full forward/back/strafe contact trajectories are in-place; speed is integrator-owned.
    direction=Vector((0,1,0))
    if 'back' in clip:direction=Vector((0,-1,0))
    if 'left' in clip:direction=Vector((-1,0,0))
    if 'right' in clip:direction=Vector((1,0,0))
    for side,sign in [('r',1),('l',-1)]:
        hip=Vector((sign*.135,0,.92+bob))
        a=phase+(math.pi if side=='l' else 0)
        travel=math.sin(a)*stride if moving else 0
        if direction.x:travel*=.60
        ankle=Vector((sign*.14,0,.12))+direction*travel
        ankle.z+=(max(0,math.cos(a))*lift) if moving else 0
        knee,ankle=two_bone(hip,ankle,rig.data.bones['thigh_'+side].length,
                           rig.data.bones['shin_'+side].length,(0,1,0))
        desired['thigh_'+side]=orient(rig,'thigh_'+side,hip,knee-hip)
        desired['shin_'+side]=orient(rig,'shin_'+side,knee,ankle-knee)
        foot=rig.data.bones['foot_'+side]
        desired[foot.name]=Matrix.Translation(ankle-foot.head_local) @ foot.matrix_local
        toe=rig.data.bones['toe_'+side]
        desired[toe.name]=Matrix.Translation(ankle-foot.head_local) @ toe.matrix_local
    weapon=next((w for w in ['pistol','smg','launcher'] if clip.startswith(w)),None)
    yaw=math.radians(-40 if weapon=='smg' else -50 if weapon=='launcher' else -12 if weapon else 0)
    chest_origin=Vector((0,0,1.20+bob))
    torso=Matrix.Translation(chest_origin) @ rotation('Z',yaw) @ Matrix.Translation(-chest_origin)
    upper_names=['chest','neck','head']+[b.name for b in rig.data.bones if any(b.name.startswith(p) for p in ['clavicle','upper_arm','forearm','hand','thumb','index','fingers'])]
    for name in upper_names:desired[name]=torso @ desired[name]
    # Keep the face looking down the firing line. Launcher head leans clear of the tube.
    for name in ['neck','head']:
        rest=rig.data.bones[name].matrix_local.copy()
        lean=Matrix.Translation((0,0,1.40+bob)) @ rotation('Y',-.33) @ Matrix.Translation((0,0,-1.40)) if weapon=='launcher' else Matrix.Translation((0,0,bob))
        desired[name]=lean @ rest
    # Measured cloth surfaces: SMG butt sits 0.175 m forward of the shoulder joint;
    # launcher pad sits 0.075 m above it. These are skin-fit offsets, not rest edits.
    grip=None
    if weapon:
        shoulder=desired['upper_arm_r'].translation
        if weapon=='pistol':grip=Vector((.30,.43,1.20+bob))
        elif weapon=='smg':grip=shoulder+Vector((0,.455,-.128))
        else:grip=shoulder+Vector((.140,.280,-.010))
        if 'fire' in clip:
            pulse=math.sin(min(1,t/(duration*.33))*math.pi)*.035 if t<duration*.33 else 0
            grip+=Vector((0,-pulse,pulse*.45))
        if 'reload' in clip:
            weight=math.sin(math.pi*t/duration)**2
            grip+=Vector((-.065*weight,-.13*weight,-.07*weight))
    for side,sign in [('r',1),('l',-1)]:
        upper='upper_arm_'+side;fore='forearm_'+side;hand='hand_'+side
        shoulder=desired[upper].translation
        if weapon and side=='r':
            width=.061 if weapon=='pistol' else .032 if weapon=='smg' else .045
            wrist=grip+Vector((width+.015,-.025,.055))
            hand_dir=Vector((0,.12,-1));normal=Vector((-1,0,0))
        elif weapon in ['smg','launcher']:
            contact=grip+Vector((0,.310,.055)) if weapon=='smg' else grip+Vector((0,.430,-.0825))
            wrist=contact+Vector((-.065,-.045,-.039))
            hand_dir=Vector((.8,.6,0));normal=Vector((0,0,1))
        elif weapon=='pistol' and 'reload' in clip:
            wrist=grip+Vector((-.060,.01,-.17))
            hand_dir=Vector((0,.7,.7));normal=Vector((1,0,0))
        else:
            arm_phase=phase+(math.pi if side=='r' else 0)
            swing=(.19 if running else .11)*math.sin(arm_phase) if moving else .008*math.sin(phase)
            wrist=Vector((sign*.31,swing,.875+bob+(.07 if running else 0)))
            hand_dir=Vector((sign*.08,.12,-1));normal=Vector((0,1,0))
        if weapon and side=='l' and 'reload' in clip:
            weight=math.sin(math.pi*t/duration)**2
            target=grip+Vector((-.065,0,-.18))
            wrist=wrist.lerp(target,weight)
        elbow,wrist=two_bone(shoulder,wrist,rig.data.bones[upper].length,
                            rig.data.bones[fore].length,(sign*.8,-.3,-1))
        desired[upper]=orient(rig,upper,shoulder,elbow-shoulder)
        desired[fore]=orient(rig,fore,elbow,wrist-elbow)
        desired[hand]=orient(rig,hand,wrist,hand_dir,normal)
        transform=desired[hand] @ rig.data.bones[hand].matrix_local.inverted()
        for prefix in ['thumb','index','fingers']:
            name=prefix+'_'+side;b=rig.data.bones[name]
            desired[name]=transform @ b.matrix_local
            if weapon and (side=='r' or weapon!='pistol'):
                curl=.55 if prefix=='index' else .82 if prefix=='fingers' else .30
                desired[name]=desired[name] @ rotation('X',curl)
    return desired


def assign(rig, desired, frame):
    """Convert global authored poses to stable local keyed channels without rest edits."""
    for bone in rig.data.bones:
        pb=rig.pose.bones[bone.name]
        parent=bone.parent
        if parent:
            basis=bone.convert_local_to_pose(desired[bone.name],bone.matrix_local,
                    parent_matrix=desired[parent.name],parent_matrix_local=parent.matrix_local,invert=True)
        else:basis=bone.convert_local_to_pose(desired[bone.name],bone.matrix_local,invert=True)
        pb.matrix_basis=basis
        pb.rotation_mode='QUATERNION'
        for channel in ['location','rotation_quaternion','scale']:
            pb.keyframe_insert(channel,frame=frame,group=bone.name)


def library(kind):
    """Save one separate motion library with explicit actions and preserved bind carrier."""
    bpy.ops.wm.open_mainfile(filepath=str(CANON))
    rig=bpy.data.objects['Rig'];rig.animation_data_create()
    col=bpy.data.collections['export_shared_humanoid_bind_v1'];col.name='export_shared_humanoid_'+kind+'_v1'
    clips={'idle':(2,True),'walk':(1,True),'run':(.8,True),'death':(1.2,False)}
    if kind=='player':
        for gait in ['walk','run']:
            for direction in ['back','left','right']:clips[gait+'_'+direction]=(.8 if gait=='run' else 1,True)
        for weapon in ['pistol','smg','launcher']:
            clips[weapon+'_hold']=(2,True)
            clips[weapon+'_walk']=(1,True);clips[weapon+'_run']=(.8,True)
            clips[weapon+'_fire']=(.4 if weapon!='launcher' else .7,False)
        clips['pistol_reload']=(1.4,False);clips['smg_reload']=(1.7,False)
    if kind=='player':
        profiles={}
        for weapon in ['pistol','smg','launcher']:
            matrices=pose(rig,weapon+'_hold',0,2,kind)
            shoulder=matrices['upper_arm_r'].translation
            grip=Vector((.30,.43,1.175)) if weapon=='pistol' else shoulder+Vector((0,.455,-.128)) if weapon=='smg' else shoulder+Vector((.140,.280,-.010))
            offset=matrices['hand_r'].inverted() @ Matrix.Translation(grip)
            profiles[weapon]={'hold_grip_blender':list(grip),'hand_to_grip_blender':[list(row) for row in offset]}
        (ROOT/'art/source/models/characters/coral_courier/weapon_profiles.json').write_text(json.dumps({'contract':'shared_humanoid/1.0.0','profiles':profiles},indent=2)+'\n')
    records=[]
    for name,(duration,loop) in clips.items():
        rig.animation_data.action=None
        for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
        count=round(duration*FPS)
        # Include both endpoints for exact loop seams; frames start at zero.
        for frame in range(count+1):assign(rig,pose(rig,name,frame/FPS,duration,kind),frame)
        action=rig.animation_data.action;action.name=name;action.use_fake_user=True
        track=rig.animation_data.nla_tracks.new();track.name=name
        strip=track.strips.new(name,0,action);strip.action_slot=rig.animation_data.action_slot;track.mute=True
        records.append({'name':name,'frames':[0,count],'fps':FPS,'duration_s':count/FPS,'loop':loop})
    rig.animation_data.action=None
    for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
    bpy.context.scene.frame_set(0)
    source=CANON.parent/('shared_humanoid_'+kind+'_motion_v1.blend')
    output=ROOT/'art/models/characters/shared_humanoid'/('shared_humanoid_'+kind+'_motion_v1.glb')
    bpy.ops.wm.save_as_mainfile(filepath=str(source))
    settings=json.loads((ROOT/'tools/s01/export_settings.json').read_text())
    settings.update(collection=col.name,filepath=str(output),export_animations=True)
    bpy.ops.export_scene.gltf(**settings)
    manifest={'contract':'shared_humanoid/1.0.0','library':kind,'source':str(source.relative_to(ROOT)),
              'export':str(output.relative_to(ROOT)),'collection':col.name,'clips':records,
              'rest_sha256':rig['rest_sha256'],'status':'source export; acceptance tracked in docs/assets/player_character/README.md'}
    (CANON.parent/('shared_humanoid_'+kind+'_motion_v1.json')).write_text(json.dumps(manifest,indent=2)+'\n')
    print('MOTION_AUTHORED',kind,len(records))


def main():
    """Build separate NPC and player candidate action sources on the same exact skeleton."""
    assert bpy.app.version_string=='5.2.2 LTS'
    library('player')


if __name__=='__main__':main()
