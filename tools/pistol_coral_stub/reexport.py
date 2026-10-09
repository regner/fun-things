"""Export the committed Coral Stub collection; never reconstruct the model."""
from pathlib import Path
import json
import sys
import bpy

ROOT = Path(__file__).resolve().parents[2]
manifest = json.loads((Path(__file__).parent / 'manifest.json').read_text())
assert bpy.app.version_string == '5.2.2 LTS', bpy.app.version_string
assert Path(bpy.data.filepath).resolve() == ROOT / manifest['source']
assert bpy.context.scene.unit_settings.scale_length == 1
collection = bpy.data.collections[manifest['collection']]
assert sorted(o.name for o in collection.all_objects) == manifest['members']
for obj in collection.all_objects:
    assert all(abs(v - 1) < .000001 for v in obj.scale), obj.name
    assert obj.matrix_world.determinant() > 0, obj.name
    assert not obj.modifiers, obj.name
settings = json.loads((ROOT / 'tools/s01/export_settings.json').read_text())
settings['export_animations'] = False
settings['collection'] = collection.name
out = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
out.parent.mkdir(parents=True, exist_ok=True)
settings['filepath'] = str(out)
bpy.ops.export_scene.gltf(**settings)
print('PISTOL_EXPORT', bpy.app.version_string, bpy.app.build_hash, out)
