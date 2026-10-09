"""Original Coral Courier mesh authoring against the immutable shared humanoid v1.

Approved direction: docs/concepts/assets-v1/player-character/01_coral_courier.png.
Authored by the player lead under GPT-6-Astra/high; no external geometry/textures.
Run in private Blender. Saved .blend owns subsequent edits; reexport.py reads it.
"""
from pathlib import Path
import json
import math
import bpy
import bmesh
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'art/source/models/characters/coral_courier/coral_courier.blend'
OUTPUT=ROOT/'art/models/characters/coral_courier/coral_courier.glb'
COLLECTION='export_coral_courier'
PARTS=[]
MATERIALS={}


def linear(c):
    """Convert original display-referred swatches to linear Blender base colors."""
    return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4


def material(name, color, roughness=.78):
    """Create an opaque flat PBR slot with no procedural or external texture dependency."""
    m=bpy.data.materials.new(name);m.use_nodes=True
    rgb=tuple(linear(int(color[i:i+2],16)/255) for i in (0,2,4))+(1,)
    m.diffuse_color=rgb
    n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    n.inputs['Base Color'].default_value=rgb;n.inputs['Roughness'].default_value=roughness
    MATERIALS[name]=m
    return m


def own(obj):
    """Move authored geometry into the explicit export collection."""
    for col in list(obj.users_collection):col.objects.unlink(obj)
    bpy.data.collections[COLLECTION].objects.link(obj)
    PARTS.append(obj)
    return obj


def weights(obj, mapping):
    """Assign named normalized influences, independent of bone index ordering."""
    for name, values in mapping.items():
        group=obj.vertex_groups.new(name=name)
        for index,weight in values:
            if weight>0:group.add([index],weight,'REPLACE')


