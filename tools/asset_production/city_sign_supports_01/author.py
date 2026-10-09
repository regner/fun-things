"""Original Blender authoring for city_sign_supports.01; no imported geometry/artwork."""
import bpy, bmesh, math, sys
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
import export
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for col in list(bpy.data.collections): bpy.data.collections.remove(col)
bpy.context.preferences.filepaths.save_version = 0
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'; scene.unit_settings.scale_length = 1
col = bpy.data.collections.new('export_city_sign_supports_01'); scene.collection.children.link(col)
root = bpy.data.objects.new('CitySignSupports01', None); col.objects.link(root)
root['asset_id'] = 'city_sign_supports.01'
root['mounting_datum'] = 'Blender Y=0 wall; front +Y; pivot at panel centre on wall'
root['artwork_interface'] = 'artwork_carrier slot 0 sign_face; UV0 front-view left-to-right, bottom-to-top'

def material(name, rgb, metal, rough):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    # Palette inputs are sRGB; store linear base colour.
    rgb = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    mat.diffuse_color = (*rgb, 1)
    bs = mat.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value = (*rgb, 1)
    bs.inputs['Metallic'].default_value = metal; bs.inputs['Roughness'].default_value = rough
    return mat
paint = material('support_petrol', (.105,.205,.232), .18, .32)
seal = material('recess_gasket', (.043,.075,.087), 0, .72)
metal = material('mount_metal', (.31,.39,.41), .65, .38)
face = material('sign_face', (.66,.70,.67), 0, .56)

# Rings follow CCW in X/Z; bmesh recalculates outward closed-solid winding.
def outline(width, height, radius):
    points=[]
    for cx,cz,start in [(width/2-radius,height/2-radius,0),(-width/2+radius,height/2-radius,90),(-width/2+radius,-height/2+radius,180),(width/2-radius,-height/2+radius,270)]:
        for i in range(9):
            angle=math.radians(start+90*i/8)
            points.append((cx+radius*math.cos(angle),cz+radius*math.sin(angle)))
    return points

def mesh_object(name, verts, faces, mats):
    mesh=bpy.data.meshes.new(name+'_mesh'); mesh.from_pydata(verts, [], faces); mesh.update()
    bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(mesh); bm.free()
    obj=bpy.data.objects.new(name,mesh); col.objects.link(obj); obj.parent=root
    for mat in mats: mesh.materials.append(mat)
    return obj

def rings(name, profiles, mat, close=True):
    verts=[(x,y,z) for w,h,r,y in profiles for x,z in outline(w,h,r)]
    count=36; faces=[]
    for j in range(len(profiles)-1):
        for i in range(count): faces.append((j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i))
    if close:
        for i in range(count): faces.append(((len(profiles)-1)*count+i,(len(profiles)-1)*count+(i+1)%count,(i+1)%count,i))
    else: faces += [tuple(reversed(range(count))),tuple((len(profiles)-1)*count+i for i in range(count))]
    obj=mesh_object(name,verts,faces,[mat]); return obj

def finish(obj):
    for p in obj.data.polygons: p.use_smooth=True
    bpy.context.view_layer.objects.active=obj; obj.select_set(True)
    mod=obj.modifiers.new('Broad weighted highlights','WEIGHTED_NORMAL'); mod.keep_sharp=True; mod.weight=50
    bpy.ops.object.modifier_apply(modifier=mod.name); obj.select_set(False)

def block(name, size, centre, bevel, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=centre)
    obj=bpy.context.object; obj.name=name; obj.dimensions=size
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj); obj.parent=root; obj.data.materials.append(mat)
    mod=obj.modifiers.new('Soft machined edge','BEVEL'); mod.width=bevel; mod.segments=3
    bpy.ops.object.modifier_apply(modifier=mod.name); finish(obj); return obj

frame=rings('rounded_frame',[(1.37,.97,.075,.030),(1.40,1.00,.090,.047),(1.40,1.00,.090,.082),(1.366,.966,.073,.100),(1.26,.86,.055,.100),(1.24,.84,.045,.084),(1.24,.84,.045,.030)],paint)
finish(frame)
back=rings('rear_shell',[(1.338,.938,.065,.025),(1.354,.954,.073,.033),(1.354,.954,.073,.064)],paint,False); finish(back)
gasket=rings('face_gasket',[(1.253,.853,.047,.072),(1.253,.853,.047,.083),(1.214,.814,.033,.083),(1.214,.814,.033,.072)],seal); finish(gasket)
carrier=rings('artwork_carrier',[(1.214,.814,.037,.078),(1.220,.820,.040,.083),(1.220,.820,.040,.088)],metal,False)
carrier.data.materials.clear(); carrier.data.materials.append(face); carrier.data.materials.append(metal)
uv=carrier.data.uv_layers.new(name='UVMap')
for p in carrier.data.polygons:
    front = p.normal.y > .999
    p.material_index=0 if front else 1
    p.use_smooth=False
    for li in p.loop_indices:
        v=carrier.data.vertices[carrier.data.loops[li].vertex_index].co
        uv.data[li].uv=((.610-v.x)/1.220,(v.z+.410)/.820)
for z,label in [(-.28,'lower'),(.28,'upper')]:
    block('mount_rail_'+label,(1.10,.022,.10),(0,.020,z),.007,metal)
    for x,side in [(-.46,'left'),(.46,'right')]:
        block('wall_pad_'+label+'_'+side,(.13,.012,.085),(x,.006,z),.005,seal)
# Two recessed bottom-edge release tabs, no arbitrary decorative copy.
for x,label in [(-.38,'left'),(.38,'right')]:
    block('release_tab_'+label,(.075,.018,.009),(x,.063,-.494),.003,metal)
# Explicitly declared members, no studio objects at author/export time.
bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.update()
source=ROOT/'art/source/models/environment/city_sign_supports_01/city_sign_supports_01.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source))
export.perform(ROOT/'art/models/environment/city_sign_supports_01/city_sign_supports_01.glb', ROOT/'docs/assets/production/city_sign_supports_01-evidence/source_checks.json')
print('CITY_SIGN_SUPPORTS_01_COMPLETE',flush=True)
