"""Fresh isolated source overview renders; no source saves or rebuilt production geometry."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path('/tmp/six-asset-review-390377d');O=Path(__file__).resolve().parent
ids=['city_lights_01','city_lights_02','city_lights_04','city_sign_supports_01','city_planting_01','city_planting_02']
records=[]
for aid in ids:
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/source/models/environment'/aid/(aid+'.blend')))
 s=bpy.context.scene
 if s.camera is None:
  bpy.ops.object.camera_add(location=(1.65,3.4,1.15));cam=bpy.context.object;s.camera=cam;cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.95
  for loc,energy in [((2,4,3),500),((-3,2,1),200)]:
   bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=energy;light.data.size=3;light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
 if aid=='city_lights_02':
  cam=s.camera;cam.location=(1.8,2.8,3.6);cam.rotation_euler=(Vector((0,0,2.8))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.2
 s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=4
 s.render.resolution_x=800;s.render.resolution_y=600;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(O/(aid+'-fresh-source.png'))
 records.append(dict(asset=aid,source=str((R/'art/source/models/environment'/aid/(aid+'.blend')).relative_to(R)),camera=s.camera.name,position=list(s.camera.location),rotation=list(s.camera.rotation_euler),projection=s.camera.data.type,ortho_scale=s.camera.data.ortho_scale,resolution=[800,600],samples=16,view_transform=s.view_settings.view_transform,scope='Fresh source studio overview, not calibrated gameplay/engine appearance'))
 bpy.ops.render.render(write_still=True)
(O/'fresh-preview-settings.json').write_text(json.dumps(records,indent=2)+'\n');print('FRESH_SOURCE_PREVIEWS_COMPLETE',flush=True)
