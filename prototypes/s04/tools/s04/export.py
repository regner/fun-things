"""Export declared S04 collections from the committed source; never recreate geometry."""
import json
import sys
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]
output = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
output.mkdir(parents=True, exist_ok=True)
assert bpy.app.version_string == '5.2.2 LTS', bpy.app.version_string
assert Path(bpy.data.filepath).name == 's04_kit.blend'
assert bpy.context.scene.unit_settings.scale_length == 1
members = json.loads((ROOT / 'tools/s04/export_members.json').read_text())
settings = json.loads((ROOT / 'tools/s01/export_settings.json').read_text())
settings['export_animations'] = False
for name, expected in members.items():
    collection = bpy.data.collections[name]
    assert sorted(obj.name for obj in collection.all_objects) == expected
    for obj in collection.all_objects:
        assert all(abs(v - 1) < .0001 for v in obj.scale), obj.name
        assert obj.matrix_world.determinant() > 0, obj.name
    settings['collection'] = name
    settings['filepath'] = str(output / (name.removeprefix('export_') + '.glb'))
    bpy.ops.export_scene.gltf(**settings)
    print('S04_EXPORT', name, expected)
