"""Original city_lights.01 construction; run with pinned Blender in background mode."""
import bpy, bmesh, math, json
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / 'docs/assets/production/city_lights_01-evidence'
SOURCE = ROOT / 'art/source/models/environment/city_lights_01/city_lights_01.blend'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new('export_city_lights_01')
scene.collection.children.link(collection)

def material(name, rgb, metal=0, rough=.45, emission=0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*rgb, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    p.inputs['Emission Color'].default_value = (*rgb, 1)
    p.inputs['Emission Strength'].default_value = emission
    m.diffuse_color = (*rgb, 1)
    return m

petrol = material('pole_petrol', (.025,.075,.09), .45, .46)
trim = material('fixture_rim', (.07,.13,.15), .50, .42)
recess = material('service_recess', (.012,.025,.03), .25, .5)
warm = material('lens_warm', (.95,.69,.32), .0, .32, .45)
cool = material('lens_cool', (.46,.78,.92), .0, .32, .45)
cool.use_fake_user = True
parts = []

def finish(obj, name, mat, bevel=0):
    obj.name = name
    for c in list(obj.users_collection): c.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=0.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    for p in obj.data.polygons: p.use_smooth = True
    mod = obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    mod.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.select_set(False)
    parts.append(obj)
    return obj

def box(name, loc, dims, mat, bevel):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.dimensions = dims
    return finish(obj,name,mat,bevel)

def lathe(name, rings, mat):
    count = 20
    verts = [(r*math.cos(i*2*math.pi/count),r*math.sin(i*2*math.pi/count),z)
             for z,r in rings for i in range(count)]
    faces = [tuple(reversed(range(count)))]
    for j in range(len(rings)-1):
        for i in range(count):
            a=j*count+i; b=j*count+(i+1)%count
            faces.append((a,b,b+count,a+count))
    faces.append(tuple(range((len(rings)-1)*count,len(rings)*count)))
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); collection.objects.link(obj)
    return finish(obj,name,mat,.008)

lathe('Tapered pole',[(.12,.135),(.40,.135),(.55,.102),(5.45,.066)],petrol)
lathe('Cast base shoe',[(0,.21),(.045,.21),(.075,.19),(.27,.175),(.32,.145)],petrol)
lathe('Base collar',[(.27,.177),(.32,.177)],trim)
box('Service hatch',(0,.125,.65),(.105,.025,.28),recess,.019)
box('Hatch inset',(0,.141,.65),(.079,.013,.244),petrol,.015)
# Swept arm: circular sections follow a gentle right-angle bend, never a box strut.
path=[(0,5.45,.066),(0,5.60,.066),(.025,5.73,.065),(.085,5.84,.063),
      (.18,5.92,.06),(.30,5.96,.058)]
verts=[]; faces=[]; n=16
for j,(y,z,r) in enumerate(path):
    prev=Vector((0,*path[max(0,j-1)][:2])); nex=Vector((0,*path[min(len(path)-1,j+1)][:2]))
    tangent=(nex-prev).normalized(); across=Vector((1,0,0)); other=tangent.cross(across)
    for i in range(n):
        v=Vector((0,y,z))+r*(math.cos(i*2*math.pi/n)*across+math.sin(i*2*math.pi/n)*other)
        verts.append(tuple(v))
for j in range(len(path)-1):
    for i in range(n): faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
faces += [tuple(reversed(range(n))),tuple(range((len(path)-1)*n,len(path)*n))]
mesh=bpy.data.meshes.new('Swept arm'); mesh.from_pydata(verts,[],faces); mesh.update()
obj=bpy.data.objects.new('Swept arm',mesh); collection.objects.link(obj); finish(obj,'Swept arm',petrol)
# Broad rounded head, stacked shell and recessed luminous underside.
box('Lower housing',(0,.72,6.025),(.72,1.36,.15),trim,.10)
box('Upper canopy',(0,.69,6.115),(.67,1.25,.17),petrol,.08)
box('Lens gasket',(0,.90,5.953),(.60,.99,.032),recess,.075)
lens=box('Broad lens',(0,.90,5.941),(.53,.90,.038),warm,.065)
# Join static subparts into one draw object, with ground-centred root/pivot.
bpy.ops.object.select_all(action='DESELECT')
for obj in parts: obj.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
obj=bpy.context.object; obj.name='CityLights01_Mesh'
scene.cursor.location=(0,0,0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
root=bpy.data.objects.new('CityLights01',None); collection.objects.link(root); obj.parent=root
root['asset_id']='city_lights.01'
root['front_axis']='Blender +Y maps to Godot -Z'
root['authorship']='Original Blender geometry authored by Codex, commissioned 2026-10-09'
root['ground_pivot']='Pole base centre at (0,0,0); lamp projects +Y'
# Studio stays outside export collection.
world=scene.world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.19,.24,.29,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.5
bpy.ops.mesh.primitive_plane_add(size=200)
ground=bpy.context.object; ground.name='STUDIO_ground'; ground.location.z=-.015
ground.data.materials.append(material('STUDIO_slate',(.15,.19,.22),0,.65))

def aim(obj, target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def light(name,loc,power,size):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj); obj.location=loc; aim(obj,(0,0,3))
light('STUDIO_key',(4,4,9),1600,7)
light('STUDIO_rim',(-4,-3,7),1900,5)
light('STUDIO_fill',(1,5,3),450,4)
data=bpy.data.cameras.new('STUDIO_camera'); camera=bpy.data.objects.new('STUDIO_camera',data)
scene.collection.objects.link(camera); scene.camera=camera
scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
# Save editable source before exports; never save temporary cool variant over warm source.
camera.location=(9,12,8); aim(camera,(0,.3,3.05)); data.type='ORTHO'; data.ortho_scale=7.3
scene.render.resolution_x=720; scene.render.resolution_y=900
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent/'export.py').read_text(),str(Path(__file__).parent/'export.py'),'exec'))
for name,loc,target,scale in [
    ('hero',(9,12,8),(0,.3,3.05),7.3),
    ('side', (10,0,4),(0,.5,3.05),7.3),
    ('lens_detail',(2.5,3.5,3.9),(0,.68,5.99),2.15)]:
    camera.location=loc; aim(camera,target); data.ortho_scale=scale
    scene.render.filepath=str(EVIDENCE/(name+'.png')); bpy.ops.render.render(write_still=True)
# Calibrated Blender-only provisional gameplay camera, no engine acceptance implied.
camera.location=(0,0,47); camera.rotation_euler=(0,0,0); data.type='PERSP'
data.sensor_fit='VERTICAL'; data.angle=math.radians(42)
scene.render.resolution_x=1280; scene.render.resolution_y=800
scene.render.filepath=str(EVIDENCE/'overhead_47m_42deg.png'); bpy.ops.render.render(write_still=True)
