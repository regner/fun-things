"""Author a clearly labelled technical mounting wall; never modify production sources."""
import bpy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'tests/assets/asset_production/batch_03_upper_wall'
OUT.mkdir(exist_ok=True)
assert bpy.app.version == (5, 2, 2)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new('export_batch_03_upper_wall')
bpy.context.scene.collection.children.link(collection)
material = bpy.data.materials.new('Technical mounting fixture warm grey')
material.diffuse_color = (.35, .37, .34, 1)
material.use_backface_culling = True
# Four independent solid pieces leave a real 4.680 x 1.480m opening.
boxes = [(-3.2, -2.34, 4.3, 7.3), (2.34, 3.2, 4.3, 7.3),
         (-2.34, 2.34, 4.3, 4.71), (-2.34, 2.34, 6.19, 7.3)]
for i, (left, right, bottom, top) in enumerate(boxes):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((left + right)/2, -.14, (bottom+top)/2))
    obj = bpy.context.object
    obj.name = f'Technical_mount_wall_{i}'
    obj.dimensions = (right-left, .28, top-bottom)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for c in list(obj.users_collection): c.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(material)
root = bpy.data.objects.new('batch_03_upper_wall', None)
collection.objects.link(root)
for obj in list(collection.objects):
    if obj.type == 'MESH': obj.parent = root
source = ROOT / 'art/source/models/spikes/batch_03_upper_wall'
source.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(source/'batch_03_upper_wall.blend'))
bpy.ops.object.select_all(action='DESELECT')
for obj in collection.all_objects: obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'batch_03_upper_wall.glb'), export_format='GLB',
                          use_selection=True, export_yup=True, export_cameras=False,
                          export_lights=False, export_animations=False)
(OUT/'authoring.json').write_text(json.dumps({'pin':bpy.app.version_string,
    'build_hash':bpy.app.build_hash.decode(), 'purpose':'Technical mounting comparison, not a district asset or accepted shell extension',
    'bounds_blender': [[-3.2,-.28,4.3],[3.2,0,7.3]], 'opening_blender_xz':[-2.34,2.34,4.71,6.19],
    'window_mount_blender':[0,0,4.65], 'rear_void_m':.28,
    'axis_map':'(X,Y,Z) -> (X,Z,-Y)', 'fixtures_only':True},indent=2)+'\n')
