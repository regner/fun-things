"""Exact owned delivery inventory; no Git/index access. Manifest excludes itself only."""
import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_02-evidence'
roots=[R/'art/source/models/environment/city_shop_fittings_02',R/'art/models/environment/city_shop_fittings_02',R/'art/materials/environment/city_shop_fittings_02',R/'art/textures/environment/city_shop_fittings_02',R/'tools/asset_production/city_shop_fittings_02',E]
files=[R/'docs/assets/production/city_shop_fittings_02.md']
for root in roots:
    if root.exists():files.extend(p for p in root.rglob('*') if p.is_file() and p!=E/'manifest.json')
actual=[dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(files)]
if '--verify' in sys.argv:
    expected=json.loads((E/'manifest.json').read_text());assert actual==expected['files'];print('MANIFEST_PASS',len(actual),'files')
else:
    (E/'manifest.json').write_text(json.dumps(dict(asset_id='city_shop_fittings.02',scope='Exact owned files; initial/ is historical evidence; manifest excludes itself only',files=actual),indent=2)+'\n');print('MANIFEST_WRITTEN',len(actual),'files')
