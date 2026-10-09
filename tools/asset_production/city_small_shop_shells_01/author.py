"""Original narrow/deep commercial shell, authored as editable Blender meshes."""
import bpy, bmesh
from pathlib import Path
import io_scene_gltf2
R=Path(__file__).resolve().parents[3]
assert bpy.app.version[:3]==(5,2,2) and bpy.app.build_hash.decode()=='d13f752e3b9c'
assert io_scene_gltf2.bl_info['version']==(5,2,40)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections): bpy.data.collections.remove(c)
s=bpy.context.scene; s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1
col=bpy.data.collections.new('export_city_small_shop_shells_01'); s.collection.children.link(col)
excluded=bpy.data.collections.new('authoring_excluded'); s.collection.children.link(excluded)
root=bpy.data.objects.new('city_small_shop_shells_01',None); col.objects.link(root)
root['datum']='Ground-centred structural footprint 6.4 x 14m; front Blender Y=7m; +Y outward, +Z up'
root['provenance']='Original Codex Blender-authored geometry, no external model/image geometry; commissioned production candidate'

def material(name,hexcolor,metal,rough):
    m=bpy.data.materials.new(name); m.use_nodes=True; m.use_backface_culling=True
    rgb=[int(hexcolor[i:i+2],16)/255 for i in (0,2,4)]
    color=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=color
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    m.diffuse_color=color; return m
wall=material('shell_muted_plum_render','81777C',0,.78)
roof=material('shell_quiet_blue_roof','405B68',.12,.65)
stone=material('shell_warm_structural_trim','BBB6A8',0,.7)
base=material('shell_slate_plinth','4A5358',0,.78)
metal=material('shell_dark_drain_coping','334950',.35,.48)

def mesh(name,verts,faces,mat,bevel=0):
    data=bpy.data.meshes.new(name); data.from_pydata(verts,[],faces); data.update()
    o=bpy.data.objects.new(name,data); col.objects.link(o); o.parent=root; data.materials.append(mat)
    bm=bmesh.new(); bm.from_mesh(data); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(data); bm.free()
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
    if bevel:
        mod=o.modifiers.new('soft_architectural_edges','BEVEL'); mod.width=bevel; mod.segments=3
        bpy.ops.object.modifier_apply(modifier=mod.name)
        for p in data.polygons: p.use_smooth=True
        mod=o.modifiers.new('broad_plane_normals','WEIGHTED_NORMAL'); mod.keep_sharp=True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    o.select_set(False); return o

