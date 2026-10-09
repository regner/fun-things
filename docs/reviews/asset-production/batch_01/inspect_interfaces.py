"""Bounded follow-up measures interfaces and locates exported shading anomaly."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/tmp/six-asset-review-390377d');O=Path(__file__).resolve().parent
results={}
def load(aid):
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/source/models/environment'/aid/(aid+'.blend')));bpy.context.view_layer.update()
load('city_lights_02');neck=bpy.data.objects['lantern_neck'].data;neck.calc_loop_triangles();shield=bpy.data.objects['lower_shield'].data
verts=[v.co.copy() for v in shield.vertices];polys=[list(p.vertices) for p in shield.polygons];bvh=BVHTree.FromPolygons(verts,polys)
rows=[]
for t in neck.loop_triangles:
 a,b,c=[neck.vertices[i].co for i in t.vertices];n=(b-a).cross(c-a).normalized();dots=[n.dot(neck.corner_normals[i].vector) for i in t.loops]
 if min(dots)<-1e-6:
  centre=(a+b+c)/3;hit=bvh.ray_cast(centre,Vector((0,0,1)),100);inside=bool(hit[0]) and hit[1].dot(Vector((0,0,1)))>0
  rows.append(dict(triangle_vertices=list(t.vertices),polygon=t.polygon_index,coordinates=[list(a),list(b),list(c)],normal_dots=dots,centroid_inside_shield=inside))
results['neck_negative_normals']=rows
results['neck_anomaly_summary']=dict(affected_triangles=len(rows),affected_polygons=sorted(set(r['polygon'] for r in rows)),all_centroids_inside_shield=all(r['centroid_inside_shield'] for r in rows),minimum_dot=min(min(r['normal_dots']) for r in rows),z_range=[min(v[2] for r in rows for v in r['coordinates']),max(v[2] for r in rows for v in r['coordinates'])])
load('city_planting_02')
meshes=[o.data for o in bpy.data.collections['export_city_planting_02'].objects if o.type=='MESH']
# Radial polygon edge distance (rather than vertex radius) measures narrowest opening.
radii=[]
for m in meshes:
 for e in m.edges:
  a,b=[m.vertices[i].co for i in e.vertices]
  if abs(a.z-b.z)<1e-6 and abs(a.xy.length-.62)<1e-5 and abs(b.xy.length-.62)<1e-5:
   u=Vector((a.x,a.y));v=Vector((b.x,b.y));d=v-u;t=max(0,min(1,-u.dot(d)/d.length_squared));radii.append((u+t*d).length)
results['round_clearance']=dict(narrowest_horizontal_inscribed_radius=min(radii),narrowest_diameter=2*min(radii),root_radius_limit=.60,radial_margin=min(radii)-.60)
load('city_planting_01');m=bpy.data.objects['separate_recessed_soil_insert'].data;top=max(v.co.z for v in m.vertices)
results['rectangular_soil']=dict(top_y_godot=top,bounds_blender=[[min(v.co[i] for v in m.vertices) for i in range(3)],[max(v.co[i] for v in m.vertices) for i in range(3)]])
load('city_lights_04');o=bpy.data.objects['reference_one_metre'];results['wall_light_reference']=dict(empty_display_type=o.empty_display_type,empty_display_size=o.empty_display_size,scale=list(o.scale),dimensions=list(o.dimensions))
load('city_sign_supports_01');m=bpy.data.objects['artwork_carrier'].data
results['sign_face']=dict(slots=[x.name for x in m.materials],faces=[dict(index=p.index,material=p.material_index,normal=list(p.normal),vertices=len(p.vertices),centre=list(p.center)) for p in m.polygons if p.material_index==0])
(O/'independent-interface-check.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps({k:v for k,v in results.items() if k!='neck_negative_normals'},indent=2))