def ellipsoid(name, center, radius, mat, bone, direction=None, segments=16, rings=10):
    """Author smooth rounded anatomy/accessory forms with explicit UVs and skin group."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=center)
    obj=own(bpy.context.object);obj.name=name;obj.scale=radius
    if direction is not None:
        obj.rotation_mode='QUATERNION'
        obj.rotation_quaternion=Vector((0,0,1)).rotation_difference(Vector(direction))
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    obj.data.materials.append(MATERIALS[mat])
    obj.vertex_groups.new(name=bone).add(list(range(len(obj.data.vertices))),1,'REPLACE')
    for p in obj.data.polygons:p.use_smooth=True
    return obj


def box(name, center, size, bevel, mat, bone):
    """Author a broad bevelled cloth/leather detail, keeping all object transforms unit."""
    bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    obj=own(bpy.context.object);obj.name=name;obj.scale=size
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    mod=obj.modifiers.new('Broad edge rounding','BEVEL');mod.width=bevel;mod.segments=3
    bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.data.materials.append(MATERIALS[mat])
    obj.vertex_groups.new(name=bone).add(list(range(len(obj.data.vertices))),1,'REPLACE')
    for p in obj.data.polygons:p.use_smooth=True
    return obj


def loft(name, stations, materials, segments=16, front_open=False):
    """Build an original ring surface with station skin blends and cylindrical UVs.

    Stations are (centre, horizontal_radius, depth_radius, weight_dictionary).
    Rings use local XY around the supplied centre; torso/legs are vertical.
    """
    verts=[];faces=[];assignments={}
    for j,(center,rx,ry,skin) in enumerate(stations):
        for i in range(segments):
            angle=2*math.pi*i/segments
            verts.append((center[0]+rx*math.cos(angle),center[1]+ry*math.sin(angle),center[2]))
            index=len(verts)-1
            for bone,w in skin.items():assignments.setdefault(bone,[]).append((index,w))
    # End caps stay at existing rings; no stray origin vertices.
    faces.append(tuple(reversed(range(segments))))
    slots=[0]
    for j in range(len(stations)-1):
        for i in range(segments):
            # Open bomber front exposes the separately skinned shirt.
            mid=2*math.pi*(i+.5)/segments
            if front_open and abs(mid-math.pi/2)<.26:continue
            faces.append((j*segments+i,j*segments+(i+1)%segments,
                          (j+1)*segments+(i+1)%segments,(j+1)*segments+i))
            slots.append(min(j,len(materials)-1))
    faces.append(tuple((len(stations)-1)*segments+i for i in range(segments)))
    slots.append(len(materials)-1)
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.data.collections[COLLECTION].objects.link(obj);PARTS.append(obj)
    for mat in materials:mesh.materials.append(MATERIALS[mat])
    for polygon,slot in zip(mesh.polygons,slots):polygon.material_index=slot;polygon.use_smooth=True
    uv=mesh.uv_layers.new(name='UVMap')
    for polygon in mesh.polygons:
        for loop in polygon.loop_indices:
            vi=mesh.loops[loop].vertex_index
            uv.data[loop].uv=((vi%segments)/segments,(vi//segments)/(len(stations)-1))
    weights(obj,assignments)
    return obj


def sweep(name, points, radii, skin, mat, segments=12):
    """Loft sleeves/limbs along a centre line with normalized joint transition weights."""
    vertices=[];faces=[];groups={}
    for j,p in enumerate(points):
        p=Vector(p)
        direction=Vector(points[min(j+1,len(points)-1)])-Vector(points[max(0,j-1)])
        direction.normalize()
        u=direction.cross(Vector((0,1,0))).normalized();v=direction.cross(u).normalized()
        for i in range(segments):
            a=i*2*math.pi/segments
            vertex=p+radii[j][0]*math.cos(a)*u+radii[j][1]*math.sin(a)*v
            vertices.append(vertex)
            for b,w in skin[j].items():groups.setdefault(b,[]).append((len(vertices)-1,w))
    faces.append(tuple(reversed(range(segments))))
    for j in range(len(points)-1):
        for i in range(segments):faces.append((j*segments+i,j*segments+(i+1)%segments,
             (j+1)*segments+(i+1)%segments,(j+1)*segments+i))
    faces.append(tuple((len(points)-1)*segments+i for i in range(segments)))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.data.collections[COLLECTION].objects.link(obj);PARTS.append(obj)
    mesh.materials.append(MATERIALS[mat])
    for face in mesh.polygons:face.use_smooth=True
    uv=mesh.uv_layers.new(name='UVMap')
    for face in mesh.polygons:
        for li in face.loop_indices:
            i=mesh.loops[li].vertex_index;uv.data[li].uv=((i%segments)/segments,(i//segments)/(len(points)-1))
    weights(obj,groups)
    return obj


def torso():
    """Build the cropped bomber, continuous ivory shoulder yoke and visible dark shirt."""
    loft('Body',[( (0,0,z),rx,ry,w) for z,rx,ry,w in [
         (.90,.18,.12,{'pelvis':1}), (1.03,.175,.12,{'pelvis':.4,'spine':.6}),
         (1.15,.19,.13,{'spine':.7,'chest':.3}), (1.32,.23,.14,{'chest':1}),
         (1.41,.18,.105,{'chest':1})]],['skin_warm']*4)
    loft('CroppedTop',[((0,.013,z),rx,ry,w) for z,rx,ry,w in [
         (1.105,.184,.124,{'spine':1}),(1.20,.209,.143,{'spine':.5,'chest':.5}),
         (1.35,.241,.145,{'chest':1}),(1.42,.10,.093,{'chest':1})]],['shirt_petrol']*3)
    loft('Bomber',[( (0,0,z),rx,ry,w) for z,rx,ry,w in [
         (1.085,.21,.15,{'spine':1}),(1.115,.225,.165,{'spine':.85,'chest':.15}),
         (1.205,.265,.18,{'spine':.35,'chest':.65}),(1.305,.288,.18,{'chest':1}),
         (1.375,.27,.157,{'chest':1}),(1.41,.185,.115,{'chest':1})]],
         ['coral_rib','coral_shell','coral_shell','ivory_yoke','ivory_yoke'],front_open=True)
    loft('Collar',[((0,0,z),rx,ry,{'chest':1}) for z,rx,ry in [
         (1.394,.105,.087),(1.445,.107,.082),(1.454,.092,.073)]],['coral_shell']*2,front_open=True)
    loft('Neck',[((0,0,z),r,r,{'neck':1}) for z,r in [(1.40,.071),(1.51,.073),(1.54,.079)]],['skin_warm']*2)
    loft('Waistband',[((0,0,z),rx,.145,{'pelvis':1}) for z,rx in [(1.015,.207),(1.052,.205)]],['glove_dark'])
    box('Buckle',(0,.151,1.034),(.055,.018,.034),.006,'metal_dark','pelvis')
    box('WaistPouch',(.19,.111,1.024),(.137,.102,.135),.025,'glove_dark','pelvis')
    box('PouchLatch',(.19,.167,1.04),(.038,.016,.034),.005,'coral_shell','pelvis')


def limbs(rig):
    """Author weighted cloth legs and puffy sleeves around the unchanged A-pose joints."""
    for side,sign in [('r',1),('l',-1)]:
        p=lambda x,y,z:(sign*x,y,z)
        thigh,shin='thigh_'+side,'shin_'+side
        loft('Trouser_'+side,[(p(x,y,z),rx,ry,w) for x,y,z,rx,ry,w in [
            (.12,0,1.02,.12,.147,{'pelvis':.6,thigh:.4}),(.13,0,.89,.137,.145,{thigh:1}),
            (.137,.008,.68,.129,.132,{thigh:1}),(.14,.023,.54,.105,.116,{thigh:.8,shin:.2}),
            (.14,.025,.49,.099,.107,{thigh:.45,shin:.55}),(.14,.021,.44,.104,.109,{thigh:.1,shin:.9}),
            (.14,.008,.29,.099,.097,{shin:1}),(.14,0,.17,.074,.079,{shin:1}),
            (.14,0,.148,.074,.078,{shin:1})]],['trouser_slate']*8)
        box('CargoPocket_'+side,p(.254,.01,.756),(.068,.17,.174),.025,'pocket_slate',thigh)
        box('PocketFlap_'+side,p(.258,.013,.827),(.076,.179,.042),.012,'trouser_slate',thigh)
        foot='foot_'+side
        box('SneakerSole_'+side,p(.14,.099,.033),(.197,.355,.061),.025,'coral_rib',foot)
        box('SneakerUpper_'+side,p(.14,.096,.091),(.183,.318,.115),.039,'ivory_yoke',foot)
        ellipsoid('ShoeTongue_'+side,p(.14,.054,.143),(.065,.091,.032),'ivory_yoke',foot)
        for y in [.10,.13,.16]:
            box('Lace_'+side+str(y),p(.14,y,.150),(.112,.012,.011),.004,'cream_laces',foot)
        upper,fore='upper_arm_'+side,'forearm_'+side
        a,b,c=Vector(p(.245,0,1.38)),Vector(p(.445,0,1.16)),Vector(p(.635,.015,.96))
        sweep('ArmSkin_'+side,[a,b,b.lerp(c,.45),c],[(.073,.079),(.070,.073),(.066,.067),(.053,.052)],
              [{upper:1},{upper:.5,fore:.5},{fore:1},{fore:1}],'skin_warm')
        sweep('PuffSleeve_'+side,[a.lerp(b,-.08),a.lerp(b,.22),a.lerp(b,.62),b,b.lerp(c,.32)],
              [(.095,.105),(.145,.14),(.13,.132),(.112,.112),(.090,.09)],
              [{upper:.75,'chest':.25},{upper:1},{upper:1},{upper:.5,fore:.5},{fore:1}], 'coral_shell')
        sweep('SleeveYoke_'+side,[a.lerp(b,-.04),a.lerp(b,.18)],[(.109,.115),(.149,.144)],
              [{upper:.7,'chest':.3},{upper:1}],'ivory_yoke')
        sweep('RibCuff_'+side,[b.lerp(c,.28),b.lerp(c,.40)],[(.092,.092),(.083,.086)],
              [{fore:1},{fore:1}],'coral_rib')
        hand='hand_'+side
        hb=rig.data.bones[hand];centre=(hb.head_local+hb.tail_local)*.5
        ellipsoid('Palm_'+side,centre,(.050,.038,.070),'skin_warm',hand,hb.tail_local-hb.head_local)
        ellipsoid('FingerlessGlove_'+side,centre+Vector((0,-.009,.004)),(.054,.039,.058),
                  'glove_dark',hand,hb.tail_local-hb.head_local)
        for bn in ['thumb_'+side,'index_'+side,'fingers_'+side]:
            bone=rig.data.bones[bn];rad=.021 if bn.startswith('thumb') else .024
            if bn.startswith('fingers'):rad=.035
            ellipsoid('Digits_'+bn,(bone.head_local+bone.tail_local)*.5,(rad,.027,bone.length*.60),
                      'skin_warm',bn,bone.tail_local-bone.head_local,segments=12,rings=8)


def head():
    """Author a simplified face, cropped dark hair mass and broad ivory forelock."""
    loft('Head',[( (0,y,z),rx,ry,{'head':1}) for z,y,rx,ry in [
        (1.492,.024,.062,.065),(1.53,.014,.097,.096),(1.59,.004,.124,.12),
        (1.665,0,.135,.126),(1.724,-.005,.125,.118),(1.763,-.01,.092,.095),
        (1.78,-.015,.025,.032)]],['skin_warm']*6,segments=20)
    for s in [-1,1]:
        ellipsoid('Ear'+str(s),(s*.13,.0,1.623),(.035,.029,.052),'skin_warm','head',segments=12,rings=8)
        ellipsoid('EyeWhite'+str(s),(s*.048,.116,1.657),(.030,.012,.016),'cream_laces','head')
        ellipsoid('Iris'+str(s),(s*.047,.127,1.656),(.012,.007,.012),'hair_dark','head',segments=12,rings=8)
        box('Brow'+str(s),(s*.048,.126,1.685),(.064,.012,.013),.006,'hair_dark','head')
    ellipsoid('Nose',(0,.135,1.621),(.026,.033,.039),'skin_warm','head')
    ellipsoid('Mouth',(0,.115,1.576),(.039,.011,.008),'lip_warm','head',segments=16,rings=6)
    # Broad individual locks retain their volume from the vertical camera.
    ellipsoid('HairCap',(0,-.014,1.726),(.139,.128,.080),'hair_dark','head',segments=20,rings=12)
    locks=[(-.085,-.03,1.765,-.03,-.05,.055),(-.04,-.05,1.794,-.03,-.03,.05),
           (.015,-.045,1.802,.03,-.02,.045),(.075,-.025,1.778,.05,-.02,.035),
           (.097,.045,1.756,.04,.04,.02),(-.092,.056,1.741,-.025,.04,.02)]
    for i,(x,y,z,dx,dy,dz) in enumerate(locks):
        ellipsoid('HairLock'+str(i),(x,y,z),(.045,.033,.062),'hair_dark','head',(dx,dy,dz),segments=12,rings=8)
    sweep('IvoryForelock',[(.034,.030,1.806),(.017,.081,1.803),(-.015,.124,1.769),(-.037,.136,1.714)],
          [(.033,.023),(.037,.025),(.031,.022),(.009,.010)],[{'head':1}]*4,'ivory_yoke')


def main():
    """Save an interchangeable original skin without altering the canonical skeleton."""
    assert bpy.app.version_string=='5.2.2 LTS'
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    scene.render.fps=30
    col=bpy.data.collections.new(COLLECTION);scene.collection.children.link(col)
    with bpy.data.libraries.load(str(ROOT/'art/source/models/characters/shared_humanoid/shared_humanoid_v1.blend'),link=False) as (src,dst):
        dst.objects=['Rig']
    rig=dst.objects[0];col.objects.link(rig)
    for name,color in [('skin_warm','B57B58'),('coral_shell','F46F5B'),('coral_rib','D84F44'),
        ('ivory_yoke','F3E8CD'),('cream_laces','E2DAC5'),('shirt_petrol','172B35'),
        ('trouser_slate','243A47'),('pocket_slate','304957'),('glove_dark','18242D'),
        ('metal_dark','61717A'),('hair_dark','17212B'),('lip_warm','754733')]:material(name,color)
    torso();limbs(rig);head()
    bpy.ops.object.select_all(action='DESELECT')
    for obj in PARTS:obj.select_set(True)
    bpy.context.view_layer.objects.active=PARTS[0];bpy.ops.object.join()
    skin=bpy.context.object;skin.name='Skin';skin.data.name='coral_courier_skin'
    skin.parent=rig;mod=skin.modifiers.new('SharedHumanoidV1','ARMATURE');mod.object=rig
    # Merge repeated material slots after joining, preserving stable semantic slot names.
    names=[]
    for slot in skin.data.materials:
        if slot.name not in names:names.append(slot.name)
    old=[slot.name for slot in skin.data.materials]
    assignments=[names.index(old[p.material_index]) for p in skin.data.polygons]
    skin.data.materials.clear()
    for name in names:skin.data.materials.append(MATERIALS[name])
    for p,index in zip(skin.data.polygons,assignments):p.material_index=index
    # Explicit triangulation and collapsed-bevel cleanup keep source/export topology valid.
    bm=bmesh.new();bm.from_mesh(skin.data)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.dissolve_degenerate(bm,dist=1e-6,edges=list(bm.edges))
    bm.to_mesh(skin.data);bm.free();skin.data.update()
    for vertex in skin.data.vertices:
        assert vertex.groups and len(vertex.groups)<=4
        assert abs(sum(g.weight for g in vertex.groups)-1)<1e-5
    skin['skin_contract']='shared_humanoid/1.0.0'
    skin['rest_sha256']=rig['rest_sha256']
    skin['concept']='A Coral Courier, approved Regner 2026-10-09'
    skin['author']='Player lead, GPT-6-Astra/high; original geometry, no third-party assets'
    SOURCE.parent.mkdir(parents=True,exist_ok=True);OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    bpy.context.view_layer.objects.active=rig;rig.select_set(True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    settings=json.loads((ROOT/'tools/s01/export_settings.json').read_text())
    settings.update(collection=COLLECTION,export_animations=False,filepath=str(OUTPUT))
    bpy.ops.export_scene.gltf(**settings)
    report={'source':str(SOURCE.relative_to(ROOT)),'export':str(OUTPUT.relative_to(ROOT)),
            'collection':COLLECTION,'members':['Rig','Skin'],'materials':names,
            'vertices':len(skin.data.vertices),'triangles':sum(len(p.vertices)-2 for p in skin.data.polygons),
            'rest_sha256':rig['rest_sha256'],'textures':[],'uv':'UVMap; original primitive/loft UVs; flat materials',
            'blender':bpy.app.version_string}
    (SOURCE.parent/'coral_courier.json').write_text(json.dumps(report,indent=2)+'\n')
    print('CORAL_COURIER_AUTHORED',json.dumps(report))


if __name__=='__main__':
    main()
