"""Original editable Blender blade housing and twin cantilever mounting hardware."""
import bpy, bmesh, math
from pathlib import Path
import io_scene_gltf2
R=Path(__file__).resolve().parents[3]
assert bpy.app.version[:3]==(5,2,2) and bpy.app.build_hash.decode()=='d13f752e3b9c'
assert io_scene_gltf2.bl_info['version']==(5,2,40)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):bpy.data.collections.remove(c)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new('export_city_shop_fittings_08');s.collection.children.link(col)
studio=bpy.data.collections.new('authoring_excluded');s.collection.children.link(studio)
root=bpy.data.objects.new('city_shop_fittings_08',None);col.objects.link(root)
root['datum']='Origin: wall contact Y=0, mounting centre Z=0. +Y outward; +Z vertical.'
root['artwork']='face_positive_x / face_negative_x; separate slot 0 materials; UV0 upright unmirrored from each outward side.'

def material(name,swatch,metal,rough):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.use_backface_culling=True
    rgb=[int(swatch[i:i+2],16)/255 for i in (0,2,4)]
    rgba=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rgba
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    m.diffuse_color=rgba;return m
paint=material('blade_slate_petrol','405B68',.25,.46)
trim=material('blade_warm_trim','C8C2AD',.22,.48)
seal=material('blade_recess','23333B',0,.72)
metal=material('blade_mount_metal','384850',.45,.50)
a=material('blade_artwork_positive_x','C3C7BC',0,.56)
b=material('blade_artwork_negative_x','C3C7BC',0,.56)

def finish(o,mat,smooth=True):
    for c in list(o.users_collection):c.objects.unlink(o)
    col.objects.link(o);o.parent=root;o.data.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    if smooth:
        for p in o.data.polygons:p.use_smooth=True
        m=o.modifiers.new('Broad manufactured normals','WEIGHTED_NORMAL');m.keep_sharp=True
        bpy.ops.object.modifier_apply(modifier=m.name)
    o.select_set(False);return o

def outline(w,h,r):
    pts=[]
    for cy,cz,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
        for i in range(9):
            angle=math.radians(start+i*90/8);pts.append((.54+cy+r*math.cos(angle),cz+r*math.sin(angle)))
    return pts

def profile(name,sections,mat,ring=False,smooth=True):
    n=36;v=[(x,y,z) for x,w,h,r in sections for y,z in outline(w,h,r)];f=[]
    for j in range(len(sections)-1):
        f.extend((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for i in range(n))
    if ring:
        f.extend(((len(sections)-1)*n+i,(len(sections)-1)*n+(i+1)%n,(i+1)%n,i) for i in range(n))
    else:f.extend([tuple(reversed(range(n))),tuple((len(sections)-1)*n+i for i in range(n))])
    mesh=bpy.data.meshes.new(name+'_mesh');mesh.from_pydata(v,[],f);mesh.update()
    o=bpy.data.objects.new(name,mesh);col.objects.link(o);return finish(o,mat,smooth)

def box(name,centre,size,bevel,mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    m=o.modifiers.new('Soft rolled edge','BEVEL');m.width=bevel;m.segments=3
    bpy.ops.object.modifier_apply(modifier=m.name);return finish(o,mat)

# Closed broad shell, custom rounded extrusion with a rolled shoulder on both faces.
profile('formed_blade_shell',[(-.061,.652,1.132,.086),(-.049,.680,1.160,.100),(.049,.680,1.160,.100),(.061,.652,1.132,.086)],paint)
for sign,label,face_mat in [(1,'positive_x',a),(-1,'negative_x',b)]:
    profile('continuous_trim_'+label,[(sign*x,w,h,r) for x,w,h,r in [(.056,.653,1.133,.087),(.069,.645,1.125,.083),(.074,.630,1.110,.076),(.074,.603,1.083,.062),(.066,.592,1.072,.056),(.052,.592,1.072,.056)]],trim,True)
    profile('dark_reveal_'+label,[(sign*x,.608,1.088,.064) for x in [.052,.064]],seal)
    o=profile('face_'+label,[(sign*.042,.574,1.054,.042),(sign*.067,.580,1.060,.045)],metal,smooth=False)
    o.data.materials.clear();o.data.materials.append(face_mat);o.data.materials.append(metal)
    uv=o.data.uv_layers.new(name='UV0')
    for p in o.data.polygons:
        p.material_index=0 if p.normal.x*sign>.999 else 1
        for li in p.loop_indices:
            v=o.data.vertices[o.data.loops[li].vertex_index].co
            uv.data[li].uv=(.5+sign*(v.y-.54)/.580,.5+v.z/1.060)
    o['artwork_size_m']=[.580,1.060];o['safe_content_m']=[.500,.980]
# Wall plate, twin arms and shaped tapered gussets are a blade-specific assembly.
box('wall_backplate',(0,.015,0),(.200,.030,.960),.012,metal)
for z,label in [(-.36,'lower'),(.36,'upper')]:
    box('cantilever_arm_'+label,(0,.1375,z),(.080,.225,.064),.012,metal)
    # Tapered underside reinforcement meets both arm and plate; no floating hardware.
    pts=[(.026,z-.022),(.235,z-.022),(.235,z-.045),(.050,z-.130),(.026,z-.130)]
    n=len(pts);v=[(x,y,h) for x in [-.026,.026] for y,h in pts]
    f=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
    mesh=bpy.data.meshes.new('gusset_'+label);mesh.from_pydata(v,[],f);mesh.update()
    o=bpy.data.objects.new('tapered_gusset_'+label,mesh);col.objects.link(o)
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    m=o.modifiers.new('Soft gusset perimeter','BEVEL');m.width=.006;m.segments=3
    bpy.ops.object.modifier_apply(modifier=m.name);finish(o,metal)
for x in [-.065,.065]:
    for z in [-.420,.420]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.016,depth=.012,location=(x,.034,z),rotation=(math.pi/2,0,0))
        o=bpy.context.object;o.name='captive_hex_'+('left' if x<0 else 'right')+('_lower' if z<0 else '_upper')
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        m=o.modifiers.new('Fastener edge','BEVEL');m.width=.002;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name)
        finish(o,trim)
# Only datum marker is the export root. No animations, lamps or collision suffixes.
bpy.ops.mesh.primitive_cube_add(size=1,location=(-.9,.54,0));ref=bpy.context.object;ref.name='authoring_1m_reference'
for c in list(ref.users_collection):c.objects.unlink(ref)
studio.objects.link(ref);ref.hide_render=True;ref.hide_set(True);ref['dimensions_m']=[1.,1.,1.]
s['provenance']='Original Codex Blender-authored blade housing, shaped paired cantilevers and captive fixings; no copied mesh, external texture or district content.'
s['axis_contract']='Blender +Y forward/+Z up -> Godot -Z forward/+Y up'
s['measured_contract']='AABB X [-.100,.100], Y [0,.880], Z [-.580,.580] metres; wall plane Y=0; mount centre origin.'
s['clearance']='Reserved X +/-.20, Y [-.02,.98], Z +/-.68 m. Suggested pivot 3.2m above finished ground, lower edge 2.62m. Shell/route acceptance pending.'
s['geometry']='Closed separate editable components with intentional seated assembly overlap, not hollow engineered hardware. All object transforms applied.'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'art/source/models/environment/city_shop_fittings_08/city_shop_fittings_08.blend'))
print('AUTHOR_COMPLETE',len(col.objects),'export members')
