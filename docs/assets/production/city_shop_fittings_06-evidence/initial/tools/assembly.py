"""Read-only .03 source and GLB mating, actual geometry probes and scratch assembly."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_shop_fittings_06-evidence'
paths=[R/'art/source/models/environment/city_shop_fittings_03/city_shop_fittings_03.blend']+[R/('art/models/environment/city_shop_fittings_03/city_shop_fittings_03_'+v+'.glb') for v in ('single','double')]
hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
def bounds(o):
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
def tree(o):
    return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
def hit(o,p,d):
    loc,n,i,dist=tree(o).ray_cast(Vector(p),Vector(d)); assert loc is not None,(o.name,p,d)
    return list(loc)
def near(a,b): assert abs(a-b)<.00001,(a,b)
def inspect(variant,mode):
    bpy.context.view_layer.update()
    w=1.04 if variant=='single' else 1.84
    reveal=bpy.data.objects[variant+'_recessed_reveal']; sill=bpy.data.objects[variant+'_sloped_threshold']; stop=bpy.data.objects[variant+'_rear_stop']
    frames=[bpy.data.objects[variant+'_'+n] for n in ['recessed_reveal','rounded_face_casing','rear_stop','sloped_threshold']]
    intervals=[(-.512,.512)] if variant=='single' else [(-.912,-.004),(.004,.912)]
    leaves=[]; objs=[]
    for i,(a,b) in enumerate(intervals,1):
        prefix=variant+'_leaf_'+str(i); ring=bpy.data.objects[prefix+'_stiles_rails']; glass=bpy.data.objects[prefix+'_glazing']; pull=bpy.data.objects[prefix+'_static_pull']
        objs.extend([ring,glass,pull]); lo,hi=bounds(ring)
        for x,y in zip(lo,[a,-.475,.030]): near(x,y)
        for x,y in zip(hi,[b,-.430,2.232]): near(x,y)
        hlo,hhi=bounds(pull); assert hlo[0]>=a and hhi[0]<=b and hlo[2]>=.030 and hhi[2]<=2.232 and hhi[1]<=-.330
        # Cast from the actual gap into each saved surface, at broad planar regions.
        side=[]
        for y in [-.468,-.4525,-.437]:
            for z in [.10,1.6,2.18]:
                edge=a if i==1 else b; direction=-1 if i==1 else 1
                p=(edge+direction*.004,y,z)
                door=hit(ring,p,(-direction,0,0))[0]; frame=hit(reveal,p,(direction,0,0))[0]
                gap=abs(frame-door); near(gap,.008); side.append(dict(y=y,z=z,door_x=door,frame_x=frame,gap_m=gap))
        x=(a+b)/2
        head=hit(reveal,(x,-.4525,2.236),(0,0,1))[2]-hit(ring,(x,-.4525,2.236),(0,0,-1))[2]
        bottom=hit(ring,(x,-.4525,.025),(0,0,1))[2]-hit(sill,(x,-.4525,.025),(0,0,-1))[2]
        edge=a+.005 if i==1 else b-.005
        rear=hit(ring,(edge,-.478,1.6),(0,1,0))[1]-hit(stop,(edge,-.478,1.6),(0,-1,0))[1]
        near(head,.008); near(bottom,.010); near(rear,.006)
        leaves.append(dict(name=prefix,body_bounds_blender_m=[lo,hi],hardware_bounds_blender_m=[hlo,hhi],hardware_projection_m=hhi[1]+.430,side_probes=side,head_gap_m=head,bottom_gap_m=bottom,rear_stop_gap_m=rear))
    meeting=[]
    if variant=='double':
        for y in [-.468,-.4525,-.437]:
            for z in [.1,1.6,2.18]:
                l=hit(objs[0],(0,y,z),(-1,0,0))[0]; r=hit(objs[3],(0,y,z),(1,0,0))[0]; near(r-l,.008)
                meeting.append(dict(y=y,z=z,left_x=l,right_x=r,gap_m=r-l))
    overlap=[]
    for leaf in objs:
        for frame in frames:
            count=len(tree(leaf).overlap(tree(frame))); assert count==0,(leaf.name,frame.name,count)
            overlap.append(dict(leaf=leaf.name,surround=frame.name,intersecting_triangle_pairs=count))
    return dict(mode=mode,variant=variant,leaves=leaves,meeting_gap_probes=meeting,frame_surface_intersections=overlap,frame_bounds={o.name:bounds(o) for o in frames})
with bpy.data.libraries.load(str(paths[0]),link=False) as (a,b):
    b.collections=['export_city_shop_fittings_03']
bpy.context.scene.collection.children.link(b.collections[0])
reports=[inspect(v,'saved_source') for v in ('single','double')]
# Retain a real, editable scratch assembly. Equal per-variant translation preserves the mating datum.
for variant,x in [('single',-1.55),('double',1.05)]:
    for asset in ['03','06']: bpy.data.objects['city_shop_fittings_'+asset+'_'+variant].location.x=x
bpy.context.scene['scratch_only']='Actual .03/.06 fitted comparison; each pair translated together for viewing; not a game source/export.'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(E/'fitted_comparison.blend'))
# Independently import actual explicit game exports and repeat all mating probes.
for variant in ['single','double']:
    bpy.ops.object.select_all(action='SELECT')
    for o in bpy.context.scene.objects: o.hide_set(False); o.hide_select=False; o.select_set(True)
    bpy.ops.object.delete(use_global=False)
    for asset in ['03','06']:
        bpy.ops.import_scene.gltf(filepath=str(R/('art/models/environment/city_shop_fittings_'+asset+'/city_shop_fittings_'+asset+'_'+variant+'.glb')))
    reports.append(inspect(variant,'imported_glb_assembly'))
for p in paths: assert hashes[str(p.relative_to(R))]==hashlib.sha256(p.read_bytes()).hexdigest()
(E/'assembly_checks.json').write_text(json.dumps(dict(checks=reports,reference_hashes_before=hashes,reference_hashes_after={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},reference_modified=False,scratch='fitted_comparison.blend',scope='Saved source and actual GLB fitted surface/ray checks; no engine collision, shell or runtime acceptance.'),indent=2)+'\n')
print('ACTUAL_SOURCE_AND_GLB_ASSEMBLY_PASS')
