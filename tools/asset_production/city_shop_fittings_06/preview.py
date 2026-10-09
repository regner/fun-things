"""Retained fitted .03/.06 scratch views and excluded measured metre fixture."""
import bpy,math,json
from pathlib import Path
import os
from mathutils import Vector
R=Path(__file__).resolve().parents[3]; E=Path(os.environ.get('ASSET_EVIDENCE_DIR',R/'docs/assets/production/city_shop_fittings_06-evidence'))
s=bpy.context.scene; studio=bpy.data.collections['authoring_excluded']
s.world.use_nodes=True; s.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.20,.26,1); s.world.node_tree.nodes['Background'].inputs[1].default_value=.6
for name,loc,energy,size in [('key',(1,4,6),1000,5),('fill',(-4,2,3),650,4),('rim',(0,-3,5),850,3)]:
    d=bpy.data.lights.new(name,'AREA'); d.energy=energy; d.shape='DISK'; d.size=size
    o=bpy.data.objects.new(name,d); studio.objects.link(o); o.location=loc; o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('preview_camera'); cam=bpy.data.objects.new('preview_camera',d); studio.objects.link(cam); s.camera=cam
s.render.engine='CYCLES'; s.cycles.samples=32; s.cycles.use_denoising=True
s.render.resolution_percentage=100; s.render.image_settings.file_format='PNG'; s.view_settings.view_transform='AgX'; views=[]
def render(name,loc,target,lens=50,res=(1280,900),ortho=None):
    cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    d.type='ORTHO' if ortho else 'PERSP'; d.lens=lens
    if ortho:d.ortho_scale=ortho
    s.render.resolution_x,s.render.resolution_y=res; s.render.filepath=str(E/(name+'.png'))
    bpy.ops.render.render(write_still=True); views.append(dict(file=name+'.png',location=list(loc),target=list(target),lens_mm=lens,ortho_scale=ortho,resolution=res))
render('fitted_hero',(.9,8,3),(0,-.2,1.1),52)
render('fitted_front',(0,8,1.24),(0,0,1.24),ortho=5.35)
render('fitted_rear',(-3,-8,3),(0,-.2,1.15),52)
# Leaf-only hero is the same actual production meshes, surround visibility toggled only in scratch.
surrounds=[bpy.data.objects[v+'_'+n] for v in ['single','double'] for n in ['recessed_reveal','rounded_face_casing','rear_stop','sloped_threshold']]
for o in surrounds:o.hide_render=True
assert all(o.hide_render for o in surrounds)
render('hero',(3,8,3),(0,-.4,1.12),56)
ref=bpy.data.objects['authoring_1m_reference']; ref.hide_render=False; ref.hide_set(False); ref.location=(-3,0,.5)
bpy.context.view_layer.update(); assert all(abs(v-1)<1e-6 for v in ref.dimensions)
render('measured_1m_comparison',(4,10,4),(-.65,-.3,1.05),52)
ref.hide_render=True
for o in surrounds:o.hide_render=False
# Straight-down camera at the project's provisional height and vertical FOV.
d.sensor_fit='VERTICAL'; d.sensor_height=32
render('project_camera',(0,8,47),(0,8,0),16/math.tan(math.radians(42)/2),(1280,800))
frame=d.view_frame(scene=s); fov=math.degrees(2*math.atan(max(abs(v.y/v.z) for v in frame))); assert abs(fov-42)<.001
assert all(abs(v)<1e-6 for v in cam.rotation_euler)
(E/'preview_checks.json').write_text(json.dumps(dict(views=views,metre_reference_dimensions_m=list(ref.dimensions),project_camera_height_m=47,project_vertical_fov_degrees=fov,renderer='Cycles CPU, 4 threads, 32 samples, AgX',scope='Actual source fitted comparison in Blender; isolated fittings, no shell/roof or engine; project view is deliberately at true scale.'),indent=2)+'\n')
print('PREVIEWS_COMPLETE')
