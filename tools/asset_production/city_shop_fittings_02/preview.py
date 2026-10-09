"""Unsaved studio, scale and scratch-artwork-interface previews from saved source."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_02-evidence'
s=bpy.context.scene;studio=bpy.data.collections['authoring_excluded'];root=bpy.data.objects['city_shop_fittings_02']
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.21,.25,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
for name,loc,energy,size in [('key',(-2,4,5),850,4),('fill',(4,2,1),450,4),('rim',(0,-3,4),600,3)]:
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('STUDIO_camera');cam=bpy.data.objects.new('STUDIO_camera',d);studio.objects.link(cam);s.camera=cam
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
views=[]
def render(name,loc,target,lens=50,res=(1400,800)):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    d.type='PERSP';d.lens=lens;s.render.resolution_x,s.render.resolution_y=res
    s.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True)
    views.append(dict(file=name+'.png',location_blender_m=list(loc),target_blender_m=list(target),lens_mm=lens,resolution=res))
render('hero',(2.3,5.8,1.5),(0,.07,0),55)
render('rear_mounts',(-2.4,-5.5,1.35),(0,.07,0),55)
ref=bpy.data.objects['authoring_1m_reference'];ref.hide_set(False);ref.hide_render=False
render('measured_1m_comparison',(1.2,8,2.4),(-.65,0,0),50)
ref.hide_render=True;ref.hide_set(True)
carrier=bpy.data.objects['fascia_artwork_carrier'];original=carrier.data.materials[0]
test=original.copy();test.name='STUDIO_original_scratch_UV';carrier.data.materials[0]=test
tex=test.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(E/'uv_diagnostic.png'));tex.extension='EXTEND'
test.node_tree.links.new(tex.outputs['Color'],test.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
render('artwork_interface',(0,5.6,0),(0,.128,0),55)
carrier.data.materials[0]=original
path=R/'art/models/brackett_greybox/shop.glb';h=hashlib.sha256(path.read_bytes()).hexdigest()
before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));imported=set(bpy.data.objects)-before
bpy.context.view_layer.update();coords=[o.matrix_world@v.co for o in imported if o.type=='MESH' for v in o.data.vertices]
lo=[min(v[i] for v in coords) for i in range(3)];hi=[max(v[i] for v in coords) for i in range(3)]
assert all(abs(a-b)<1e-4 for a,b in zip([hi[i]-lo[i] for i in range(3)],[18,15,10]))
root.location=(0,hi[1],3.8)
for o in studio.objects:
    if o.type=='LIGHT':o.hide_render=True
sun=bpy.data.lights.new('STUDIO_daylight','SUN');sun.energy=2;sun.angle=.2
o=bpy.data.objects.new('STUDIO_daylight',sun);studio.objects.link(o);o.rotation_euler=(.45,-.55,-.3)
render('unchanged_shop_scale_comparison',(23,29,17),(0,0,4),48,(1280,900))
d.sensor_fit='VERTICAL';d.sensor_height=32
render('project_camera',(0,12,47),(0,12,0),16/math.tan(math.radians(42)/2),(1280,800))
frame=d.view_frame(scene=s);fov=math.degrees(2*math.atan(max(abs(v.y/v.z) for v in frame)))
assert abs(fov-42)<.001 and all(abs(v)<1e-6 for v in cam.rotation_euler)
assert h==hashlib.sha256(path.read_bytes()).hexdigest()
(E/'preview_checks.json').write_text(json.dumps(dict(scope='Blender calibration only; no engine or placement acceptance',reference=dict(path=str(path.relative_to(R)),sha256_before=h,sha256_after=h,blender_bounds_m=[lo,hi],dimensions_m=[18,15,10],modified=False),fascia_pivot_blender_m=list(root.location),mount_ground_height_m=3.8,lowest_clearance_m=3.4,fascia_to_facade_width_ratio=3.2/18,one_metre_reference_dimensions=list(ref.dimensions),width_to_reference_ratio=3.2,project_camera=dict(height_m=47,vertical_fov_degrees=fov,rotation=list(cam.rotation_euler)),views=views,renderer='Cycles CPU 4 threads, 32 samples, AgX',source_saved=False,diagnostic='Original scratch TL/TR/BL/BR and axis-arrow chart, unsaved material substitution'),indent=2)+'\n')
print('PREVIEWS_COMPLETE')
