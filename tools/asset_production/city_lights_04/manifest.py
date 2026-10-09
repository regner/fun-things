"""Fingerprint exact producer artifacts only; Godot sidecars belong to the integrator."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'docs/assets/production/city_lights_04-evidence'
paths=[ROOT/'docs/assets/production/city_lights_04.md']
for directory in ['art/source/models/environment/city_lights_04','art/models/environment/city_lights_04','tools/asset_production/city_lights_04','docs/assets/production/city_lights_04-evidence']:
    paths.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and not p.name.endswith(('.import','.pyc','.blend1')) and p.name!='manifest.json')
records=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(paths))]
(E/'manifest.json').write_text(json.dumps({'producer':'city_lights.04 original Blender specialist','workspace':str(ROOT),'exclusions':['manifest self-hash','integrator-owned .import sidecars','Python bytecode','Blender backup already retained in initial_visual_failure.zip'],'files':records},indent=2)+'\n')
print(json.dumps([r for r in records if r['path'].startswith('art/')],indent=2))
