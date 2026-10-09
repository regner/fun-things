"""Write exact candidate inventory, including retained failure evidence, excluding self."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_planting_05-evidence'
roots=[R/'art/source/models/environment/city_planting_05',R/'art/models/environment/city_planting_05',R/'tools/asset_production/city_planting_05',E]
files=[R/'docs/assets/production/city_planting_05.md']
for root in roots:files.extend(p for p in root.rglob('*') if p.is_file() and p!=E/'manifest.json')
rows=[]
for p in sorted(files):
    assert not p.is_symlink()
    rows.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(E/'manifest.json').write_text(json.dumps({'asset_id':'city_planting.05','status':'source_export_candidate_pending_engine_and_independent_acceptance','excluded_self':'docs/assets/production/city_planting_05-evidence/manifest.json','files':rows},indent=2)+'\n')
print('MANIFEST',len(rows),'files',sum(r['bytes'] for r in rows),'bytes')
