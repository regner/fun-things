"""Original broad three-light upper-storey fitting, constructed in private Blender."""
from pathlib import Path
import bpy, bmesh, math
import io_scene_gltf2
R=Path(__file__).resolve().parents[3]
assert bpy.app.version[:3]==(5,2,2) and bpy.app.build_hash.decode()=='d13f752e3b9c'
assert io_scene_gltf2.bl_info['version']==(5,2,40)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):bpy.data.collections.remove(c)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new('export_city_shop_fittings_07');s.collection.children.link(col)
root=bpy.data.objects.new('city_shop_fittings_07',None);col.objects.link(root)
root['datum']='Lower centre at facade plane. Metres. Blender +Y front, +Z up.'
root['rough_opening_xz_m']=[4.68,1.48];root['rough_opening_bottom_z_m']=.06
root['suggested_pivot_above_ground_m']=4.65

def material(name,hexcolor,metal,rough):
    rgb=[int(hexcolor[k:k+2],16)/255 for k in (0,2,4)]
    rgba=tuple(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in rgb)+(1,)
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=rgba;m.use_backface_culling=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rgba
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    return m
paint=material('upper_slate_petrol','405B68',.25,.46)
trim=material('upper_warm_ivory','C8C2AD',.22,.48)
seal=material('upper_dark_gasket','23333B',0,.72)
glass=material('upper_opaque_tint','345D64',.18,.28)
metal=material('upper_satin_sill','929D9F',.65,.38)

def mesh(name,vertices,faces,mat,bevel=0):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update()
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    o=bpy.data.objects.new(name,data);col.objects.link(o);o.parent=root;data.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    if bevel:
        mod=o.modifiers.new('Soft folded edges','BEVEL');mod.width=bevel;mod.segments=3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    for p in data.polygons:p.use_smooth=True
    mod=o.modifiers.new('Broad face normals','WEIGHTED_NORMAL');mod.keep_sharp=True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    o.select_set(False);return o

def loop(width,height,radius):
    result=[]
    for x,z,a in [(1,1,0),(-1,1,90),(-1,-1,180),(1,-1,270)]:
        for i in range(5):
            ang=math.radians(a+i*22.5)
            result.append((x*(width/2-radius)+radius*math.cos(ang),z*(height/2-radius)+radius*math.sin(ang)))
    return result

def profiled(name,sections,mat,x=0,z=.8,solid=False):
    verts=[(px+x,y,pz+z) for w,h,r,y in sections for px,pz in loop(w,h,r)]
    n=20;faces=[]
    for k in range(len(sections)-1):
        for i in range(n):
            j=(i+1)%n;faces.append((k*n+i,k*n+j,(k+1)*n+j,(k+1)*n+i))
    if solid:
        faces.extend([tuple(reversed(range(n))),tuple((len(sections)-1)*n+i for i in range(n))])
    else:
        faces.extend(((len(sections)-1)*n+i,(len(sections)-1)*n+(i+1)%n,(i+1)%n,i) for i in range(n))
    return mesh(name,verts,faces,mat)

# Eight connected profile loops form the shallow sleeve, covering flange and rebate.
profiled('continuous_window_frame',[(4.64,1.44,.025,-.16),(4.64,1.44,.025,.01),
    (4.80,1.60,.055,.01),(4.80,1.60,.055,.054),(4.784,1.584,.047,.074),
    (4.56,1.36,.03,.074),(4.54,1.34,.024,.052),(4.54,1.34,.024,-.16)],paint)
# Narrow warm bead follows the glazing edge, leaving the broad outer frame quiet.
profiled('inner_ivory_bead',[(4.594,1.394,.035,.066),(4.584,1.384,.030,.081),
    (4.548,1.348,.025,.081),(4.538,1.338,.020,.056)],trim)
# Deliberately unequal 1:2:1 rhythm, no transoms and no micro-grid.
for name,x,w in [('left',-1.725,1.07),('centre',0,2.25),('right',1.725,1.07)]:
    profiled(name+'_glazing_seal',[(w+.04,1.35,.023,-.065),(w+.04,1.35,.023,.048),
        (w-.022,1.288,.017,.048),(w-.034,1.276,.014,.028),(w-.034,1.276,.014,-.065)],seal,x=x)
    profiled(name+'_opaque_pane',[(w,1.31,.018,-.074),(w,1.31,.018,.024)],glass,x=x,solid=True)
for name,x in [('left',-1.15),('right',1.15)]:
    profiled(name+'_meeting_stile',[(.086,1.37,.014,-.13),(.086,1.37,.014,.052),
        (.070,1.354,.008,.074)],paint,x=x,solid=True)
# Shallow folded drip shoe belongs to the removable fitting, not shell masonry trim.
section=[(.010,0),(.150,0),(.150,.026),(.127,.045),(.032,.063),(.010,.063)]
n=len(section);verts=[(x,y,z) for x in (-2.4,2.4) for y,z in section]
faces=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]
faces.extend((i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n))
mesh('folded_drip_shoe',verts,faces,metal,.002)
studio=bpy.data.collections.new('authoring_excluded');s.collection.children.link(studio)
bpy.ops.mesh.primitive_cube_add(size=1,location=(-3.25,0,.5));ref=bpy.context.object;ref.name='authoring_1m_reference'
for c in list(ref.users_collection):c.objects.unlink(ref)
studio.objects.link(ref);ref.data.materials.append(trim);ref.hide_render=True;ref.hide_set(True)
s['provenance']='Original city_shop_fittings.07 Blender geometry. No imported source meshes or textures.'
s['scope']='Static upper-floor three-light window. Shell owns opening and structural trim. No collision or interiors.'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'art/source/models/environment/city_shop_fittings_07/city_shop_fittings_07.blend'))
print('AUTHOR_COMPLETE')
