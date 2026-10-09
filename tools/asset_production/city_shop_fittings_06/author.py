"""Original static glazed leaves; private Blender authoring, metres and identity roots."""
import bpy, bmesh
from pathlib import Path
import io_scene_gltf2
R=Path(__file__).resolve().parents[3]
assert bpy.app.version[:3]==(5,2,2) and bpy.app.build_hash.decode()=='d13f752e3b9c'
assert io_scene_gltf2.bl_info['version']==(5,2,40)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections): bpy.data.collections.remove(c)
s=bpy.context.scene; s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1
export=bpy.data.collections.new('export_city_shop_fittings_06'); s.collection.children.link(export)
studio=bpy.data.collections.new('authoring_excluded'); s.collection.children.link(studio)
def material(name,hex,metal,rough):
    m=bpy.data.materials.new(name); m.use_nodes=True; m.use_backface_culling=True
    rgb=[int(hex[i:i+2],16)/255 for i in (0,2,4)]
    rgba=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=rgba
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    m.diffuse_color=rgba; return m
paint=material('door_slate_petrol','405B68',.25,.40)
glass=material('door_opaque_tinted_glazing','163D48',.32,.22)
metal=material('door_satin_handle','C8C2AD',.65,.30)
def mesh(name,verts,faces,mat,col,root,bevel):
    d=bpy.data.meshes.new(name); d.from_pydata(verts,[],faces); d.update()
    o=bpy.data.objects.new(name,d); col.objects.link(o); o.parent=root; d.materials.append(mat)
    bm=bmesh.new(); bm.from_mesh(d); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(d); bm.free()
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
    m=o.modifiers.new('soft_manufactured_edges','BEVEL'); m.width=bevel; m.segments=4
    bpy.ops.object.modifier_apply(modifier=m.name)
    for p in d.polygons: p.use_smooth=True
    m=o.modifiers.new('broad_face_normals','WEIGHTED_NORMAL'); m.keep_sharp=True
    bpy.ops.object.modifier_apply(modifier=m.name); return o
def box(name,lo,hi,mat,col,root,bevel):
    verts=[(x,y,z) for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])]
    return mesh(name,verts,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],mat,col,root,bevel)
for variant,intervals in [('single',[(-.512,.512)]),('double',[(-.912,-.004),(.004,.912)])]:
    col=bpy.data.collections.new('variant_'+variant); export.children.link(col)
    root=bpy.data.objects.new('city_shop_fittings_06_'+variant,None); col.objects.link(root)
    root['datum']='Wall-plane/floor identity: +Y street, +Z up; mate .03 Interface v1 without correction'
    for index,(a,b) in enumerate(intervals):
        prefix=variant+'_leaf_'+str(index+1)
        outer=[(a,.030),(b,.030),(b,2.232),(a,2.232)]
        inner=[(a+.085,.270),(b-.085,.270),(b-.085,2.107),(a+.085,2.107)]
        verts=[(x,y,z) for y in (-.475,-.430) for loop in (outer,inner) for x,z in loop]
        faces=[]
        for i in range(4):
            j=(i+1)%4
            faces.extend([(i,j,4+j,4+i),(8+i,12+i,12+j,8+j),(i,8+i,8+j,j),(4+i,4+j,12+j,12+i)])
        mesh(prefix+'_stiles_rails',verts,faces,paint,col,root,.004)
        # Glazing tucks 6 mm behind the leaf ring, hiding seams without a second fixed frame.
        box(prefix+'_glazing',(a+.079,-.467,.264),(b-.079,-.438,2.113),glass,col,root,.003)
        x=b-.043 if index==0 else a+.043
        profile=[(-.434,.920),(-.352,.920),(-.352,1.320),(-.434,1.320),(-.434,1.288),(-.384,1.288),(-.384,.952),(-.434,.952)]
        verts=[(xx,y,z) for xx in (x-.018,x+.018) for y,z in profile]; n=len(profile)
        faces=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]
        faces.extend((i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n))
        mesh(prefix+'_static_pull',verts,faces,metal,col,root,.006)
bpy.ops.mesh.primitive_cube_add(size=1,location=(-2,0,.5)); ref=bpy.context.object; ref.name='authoring_1m_reference'
for c in list(ref.users_collection): c.objects.unlink(ref)
studio.objects.link(ref); ref.data.materials.append(metal); ref.hide_render=True; ref.hide_set(True)
s['provenance']='Original Blender meshes by assigned Codex worker, requested Astra MEDIUM commission; no external model/image/texture input.'
s['scope']='Static closed leaf only: no surround, shell, tenant graphics, interior, lock, working hinge, rig or animation.'
s['axis_contract']='metres; (X,Y,Z) Blender to (X,Z,-Y) Godot; variant roots identity and overlapping by design'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'art/source/models/environment/city_shop_fittings_06/city_shop_fittings_06.blend'))
print('AUTHOR_COMPLETE')
