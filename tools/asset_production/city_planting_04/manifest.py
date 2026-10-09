"""Exact producer-owned payload manifest, excluding only this manifest itself."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_planting_04-evidence'
owned=['art/source/models/environment/city_planting_04','art/models/environment/city_planting_04','tools/asset_production/city_planting_04','docs/assets/production/city_planting_04.md','docs/assets/production/city_planting_04-evidence']
rows=[]
for rel in owned:
 p=R/rel
 for f in ([p] if p.is_file() else sorted(p.rglob('*'))):
  if not f.is_file() or f==E/'manifest.json' or '__pycache__' in f.parts:continue
  rows.append({'path':str(f.relative_to(R)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(E/'manifest.json').write_text(json.dumps({'asset':'city_planting.04','scope':'producer payload; excludes manifest itself and Python cache; importer-owned .import sidecars are not producer outputs','files':rows},indent=2)+'\n')
print(len(rows),'files manifested')
