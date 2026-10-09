import subprocess,re,json,math
from pathlib import Path
O=Path(__file__).resolve().parent;C='c4067ff3abe1384301471d9a64e94e84201235e2';path='scenes/prefabs/environment/city_planting_02.tscn';text=subprocess.check_output(['git','show',C+':'+path],text=True)
parts=re.findall(r'\[sub_resource type="ConvexPolygonShape3D" id="([^"]+)"\]\npoints = PackedVector3Array\(([^)]+)\)',text);assert len(parts)==16
rows=[]
for resource,coords in parts:
 n=[float(x.strip()) for x in coords.split(',')];assert len(n)==24
 vertices=[n[i:i+3] for i in range(0,len(n),3)];heights=sorted({v[1] for v in vertices});assert heights==[0,0.48]
 bottom=[v for v in vertices if v[1]==0];radii=[math.hypot(v[0],v[2]) for v in bottom];inner=[v for v,r in zip(bottom,radii) if r<0.7];assert len(inner)==2
 a,b=inner;apothem=abs(a[0]*b[2]-a[2]*b[0])/math.hypot(a[0]-b[0],a[2]-b[2]);assert abs(apothem-0.62)<1e-6
 assert all(abs(r-0.9)<1e-6 for r in radii if r>0.7)
 rows.append(dict(resource=resource,vertices=vertices,inner_apothem_m=apothem,outer_radii_m=[r for r in radii if r>0.7],heights_m=heights))
shapes=re.findall(r'\[node name="Segment(\d+)" type="CollisionShape3D" parent="Collision/Body"[^\]]*\]\nshape = SubResource\("([^"]+)"\)',text);assert len(shapes)==16 and {i for i,r in shapes}=={str(i) for i in range(16)} and {r for i,r in shapes}=={r for r,c in parts}
result=dict(candidate=C,path=path,method='independent saved convex vertex decoding and inner chord distance; no producer construction formula used',sectors=rows,node_shape_links=shapes,max_inner_radius_error_m=max(abs(r['inner_apothem_m']-0.62) for r in rows))
(O/'independent-ring-collision.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS 16 actual saved linked sectors, .62m opening, .9m outer radii, [0,.48]m height; max opening deviation',result['max_inner_radius_error_m'])
