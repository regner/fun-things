"""Exact producer-owned delivery set; importer sidecars remain integrator-owned."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_roof_details_01-evidence'
manifest=E/'manifest.json'
roots=[R/'art/source/models/environment/city_roof_details_01',R/'art/models/environment/city_roof_details_01',R/'tools/asset_production/city_roof_details_01',E]
paths=[R/'docs/assets/production/city_roof_details_01.md']
for root in roots:
    paths.extend(p for p in root.rglob('*') if p.is_file() and p!=manifest and p.suffix!='.import' and '__pycache__' not in p.parts)
entries=[dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(paths)]
manifest.write_text(json.dumps(dict(asset_id='city_roof_details.01',scope='Exact producer expected files; excludes this manifest and integrator-owned .import sidecars',files=entries),indent=2)+'\n')
for entry in entries:
    p=R/entry['path']; assert p.stat().st_size==entry['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256']
print('MANIFEST_VERIFIED',len(entries),'files',sum(v['bytes'] for v in entries),'bytes')
