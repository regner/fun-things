"""Record exact owned handoff file bytes; manifest excludes its own recursive hash."""
from pathlib import Path
import hashlib, json
R=Path(__file__).resolve().parents[3]
E=R/'docs/assets/production/city_shop_fittings_01-evidence'
roots=[R/'art/source/models/environment/city_shop_fittings_01',
       R/'art/models/environment/city_shop_fittings_01',
       R/'tools/asset_production/city_shop_fittings_01', E]
files=[R/'docs/assets/production/city_shop_fittings_01.md']
for root in roots:
    files.extend(p for p in root.rglob('*') if p.is_file() and p.name!='manifest.json')
rows=[dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,
           sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(files)]
(E/'manifest.json').write_text(json.dumps(dict(asset='city_shop_fittings.01',
    scope='Exact owned deliverables, including initial failure/fix evidence; excludes this manifest itself',
    files=rows),indent=2)+'\n')
print('MANIFEST',len(rows),'files')
