"""Re-export the open committed Blender source to a validated scratch GLB."""
import json
import sys
from pathlib import Path
import bpy

root = Path(__file__).resolve().parents[2]
asset = Path(bpy.data.filepath).stem
settings = json.loads((root / 'tools/s01/export_settings.json').read_text())
settings['collection'] = 'export_' + asset
settings['export_animations'] = asset == 's01_rig'
output = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
output.parent.mkdir(parents=True, exist_ok=True)
settings['filepath'] = str(output)
assert bpy.app.version_string == '5.2.2 LTS', bpy.app.version_string
assert settings['collection'] in bpy.data.collections
collection = bpy.data.collections[settings['collection']]
expected = {'Body', 'Front', 'Meter', 'socket_muzzle', 'right_axis', 'up_axis'} if asset == 's01_static' else {'Rig', 'Skin', 'socket_grip'}
assert {o.name for o in collection.all_objects} == expected
for obj in collection.all_objects:
    assert all(abs(v - 1) < .0001 for v in obj.scale), obj.name
    assert obj.matrix_world.determinant() > 0, obj.name
if asset == 's01_rig':
    assert set(bpy.data.actions.keys()) == {'idle', 'walk', 'run', 'death'}
    assert [b.name for b in bpy.data.objects['Rig'].data.bones] == ['root', 'hand']
    assert bpy.data.objects['Skin'].modifiers[0].type == 'ARMATURE'
import io_scene_gltf2
print('S01_EXPORTER', getattr(io_scene_gltf2, 'bl_info', {}))
assert bpy.context.scene.unit_settings.scale_length == 1
bpy.ops.export_scene.gltf(**settings)
assert output.is_file()
print('S01_EXPORT', asset, bpy.app.version_string, bpy.app.build_hash.decode())
