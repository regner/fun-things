"""Original two-light display window; editable manufactured profiles in pinned Blender."""
import bpy, bmesh, math
from pathlib import Path
import io_scene_gltf2
R=Path(__file__).resolve().parents[3]
assert bpy.app.version[:3]==(5,2,2) and bpy.app.build_hash.decode()=='d13f752e3b9c'
assert io_scene_gltf2.bl_info['version']==(5,2,40)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):bpy.data.collections.remove(c)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
col=bpy.data.collections.new('export_city_shop_fittings_05');s.collection.children.link(col)
root=bpy.data.objects.new('city_shop_fittings_05',None);col.objects.link(root)
root['datum']='Bottom centre at wall plane; metres; +Y front +Z up'
root['rough_opening_xz_m']=[3.04,1.88];root['rough_opening_bottom_z_m']=.04
root['suggested_pivot_above_floor_m']=.48

def material(name,swatch,metal,rough):
    rgb=[int(swatch[i:i+2],16)/255 for i in (0,2,4)]
    rgba=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=rgba;m.use_backface_culling=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rgba
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    return m
paint=material('window_slate_petrol','405B68',.25,.46)
trim=material('window_warm_ivory','C8C2AD',.22,.48)
seal=material('window_dark_gasket','23333B',0,.72)
glass=material('window_opaque_tint','345D64',.18,.24)
sill=material('window_satin_sill','929D9F',.65,.38)

def finish(name,verts,faces,mat,bevel=0):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);col.objects.link(o);o.parent=root;me.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    if bevel:
        m=o.modifiers.new('Soft manufactured edge','BEVEL');m.width=bevel;m.segments=3
        bpy.ops.object.modifier_apply(modifier=m.name)
    for f in me.polygons:f.use_smooth=True
    m=o.modifiers.new('Broad highlight normals','WEIGHTED_NORMAL');m.keep_sharp=True
    bpy.ops.object.modifier_apply(modifier=m.name);o.select_set(False)
    return o

def outline(w,h,r):
    pts=[]
    for cx,cz,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
        for i in range(5):
            a=math.radians(start+90*i/4);pts.append((cx+r*math.cos(a),cz+r*math.sin(a)))
    return pts

def ring(name,profiles,mat,cx=0,cz=1,closed=True):
    n=20;vs=[(x+cx,y,z+cz) for w,h,r,y in profiles for x,z in outline(w,h,r)];fs=[]
    for k in range(len(profiles)-1):
        fs.extend((k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for i in range(n))
    if closed:
        fs.extend(((len(profiles)-1)*n+i,(len(profiles)-1)*n+(i+1)%n,(i+1)%n,i) for i in range(n))
    else:fs.extend([tuple(reversed(range(n))),tuple((len(profiles)-1)*n+i for i in range(n))])
    return finish(name,vs,fs,mat)

# Insertion sleeve fits shell aperture; face flange covers the installation gap.
ring('formed_perimeter',[(3.00,1.84,.022,-.18),(3.00,1.84,.022,.012),(3.20,2.0,.055,.012),(3.20,2.0,.055,.066),(3.178,1.978,.044,.09),(2.96,1.76,.03,.09),(2.94,1.74,.024,.07),(2.94,1.74,.024,-.18)],paint)
ring('ivory_perimeter_inlay',[(3.158,1.958,.039,.084),(3.15,1.95,.035,.099),(3.11,1.91,.028,.099),(3.10,1.90,.023,.084)],trim)
# Only one vertical mullion. Each broad pane seats into its own gasket.
for x,label in [(-.75,'left'),(.75,'right')]:
    ring(label+'_glazing_gasket',[(1.49,1.76,.025,-.032),(1.49,1.76,.025,.061),(1.41,1.68,.018,.061),(1.40,1.67,.014,.045),(1.40,1.67,.014,-.032)],seal,cx=x)
    ring(label+'_opaque_glazing',[(1.438,1.708,.018,-.04),(1.438,1.708,.018,.035)],glass,cx=x,closed=False)
# Extruded rounded rectangular mullion, deep enough to sit between the opaque units.
ring('centre_mullion',[(.076,1.78,.018,-.12),(.076,1.78,.018,.075),(.060,1.764,.010,.09)],paint,closed=False)
# Custom sloped sill, folded nose and rear heel, full width without fine drainage grooves.
profile=[(-.18,0),(.22,0),(.22,.035),(.19,.055),(.05,.085),(-.18,.085)]
n=len(profile);vs=[(x,y,z) for x in (-1.6,1.6) for y,z in profile]
fs=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]
fs.extend((i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n))
finish('sloped_sill',vs,fs,sill,.003)
studio=bpy.data.collections.new('authoring_excluded');s.collection.children.link(studio)
bpy.ops.mesh.primitive_cube_add(size=1,location=(-2.6,0,.5));ref=bpy.context.object;ref.name='authoring_1m_reference'
for c in list(ref.users_collection):c.objects.unlink(ref)
studio.objects.link(ref);ref.data.materials.append(trim);ref.hide_render=True;ref.hide_set(True)
s['provenance']='Original Blender meshes authored for city_shop_fittings.05; no external geometry or textures.'
s['scope']='Static opaque display window fitting; shell owns wall opening, no interior or window mechanics.'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'art/source/models/environment/city_shop_fittings_05/city_shop_fittings_05.blend'))
print('AUTHOR_COMPLETE')
