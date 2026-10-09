"""Unsaved studio and dimensioned shell-aperture assembly; no production scene writes."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_05-evidence'
s=bpy.context.scene;studio=bpy.data.collections['authoring_excluded'];root=bpy.data.objects['city_shop_fittings_05']
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.18,.23,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
for name,loc,energy,size in [('key',(-3,4,5),950,4),('fill',(4,3,2),450,3),('rim',(0,-3,4),650,3)]:
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('STUDIO_camera');cam=bpy.data.objects.new('STUDIO_camera',d);studio.objects.link(cam);s.camera=cam
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
views=[]
def render(name,loc,target,lens=50,res=(1400,1000)):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.type='PERSP';d.lens=lens
    s.render.resolution_x,s.render.resolution_y=res;s.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True)
    views.append(dict(file=name+'.png',location_blender_m=list(loc),target_blender_m=list(target),lens_mm=lens,resolution=res))
render('hero',(3.4,6.0,3.0),(0,0,1),55)
render('rear_attachment',(-3,-5,2.6),(0,0,1),50)
ref=bpy.data.objects['authoring_1m_reference'];ref.hide_set(False);ref.hide_render=False
render('measured_1m_comparison',(1,8.5,3.5),(-.7,0,.9),48)
ref.hide_render=True;ref.hide_set(True)
# Demonstration shell owns the rough opening. No borrowed shell mesh is modified.
# Its four simple blocks are original Blender-authored evidence only, never saved/exported.
wall=bpy.data.materials.new('STUDIO_shell');wall.diffuse_color=(.34,.30,.25,1)
def block(name,size,loc):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name='STUDIO_'+name;o.dimensions=size;o.data.materials.append(wall)
    for c in list(o.users_collection):c.objects.unlink(o)
    studio.objects.link(o)
# root at .48 floor height; opening x +-1.52, z .54..2.42
root.location.z=.48
block('wall_left',(.88,.30,3.2),(-1.96,-.15,1.6))
block('wall_right',(.88,.30,3.2),(1.96,-.15,1.6))
block('wall_below',(3.04,.30,.54),(0,-.15,.27))
block('wall_above',(3.04,.30,.78),(0,-.15,2.81))
render('attachment_opening',(4.6,6.5,3.7),(0,0,1.5),52)
d.sensor_fit='VERTICAL';d.sensor_height=32
render('project_camera',(0,12,47),(0,12,0),16/math.tan(math.radians(42)/2),(1280,800))
fov=math.degrees(2*math.atan(max(abs(v.y/v.z) for v in d.view_frame(scene=s))))
assert abs(fov-42)<.001 and all(abs(v)<1e-6 for v in cam.rotation_euler)
(E/'preview_checks.json').write_text(json.dumps(dict(scope='Unsaved Blender calibration only, no engine/gameplay acceptance',reference_dimensions_m=list(ref.dimensions),width_to_reference_ratio=3.2,height_to_reference_ratio=2,attachment_pivot_m=list(root.location),shell_opening_blender=dict(x=[-1.52,1.52],y=[-.30,0],z=[.54,2.42]),shell='Original temporary Blender-authored aperture jig; not production shell or export',project_camera=dict(height_m=47,vertical_fov_degrees=fov,rotation=list(cam.rotation_euler)),views=views,renderer='Cycles CPU, 4 threads, 32 samples, AgX',source_saved=False),indent=2)+'\n')
print('PREVIEWS_COMPLETE')