def box(name,lo,hi,mat,bevel=.012):
    a,b,c=lo; d,e,f=hi
    return mesh(name,[(a,b,c),(d,b,c),(d,e,c),(a,e,c),(a,b,f),(d,b,f),(d,e,f),(a,e,f)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,bevel)

# A single continuous facade grid has real rectangular holes, welded cell boundaries,
# and no duplicate coplanar cell faces. Square hole edges preserve exact fitting gaps.
xs=[-3.2,-2.47,.57,1.24,2.66,3.2]; zs=[0,.54,2.42,2.45,4.95]
verts=[]; faces=[]; index={}; surface={}
def vtx(p):
    if p not in index: index[p]=len(verts); verts.append(p)
    return index[p]
for i in range(len(xs)-1):
    for j in range(len(zs)-1):
        x=(xs[i]+xs[i+1])/2; z=(zs[j]+zs[j+1])/2
        if (-2.47<x<.57 and .54<z<2.42) or (1.24<x<2.66 and 0<z<2.45): continue
        a,b=xs[i:i+2]; c,d=zs[j:j+2]
        vs=[(a,6.72,c),(b,6.72,c),(b,7,c),(a,7,c),(a,6.72,d),(b,6.72,d),(b,7,d),(a,7,d)]
        ids=[vtx(p) for p in vs]
        for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
            f=tuple(ids[k] for k in face); key=tuple(sorted(f))
            if key in surface: del surface[key]
            else: surface[key]=f
mesh('front_structural_wall_with_two_openings',verts,list(surface.values()),wall)
box('party_wall_left',(-3.2,-7,0),(-2.92,6.72,4.6),wall,0)
box('party_wall_right',(2.92,-7,0),(3.2,6.72,4.6),wall,0)
# Rear wall stops at roof deck; parapet is separated around a real scupper throat.
box('rear_structural_wall',(-2.92,-7,0),(2.92,-6.72,4.3),wall,0)
box('rear_parapet_left',(-2.92,-7,4.3),(2.63,-6.72,4.6),wall,0)
box('rear_parapet_right',(2.87,-7,4.3),(2.92,-6.72,4.6),wall,0)
box('rear_scupper_header',(2.63,-7,4.48),(2.87,-6.72,4.6),wall,0)
box('flat_roof_deck',(-2.92,-6.72,4.14),(2.92,6.72,4.3),roof,.012)
# Two broad standing folds cue a deep ordinary roof without rooftop equipment.
for x in [-.98,.98]: box('roof_seam_'+('left' if x<0 else 'right'),(x-.018,-6.60,4.296),(x+.018,6.60,4.322),roof,.006)
box('front_parapet_coping',(-3.2,6.65,4.95),(3.2,7.12,5.05),metal,.022)
for side,x in [('left',-3.2),('right',2.88)]:
    box('party_coping_'+side,(x,-6.65,4.6),(x+.32,6.66,4.7),metal,.012)
box('rear_coping',(-3.2,-7.08,4.6),(3.2,-6.65,4.7),metal,.015)
# Structural corner pilasters and head course stay outside all fitting envelopes.
for name,a,b in [('left',-3.2,-2.83),('right',2.83,3.2)]:
    box('front_corner_pier_'+name,(a,6.99,0),(b,7.065,4.55),stone,.015)
box('front_head_course',(-3.2,7,4.48),(3.2,7.06,4.61),stone,.012)
# Low structural plinth is interrupted at the entrance, not a duplicate door threshold.
box('front_plinth_left',(-3.2,7.001,0),(1.10,7.045,.30),base,.01)
box('front_plinth_right',(2.80,7.001,0),(3.2,7.045,.30),base,.01)
box('rear_plinth',(-3.2,-7.04,0),(3.2,-6.99,.30),base,.01)
# Ordinary rain disposal, within width; no duplicated vent/AC or shared fitting.
box('scupper_lower_lip',(2.63,-7.17,4.285),(2.87,-6.70,4.315),metal,.006)
box('rain_hopper_back',(2.58,-7.04,4.04),(2.92,-7.005,4.40),metal,.006)
box('rain_hopper_front',(2.58,-7.22,4.04),(2.92,-7.185,4.40),metal,.006)
for label,a,b in [('left',2.58,2.615),('right',2.885,2.92)]:
    box('rain_hopper_'+label,(a,-7.185,4.04),(b,-7.04,4.40),metal,.006)
box('rain_hopper_base',(2.58,-7.22,4.02),(2.92,-7.005,4.055),metal,.005)
box('rear_downpipe',(2.69,-7.16,.18),(2.81,-7.04,4.055),metal,.024)
for z in [.65,2.45,3.65]: box('drain_saddle_'+str(z),(2.665,-7.17,z),(2.835,-7,z+.05),metal,.008)
markers={'mount_entrance_single':(1.95,7,0),'mount_door_single':(1.95,7,0),'mount_display_window':(-.95,7,.48),'mount_canopy':(-.95,7,3),'mount_fascia':(-.95,7,3.8),'mount_roof_detail':(0,-1,4.3),'join_party_left':(-3.2,0,0),'join_party_right':(3.2,0,0)}
for name,pos in markers.items():
    o=bpy.data.objects.new(name,None); col.objects.link(o); o.parent=root; o.location=pos; o.empty_display_size=.20
    o['contract']='Translation in metres, identity rotation and scale; see production report'
# Saved metre reference is explicitly excluded and never exported.
bpy.ops.mesh.primitive_cube_add(size=1,location=(-4.4,7,.5)); ref=bpy.context.object; ref.name='authoring_1m_reference'
for c in list(ref.users_collection): c.objects.unlink(ref)
excluded.objects.link(ref); ref.data.materials.append(stone); ref.hide_render=True; ref.hide_set(True)
s['scope']='Static architectural shell only; no fittings, interiors, collision, runtime geometry or tenant art.'
s['roof_attachment']='Flat Z=4.30; clear central patch X[-.70,.70], Y[-2,0]; no structural load/gameplay claim.'
s['source_front_plane_m']=7.; s['footprint_m']=[6.4,14.]
s['opening_contract']='Entrance X[1.24,2.66] Z[0,2.45], rear to6.46. Window X[-2.47,.57] Z[.54,2.42], rear to6.8.'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'art/source/models/environment/city_small_shop_shells_01/city_small_shop_shells_01.blend'))
print('ORIGINAL_SOURCE_SAVED',len(col.objects),'objects')
