"""Render owned scratch assembly; studios and fitting geometry never enter shell source/export."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_small_shop_shells_01-evidence'
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=32
s.render.threads_mode='FIXED'; s.render.threads=4
s.render.resolution_x=1280; s.render.resolution_y=800; s.render.resolution_percentage=100
s.view_settings.view_transform='AgX'; s.render.image_settings.file_format='PNG'
s.world.use_nodes=True; s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.40,.48,.60,1)
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
mat=bpy.data.materials.new('preview_ground_only'); mat.diffuse_color=(.18,.20,.22,1); mat.use_nodes=True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.18,.20,.22,1)
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.035)); floor=bpy.context.object; floor.name='preview_ground_excluded'; floor.data.materials.append(mat)
for name,pos,power,size in [('key',(4,9,18),2800,10),('fill',(-12,3,11),1800,9),('roof',(1,-12,15),2400,8)]:
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    o=bpy.data.objects.new(name,data); s.collection.objects.link(o); o.location=pos; o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
camdata=bpy.data.cameras.new('preview_camera'); cam=bpy.data.objects.new('preview_camera',camdata); s.collection.objects.link(cam); s.camera=cam
shell=set(bpy.data.collections['export_city_small_shop_shells_01'].objects)
fittings=[o for o in s.objects if o.type=='MESH' and o not in shell and o.name!='authoring_1m_reference' and o!=floor]
ref=bpy.data.objects['authoring_1m_reference']; records=[]
def render(name,pos,target,lens=45,assembled=False,reference=False,project=False):
    for o in fittings: o.hide_render=not assembled
    ref.hide_render=not reference; ref.hide_set(not reference)
    cam.location=pos; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); camdata.type='PERSP'; camdata.lens=lens
    if project:
        cam.rotation_euler=(0,0,0); camdata.sensor_fit='VERTICAL'; camdata.sensor_height=24
        camdata.lens=24/(2*math.tan(math.radians(42)/2))
    else: camdata.sensor_fit='AUTO'
    s.render.filepath=str(E/(name+'.png')); bpy.ops.render.render(write_still=True)
    records.append({'file':name+'.png','position':list(pos),'rotation_radians':list(cam.rotation_euler),'lens_mm':camdata.lens,'sensor_fit':camdata.sensor_fit,'assembled':assembled,'reference_visible':reference,'vertical_fov_degrees':42 if project else None})
render('hero',(16,23,16),(0,0,2.2),46)
render('mounted_hero',(16,23,16),(0,0,2.2),46,True)
render('mounted_frontage',(5,21,7),(0,6.9,2.5),52,True)
render('rear_roof',(-13,-22,15),(0,-1,2.3),46)
render('measured_1m_comparison',(12,24,13),(-.7,1,2),46,False,True)
render('project_camera',(0,9,47),(0,9,0),assembled=True,project=True)
(E/'preview_checks.json').write_text(json.dumps({'renderer':'Cycles CPU 32 samples, four threads, AgX','resolution':[1280,800],'views':records,'reference_measured_dimensions_m':list(ref.dimensions),'scope':'Blender calibrated preview only; no native Godot gameplay-camera acceptance'},indent=2)+'\n')
print('PREVIEWS_COMPLETE')
