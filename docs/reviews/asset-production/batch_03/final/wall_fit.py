import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parent;F=Path('/tmp/batch03-final/frozen');src=F/'art/source/models/spikes/batch_03_upper_wall/batch_03_upper_wall.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));assert bpy.app.version==(5,2,2) and bpy.app.build_hash==b'd13f752e3b9c';assert bpy.context.scene.unit_settings.scale_length==1
col=bpy.data.collections['export_batch_03_upper_wall'];ms=[o for o in col.all_objects if o.type=='MESH'];assert len(ms)==4
vertices=[];faces=[];boxes=[]
for o in ms:
 assert not o.modifiers and list(o.scale)==[1,1,1] and list(o.rotation_euler)==[0,0,0]
 v=[o.matrix_world@p.co for p in o.data.vertices];n=len(vertices);vertices+=v;faces += [tuple(n+i for i in p.vertices) for p in o.data.polygons];boxes.append([[min(p[a] for p in v) for a in range(3)],[max(p[a] for p in v) for a in range(3)]])
bvh=BVHTree.FromPolygons(vertices,faces);rays=[]
for xi in range(19):
 for zi in range(17):
  x=-2.33+xi*4.66/18;z=4.72+zi*1.46/16;hit=bvh.ray_cast(Vector((x,.3,z)),Vector((0,-1,0)),.9);rays.append(hit[0] is None)
assert all(rays)
bpy.ops.object.select_all(action='DESELECT')
for o in col.all_objects:o.select_set(True)
export=O/'reexports/batch_03_upper_wall.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_cameras=False,export_lights=False,export_animations=False)
original=Path('tests/fixtures/asset_production/batch_03_upper_wall/batch_03_upper_wall.glb');identical=export.read_bytes()==original.read_bytes();assert identical
p=F/'art/source/models/environment/city_shop_fittings_07/city_shop_fittings_07.blend';bpy.ops.wm.open_mainfile(filepath=str(p));rear=[]
for o in bpy.data.collections['export_city_shop_fittings_07'].all_objects:
 if o.type=='MESH':rear += [o.matrix_world@v.co+Vector((0,0,4.65)) for v in o.data.vertices if (o.matrix_world@v.co).y<-.00001]
gaps=[min(v.x+2.34,2.34-v.x,v.z-4.71,6.19-v.z) for v in rear];assert len(rear)==260 and min(gaps)>.018
r=dict(source=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),boxes=boxes,through_void_rays=len(rays),all_clear=all(rays),fresh_export_byte_identical=identical,glb_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),rear_vertices=len(rear),minimum_side_head_bottom_gap_m=min(gaps),rear_void_clearance_m=min(v.y+.28 for v in rear),window_top_m=6.25,shell_top_m=5.05,shell_upper_mount_compatible=False)
(O/'wall-fit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
