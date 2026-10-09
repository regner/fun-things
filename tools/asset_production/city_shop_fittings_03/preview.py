"""Unsaved review views; references never enter source/export membership."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_shop_fittings_03-evidence'
s=bpy.context.scene; studio=bpy.data.collections['authoring_excluded']
roots=[bpy.data.objects['city_shop_fittings_03_'+v] for v in ('single','double')]
roots[0].location.x=-1.48; roots[1].location.x=.95
s.world.use_nodes=True; s.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.20,.26,1)
s.world.node_tree.nodes['Background'].inputs[1].default_value=.6
for name,loc,energy,size in [('key',(1,4,6),1000,5),('fill',(-4,2,3),650,4),('rim',(0,-3,5),850,3)]:
    d=bpy.data.lights.new(name,'AREA'); d.energy=energy; d.shape='DISK'; d.size=size
    o=bpy.data.objects.new(name,d); studio.objects.link(o); o.location=loc
    o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('preview_camera'); cam=bpy.data.objects.new('preview_camera',d); studio.objects.link(cam); s.camera=cam
s.render.engine='CYCLES'; s.cycles.samples=32; s.cycles.use_denoising=True
s.render.resolution_percentage=100; s.render.image_settings.file_format='PNG'; s.view_settings.view_transform='AgX'
views=[]
def render(name,loc,target,lens=50,res=(1280,900),ortho=None):
    cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    d.type='ORTHO' if ortho else 'PERSP'; d.lens=lens
    if ortho: d.ortho_scale=ortho
    s.render.resolution_x,s.render.resolution_y=res; s.render.filepath=str(E/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    views.append(dict(file=name+'.png',location_blender_m=list(loc),target_blender_m=list(target),lens_mm=lens,ortho_scale=ortho,resolution=res))
render('hero',(4,8,4),(-.15,-.12,1.15),52)
render('rear_interface',(-4,-7,3),(-.15,-.12,1.15),52)
render('front_elevation',(0,8,1.24),(0,0,1.24),res=(1280,850),ortho=5.4)
ref=bpy.data.objects['authoring_1m_reference']; ref.hide_set(False); ref.hide_render=False
ref.location=(-3,0,.5)
render('measured_1m_comparison',(5,11,5),(-.7,0,1.1),52)
ref.hide_render=True
path=R/'art/models/brackett_greybox/shop.glb'; h=hashlib.sha256(path.read_bytes()).hexdigest()
before=set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=str(path)); imported=set(bpy.data.objects)-before
bpy.context.view_layer.update()
coords=[o.matrix_world@v.co for o in imported if o.type=='MESH' for v in o.data.vertices]
lo=[min(v[i] for v in coords) for i in range(3)]; hi=[max(v[i] for v in coords) for i in range(3)]
assert all(abs(a-b)<1e-4 for a,b in zip([hi[i]-lo[i] for i in range(3)],[18,15,10]))
for root in roots: root.location.y=hi[1]+2
for o in studio.objects:
    if o.type=='LIGHT': o.hide_render=True
sun=bpy.data.lights.new('daylight','SUN'); sun.energy=2; sun.angle=.2
light=bpy.data.objects.new('daylight',sun); studio.objects.link(light); light.rotation_euler=(.45,-.55,-.3)
render('unchanged_shop_scale_comparison',(20,29,17),(0,1,4),48,(1280,900))
d.sensor_fit='VERTICAL'; d.sensor_height=32
render('project_camera',(0,14,47),(0,14,0),16/math.tan(math.radians(42)/2),(1280,800))
frame=d.view_frame(scene=s); fov=math.degrees(2*math.atan(max(abs(v.y/v.z) for v in frame)))
assert abs(fov-42)<.001 and all(abs(v)<1e-6 for v in cam.rotation_euler)
assert h==hashlib.sha256(path.read_bytes()).hexdigest()
(E/'preview_checks.json').write_text(json.dumps(dict(scope='Blender-only scale comparison. Existing shop has no compatible opening; surrounds deliberately detached 2m in front, not a mounting/assembly test.',reference=dict(path=str(path.relative_to(R)),sha256_before=h,sha256_after=h,blender_bounds_m=[lo,hi],dimensions_m=[18,15,10],modified=False),surround_pivots_blender_m=[list(o.location) for o in roots],one_metre_reference_dimensions=list(ref.dimensions),height_ratio_to_shop=2.48/10,project_camera=dict(height_m=47,vertical_fov_degrees=fov,rotation=list(cam.rotation_euler)),views=views,renderer='Cycles CPU 4 threads, 32 samples, AgX',source_saved=False),indent=2)+'\n')
print('PREVIEWS_COMPLETE')
