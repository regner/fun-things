"""Render source and read-only scale comparisons; never save preview placements."""
import bpy, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_planting_05-evidence'
def render():
    """Permit a measurement-only rerun without rewriting reviewed captures."""
    if '--measure-only' not in sys.argv:bpy.ops.render.render(write_still=True)
s=bpy.context.scene; hero=bpy.data.objects['hero_camera']; fixture=bpy.data.objects['reference_one_metre_vertical']
fixture.hide_render=True
variants=['short_tuft','spreading_clump']
for variant in variants:
    for other in variants:bpy.data.collections['variant_'+other].hide_render=(variant!=other)
    s.camera=hero; hero.data.ortho_scale=1.1 if variant=='short_tuft' else 1.55
    s.render.filepath=str(E/(variant+'_hero.png')); render()
# Retain unmodified, unit-scale production actor and shrub for scale and vocabulary.
inputs=[]; groups={}
def imported(rel,offset,label):
    path=R/rel; data=path.read_bytes(); before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    objects=set(bpy.data.objects)-before
    for o in objects:
        if o.parent is None:o.location+=Vector(offset)
    assert path.read_bytes()==data
    inputs.append({'path':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'scale_factor':1,'translation_blender_m':offset})
    groups[label]=list(objects)
for variant,x in [('short_tuft',-1.8),('spreading_clump',-.55)]:
    col=bpy.data.collections['variant_'+variant]; col.hide_render=False
    col.objects['city_planting_05_'+variant].location=(x,0,0)
    groups[variant]=list(col.objects)
imported('art/models/environment/city_planting_03/city_planting_03.glb',(1.05,0,0),'shrub_03')
imported('art/models/characters/coral_courier/coral_courier.glb',(2.4,-.1,0),'courier')
fixture.hide_render=False; fixture.location=(-2.6,0,.5); groups['one_metre_fixture']=[fixture]
bpy.context.view_layer.update()
hero.location=(3,-7,4.6); hero.rotation_euler=(Vector((0,0,.55))-hero.location).to_track_quat('-Z','Y').to_euler(); hero.data.ortho_scale=6.5
s.camera=hero; s.render.resolution_x=1400; s.render.resolution_y=850
s.render.filepath=str(E/'scale_comparison_hero.png'); render()
project=bpy.data.objects['project_vertical_47m_42deg']; s.camera=project
s.render.resolution_x=1280; s.render.resolution_y=800
frame=project.data.view_frame(scene=s)
vfov=math.degrees(2*math.atan(max(abs(v.y/v.z) for v in frame)))
assert abs(vfov-42)<.001 and all(abs(v)<1e-6 for v in project.rotation_euler)
s.render.filepath=str(E/'scale_comparison_gameplay.png'); render()
def bounds(objects,screen=False):
    """Measure evaluated geometry, including the existing actor's rest deformation."""
    pts=[]; dg=bpy.context.evaluated_depsgraph_get()
    for ob in objects:
        if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
        ev=ob.evaluated_get(dg); me=ev.to_mesh()
        for v in me.vertices:
            p=ev.matrix_world@v.co
            pts.append(world_to_camera_view(s,s.camera,p) if screen else p)
        ev.to_mesh_clear()
    n=2 if screen else 3
    factor=[1280,800] if screen else [1,1,1]
    return [[min(p[i] for p in pts)*factor[i] for i in range(n)],[max(p[i] for p in pts)*factor[i] for i in range(n)]]
measurements={k:{'blender_world_bounds_m':bounds(obs),'gameplay_pixel_bounds_bottom_left':bounds(obs,True)} for k,obs in groups.items()}
# Authoring-only all-black overhead comparison exposes the gaps and separates
# blade silhouettes from the grouped-volume shrub. It is deliberately enlarged.
black=bpy.data.materials.new('diagnostic_silhouette_black'); black.use_nodes=True
p=black.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(.003,.003,.003,1); p.inputs['Roughness'].default_value=1
for label,objects in groups.items():
    for ob in objects:
        if ob.type=='MESH':
            for i in range(len(ob.data.materials)):ob.data.materials[i]=black
s.camera=hero; hero.location=(0,0,8); hero.rotation_euler=(0,0,0); hero.data.ortho_scale=6.5
s.render.resolution_x=1400; s.render.resolution_y=850
s.render.filepath=str(E/'silhouette_overhead_enlarged.png'); render()
(E/'preview_checks.json').write_text(json.dumps({'scope':'Blender source studio comparison only; no Godot/runtime/device acceptance','inputs':inputs,'camera':{'height_m':47,'vertical_fov_deg':vfov,'viewport':[1280,800],'rotation_radians':list(project.rotation_euler)},'order_left_to_right':['one_metre_fixture','short_tuft','spreading_clump','shrub_03','courier'],'measurements':measurements,'source_saved':False},indent=2)+'\n')
print('PREVIEW_CHECKS_PASS',json.dumps(measurements))
