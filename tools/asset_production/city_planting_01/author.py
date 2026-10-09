"""Original rounded trough, authored in private Blender; all dimensions in metres."""
import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'docs/assets/production/city_planting_01-evidence'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1
col=bpy.data.collections.new('export_city_planting_01'); s.collection.children.link(col)
root=bpy.data.objects.new('city_planting_01',None); col.objects.link(root)
root['authorship']='Original Codex Blender construction, 2026-10-09; city_planting.01 commission'
root['front']='Blender +Y maps Godot -Z; symmetric body'
root['planting_surface_godot_y_m']=.40
root['safe_planting_rectangle_xz_m']=[1.90,.40]
def mat(name,rgb,rough):
    m=bpy.data.materials.new(name); m.use_nodes=True
    c=[((v/255+.055)/1.055)**2.4 if v>10 else v/3294.6 for v in rgb]
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough
    m.diffuse_color=(*c,1); return m
body=mat('planter_sage_cast_stone',(151,164,151),.76)
rim=mat('planter_pale_stone_rim',(187,194,172),.70)
foot=mat('planter_recess_petrol',(48,73,72),.8)
soil=mat('planter_quiet_earth',(63,57,44),.95)
def ring(w,d,r,z):
    pts=[]
    for x,y,start in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
        for i in range(9):
            a=math.radians(start+i*90/8); pts.append((x+r*math.cos(a),y+r*math.sin(a),z))
    return pts

def loft(name,profiles,mats,slots=None):
    verts=[v for p in profiles for v in ring(*p)]; n=36
    faces=[tuple(reversed(range(n)))]; material_ids=[0]
    for j in range(len(profiles)-1):
        for i in range(n):
            a=j*n+i; b=j*n+(i+1)%n; faces.append((a,b,b+n,a+n)); material_ids.append(slots[j] if slots else 0)
    faces.append(tuple((len(profiles)-1)*n+i for i in range(n))); material_ids.append(0)
    mesh=bpy.data.meshes.new(name+'_mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); col.objects.link(o); o.parent=root
    for m in mats: mesh.materials.append(m)
    for p,idx in zip(mesh.polygons,material_ids): p.material_index=idx; p.use_smooth=len(p.vertices)==4
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    mod=o.modifiers.new('broad_surface_normals','WEIGHTED_NORMAL'); mod.keep_sharp=True; mod.weight=40
    bpy.ops.object.modifier_apply(modifier=mod.name); o.select_set(False)
    return o
loft('recessed_ground_foot',[(2.16,.68,.10,0),(2.20,.72,.12,.018),(2.20,.72,.12,.072),(2.16,.68,.10,.09)],[foot])
# Single watertight shell: outer wall -> softly rolled lip -> inner wall -> floor.
loft('rounded_cast_trough',[(2.22,.72,.12,.05),(2.27,.77,.135,.067),(2.30,.80,.15,.105),(2.36,.86,.17,.51),(2.39,.89,.18,.54),(2.40,.90,.185,.565),(2.39,.89,.18,.588),(2.365,.865,.17,.60),(2.085,.585,.115,.60),(2.06,.56,.105,.585),(2.05,.55,.10,.56),(2.00,.50,.09,.20),(1.96,.46,.075,.16)],[body,rim],[0,0,0,0,1,1,1,1,1,1,0,0])
loft('separate_recessed_soil_insert',[(1.99,.49,.085,.34),(2.015,.515,.09,.39),(2.01,.51,.09,.40)],[soil])
studio=bpy.data.collections.new('studio_do_not_export'); s.collection.children.link(studio)
def move(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    studio.objects.link(o); return o
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.005)); o=move(bpy.context.object); o.name='studio_floor'; o.data.materials.append(mat('studio_slate',(104,119,126),.9))
def camera(name,loc,target):
    bpy.ops.object.camera_add(location=loc); c=move(bpy.context.object); c.name=name; c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler(); return c
hero=camera('hero_camera',(3.3,4.0,2.8),(0,0,.27)); hero.data.type='ORTHO'; hero.data.ortho_scale=3.7
project=camera('project_vertical_47m_42deg',(0,0,47),(0,0,0)); project.data.type='PERSP'; project.data.sensor_fit='VERTICAL'; project.data.angle=math.radians(42)
for name,loc,power,size in [('key',(1,3,6),800,4),('fill',(-4,1,3),450,5),('rim',(2,-3,4),600,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=move(bpy.context.object); o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector((0,0,.2))-o.location).to_track_quat('-Z','Y').to_euler()
s.world.color=(.25,.25,.25); s.render.engine='CYCLES'; s.cycles.samples=32; s.cycles.use_denoising=True; s.render.threads_mode='FIXED'; s.render.threads=6
s.render.image_settings.file_format='PNG'; s.view_settings.view_transform='AgX'; s.render.resolution_percentage=100
s.camera=hero; s.render.resolution_x=1100; s.render.resolution_y=800
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/source/models/environment/city_planting_01/city_planting_01.blend'))
s.render.filepath=str(E/'hero.png'); bpy.ops.render.render(write_still=True)
s.camera=project; s.render.resolution_x=1280; s.render.resolution_y=800; s.render.filepath=str(E/'project_camera_reference.png'); bpy.ops.render.render(write_still=True)
