"""Read-only fixture assembly of delivered planters; does not save or export models."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_planting_03-evidence'
s=bpy.context.scene
col=bpy.data.collections['export_city_planting_03']; root=col.objects['city_planting_03']
# Two original shrub instances on rectangular soil; one at round surround ground.
def copy_cluster(name,offset):
    r=bpy.data.objects.new(name,None); s.collection.objects.link(r); r.location=offset
    for o in col.objects:
        if o.type=='MESH':
            c=o.copy(); s.collection.objects.link(c); c.parent=r
    return r
root.location=(-1.7-.48,0,.40)
copy_cluster('rectangular_second_shrub',(-1.7+.48,0,.40))
copy_cluster('round_shrub',(1.2,0,0))
for ident,offset in [('01',(-1.7,0,0)),('02',(1.2,0,0))]:
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(R/f'art/models/environment/city_planting_{ident}/city_planting_{ident}.glb'))
    for o in set(bpy.data.objects)-before:
        if o.parent is None:o.location=offset
c=s.camera; c.location=(3,6,4.8); c.rotation_euler=(Vector((-.5,0,.5))-c.location).to_track_quat('-Z','Y').to_euler(); c.data.ortho_scale=6.4
s.render.resolution_x=1400; s.render.resolution_y=850; s.render.filepath=str(E/'planter_fit_studio.png'); bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['project_vertical_47m_42deg']; s.render.resolution_x=1280; s.render.resolution_y=800
frame=s.camera.data.view_frame(scene=s)
vfov=math.degrees(2*math.atan(max(abs(v.y/v.z) for v in frame)))
assert abs(vfov-42)<.001, vfov
assert all(abs(v)<1e-6 for v in s.camera.rotation_euler)
s.render.filepath=str(E/'planter_fit_project_camera.png'); bpy.ops.render.render(write_still=True)
(E/'assembly_preview.json').write_text(json.dumps({'scope':'Blender studio only, read-only imported planter GLBs; no prefab/physics acceptance','rectangular_shrub_translations_blender':[[-2.18,0,.4],[-1.22,0,.4]],'round_shrub_translation_blender':[1.2,0,0],'camera':{'height_m':47,'vertical_fov_degrees':42,'viewport':[1280,800]},'source_saved':False},indent=2)+'\n')
