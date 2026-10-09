"""Inspect actual unmodified fitting sources and GLBs in a read-only scratch storefront."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_small_shop_shells_01-evidence'
mode=sys.argv[sys.argv.index('--')+1]
assert mode in ['source','glb']
fit={'01':('mount_canopy',''),'02':('mount_fascia',''),'03':('mount_entrance_single','_single'),'05':('mount_display_window',''),'06':('mount_door_single','_single')}
paths=[]
for id in fit:
    paths.extend([R/f'art/source/models/environment/city_shop_fittings_{id}/city_shop_fittings_{id}.blend',R/f'art/models/environment/city_shop_fittings_{id}/city_shop_fittings_{id}{fit[id][1]}.glb',R/f'docs/assets/production/city_shop_fittings_{id}.md'])
hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
def bounds(obs):
    vs=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
    return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
def tree(o):
    o.data.calc_loop_triangles()
    return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.loop_triangles],all_triangles=True)
def hit(obs,p,d,length=100):
    hits=[r for o in obs if (r:=tree(o).ray_cast(Vector(p),Vector(d),length))[0] is not None]
    return min(hits,key=lambda r:r[3])[0] if hits else None
def near(a,b,tol=.00002): assert abs(a-b)<tol,(a,b)
if mode=='glb':
    for o in list(bpy.data.objects): bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(R/'art/models/environment/city_small_shop_shells_01/city_small_shop_shells_01.glb'))
shell=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name!='authoring_1m_reference']
mounts={name:list(bpy.data.objects[name].location) for name,_ in fit.values()}
assemblies={}; roots={}
for id,(marker,suffix) in fit.items():
    before=set(bpy.data.objects)
    if mode=='source':
        with bpy.data.libraries.load(str(R/f'art/source/models/environment/city_shop_fittings_{id}/city_shop_fittings_{id}.blend'),link=False) as (a,b):
            b.collections=['export_city_shop_fittings_'+id]
        bpy.context.scene.collection.children.link(b.collections[0])
        for o in list(set(bpy.data.objects)-before):
            if o.name.startswith('double_') or o.name.endswith('_double'):
                bpy.data.objects.remove(o,do_unlink=True)
    else:
        bpy.ops.import_scene.gltf(filepath=str(R/f'art/models/environment/city_shop_fittings_{id}/city_shop_fittings_{id}{suffix}.glb'))
    objs=list(set(bpy.data.objects)-before)
    root=bpy.data.objects['city_shop_fittings_'+id+suffix]; root.location=mounts[marker]; roots[id]=root
    assemblies[id]=[o for o in objs if o.type=='MESH']
bpy.context.view_layer.update()
report={'mode':mode,'reference_hashes_before':hashes,'mount_transforms_blender':mounts,'fitting_bounds_blender':{id:bounds(obs) for id,obs in assemblies.items()}}
# Authoritative independent expected dimensions and original pivot alignment, no fitting stretch.
expected={'01':[3.2,1.1,.66],'02':[3.2,.14,.8],'03':[1.54,.63,2.48],'05':[3.2,.4,2.0],'06':[1.024,.123,2.202]}
for id,obs in assemblies.items():
    lo,hi=bounds(obs)
    for i in range(3): near(hi[i]-lo[i],expected[id][i])
    for o in [roots[id]]+obs:
        assert all(abs(v-1)<1e-6 for v in o.scale) and all(abs(v)<1e-6 for v in o.rotation_euler)
# Trace through the entire actual hole/rear-void contract, avoiding boundary surfaces only.
probes=[]
for name,x0,x1,z0,z1,back in [('entrance',1.24,2.66,0,2.45,6.46),('window',-2.47,.57,.54,2.42,6.8)]:
    count=0
    for i in range(15):
        for j in range(15):
            x=x0+.0002+(x1-x0-.0004)*i/14; z=z0+.0002+(z1-z0-.0004)*j/14
            assert hit(shell,(x,7.4,z),(0,-1,0),7.4-back) is None,(name,x,z)
            count+=1
    wall=[bpy.data.objects['front_structural_wall_with_two_openings']]
    z=(z0+z1)/2; x=(x0+x1)/2
    left=hit(wall,(x,6.85,z),(-1,0,0)); right=hit(wall,(x,6.85,z),(1,0,0)); top=hit(wall,(x,6.85,z),(0,0,1))
    near(left.x,x0); near(right.x,x1); near(top.z,z1)
    if z0:
        bottom=hit(wall,(x,6.85,z),(0,0,-1)); near(bottom.z,z0)
    probes.append({'opening':name,'ray_count':count,'x_measured':[left.x,right.x],'head_measured':top.z,'rear_void_y':back,'width_m':right.x-left.x,'height_m':z1-z0})
report['hole_and_void_probes']=probes
# Surface intersections against all actual shell triangles. Flush canopy/fascia rail
# contact at the declared wall plane is allowed; every other crossing is a defect.
pairs=[]; contacts=[]
for id,obs in assemblies.items():
    for a in obs:
        for b in shell:
            overlaps=tree(a).overlap(tree(b))
            for ia,ib in overlaps:
                av=[a.matrix_world@a.data.vertices[i].co for i in a.data.loop_triangles[ia].vertices]
                bv=[b.matrix_world@b.data.vertices[i].co for i in b.data.loop_triangles[ib].vertices]
                contact=id in ['01','02'] and min(v.y for v in av)>=7-.00001 and max(abs(v.y-7) for v in bv)<.00001
                if contact: contacts.append([a.name,b.name,ia,ib])
                else: pairs.append([id,a.name,b.name,ia,ib])
report['unexpected_shell_triangle_intersections']=pairs; report['permitted_wall_contact_pairs']=len(contacts)
assert not pairs,pairs[:12]
# Independent actual rear vertices certify insertion-envelope clearance; straight edged
# source profiles are contained by these convex axis-aligned envelopes.
for id,x0,x1,z0,z1,ymin in [('03',1.24,2.66,0,2.45,6.46),('05',-2.47,.57,.54,2.42,6.8)]:
    rear=[o.matrix_world@v.co for o in assemblies[id] for v in o.data.vertices if (o.matrix_world@v.co).y<7-1e-6]
    assert rear
    lo=[min(v[i] for v in rear) for i in range(3)]; hi=[max(v[i] for v in rear) for i in range(3)]
    assert lo[0]>=x0-.00001 and hi[0]<=x1+.00001 and lo[2]>=z0-.00001 and hi[2]<=z1+.00001 and lo[1]>=ymin-.00001
    report['insertion_'+id]={'rear_geometry_bounds':[lo,hi],'side_gaps':[lo[0]-x0,x1-hi[0]],'head_gap':z1-hi[2],'rear_gap':lo[1]-ymin,'bottom_gap':lo[2]-z0}
# Actual leaf/surround gap at rear mating plane, not duplicated door geometry.
ring=[o for o in assemblies['06'] if o.name.endswith('stiles_rails')]
reveal=[o for o in assemblies['03'] if o.name.endswith('recessed_reveal')]
p=(1.95-.516,7-.4525,1.6)
side=hit(ring,p,(1,0,0)).x-hit(reveal,p,(-1,0,0)).x; near(side,.008)
head=hit(reveal,(1.95,6.5475,2.236),(0,0,1)).z-hit(ring,(1.95,6.5475,2.236),(0,0,-1)).z; near(head,.008)
for a in assemblies['06']:
    for b in assemblies['03']: assert not tree(a).overlap(tree(b)),(a.name,b.name)
report['door_side_head_gap_m']=[side,head]
bb=report['fitting_bounds_blender']; gap1=bb['01'][0][2]-bb['05'][1][2]; gap2=bb['02'][0][2]-bb['01'][1][2]
near(gap1,.1); near(gap2,.16)
report['visible_vertical_gaps_m']={'window_to_canopy':gap1,'canopy_to_fascia':gap2,'fascia_to_head_course':4.48-bb['02'][1][2]}
report['canopy_lowest_m']=bb['01'][0][2]; report['flat_bay_width_m']=3.4
# Roof patch and party joins are measured architectural interfaces only.
roof=bpy.data.objects['flat_roof_deck']; roof_points=[]
for x in [-.7,0,.7]:
    for y in [-2,-1,0]:
        h=hit([roof],(x,y,5),(0,0,-1)); near(h.z,4.3); roof_points.append(list(h))
report['roof_attachment_surface_probes']=roof_points
for o in shell:
    lo,hi=bounds([o]); assert lo[0]>=-3.20001 and hi[0]<=3.20001
report['party_wall_join_pitch_m']=6.4
report['reference_hashes_after']={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
assert report['reference_hashes_before']==report['reference_hashes_after']
report['checks']='PASS actual source/GLB scratch fit; not Godot, world, movement, collision, weather-seal or engineering acceptance'
(E/(mode+'_assembly_checks.json')).write_text(json.dumps(report,indent=2)+'\n')
if mode=='source':
    bpy.context.scene['scratch_only']='Actual unchanged fitting sources + shell, translation-only mounts; not a game asset or prefab'
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(E/'mounted_frontage_scratch.blend'))
print('ASSEMBLY_PASS',mode,json.dumps(report['visible_vertical_gaps_m']))
