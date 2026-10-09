"""Unsaved Blender studio evidence; source/export remain blank and unchanged."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_08-evidence'
s=bpy.context.scene;studio=bpy.data.collections['authoring_excluded'];root=bpy.data.objects['city_shop_fittings_08']
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.18,.23,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
for name,loc,power,size in [('key',(3,2,4),450,4),('fill',(-3,3,2),350,3),('rim',(0,-3,4),500,3)]:
    d=bpy.data.lights.new('STUDIO_'+name,'AREA');d.energy=power;d.shape='DISK';d.size=size
    o=bpy.data.objects.new('STUDIO_'+name,d);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,.4,0))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('STUDIO_camera');cam=bpy.data.objects.new('STUDIO_camera',d);studio.objects.link(cam);s.camera=cam
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
views=[]
def render(name,loc,target,lens=50,res=(1400,1000),ortho=None):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO' if ortho else 'PERSP';d.lens=lens
    if ortho:d.ortho_scale=ortho
    s.render.resolution_x,s.render.resolution_y=res;s.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True)
    views.append(dict(file=name+'.png',location_blender_m=list(loc),target_blender_m=list(target),lens_mm=lens,orthographic_scale=ortho,resolution=res,rotation_radians=list(cam.rotation_euler)))
render('hero',(2.5,2.8,1.2),(0,.42,0),58)
render('bracket_detail',(2,-1.9,1.15),(0,.24,0),65)
render('source_elevation',(3,.44,0),(0,.44,0),ortho=1.85)
ref=bpy.data.objects['authoring_1m_reference'];ref.hide_set(False);ref.hide_render=False;ref.location=(0,1.62,0)
render('measured_1m_comparison',(4,1.1,1.5),(0,1.1,0),60)
ref.hide_set(True);ref.hide_render=True
image=bpy.data.images.load(str(E/'uv_chart.png'))
for label in ['positive_x','negative_x']:
    mat=bpy.data.materials['blade_artwork_'+label];n=mat.node_tree.nodes.new('ShaderNodeTexImage');n.image=image;n.extension='EXTEND'
    mat.node_tree.links.new(n.outputs['Color'],mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
render('uv_positive_x',(3,.44,0),(0,.44,0),res=(1000,1000),ortho=1.50)
render('uv_negative_x',(-3,.44,0),(0,.44,0),res=(1000,1000),ortho=1.50)
for label in ['positive_x','negative_x']:
    mat=bpy.data.materials['blade_artwork_'+label]
    for n in list(mat.node_tree.nodes):
        if n.type=='TEX_IMAGE':mat.node_tree.nodes.remove(n)
# A simple dimensional wall/ground jig; no copied shell and no saved world writes.
wallmat=bpy.data.materials.new('STUDIO_wall');wallmat.diffuse_color=(.29,.25,.24,1)
def block(name,size,loc):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name='STUDIO_'+name;o.dimensions=size;o.data.materials.append(wallmat)
    for c in list(o.users_collection):c.objects.unlink(o)
    studio.objects.link(o)
block('wall',(2.8,.2,4.4),(0,-.1,2.2));block('ground',(3.6,2.8,.04),(0,.9,-.02))
root.location.z=3.2
for o in studio.objects:
    if o.type=='LIGHT':o.location.z+=3.2
render('mounting_preview',(4.5,5.5,4.5),(0,.25,2.25),52)
d.sensor_fit='VERTICAL';d.sensor_height=32
render('project_camera',(0,10,47),(0,10,0),16/math.tan(math.radians(42)/2),(1280,800))
fov=math.degrees(2*math.atan(max(abs(v.y/v.z) for v in d.view_frame(scene=s))))
assert abs(fov-42)<.001 and all(abs(v)<1e-6 for v in cam.rotation_euler)
(E/'preview_checks.json').write_text(json.dumps(dict(scope='Blender source previews only, not engine or independent art acceptance',reference_dimensions_m=list(ref.dimensions),sign_body_height_to_1m=1.16,sign_projection_to_1m=.88,attachment_pivot_m=list(root.location),lowest_geometry_above_jig_ground_m=2.62,wall_plane_y=0,wall_size_m=[2.8,.2,4.4],source_saved=False,diagnostic_chart='uv_chart.png, scratch material only, not source or GLB',project_camera=dict(height_m=47,vertical_fov_degrees=fov,fixed_yaw_radians=0),views=views,renderer='Cycles CPU / 4 threads / 32 samples / AgX'),indent=2)+'\n')
print('PREVIEWS_COMPLETE')
