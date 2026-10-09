"""Original broad fascia, authored in Blender; helper pattern follows sign support tooling."""
import bpy, bmesh, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).parent));sys.dont_write_bytecode=True
import export
export.verify_pin()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections): bpy.data.collections.remove(c)
bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
col=bpy.data.collections.new('export_city_shop_fittings_02');scene.collection.children.link(col)
root=bpy.data.objects.new('city_shop_fittings_02',None);col.objects.link(root)
root['asset_id']='city_shop_fittings.02'
root['interface']='Wall Y=0; +Y out; +Z up. 3.2 x .8 x .14 m; no wall recess.'
root['artwork']='fascia_artwork_carrier slot 0 fascia_artwork_face; UV0 left-to-right / bottom-to-top viewed from +Y'

def material(name,hexcolor,metal,rough):
    rgb=[int(hexcolor[i:i+2],16)/255 for i in (0,2,4)]
    rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*rgb,1)
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    return m
paint=material('fascia_slate_petrol','405B68',.25,.46)
trim=material('fascia_warm_trim','C8C2AD',.22,.48)
seal=material('fascia_recess','23333B',0,.72)
face=material('fascia_artwork_face','C3C7BC',0,.56)
mount=material('fascia_mount_metal','384850',.45,.5)

def outline(w,h,r):
    pts=[]
    for cx,cz,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
        for i in range(7):
            a=math.radians(start+90*i/6);pts.append((cx+r*math.cos(a),cz+r*math.sin(a)))
    return pts

def rings(name,profiles,mat,closed_ring=True):
    n=28;verts=[(x,y,z) for w,h,r,y in profiles for x,z in outline(w,h,r)];faces=[]
    for j in range(len(profiles)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    if closed_ring:
        for i in range(n):faces.append(((len(profiles)-1)*n+i,(len(profiles)-1)*n+(i+1)%n,(i+1)%n,i))
    else:faces.extend([tuple(reversed(range(n))),tuple((len(profiles)-1)*n+i for i in range(n))])
    mesh=bpy.data.meshes.new(name+'_mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
    obj=bpy.data.objects.new(name,mesh);col.objects.link(obj);obj.parent=root;mesh.materials.append(mat)
    return obj

def finish(o):
    for p in o.data.polygons:p.use_smooth=True
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    m=o.modifiers.new('Manufactured weighted highlights','WEIGHTED_NORMAL');m.keep_sharp=True;m.weight=50
    bpy.ops.object.modifier_apply(modifier=m.name);o.select_set(False)

def block(name,size,centre,bevel,mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    for c in list(o.users_collection):c.objects.unlink(o)
    col.objects.link(o);o.parent=root;o.data.materials.append(mat)
    m=o.modifiers.new('Soft formed edge','BEVEL');m.width=bevel;m.segments=3
    bpy.ops.object.modifier_apply(modifier=m.name);finish(o);return o

# Broad folded perimeter with a continuous quiet trim band; not four intersecting bars.
body=rings('formed_fascia_frame',[(3.17,.77,.04,.036),(3.20,.80,.055,.053),(3.20,.80,.055,.112),(3.178,.778,.044,.134),(3.10,.70,.032,.134),(3.072,.672,.024,.116),(3.072,.672,.024,.036)],paint)
finish(body)
lip=rings('continuous_face_trim',[(3.118,.718,.041,.126),(3.112,.712,.038,.140),(3.052,.652,.025,.140),(3.032,.632,.019,.127),(3.032,.632,.019,.115),(3.118,.718,.041,.115)],trim)
finish(lip)
back=rings('folded_back_tray',[(3.132,.732,.030,.028),(3.148,.748,.038,.036),(3.148,.748,.038,.073)],paint,False);finish(back)
gasket=rings('artwork_reveal',[(3.047,.647,.024,.116),(3.047,.647,.024,.129),(3.006,.606,.013,.129),(3.006,.606,.013,.116)],seal);finish(gasket)
carrier=rings('fascia_artwork_carrier',[(2.994,.594,.009,.070),(3.0,.60,.012,.122),(3.0,.60,.012,.128)],mount,False)
carrier.data.materials.clear();carrier.data.materials.append(face);carrier.data.materials.append(mount)
uv=carrier.data.uv_layers.new(name='UV0')
for p in carrier.data.polygons:
    p.material_index=0 if p.normal.y>.999 else 1
    for li in p.loop_indices:
        v=carrier.data.vertices[carrier.data.loops[li].vertex_index].co
        uv.data[li].uv=(.5-v.x/3.0,.5+v.z/.60)
for z,label in [(-.24,'lower'),(.24,'upper')]:
    block('wall_mount_rail_'+label,(2.88,.045,.085),(0,.0225,z),.006,mount)
# Retained exact one-metre source reference, hidden and never selected for export.
refcol=bpy.data.collections.new('authoring_excluded');scene.collection.children.link(refcol)
bpy.ops.mesh.primitive_cube_add(size=1,location=(-2.5,0,0));ref=bpy.context.object;ref.name='authoring_1m_reference'
for c in list(ref.users_collection):c.objects.unlink(ref)
refcol.objects.link(ref);ref.hide_render=True;ref.hide_set(True)
ref['purpose']='Exact 1 metre comparison only; excluded from all exports'
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.update()
source=ROOT/'art/source/models/environment/city_shop_fittings_02/city_shop_fittings_02.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source))
export.perform(ROOT/'art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb',ROOT/'docs/assets/production/city_shop_fittings_02-evidence/source_checks.json')
