"""Export the sole declared member from the saved source, without authoring geometry."""
import json
import sys
from pathlib import Path

import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
output = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
assert bpy.app.version_string == '5.2.2 LTS'
assert bpy.app.build_hash == b'd13f752e3b9c'
assert io_scene_gltf2.bl_info['version'] == (5, 2, 40)
assert Path(bpy.data.filepath) == ROOT / 'art/source/models/spikes/s05_explosion_carrier.blend'
collection = bpy.data.collections['export_s05_explosion_carrier']
assert sorted(o.name for o in collection.all_objects) == ['ExplosionCarrier']
obj = collection.objects['ExplosionCarrier']
assert obj.type == 'MESH' and not obj.modifiers
assert tuple(obj.location) == (0, 0, 0) and tuple(obj.scale) == (1, 1, 1)
assert tuple(obj.rotation_euler) == (0, 0, 0)
assert bpy.context.scene.unit_settings.system == 'METRIC'
assert bpy.context.scene.unit_settings.scale_length == 1
settings = json.loads((ROOT / 'tools/s01/export_settings.json').read_text())
settings.update(collection=collection.name, filepath=str(output), export_animations=False,
                export_skins=False, export_texcoords=False)
assert not output.exists(), 'Never overwrite an export'
bpy.ops.export_scene.gltf(**settings)
print('S05_EXPORT_SETTINGS', json.dumps(settings, sort_keys=True))
print('S05_EXPORT_SAVED', output, io_scene_gltf2.bl_info['version'])
