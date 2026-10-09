"""Decode GLB positions and include declared node translations in model-space AABBs."""
import json,struct
from pathlib import Path
R=Path('/tmp/six-asset-review-390377d');O=Path(__file__).resolve().parent
ids=['city_lights_01','city_lights_02','city_lights_04','city_sign_supports_01','city_planting_01','city_planting_02'];rows=[]
expected={
'city_lights_01':[[-.36,0,-1.4],[.36,6.2,.21]],'city_lights_02':[[-.36,0,-.36],[.36,3,.36]],'city_lights_04':[[-.32,-.23,-.71],[.32,.305,0]],'city_sign_supports_01':[[-.7,-.5,-.1],[.7,.5,0]],'city_planting_01':[[-1.2,0,-.45],[1.2,.6,.45]],'city_planting_02':[[-.9,0,-.9],[.9,.48,.9]]}
for aid in ids:
 for path in sorted((R/'art/models/environment'/aid).glob('*.glb')):
  b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);start=20+n;bn=struct.unpack_from('<I',b,start)[0];buf=b[start+8:start+8+bn];points=[];nodes=[]
  def visit(i,parent):
   obj=d['nodes'][i];assert 'matrix' not in obj and obj.get('rotation',[0,0,0,1])==[0,0,0,1] and obj.get('scale',[1,1,1])==[1,1,1]
   pos=[a+c for a,c in zip(parent,obj.get('translation',[0,0,0]))];nodes.append(dict(name=obj['name'],translation=pos))
   if 'mesh' in obj:
    for pr in d['meshes'][obj['mesh']]['primitives']:
     a=d['accessors'][pr['attributes']['POSITION']];v=d['bufferViews'][a['bufferView']];assert a['componentType']==5126 and a['type']=='VEC3';at=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12)
     points.extend([[x+y for x,y in zip(struct.unpack_from('<fff',buf,at+j*stride),pos)] for j in range(a['count'])])
   for child in obj.get('children',[]):visit(child,pos)
  for i in d['scenes'][d.get('scene',0)]['nodes']:visit(i,[0,0,0])
  bounds=[[min(p[k] for p in points) for k in range(3)],[max(p[k] for p in points) for k in range(3)]];error=max(abs(x-y) for bx,by in zip(bounds,expected[aid]) for x,y in zip(bx,by));assert error<=.001
  rows.append(dict(asset=aid,path=str(path.relative_to(R)),bounds_model_godot=bounds,max_contract_deviation_m=error,node_transforms=nodes))
(O/'independent-model-bounds.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
