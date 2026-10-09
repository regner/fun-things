"""Original wall sconce construction; source is editable and owns the export collection."""
import bpy, bmesh, math, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).parent))
import export
assert bpy.app.version[:3]==(5,2,2)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):bpy.data.collections.remove(c)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
col=bpy.data.collections.new('export_city_lights_04');scene.collection.children.link(col)
studio=bpy.data.collections.new('studio_do_not_export');scene.collection.children.link(studio)
root=bpy.data.objects.new('CityLights04',None);col.objects.link(root)
root['interface']='Backplate rear centre; wall Blender Y=0; forward +Y; up +Z; metres'

def material(name,hexcode,metal,rough,emission=0):
    m=bpy.data.materials.new('city_lights_04_'+name);m.use_nodes=True;m.use_fake_user=True
    rgb=[int(hexcode[i:i+2],16)/255 for i in (0,2,4)]
    rgba=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rgba
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    p.inputs['Emission Color'].default_value=rgba;p.inputs['Emission Strength'].default_value=emission
    m.diffuse_color=rgba;return m
metal=material('petrol_metal','193F46',.55,.38)
dark=material('recess_dark','0D1D22',.30,.42)
warm=material('lens_warm','FFDCA3',0,.55,.45)
cool=material('lens_cool','ACDEEF',0,.55,.45)

def finish(obj,name,mat,collection=col):
    obj.name=name
    for c in list(obj.users_collection):c.objects.unlink(obj)
    collection.objects.link(obj);obj.data.materials.clear();obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
    for p in obj.data.polygons:p.use_smooth=True
    if collection==col:obj.parent=root
    obj.select_set(False);return obj

def box(name,loc,dim,bevel,mat,collection=col):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    mod=o.modifiers.new('soft_cast_edges','BEVEL');mod.width=bevel;mod.segments=4
    bpy.ops.object.modifier_apply(modifier=mod.name)
    o=finish(o,name,mat,collection)
    bpy.context.view_layer.objects.active=o
    mod=o.modifiers.new('broad_face_normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50
    bpy.ops.object.modifier_apply(modifier=mod.name);return o

def profile(name,rings,mat,cy=.46,ratio=.78125,n=64):
    # Closed oval lathe: cap ngons avoid coincident pole vertices.
    vertices=[(r*math.cos(2*math.pi*j/n),cy+ratio*r*math.sin(2*math.pi*j/n),z) for z,r in rings for j in range(n)]
    faces=[tuple(reversed(range(n)))]
    for k in range(len(rings)-1):
        for j in range(n):faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
    faces.append(tuple((len(rings)-1)*n+j for j in range(n)))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);col.objects.link(o);return finish(o,name,mat)

box('mounting_backplate',(0,.028,0),(.20,.056,.46),.022,metal)
box('mounting_gasket',(0,.006,0),(.18,.012,.432),.005,dark)
# Two restrained captive fasteners on the exposed backplate face.
for z,label in [(-.171,'lower'),(.171,'upper')]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=(0,.057,z))
    o=bpy.context.object;o.scale=(.017,.006,.017);finish(o,'mount_fastener_'+label,dark)
# Smooth rising cast arm, circular sweep with tangent-consistent rings.
points=[]
a=Vector((0,.043,-.095));b=Vector((0,.20,-.095));c=Vector((0,.22,.105));d=Vector((0,.46,.125))
for i in range(21):
    t=i/20;points.append((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d)
verts=[];faces=[];n=16
for i,p in enumerate(points):
    tangent=(points[min(i+1,20)]-points[max(0,i-1)]).normalized();side=Vector((1,0,0));normal=tangent.cross(side).normalized()
    r=.036-(i/20)*.005
    verts.extend(p+r*(math.cos(j*2*math.pi/n)*side+math.sin(j*2*math.pi/n)*normal) for j in range(n))
faces.append(tuple(reversed(range(n))))
for i in range(20):
    for j in range(n):faces.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
faces.append(tuple(20*n+j for j in range(n)))
mesh=bpy.data.meshes.new('curved_arm');mesh.from_pydata(verts,[],faces);mesh.update()
o=bpy.data.objects.new('curved_arm',mesh);col.objects.link(o);finish(o,'curved_cast_arm',metal)
profile('lower_shield',[(.073,.057),(.081,.12),(.105,.215),(.127,.284),(.137,.291),(.145,.285)],metal)
profile('broad_recessed_diffuser',[(.140,.265),(.148,.28),(.212,.286),(.224,.281)],warm)
profile('canopy_seal',[(.219,.277),(.224,.302),(.234,.303),(.238,.287)],dark)
profile('broad_oval_canopy',[(.231,.294),(.239,.315),(.250,.32),(.265,.313),(.284,.27),(.300,.19),(.305,.095)],metal)
# Saved source uses the warm variant; cool material is retained with a fake user.
scene['producer']='Original Codex Blender modeling for city_lights.04; no third-party assets'
scene['axis_contract']='Blender +Y forward/+Z up -> glTF Godot -Z/+Y'
scene['attachment_plane']='Y=0 rear gasket, root at backplate centre'
# Studio is source-only. One-metre reference is hidden from render and export.
ref=bpy.data.objects.new('reference_one_metre',None);studio.objects.link(ref);ref.empty_display_type='CUBE';ref.empty_display_size=.5
ref.location=(-1,0,0);ref.hide_render=True
wallmat=material('studio_slate','576770',0,.8)
box('studio_wall',(0,-.09,0),(200,.18,200),.001,wallmat,studio)
world=bpy.data.worlds.new('studio_world') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.20,.25,1);world.node_tree.nodes['Background'].inputs[1].default_value=.4
for name,loc,energy,size,color in [('key',(1,2,3),250,3,(.82,.91,1)),('fill',(-2,1,1),170,2,(1,.86,.69)),('rim',(0,.3,2),100,1.5,(.8,1,1))]:
    data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;data.color=color
    obj=bpy.data.objects.new(name,data);studio.objects.link(obj);obj.location=loc;obj.rotation_euler=(Vector((0,.35,.05))-obj.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('studio_camera');camera=bpy.data.objects.new('studio_camera',data);studio.objects.link(camera);scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
source=ROOT/'art/source/models/environment/city_lights_04/city_lights_04.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source))
export.perform(ROOT/'art/models/environment/city_lights_04',export.E/'source_checks.json')

def render(name,loc,target,lens=52,res=(1000,900),cool_variant=False):
    bpy.data.objects['broad_recessed_diffuser'].data.materials[0]=cool if cool_variant else warm
    camera.location=loc;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.type='PERSP';data.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=res
    scene.render.filepath=str(export.E/(name+'.png'));bpy.ops.render.render(write_still=True)
render('hero_warm',(1.1,1.6,.85),(0,.30,.02))
render('detail_underside',(.90,1.50,-.40),(0,.33,.04),60)
render('hero_cool',(-1.1,1.6,.75),(0,.30,.02),cool_variant=True)
# Vertical-down close view isolates footprint; wall excluded to avoid infinite-wall occlusion.
bpy.data.objects['studio_wall'].hide_render=True
render('vertical_down_detail',(0,.36,2.5),(0,.36,0),60)
# Scale context only: fixture root corresponds to mounting height 2.8 m.
data.sensor_fit='VERTICAL';data.sensor_height=32;data.lens=16/math.tan(math.radians(42)/2)
render('vertical_down_47m_42deg',(0,.36,44.2),(0,.36,0),data.lens,(1280,800))
print('CITY_LIGHTS_04_COMPLETE',flush=True)
