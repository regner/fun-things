"""Fingerprint the complete owned producer file set; manifest itself is excluded."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'docs/assets/production/city_sign_supports_01-evidence'
paths=['art/source/models/environment/city_sign_supports_01','art/models/environment/city_sign_supports_01','tools/asset_production/city_sign_supports_01','docs/assets/production/city_sign_supports_01-evidence']
manifest=E/'manifest.json'
files=[ROOT/'docs/assets/production/city_sign_supports_01.md']
for owned in paths:
    files.extend(p for p in (ROOT/owned).rglob('*') if p.is_file() and p!=manifest)
assert not any(p.is_symlink() for p in files)
result={'asset_id':'city_sign_supports.01','scope':'complete producer file set at handoff; no runtime .import sidecars produced','self_exclusion':str(manifest.relative_to(ROOT))+' (self-hashing exclusion; receipt hash supplied with handoff)','files':{str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)}}
manifest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'manifest':str(manifest.relative_to(ROOT)),'bytes':manifest.stat().st_size,'sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'listed_files':len(files),'total_payload_bytes':sum(v['bytes'] for v in result['files'].values())}))
