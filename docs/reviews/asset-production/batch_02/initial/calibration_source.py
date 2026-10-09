"""Read actual source fixture geometry without changing any source file."""
import bpy
import hashlib
import json
from pathlib import Path
import sys

out=Path(sys.argv[sys.argv.index('--')+1])
root=Path('/tmp/batch02-review-5e94cc0/snapshot')
ids=['city_planting_03','city_planting_04','city_planting_05',
     'city_roof_details_01','city_roof_details_02','city_shop_fittings_01']
results=[]
for asset in ids:
    path=root/f'art/source/models/environment/{asset}/{asset}.blend'
    fingerprint=hashlib.sha256(path.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(path))
    bpy.context.view_layer.update()
    fixtures=[]
    for o in bpy.data.objects:
        if 'reference' not in o.name or o.type!='MESH':
            continue
        points=[o.matrix_world@v.co for v in o.data.vertices]
        lo=[min(p[i] for p in points) for i in range(3)]
        hi=[max(p[i] for p in points) for i in range(3)]
        fixtures.append({'object':o.name,'bounds':[lo,hi],
            'dimensions_m':[hi[i]-lo[i] for i in range(3)],
            'collections':[c.name for c in o.users_collection],
            'hide_render':o.hide_render,'hide_viewport':o.hide_viewport})
    results.append({'asset':asset,'source_sha256':fingerprint,
                    'source_fixture_geometry':fixtures,
                    'units':bpy.context.scene.unit_settings.system,
                    'scale_length':bpy.context.scene.unit_settings.scale_length})
    assert hashlib.sha256(path.read_bytes()).hexdigest()==fingerprint
(out/'calibration-source.json').write_text(json.dumps(results,indent=2)+'\n')
print('SOURCE_CALIBRATION_READBACK_COMPLETE')
