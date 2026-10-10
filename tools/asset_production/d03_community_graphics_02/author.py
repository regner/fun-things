"""Original full-scale entrance plaque; approved dedicated carrier rather than scaled hardware."""
import importlib.util
import math
import sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[3]
NID='d03_community_graphics_02'
SOURCE=ROOT/f'art/source/models/environment/{NID}/{NID}.blend'
spec=importlib.util.spec_from_file_location('court_author',ROOT/'tools/asset_production/d03_court_graphics_02/author.py')
shared=importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)


def main():
    """Build one bevelled closed plaque with a planar front UV slot and wall-contact pivot."""
    assert bpy.app.version_string=='5.2.2 LTS'
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene
    scene.unit_settings.system='METRIC'
    scene.unit_settings.scale_length=1
    collection=bpy.data.collections.new('export_'+NID)
    scene.collection.children.link(collection)
    root=bpy.data.objects.new('D03CommunityGraphics02',None)
    collection.objects.link(root)
    root['asset_id']='d03_community_graphics.02'
    root['provenance']='Original commissioned Blender construction and original Pillow artwork'
    root['mount']='Wall-centred pivot; Godot (0.785,1.85,-6) on entrance bay; never scale'
    # A rounded rectangle outline, three profile rings give 3 mm face/back bevels.
    vertices=[]
    for depth,inset in ((0,.003),(.003,0),(.029,0),(.032,.003)):
        radius=.018-inset
        for cx,cz,start in ((.262,.182,0),(-.262,.182,90),(-.262,-.182,180),(.262,-.182,270)):
            for step in range(5):
                angle=math.radians(start+step*22.5)
                vertices.append((cx+radius*math.cos(angle),depth,cz+radius*math.sin(angle)))
    count=20
    faces=[tuple(range(count))] # +Y is clockwise in XZ: back normal -Y.
    for ring in range(3):
        for i in range(count):
            j=(i+1)%count
            faces.append((ring*count+i,(ring+1)*count+i,(ring+1)*count+j,ring*count+j))
    faces.append(tuple(reversed(range(3*count,4*count))))
    mesh=bpy.data.meshes.new('D03CommunityGraphics02_Geometry')
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new('D03CommunityGraphics02_Mesh',mesh)
    collection.objects.link(obj)
    obj.parent=root
    face=shared.material('entrance_number_face','587D7C',.84)
    body=shared.material('entrance_plaque_edge','294B50',.6)
    mesh.materials.append(face)
    mesh.materials.append(body)
    for polygon in mesh.polygons:
        polygon.material_index=0 if polygon.normal.y>.999 else 1
    uv=mesh.uv_layers.new(name='UVMap')
    for loop in mesh.loops:
        p=mesh.vertices[loop.vertex_index].co
        uv.data[loop.index].uv=((.28-p.x)/.56,(p.z+.2)/.4)
    image=face.node_tree.nodes.new('ShaderNodeTexImage')
    image.name='CommittedAlbedo'
    image.image=bpy.data.images.load(str(ROOT/f'art/textures/environment/{NID}/entrance_01_albedo.png'))
    image.extension='EXTEND'
    face.node_tree.links.new(image.outputs['Color'],face.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    # Only an invisible metre reference is saved; preview composes existing entrance source.
    bpy.ops.mesh.primitive_cube_add(size=1,location=(2,0,.5))
    bpy.context.object.name='STUDIO_one_metre_reference'
    bpy.context.object.hide_render=True
    SOURCE.parent.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    sys.path.insert(0,str(Path(__file__).parent))
    from export import export_plaque
    export_plaque(ROOT/f'art/models/environment/{NID}')
    print('ENTRANCE_SOURCE_AUTHORED')


if __name__=='__main__':
    main()
