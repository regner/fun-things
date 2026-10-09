"""Exact owned file inventory; manifest excludes itself, never scans shared files."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[3]
E=R/'docs/assets/production/city_shop_fittings_06-evidence'
roots=[R/'art/source/models/environment/city_shop_fittings_06',R/'art/models/environment/city_shop_fittings_06',R/'art/materials/environment/city_shop_fittings_06',R/'art/textures/environment/city_shop_fittings_06',R/'tools/asset_production/city_shop_fittings_06',E]
files={p for root in roots if root.exists() for p in root.rglob('*') if p.is_file()}
files.add(R/'docs/assets/production/city_shop_fittings_06.md'); files.discard(E/'manifest.json')
records=[]
for p in sorted(files):
    assert not p.is_symlink()
    blob=p.read_bytes(); records.append(dict(path=str(p.relative_to(R)),bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest()))
out=dict(scope='city_shop_fittings.06 exact owned inventory',excludes=['docs/assets/production/city_shop_fittings_06-evidence/manifest.json'],files=records)
(E/'manifest.json').write_text(json.dumps(out,indent=2)+'\n')
for row in records:
    p=R/row['path']; assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
print('MANIFEST_VERIFIED',len(records),'files',sum(x['bytes'] for x in records),'bytes')
