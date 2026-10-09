"""Unsaved Cycles studio and original shell-aperture jig for upper-floor mounting."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_07-evidence'
s=bpy.context.scene;studio=bpy.data.collections['authoring_excluded'];root=bpy.data.objects['city_shop_fittings_07']
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.18,.23,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
for name,loc,power,size in [('key',(-3,4,6),1100,5),('fill',(5,3,3),550,4),('rim',(0,-3,4),650,3)]:
    d=bpy.data.lights.new('STUDIO_'+name,'AREA');d.energy=power;d.shape='DISK';d.size=size
    o=bpy.data.objects.new('STUDIO_'+name,d);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.8))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('STUDIO_camera');cam=bpy.data.objects.new('STUDIO_camera',d);studio.objects.link(cam);s.camera=cam
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
views=[]
def render(name,loc,target,lens=50,res=(1400,900)):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.type='PERSP';d.lens=lens
    s.render.resolution_x,s.render.resolution_y=res;s.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True)
    views.append(dict(file=name+'.png',location_blender_m=list(loc),target_blender_m=list(target),lens_mm=lens,resolution=res))
render('hero',(3.8,8.0,3.0),(0,0,.8),55)
render('rear_attachment',(-3.6,-7.5,2.5),(0,0,.8),50)
ref=bpy.data.objects['authoring_1m_reference'];ref.hide_set(False);ref.hide_render=False
render('measured_1m_comparison',(1,10,3.7),(-.7,0,.8),48)
ref.hide_render=True;ref.hide_set(True)
wall=bpy.data.materials.new('STUDIO_shell');wall.diffuse_color=(.32,.285,.235,1)
def block(name,size,loc):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name='STUDIO_'+name;o.dimensions=size;o.data.materials.append(wall)
    for c in list(o.users_collection):c.objects.unlink(o)
    studio.objects.link(o)
# Removable fitting in an explicit hole, rather than laid across a solid wall.
root.location.z=4.65
block('left_pier',(.86,.30,7),(-2.77,-.15,3.5))
block('right_pier',(.86,.30,7),(2.77,-.15,3.5))
block('below_opening',(4.68,.30,4.71),(0,-.15,2.355))
block('above_opening',(4.68,.30,.81),(0,-.15,6.595))
render('mounting_detail',(4.5,7.8,7.1),(0,0,5.45),55)
ref.hide_set(False);ref.hide_render=False;ref.location=(-4,0,.5)
render('upper_floor_scale',(7,13,9),(0,0,3.5),48)
ref.hide_render=True;ref.hide_set(True)
d.sensor_fit='VERTICAL';d.sensor_height=32
render('project_camera',(0,10,47),(0,10,0),16/math.tan(math.radians(42)/2),(1280,800))
fov=math.degrees(2*math.atan(max(abs(v.y/v.z) for v in d.view_frame(scene=s))))
assert abs(fov-42)<.001 and all(abs(v)<1e-6 for v in cam.rotation_euler)
(E/'preview_checks.json').write_text(json.dumps(dict(scope='Blender calibration only; no Godot acceptance',reference_dimensions_m=list(ref.dimensions),width_to_reference_ratio=4.8,height_to_reference_ratio=1.6,attachment_pivot_m=list(root.location),shell_opening_blender=dict(x=[-2.34,2.34],y=[-.30,0],z=[4.71,6.19]),shell='Original temporary 6.4 x 7 m aperture wall jig; no roof/room, not an accepted shell',project_camera=dict(height_m=47,vertical_fov_degrees=fov,rotation=list(cam.rotation_euler)),views=views,renderer='Cycles CPU, 4 threads, 32 samples, AgX',source_saved=False),indent=2)+'\n');print('PREVIEWS_COMPLETE')
