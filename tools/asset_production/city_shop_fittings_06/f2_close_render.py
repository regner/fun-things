"""Fresh unsaved CLI renders of the frozen source, with literal camera calibration."""
import bpy
import json
from mathutils import Vector
from pathlib import Path

import sys
OUT=Path(sys.argv[sys.argv.index('--')+1]);OUT.mkdir(parents=True,exist_ok=True)
FROZEN=Path('/tmp/batch03-independent/frozen')
receipt=[]
def studio():
    s=bpy.context.scene
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32
    s.render.threads_mode='FIXED';s.render.threads=4
    s.render.resolution_percentage=100
    s.world=bpy.data.worlds.new('review_world');s.world.use_nodes=True
    s.world.node_tree.nodes['Background'].inputs[0].default_value=(.25,.30,.36,1)
    s.world.node_tree.nodes['Background'].inputs[1].default_value=.55
    s.view_settings.view_transform='AgX'
    for name,location,power,size in [('review_key',(4,11,13),1800,8),('review_fill',(-8,2,8),1100,7)]:
        d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
        o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=location
        o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
    d=bpy.data.cameras.new('review_camera');o=bpy.data.objects.new('review_camera',d)
    s.collection.objects.link(o);s.camera=o
    return s,o
def render(label,s,cam,location,target,scale=None,native=False):
    cam.location=location
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.resolution_x=1280 if native else 800;s.render.resolution_y=800
    if scale:cam.data.type='ORTHO';cam.data.ortho_scale=scale
    else:
        cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=32
        import math
        cam.data.lens=32/(2*math.tan(math.radians(42)/2))
    path=OUT/(label+'.png');s.render.filepath=str(path)
    receipt.append(dict(label=label,source=bpy.data.filepath,location=list(cam.location),rotation=list(cam.rotation_euler),projection=cam.data.type,ortho_scale=scale,vertical_fov_degrees=42 if not scale else None,resolution=[s.render.resolution_x,s.render.resolution_y],renderer='Cycles CPU',threads=4,samples=32,view_transform='AgX',image=str(path)))
    bpy.ops.render.render(write_still=True)

for o in bpy.data.objects:
    o.hide_render=not o.name.startswith(('city_shop_fittings_06_single','single_'))
s,cam=studio()
render('door_front_inner_bevel',s,cam,(-.38,-.1,.31),(-.427,-.432,.270),.035)
render('door_rear_inner_bevel',s,cam,(-.38,-.8,.31),(-.427,-.473,.270),.035)

(OUT/'render-readback.json').write_text(json.dumps(receipt,indent=2)+'\n')
