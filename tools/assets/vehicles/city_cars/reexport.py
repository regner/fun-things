"""Reexport only declared collections from saved vehicle sources, never bootstrap geometry."""
import json
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[4]
OUTPUT = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
OUTPUT.mkdir(parents=True, exist_ok=True)
assert bpy.app.version_string == '5.2.2 LTS'
settings = json.loads((ROOT / 'tools/s01/export_settings.json').read_text())
settings.update(export_animations=False, export_skins=False)
for record_path in sorted((ROOT / 'docs/assets/vehicle_car_evidence').glob('car_*_a_source.json')):
    record = json.loads(record_path.read_text())
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / record['source']))
    collection = bpy.data.collections[record['collection']]
    assert sorted(obj.name for obj in collection.all_objects) == record['members']
    assert bpy.context.scene.unit_settings.scale_length == 1
    for obj in collection.all_objects:
        assert all(abs(v - 1) < 0.0001 for v in obj.scale), obj.name
        assert obj.matrix_world.determinant() > 0, obj.name
        assert not obj.modifiers if obj.type == 'MESH' else True, obj.name
    settings.update(collection=collection.name, filepath=str(OUTPUT / (record['id'] + '.glb')))
    bpy.ops.export_scene.gltf(**settings)
    print('VEHICLE_REEXPORT', record['id'], flush=True)
