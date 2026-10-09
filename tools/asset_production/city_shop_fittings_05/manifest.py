"""Exact owned file/byte/SHA manifest, excluding only this self-referential manifest."""
import json,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_05-evidence';out=E/'manifest.json'
roots=[R/'art/source/models/environment/city_shop_fittings_05',R/'art/models/environment/city_shop_fittings_05',R/'art/materials/environment/city_shop_fittings_05',R/'art/textures/environment/city_shop_fittings_05',R/'tools/asset_production/city_shop_fittings_05',E]
files=sorted([p for root in roots for p in root.rglob('*') if p.is_file() and p!=out]+[R/'docs/assets/production/city_shop_fittings_05.md'])
rows=[dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]
if '--verify' in sys.argv:
    assert json.loads(out.read_text())==rows;print('MANIFEST_VERIFY_PASS',len(rows))
else:out.write_text(json.dumps(rows,indent=2)+'\n');print('MANIFEST_WRITTEN',len(rows))
