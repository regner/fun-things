import json,struct,math,sys
from pathlib import Path
root=Path(__file__).parent
report={}
for p in (root/"snapshot/art/models/rocket_launcher").glob("*.glb"):
 raw=p.read_bytes();size,kind=struct.unpack_from("<II",raw,12)
 g=json.loads(raw[20:20+size]);blen,bkind=struct.unpack_from("<II",raw,20+size);binary=raw[28+size:28+size+blen]
 def accessor(i):
  a=g["accessors"][i];v=g["bufferViews"][a["bufferView"]]
  n={"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4}[a["type"]]
  fmt={5126:"f",5125:"I",5123:"H",5121:"B"}[a["componentType"]]
  unit=struct.calcsize(fmt);start=v.get("byteOffset",0)+a.get("byteOffset",0);stride=v.get("byteStride",unit*n)
  return [struct.unpack_from("<"+fmt*n,binary,start+k*stride) for k in range(a["count"])]
 rows=[]
 for node in g["nodes"]:
  if "mesh" not in node:continue
  for prim in g["meshes"][node["mesh"]]["primitives"]:
   pos=accessor(prim["attributes"]["POSITION"]);norm=accessor(prim["attributes"]["NORMAL"])
   idx=[t[0] for t in accessor(prim["indices"])];areas=[]
   for k in range(0,len(idx),3):
    a,b,c=[pos[j] for j in idx[k:k+3]];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
    cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
    areas.append(math.sqrt(sum(t*t for t in cross))/2)
   rows.append({"object":node["name"],"triangles":len(idx)//3,"degenerate_1e-12":sum(a<1e-12 for a in areas),"exact_zero":sum(a==0 for a in areas),"minimum_area_m2":min(areas),"normal_length_min":min(math.sqrt(sum(t*t for t in n)) for n in norm),"normal_length_max":max(math.sqrt(sum(t*t for t in n)) for n in norm),"material":g["materials"][prim["material"]]["name"]})
 report[p.name]={"meshes":rows,"material_definitions":g["materials"],"generator":g["asset"],"extras":any("extras" in n for n in g["nodes"]),"external_dependencies":g.get("images",[]),"nodes":g["nodes"]}
(root/"gltf-inspection.json").write_text(json.dumps(report,indent=2)+"\n")
print("GLB_INSPECTION_COMPLETE",[(file,o["object"],o["exact_zero"]) for file,a in report.items() for o in a["meshes"] if o["exact_zero"]])
