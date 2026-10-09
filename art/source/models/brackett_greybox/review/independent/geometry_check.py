import sys,json,struct,math,importlib.util,re
from pathlib import Path
sys.path.insert(0,'/tmp/brackett-greybox/python')
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union
from shapely.affinity import rotate,translate
root=Path.cwd(); source=root/'art/source/models/brackett_greybox';plan=json.loads((source/'authoring_plan.json').read_text());editor=json.loads((root/'tools/brackett_greybox/editor_input.json').read_text())
spec=importlib.util.spec_from_file_location('streets',root/'docs/concepts/world-v1/stage-04-streets/draw_plan.py'); streets=importlib.util.module_from_spec(spec);spec.loader.exec_module(streets)
land=Polygon(streets.LAND).difference(Polygon(streets.WATER));bridge=LineString(next(r['points'] for r in streets.roads() if r['name']=='Harbour bridge')).buffer(8.5,cap_style='flat');ground=land.union(bridge)
roads=[];corridors=[]
for road in streets.roads():
 w,c,*_=streets.TYPES[road['kind']];roads.append(LineString(road['points']).buffer(w/2,quad_segs=6));corridors.append(LineString(road['points']).buffer(c/2,quad_segs=6))
 if road['dead']:
  radius=15 if road['kind']=='freight' else 10;roads.append(Point(road['points'][-1]).buffer(radius,quad_segs=12));corridors.append(Point(road['points'][-1]).buffer(radius+2,quad_segs=12))
road_area=unary_union(roads).intersection(ground);corridor=unary_union(corridors).intersection(ground);foot=unary_union([LineString(p).buffer(1,quad_segs=4) for p in streets.foot_links(streets.roads())]);walk=corridor.union(foot).difference(road_area).intersection(ground)
def glb(path):
 data=path.read_bytes();jlen=struct.unpack_from('<I',data,12)[0];d=json.loads(data[20:20+jlen]);binary=data[28+jlen:];return d,binary
formats={5123:'H',5125:'I',5126:'f'};sizes={'SCALAR':1,'VEC3':3,'VEC2':2,'VEC4':4}
def access(d,b,index):
 a=d['accessors'][index];v=d['bufferViews'][a['bufferView']];n=sizes[a['type']];fmt='<'+formats[a['componentType']]*n;stride=v.get('byteStride',struct.calcsize(fmt));start=v.get('byteOffset',0)+a.get('byteOffset',0);return [struct.unpack_from(fmt,b,start+i*stride) for i in range(a['count'])]
actual={k:[] for k in ('land','road','walk','field')}
for path in (root/'art/models/brackett_greybox').glob('ground*.glb'):
 d,b=glb(path)
 for node in d['nodes']:
  if 'mesh' not in node:continue
  mesh=d['meshes'][node['mesh']];name=node['name']; assert name in actual,name
  for prim in mesh['primitives']:
   vertices=access(d,b,prim['attributes']['POSITION']);indices=[i[0] for i in access(d,b,prim['indices'])];offset=node.get('translation',[0,0,0]);assert node.get('scale',[1,1,1])==[1,1,1]; assert 'rotation' not in node
   for i in range(0,len(indices),3):
    pts=[vertices[v] for v in indices[i:i+3]]
    if name=='land' and any(abs(p[1]+offset[1])>.0001 for p in pts):continue
    shape=Polygon([(p[0]+offset[0]+630,p[2]+offset[2]+355) for p in pts]);assert shape.area>0
    actual[name].append(shape)
for name,expected in [('land',ground),('road',road_area),('walk',walk)]:
 rendered=unary_union(actual[name]);error=expected.symmetric_difference(rendered).area;print(name,'expected_area',round(expected.area,3),'actual_area',round(rendered.area,3),'symmetric_error_m2',round(error,5));distance=expected.hausdorff_distance(rendered);print(name,'boundary_hausdorff_m',distance);buffered_error=expected.difference(rendered.buffer(.001)).area+rendered.difference(expected.buffer(.001)).area;print(name,'outside_1mm_tolerance_m2',buffered_error);assert error<.2 and buffered_error<.002,(name,error,buffered_error)
# Validate actual saved instance positions/yaws, rather than relying on the catalogue IDs.
assets={a['asset_id']:a for a in editor['kit']};districts={d['id']:Polygon(d['points']) for d in streets.BOUNDARIES};footprints=[]
for item in plan['placements']:
 scene=(root/f'scenes/world/brackett_greybox/sectors/district_{item["district_id"]:02d}.tscn').read_text();block=next(b for b in scene.split('\n[node ') if f'name="{item["world_id"].split("/")[-1]}"' in b)
 nums=[float(v.strip()) for v in re.search(r'Transform3D\(([^)]+)\)',block)[1].split(',')];assert all(abs(a-b)<.0001 for a,b in zip(nums[-3:],item['position'])),item
 angle=-math.degrees(math.atan2(-nums[2],nums[0]));assert abs(angle-item['yaw_degrees'])<.001 or abs(abs(angle-item['yaw_degrees'])-360)<.001,(angle,item)
 a=assets[item['asset_id']];shape=translate(rotate(box(-a['width']/2,-a['depth']/2,a['width']/2,a['depth']/2),-item['yaw_degrees']),nums[9]+630,nums[11]+355)
 assert shape.difference(districts[item['district_id']]).area<.00001,item;assert shape.difference(land).area<.00001,item;assert shape.intersection(corridor).area<.00001,item;assert shape.intersection(foot).area<.00001,item
 footprints.append(shape)
assert all(a.intersection(b).area<.00001 for i,a in enumerate(footprints) for b in footprints[i+1:])
print('All290 saved transforms/footprints match plan; district/land containment, road/foot-link and neighbour nonoverlap pass')
for a in editor['kit']:
 d,b=glb(root/'art/models/brackett_greybox'/f'{a["asset_id"]}.glb');points=[]
 for node in d['nodes']:
  if 'mesh' not in node:continue
  offset=node.get('translation',[0,0,0]);assert 'rotation' not in node;assert node.get('scale',[1,1,1])==[1,1,1]
  for prim in d['meshes'][node['mesh']]['primitives']:points.extend(tuple(v[i]+offset[i] for i in range(3)) for v in access(d,b,prim['attributes']['POSITION']))
 bounds=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)];assert all(abs(x-y)<.01 for x,y in zip(bounds,[a['width'],a['height'],a['depth']])),a;assert abs(min(p[1] for p in points))<.01
print('All27 GLB actual vertex bounds/datum satisfy published metre dimensions independently')
