"""Render saved-source evidence; studio and UV diagnostics are never saved/exported."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'docs/assets/production/city_sign_supports_01-evidence'
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=1100;scene.render.resolution_y=850;scene.render.resolution_percentage=100
scene.world.color=(.18,.18,.18)
scene.view_settings.view_transform='AgX'
studio=bpy.data.collections.new('STUDIO_NOT_EXPORTED');scene.collection.children.link(studio)
def put(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    studio.objects.link(obj)
def point(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def light(name,location,power,size,color):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color
    ob=bpy.data.objects.new(name,data);studio.objects.link(ob);ob.location=location;point(ob,(0,0,0))
light('soft_key',(-2.8,3.5,4.5),550,4,(.83,.91,1))
light('warm_fill',(3.5,1.8,1.5),250,3,(1,.85,.67))
light('rim',(-2,-2,2),450,3,(.62,.81,1))
bpy.ops.object.camera_add(location=(1.65,3.4,1.15));camera=bpy.context.object;put(camera);camera.name='STUDIO_camera';scene.camera=camera
camera.data.type='PERSP';camera.data.lens=55
mat=bpy.data.materials.new('STUDIO_wall');mat.diffuse_color=(.14,.20,.23,1)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-.065,0));wall=bpy.context.object;put(wall);wall.name='STUDIO_wall';wall.dimensions=(3.8,.12,3.0);wall.data.materials.append(mat)
views=[]
def render(label,location,target,lens=55):
    camera.location=location;point(camera,target);camera.data.lens=lens
    scene.render.filepath=str(E/(label+'.png'));bpy.ops.render.render(write_still=True)
    views.append(dict(name=label,resolution=[scene.render.resolution_x,scene.render.resolution_y],camera_location=list(camera.location),camera_rotation=list(camera.rotation_euler),lens_mm=camera.data.lens,vertical_fov_degrees=math.degrees(camera.data.angle_y),source='saved .blend; studio-only temporary additions',engine='Blender Cycles CPU',samples=scene.cycles.samples))
render('hero',(1.65,3.4,1.15),(0,.05,0))
render('detail',(.85,1.48,.62),(.34,.075,.20),65)
wall.hide_render=True
render('rear',(-1.6,-3.1,1.15),(0,.03,0))
wall.hide_render=False
# Load an external diagnostic PNG onto sign_face only; no source/export mutation.
carrier=bpy.data.objects['artwork_carrier'];original=carrier.data.materials[0]
test=original.copy();test.name='STUDIO_uv_test';carrier.data.materials[0]=test
image=bpy.data.images.load(str(E/'uv_diagnostic.png'));tex=test.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;tex.extension='EXTEND'
test.node_tree.links.new(tex.outputs['Color'],test.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
render('uv_interface',(0,3.25,0),(0,.088,0),60)
carrier.data.materials[0]=original
# Calibrated source preview: vertical down 47 m above notional ground, off-axis wall.
wall.hide_render=True
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-2,-.1));building=bpy.context.object;put(building);building.name='STUDIO_facade';building.dimensions=(7,4,3);building.data.materials.append(mat)
bpy.ops.mesh.primitive_plane_add(size=150,location=(0,0,-1.6));ground=bpy.context.object;put(ground);ground.name='STUDIO_ground'
ground_mat=bpy.data.materials.new('STUDIO_ground');ground_mat.diffuse_color=(.24,.29,.32,1);ground.data.materials.append(ground_mat)
scene.render.resolution_x=1280;scene.render.resolution_y=800
camera.data.sensor_fit='VERTICAL';camera.data.sensor_height=24
lens=24/(2*math.tan(math.radians(42)/2))
render('gameplay_down',(8,9,45.4),(8,9,-1.6),lens)
(E/'preview_settings.json').write_text(json.dumps(views,indent=2)+'\n')
print('CITY_SIGN_SUPPORTS_01_PREVIEWS_COMPLETE',flush=True)
