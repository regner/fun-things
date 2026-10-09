"""Export both lens appearances from the saved, explicit city_lights_01 collection."""
import bpy, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
assert bpy.app.version_string == '5.2.2 LTS', bpy.app.version_string
import io_scene_gltf2
print('EXPORTER', io_scene_gltf2.bl_info)
assert io_scene_gltf2.bl_info['version'] == (5,2,40)
settings=json.loads((ROOT/'tools/assets/blender/export_settings.json').read_text())
settings.update(collection='export_city_lights_01',export_animations=False,export_skins=False)
outdir=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else ROOT/'art/models/environment/city_lights_01'
outdir.mkdir(parents=True,exist_ok=True)
obj=bpy.data.objects['CityLights01_Mesh']
slot=next(s for s in obj.material_slots if s.material.name=='lens_warm')
for variant in ('warm','cool'):
    slot.material=bpy.data.materials['lens_'+variant]
    settings['filepath']=str(outdir/f'city_lights_01_{variant}.glb')
    bpy.ops.export_scene.gltf(**settings)
slot.material=bpy.data.materials['lens_warm']
