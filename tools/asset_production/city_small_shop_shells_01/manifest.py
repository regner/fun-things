"""Create or verify the exact owned deliverable inventory, excluding only itself."""
import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_small_shop_shells_01-evidence'; target=E/'manifest.json'
roots=[R/'art/source/models/environment/city_small_shop_shells_01',R/'art/models/environment/city_small_shop_shells_01',R/'art/materials/environment/city_small_shop_shells_01',R/'art/textures/environment/city_small_shop_shells_01',R/'tools/asset_production/city_small_shop_shells_01',E]
files=sorted([p for root in roots for p in root.rglob('*') if p.is_file() and p!=target]+[R/'docs/assets/production/city_small_shop_shells_01.md'])
entries=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
if '--verify' in sys.argv:
    assert json.loads(target.read_text())['files']==entries
    print('EXACT_MANIFEST_PASS',len(entries))
else:
    target.write_text(json.dumps({'asset':'city_small_shop_shells.01','exclusion':'manifest.json only, to avoid recursive self-hash','files':entries},indent=2)+'\n')
    print('MANIFEST_WRITTEN',len(entries))
