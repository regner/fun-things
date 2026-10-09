"""Original open round surround, authored in private Blender; all dimensions in metres."""
import bpy, math
import io_scene_gltf2
assert bpy.app.version[:3]==(5,2,2)
assert bpy.app.build_hash.decode()=='d13f752e3b9c'
assert io_scene_gltf2.bl_info['version']==(5,2,40)
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'docs/assets/production/city_planting_02-evidence'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1
col=bpy.data.collections.new('export_city_planting_02'); s.collection.children.link(col)
root=bpy.data.objects.new('city_planting_02',None); col.objects.link(root)
root['authorship']='Original Codex Blender construction, 2026-10-09; city_planting.02 commission'
root['front']='Blender +Y maps Godot -Z; symmetric body'
root['clear_open_core_diameter_m']=1.24
root['planting_datum_godot_y_m']=0.0
def mat(name,rgb,rough):
    m=bpy.data.materials.new(name); m.use_nodes=True
    c=[((v/255+.055)/1.055)**2.4 if v>10 else v/3294.6 for v in rgb]
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough
    m.diffuse_color=(*c,1); return m
body=mat('planter_sage_cast_stone',(151,164,151),.76)
rim=mat('planter_pale_stone_rim',(187,194,172),.70)
foot=mat('planter_recess_petrol',(48,73,72),.8)
soil=mat('planter_quiet_earth',(63,57,44),.95)
def lathe(name, profile, mats, rim_start=999, rim_end=999):
    # Closed radial section gives a watertight annulus with a genuinely open core.
    n=64
    verts=[(r*math.cos(2*math.pi*i/n),r*math.sin(2*math.pi*i/n),z)
           for r,z in profile for i in range(n)]
    faces=[]
    for j in range(len(profile)):
        for i in range(n):
            faces.append((j*n+i,j*n+(i+1)%n,((j+1)%len(profile))*n+(i+1)%n,
                          ((j+1)%len(profile))*n+i))
    mesh=bpy.data.meshes.new(name+'_mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); col.objects.link(o); o.parent=root
    for m in mats: mesh.materials.append(m)
    for face in mesh.polygons:
        section=face.index//n
        face.material_index=1 if rim_start<=section<=rim_end else 0
        face.use_smooth=True
    return o
lathe('recessed_annular_foot',[(.78,0),(.81,.014),(.82,.035),(.82,.065),
       (.80,.08),(.635,.08),(.62,.055),(.62,.018),(.635,0)],[foot])
lathe('cast_stone_open_surround',[(.815,.045),(.84,.06),(.853,.09),
       (.868,.37),(.878,.398),(.895,.415),(.90,.44),(.895,.46),
       (.88,.477),(.86,.48),(.715,.48),(.693,.477),(.68,.46),
       (.676,.44),(.68,.415),(.65,.10),(.635,.075),(.635,.045)],
       [body,rim],4,13)
studio=bpy.data.collections.new('studio_do_not_export'); s.collection.children.link(studio)
def move(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    studio.objects.link(o); return o
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.005)); o=move(bpy.context.object); o.name='studio_floor'; o.data.materials.append(mat('studio_slate',(104,119,126),.9))
def camera(name,loc,target):
    bpy.ops.object.camera_add(location=loc); c=move(bpy.context.object); c.name=name; c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler(); return c
hero=camera('hero_camera',(2.8,3.4,2.6),(0,0,.23)); hero.data.type='ORTHO'; hero.data.ortho_scale=2.85
project=camera('project_vertical_47m_42deg',(0,0,47),(0,0,0)); project.data.type='PERSP'; project.data.sensor_fit='VERTICAL'; project.data.angle=math.radians(42)
for name,loc,power,size in [('key',(1,3,6),800,4),('fill',(-4,1,3),450,5),('rim',(2,-3,4),600,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=move(bpy.context.object); o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector((0,0,.2))-o.location).to_track_quat('-Z','Y').to_euler()
s.world.color=(.25,.25,.25); s.render.engine='CYCLES'; s.cycles.samples=32; s.cycles.use_denoising=True; s.render.threads_mode='FIXED'; s.render.threads=4
s.render.image_settings.file_format='PNG'; s.view_settings.view_transform='AgX'; s.render.resolution_percentage=100
s.camera=hero; s.render.resolution_x=1100; s.render.resolution_y=800
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/source/models/environment/city_planting_02/city_planting_02.blend'))
s.render.filepath=str(E/'hero.png'); bpy.ops.render.render(write_still=True)
s.camera=project; s.render.resolution_x=1280; s.render.resolution_y=800; s.render.filepath=str(E/'project_camera_reference.png'); bpy.ops.render.render(write_still=True)
