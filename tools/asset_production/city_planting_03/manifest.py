"""Fingerprint only this producer's scoped deliverables, excluding this manifest."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_planting_03-evidence'
files=[R/'docs/assets/production/city_planting_03.md']
for folder in ['art/source/models/environment/city_planting_03','art/models/environment/city_planting_03','tools/asset_production/city_planting_03','docs/assets/production/city_planting_03-evidence']:
    files.extend(p for p in (R/folder).rglob('*') if p.is_file() and p!=E/'manifest.json')
entries=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(files))]
(E/'manifest.json').write_text(json.dumps({'producer':'city_planting.03 assigned specialist','scope':'Complete owned path-byte-SHA256 delivery; manifest excludes itself','files':entries},indent=2)+'\n')
print(f'MANIFEST: {len(entries)} files')
