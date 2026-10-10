"""Render the full-scale plaque mounted to the unchanged entrance, plus all four face options."""
import hashlib
import math
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
NID='d03_community_graphics_02'
SOURCE=ROOT/f'art/source/models/environment/{NID}/{NID}.blend'
BAY=ROOT/'art/source/models/environment/d03_apartment_family_08/d03_apartment_family_08.blend'
EVIDENCE=ROOT/f'docs/assets/production/{NID}-evidence'


def main():
    """Use existing studio/context without saving or modifying any shared source."""
    assert bpy.app.version_string=='5.2.2 LTS'
    before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE,BAY)]
    bpy.ops.wm.open_mainfile(filepath=str(BAY))
    scene=bpy.context.scene
    with bpy.data.libraries.load(str(SOURCE),link=False) as (_,loaded):
        loaded.collections=['export_'+NID]
    collection=loaded.collections[0]
    scene.collection.children.link(collection)
    root=bpy.data.objects['D03CommunityGraphics02']
    root.location=(.785,6,1.85)
    camera=scene.camera
    scene.render.resolution_x,scene.render.resolution_y=1280,720
    scene.render.image_settings.color_mode='RGB'
    scene.render.image_settings.compression=95
    scene.render.dither_intensity=0
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    for name,position,target,scale in [
        ('hero',(3,16,4.2),(0,6,1.55),7.1),
        ('side',(2.1,8,2.2),(.785,6,1.85),1.1),
    ]:
        camera.location=position
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        camera.data.type,camera.data.ortho_scale='ORTHO',scale
        scene.render.filepath=str(EVIDENCE/f'{name}.png')
        bpy.ops.render.render(write_still=True)
    camera.location,camera.rotation_euler=(0,0,47),(0,0,0)
    camera.data.type,camera.data.sensor_fit='PERSP','VERTICAL'
    camera.data.angle=math.radians(42)
    scene.render.filepath=str(EVIDENCE/'overhead_47m_42deg.png')
    bpy.ops.render.render(write_still=True)
    # An isolated review swatch layout only, not an authored world or duplicated export.
    bpy.data.objects['D03ApartmentFamily08_Mesh'].hide_render=True
    model=bpy.data.objects['D03CommunityGraphics02_Mesh']
    root.location=(0,0,0)
    model.hide_render=True
    for number,(x,z) in zip(('01','02','03','04'),((.37,1.8),(-.37,1.8),(.37,1.25),(-.37,1.25))):
        obj=model.copy()
        obj.data=model.data.copy()
        obj.parent=None
        obj.location=(x,6,z)
        obj.hide_render=False
        scene.collection.objects.link(obj)
        mat=model.data.materials[0].copy()
        tex=mat.node_tree.nodes['CommittedAlbedo']
        tex.image=bpy.data.images.load(str(ROOT/f'art/textures/environment/{NID}/entrance_{number}_albedo.png'))
        obj.data.materials[0]=mat
    camera.location=(0,12,1.6)
    camera.rotation_euler=(Vector((0,6,1.53))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type,camera.data.ortho_scale='ORTHO',2.1
    scene.render.filepath=str(EVIDENCE/'detail.png')
    bpy.ops.render.render(write_still=True)
    assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE,BAY)]
    print('ENTRANCE_PREVIEW_PASS: four renders; original and shared sources unchanged')


if __name__=='__main__':
    main()
