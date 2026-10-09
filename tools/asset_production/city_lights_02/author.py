"""Original city_lights.02 source construction; run once in isolated Blender 5.2.2."""
import bpy, bmesh, math, json, sys
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[3]
E = ROOT/'docs/assets/production/city_lights_02-evidence'
SOURCE = ROOT/'art/source/models/environment/city_lights_02/city_lights_02.blend'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
col = bpy.data.collections.new('export_city_lights_02')
scene.collection.children.link(col)
root = bpy.data.objects.new('city_lights_02', None)
col.objects.link(root)
root['front'] = 'Blender +Y / Godot -Z; service panel faces front'
root['author'] = 'Codex; original Blender construction commissioned 2026-10-09'
root['dimensions_m_godot'] = [0.72, 3.0, 0.72]

def material(name, rgb, metal=0, emission=0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    c=tuple(((v/255+.055)/1.055)**2.4 if v>10 else v/3294.6 for v in rgb)
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*c,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=.38 if metal else .55
    p.inputs['Emission Color'].default_value=(*c,1)
    p.inputs['Emission Strength'].default_value=emission
    m.diffuse_color=(*c,1)
    m.use_fake_user=True
    return m
petrol=material('city_lights_02_petrol_metal',(25,63,70),.55)
trim=material('city_lights_02_recess_dark',(13,29,34),.3)
warm=material('city_lights_02_lens_warm',(255,220,163),emission=.45)
cool=material('city_lights_02_lens_cool',(172,222,239),emission=.45)

def finish(o,mat):
    o.parent=root; o.data.materials.append(mat)
    for old in list(o.users_collection): old.objects.unlink(o)
    col.objects.link(o)
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    for p in o.data.polygons: p.use_smooth=True
    n=o.modifiers.new('weighted_broad_normals','WEIGHTED_NORMAL'); n.keep_sharp=True
    bpy.ops.object.modifier_apply(modifier=n.name)
    o.select_set(False)
    return o

def lathe(name, profile, mat, segments=48):
    verts=[]
    for radius,z in profile:
        verts.extend((radius*math.cos(i*2*math.pi/segments),radius*math.sin(i*2*math.pi/segments),z) for i in range(segments))
    faces=[]
    for j in range(len(profile)-1):
        for i in range(segments):
            a=j*segments+i; b=j*segments+(i+1)%segments
            faces.append((a,b,b+segments,a+segments))
    faces.extend([tuple(reversed(range(segments))),tuple((len(profile)-1)*segments+i for i in range(segments))])
    mesh=bpy.data.meshes.new(name+'_mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); col.objects.link(o)
    return finish(o,mat)

lathe('foot_splayed_casting',[(.12,0),(.135,.014),(.135,.055),(.126,.074),(.092,.11),(.078,.17),(.078,.31),(.068,.34)],petrol,32)
lathe('quiet_tapered_pole',[(.062,.31),(.062,.37),(.047,2.57),(.047,2.66)],petrol,32)
lathe('lantern_neck',[(.047,2.54),(.082,2.56),(.092,2.59),(.092,2.64),(.13,2.67)],petrol)
lathe('lower_shield',[(.09,2.63),(.20,2.65),(.294,2.695),(.312,2.714),(.312,2.737),(.301,2.749)],petrol)
lens=lathe('broad_recessed_diffuser',[(.291,2.738),(.305,2.75),(.319,2.846),(.316,2.861)],warm)
lathe('crown_seal',[(.317,2.851),(.338,2.86),(.338,2.88),(.326,2.89)],trim)
lathe('broad_rounded_canopy',[(.328,2.871),(.351,2.878),(.36,2.889),(.36,2.905),(.350,2.925),(.298,2.946),(.21,2.975),(.10,2.994),(.022,3.0)],petrol)
# Small inset access panel makes the otherwise radial fixture's +Y front explicit.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.060,.57))
o=bpy.context.object; o.name='front_service_panel'; o.scale=(.064,.012,.17)
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
b=o.modifiers.new('panel_edge_radius','BEVEL'); b.width=.003; b.segments=3
bpy.ops.object.modifier_apply(modifier=b.name); finish(o,trim)
# Editable studio remains outside export collection.
studio=bpy.data.collections.new('studio_do_not_export'); scene.collection.children.link(studio)
def studio_move(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    studio.objects.link(o)
    return o
bpy.ops.mesh.primitive_plane_add(size=200)
floor=studio_move(bpy.context.object); floor.name='studio_floor'; floor.data.materials.append(material('studio_slate',(108,125,136)))
bpy.ops.object.camera_add(location=(4.5,6.5,4.2))
cam=studio_move(bpy.context.object); cam.name='camera_three_quarter'; scene.camera=cam
cam.rotation_euler=(Vector((0,0,1.52))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=3.7
for name,loc,power,size in [('key',(3,4,6),950,5),('fill',(-4,1,3),650,4),('rim',(1,-3,4),900,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    light=studio_move(bpy.context.object); light.name='studio_'+name; light.data.energy=power; light.data.shape='DISK'; light.data.size=size
    light.rotation_euler=(Vector((0,0,1.5))-light.location).to_track_quat('-Z','Y').to_euler()
scene.world.color=(.20,.20,.20)
scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED'; scene.render.threads=6
scene.render.resolution_x=720; scene.render.resolution_y=960; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
scene.render.filepath=str(E/'warm_three_quarter.png')
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
# Export and validation operate on saved source, rather than regenerating geometry.
exec(compile((Path(__file__).with_name('export.py')).read_text(),str(Path(__file__).with_name('export.py')),'exec'))
bpy.ops.render.render(write_still=True)
lens.data.materials[0]=cool
scene.render.filepath=str(E/'cool_three_quarter.png'); bpy.ops.render.render(write_still=True)
lens.data.materials[0]=warm
cam.location=(1.8,2.8,3.6); cam.rotation_euler=(Vector((0,0,2.8))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=1.2
scene.render.resolution_x=960; scene.render.resolution_y=720
scene.render.filepath=str(E/'head_detail.png'); bpy.ops.render.render(write_still=True)
