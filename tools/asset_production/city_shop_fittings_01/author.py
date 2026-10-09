"""Original short folded shop canopy source; all geometry authored with private Blender."""
import bpy, bmesh, math
from pathlib import Path
from mathutils import Vector
import io_scene_gltf2
R=Path(__file__).resolve().parents[3]
assert bpy.app.version[:3]==(5,2,2) and bpy.app.build_hash.decode()=='d13f752e3b9c'
assert io_scene_gltf2.bl_info['version']==(5,2,40)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections): bpy.data.collections.remove(c)
s=bpy.context.scene; s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1
col=bpy.data.collections.new('export_city_shop_fittings_01'); s.collection.children.link(col)
studio=bpy.data.collections.new('authoring_excluded'); s.collection.children.link(studio)
root=bpy.data.objects.new('city_shop_fittings_01',None); col.objects.link(root)
root['datum']='Wall attachment pivot at rear plane Y=0, mount centre Z=0; +Y front'
root['purpose']='Static shop canopy; no collision or behavior'

def material(name,swatch,metal,rough):
    m=bpy.data.materials.new(name); m.use_nodes=True; m.use_backface_culling=True
    rgb=[int(swatch[i:i+2],16)/255 for i in (0,2,4)]
    rgba=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=rgba
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    m.diffuse_color=rgba; return m
def finish(o,name,mat,collection=col,bevel=0):
    o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    collection.objects.link(o); o.data.materials.clear(); o.data.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    bm=bmesh.new(); bm.from_mesh(o.data); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(o.data); bm.free()
    if bevel:
        mod=o.modifiers.new('rolled_edge','BEVEL'); mod.width=bevel; mod.segments=3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    for f in o.data.polygons: f.use_smooth=True
    mod=o.modifiers.new('restrained_broad_face_normals','WEIGHTED_NORMAL'); mod.keep_sharp=True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    if collection==col: o.parent=root
    o.select_set(False); return o

def mesh(name,verts,faces,mat,bevel=0):
    m=bpy.data.meshes.new(name); m.from_pydata(verts,[],faces); m.update()
    o=bpy.data.objects.new(name,m); col.objects.link(o); return finish(o,name,mat,bevel=bevel)

def box(name,loc,dim,mat,bevel=.02,collection=col):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.dimensions=dim
    return finish(o,name,mat,collection,bevel)

paint=material('canopy_slate_petrol','405B68',.25,.46)
edge=material('canopy_warm_ivory_rim','C8C2AD',.22,.48)
mount=material('canopy_dark_mounts','293B43',.35,.55)
def profile(name,x0,x1,points,mat,bevel):
    n=len(points); verts=[(x,y,z) for x in (x0,x1) for y,z in points]
    faces=[tuple(reversed(range(n))),tuple(n+j for j in range(n))]
    faces.extend((j,(j+1)%n,n+(j+1)%n,n+j) for j in range(n))
    return mesh(name,verts,faces,mat,bevel)
# Smooth descending manufactured top with a rolled downturned nose and finite soffit.
profile('formed_canopy',-1.58,1.58,[(.05,.20),(.84,.095),(1.003,.045),
    (1.073,-.015),(1.088,-.045),(1.088,-.095),(1.063,-.12),(.978,-.145),(.05,.065)],paint,.018)
# Separate broad rim traces the nose; neutral trim leaves tenant graphics to fascia .02.
profile('rolled_front_rim',-1.6,1.6,[(1.082,-.025),(1.10,-.045),(1.10,-.095),
    (1.075,-.135),(.99,-.16),(.985,-.12),(1.043,-.102),(1.058,-.058)],edge,.006)
box('wall_mount_rail',(0,.035,0),(3.04,.07,.48),mount,.014)
# Two tapered cantilever gussets meet the mounting rail and underside, no ground legs.
parts=[]
for x in (-1.15,1.15):
    parts.append(profile('gusset',x-.055,x+.055,[(.055,.075),(.85,-.05),
        (.81,-.115),(.19,-.37),(.07,-.42),(.055,-.42)],mount,.012))
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]; bpy.ops.object.join(); parts[0].name='paired_tapered_gussets'
bpy.ops.object.select_all(action='DESELECT')
ref=box('authoring_1m_reference',(-2.4,.5,.08),(1,1,1),edge,0,studio)
ref.hide_render=True; ref.hide_set(True); ref['measured_dimensions_m']=[1.,1.,1.]
s['provenance']='Original Codex Blender geometry for city_shop_fittings.01; no external mesh or textures.'
s['axis_contract']='Blender +Y front/+Z up -> Godot -Z front/+Y up'
s['interface']='Wall plane Blender Y=0; mount centre Z=0. Recommended pivot 3.0 m above ground, lowest point 2.58 m. Flat facade only.'
s['tolerance']='AABB +/-0.001m; wall-plane placement +/-0.002m; reserve 3.4m width x 1.2m projection x 0.86m height.'
s['geometry_note']='Closed separately editable manufactured components; intentional rail, gusset and rim assembly overlaps.'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'art/source/models/environment/city_shop_fittings_01/city_shop_fittings_01.blend'))
print('AUTHOR_COMPLETE')
