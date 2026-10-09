"""Independent actual-mesh entrance, insertion, shell void and mount measurements."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT=Path(__file__).resolve().parent
FROZEN=Path('/tmp/batch03-independent/frozen')
issues=[]
def close(a,b,tol=2e-5):
    if abs(a-b)>tol:issues.append(dict(expected=b,observed=a))
def clean():
    for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
def load_source(ident,variant=None):
    path=FROZEN/'art/source/models/environment'/ident/(ident+'.blend')
    collection='variant_'+variant if variant else 'export_'+ident
    with bpy.data.libraries.load(str(path),link=False) as (a,b):b.collections=[collection]
    col=b.collections[0];bpy.context.scene.collection.children.link(col)
    bpy.context.view_layer.update()
    return {o.name:o for o in col.all_objects}
def load_glb(ident,variant=None):
    before=set(bpy.data.objects)
    name=ident+('_'+variant if variant else '')
    bpy.ops.import_scene.gltf(filepath=str(FROZEN/'art/models/environment'/ident/(name+'.glb')))
    return {o.name:o for o in set(bpy.data.objects)-before}
def meshes(objects):return [o for o in objects.values() if o.type=='MESH']
def trees(objects):
    result=[]
    for o in objects:
        o.data.calc_loop_triangles()
        vs=[o.matrix_world@v.co for v in o.data.vertices]
        result.append((o,BVHTree.FromPolygons(vs,[list(t.vertices) for t in o.data.loop_triangles],all_triangles=True)))
    return result
def hit(ts,p,d,distance=100):
    hits=[(r[3],r[0],o.name) for o,t in ts if (r:=t.ray_cast(Vector(p),Vector(d),distance))[0] is not None]
    return min(hits,key=lambda r:r[0]) if hits else None
def bounds(obs):
    coords=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
    return [[min(p[i] for p in coords) for i in range(3)],[max(p[i] for p in coords) for i in range(3)]]
results=[]
for mode in ('source','glb'):
    loader=load_source if mode=='source' else load_glb
    entrances=[]
    for variant,width in (('single',1.04),('double',1.84)):
        clean();surround=loader('city_shop_fittings_03',variant);door=loader('city_shop_fittings_06',variant)
        st=trees(meshes(surround));dt=trees(meshes(door))
        reveal=trees([o for o in meshes(surround) if o.name.endswith('recessed_reveal')])
        stop=trees([o for o in meshes(surround) if o.name.endswith('rear_stop')])
        sill=trees([o for o in meshes(surround) if o.name.endswith('sloped_threshold')])
        frames=[o for o in meshes(door) if o.name.endswith('stiles_rails')]
        gaps=[]
        for y in (-.471,-.4525,-.434):
            for z in (.4,1.1,1.8):
                left=hit(reveal,(0,y,z),(-1,0,0))[1].x
                right=hit(reveal,(0,y,z),(1,0,0))[1].x
                close(right-left,width)
                lo,hi=bounds(frames)
                close(lo[0]-left,.008);close(right-hi[0],.008)
                gaps.append(dict(depth=y,height=z,aperture=right-left,left_gap=lo[0]-left,right_gap=right-hi[0]))
        leaf_bounds=bounds(frames)
        head=hit(reveal,(0,-.4525,2.236),(0,0,1))[1].z
        threshold=hit(sill,(0,-.4525,.025),(0,0,-1))[1].z
        # Stop jamb is behind the edge of the leaf and overlaps the leaf by design.
        stop_y=hit(stop,(width/2-.01,-.478,1.2),(0,-1,0))[1].y
        close(head,2.240);close(head-leaf_bounds[1][2],.008)
        close(threshold,.020);close(leaf_bounds[0][2]-threshold,.010)
        close(leaf_bounds[0][1]-stop_y,.006)
        overlaps=[]
        for a,ta in dt:
            for b,tb in st:
                if pairs:=ta.overlap(tb):overlaps.append(dict(door=a.name,surround=b.name,pairs=len(pairs)))
        if overlaps:issues.append(dict(mode=mode,variant=variant,overlaps=overlaps))
        if variant=='double':
            left=next(o for o in frames if 'leaf_1_' in o.name)
            right=next(o for o in frames if 'leaf_2_' in o.name)
            meeting=bounds([right])[0][0]-bounds([left])[1][0];close(meeting,.008)
        else:meeting=None
        entrances.append(dict(variant=variant,side_probes=gaps,head=head,sill=threshold,stop_y=stop_y,
            head_gap=head-leaf_bounds[1][2],sill_gap=leaf_bounds[0][2]-threshold,
            stop_gap=leaf_bounds[0][1]-stop_y,meeting_gap=meeting,overlaps=overlaps))
    # Inspect rear insertion geometry of both window groups independently of a fabricated wall.
    windows=[]
    for ident,xhalf,zlo,zhi,rear_depth in [('city_shop_fittings_05',1.52,.06,1.94,.2),('city_shop_fittings_07',2.34,.06,1.54,.18)]:
        clean();group=loader(ident)
        rear=[o.matrix_world@v.co for o in meshes(group) for v in o.data.vertices if (o.matrix_world@v.co).y<-1e-6]
        lo=[min(p[i] for p in rear) for i in range(3)];hi=[max(p[i] for p in rear) for i in range(3)]
        gaps=[lo[0]+xhalf,xhalf-hi[0],lo[2]-zlo,zhi-hi[2],lo[1]+rear_depth]
        for gap in gaps:close(gap,.020)
        windows.append(dict(id=ident,rear_bounds=[lo,hi],jamb_bottom_head_rear_gaps=gaps))
    clean();shell=loader('city_small_shop_shells_01');shell_meshes=meshes(shell);shell_trees=trees(shell_meshes)
    holes=[]
    wall=trees([shell['front_structural_wall_with_two_openings']])
    for name,x0,x1,z0,z1,back in [('entrance',1.24,2.66,0,2.45,6.46),('window',-2.47,.57,.54,2.42,6.8)]:
        blocked=[]
        for i in range(17):
            for j in range(19):
                x=x0+.0003+(x1-x0-.0006)*i/16;z=z0+.0003+(z1-z0-.0006)*j/18
                if h:=hit(shell_trees,(x,7.3,z),(0,-1,0),7.3-back):blocked.append(dict(x=x,z=z,hit=list(h[1]),object=h[2]))
        centre=((x0+x1)/2,6.86,(z0+z1)/2)
        left=hit(wall,centre,(-1,0,0))[1].x;right=hit(wall,centre,(1,0,0))[1].x
        top=hit(wall,centre,(0,0,1))[1].z
        bottom=hit(wall,centre,(0,0,-1)) if z0 else None
        close(left,x0);close(right,x1);close(top,z1)
        if bottom:close(bottom[1].z,z0)
        if blocked:issues.append(dict(mode=mode,hole=name,blocked=blocked))
        holes.append(dict(name=name,rays=17*19,blocked=blocked,left=left,right=right,head=top,bottom=bottom[1].z if bottom else 'open to ground',rear_void=back))
    mount_contract={'mount_entrance_single':[1.95,7,0],'mount_door_single':[1.95,7,0],
      'mount_display_window':[-.95,7,.48],'mount_canopy':[-.95,7,3],
      'mount_fascia':[-.95,7,3.8],'mount_roof_detail':[0,-1,4.3],
      'join_party_left':[-3.2,0,0],'join_party_right':[3.2,0,0]}
    mounts={}
    for name,expected in mount_contract.items():
        mounts[name]=list(shell[name].matrix_world.translation)
        for a,b in zip(mounts[name],expected):close(a,b)
    fittings={}
    for n,variant,marker in [('01',None,'mount_canopy'),('02',None,'mount_fascia'),('03','single','mount_entrance_single'),('05',None,'mount_display_window'),('06','single','mount_door_single')]:
        ident='city_shop_fittings_'+n;group=loader(ident,variant)
        root=group[ident+('_'+variant if variant else '')];root.location=mounts[marker]
        bpy.context.view_layer.update();fittings[n]=meshes(group)
    inter=[];contacts=[]
    for n,obs in fittings.items():
        for a,ta in trees(obs):
            for b,tb in shell_trees:
                for ia,ib in ta.overlap(tb):
                    av=[a.matrix_world@a.data.vertices[i].co for i in a.data.loop_triangles[ia].vertices]
                    bv=[b.matrix_world@b.data.vertices[i].co for i in b.data.loop_triangles[ib].vertices]
                    allowed=n in ('01','02') and min(v.y for v in av)>=7-1e-5 and max(abs(v.y-7) for v in bv)<1e-5
                    (contacts if allowed else inter).append(dict(fitting=n,a=a.name,b=b.name,triangles=[ia,ib]))
    if inter:issues.append(dict(mode=mode,shell_intersections=inter))
    fitting_bounds={n:bounds(obs) for n,obs in fittings.items()}
    clearance=[fitting_bounds['01'][0][2]-fitting_bounds['05'][1][2],fitting_bounds['02'][0][2]-fitting_bounds['01'][1][2]]
    close(clearance[0],.100);close(clearance[1],.160)
    roof_points=[]
    roof=trees([shell['flat_roof_deck']])
    for x in (-.7,0,.7):
        for y in (-2,-1,0):
            h=hit(roof,(x,y,5),(0,0,-1));close(h[1].z,4.3);roof_points.append(list(h[1]))
    results.append(dict(mode=mode,entrances=entrances,window_insertions=windows,
        shell=dict(holes=holes,mounts=mounts,mesh_count=len(shell_meshes),
          no_fitting_names=all(not any(k in o.name for k in ('leaf','glazing','casing','canopy','fascia')) for o in shell_meshes),
          shell_bounds=bounds(shell_meshes),fitting_bounds=fitting_bounds,unexpected_intersections=inter,
          permitted_contact_count=len(contacts),vertical_clearances=clearance,roof_patch_points=roof_points)))
(OUT/'interface-audit.json').write_text(json.dumps(dict(results=results,issues=issues),indent=2)+'\n')
print(json.dumps(dict(issues=issues,summary=[dict(mode=r['mode'],entrances=[dict(variant=e['variant'],head=e['head'],sill=e['sill'],head_gap=e['head_gap'],sill_gap=e['sill_gap'],stop_gap=e['stop_gap'],meeting_gap=e['meeting_gap']) for e in r['entrances']],shell_holes=[dict(name=h['name'],rays=h['rays'],blocked=len(h['blocked'])) for h in r['shell']['holes']],unexpected_intersections=len(r['shell']['unexpected_intersections']),clearances=r['shell']['vertical_clearances']) for r in results]),indent=2))
assert not issues,issues
