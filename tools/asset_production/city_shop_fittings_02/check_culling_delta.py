"""Assert raw GLB change is exclusively five doubleSided flags, with identical binary data."""
import hashlib,json,struct
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_02-evidence/f1_culling'
p=R/'art/models/environment/city_shop_fittings_02/city_shop_fittings_02.glb';b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);binary=b[28+n:]
old=json.loads((E/'pre_fix_glb.json').read_text());oldj=old['document'];flags=[]
assert len(j['materials'])==len(oldj['materials'])==5
for prior,current in zip(oldj['materials'],j['materials']):
    assert prior['name']==current['name'] and prior.pop('doubleSided') is True
    raw=current.pop('doubleSided',None);assert raw is None or raw is False
    flags.append(dict(name=current['name'],previous_doubleSided=True,raw_current_doubleSided=raw,effective_current_doubleSided=False))
assert oldj==j,'GLB JSON changed beyond material sidedness'
assert hashlib.sha256(binary).hexdigest()==old['binary_sha256']
assert b==(E/'reexport_city_shop_fittings_02.glb').read_bytes()
# Every old substantive evidence file stays present and byte-identical, including
# original reexports/checks/previews/logs; only manifest is replaced with a new inventory.
prior=json.loads((E/'pre_fix_manifest.json').read_text());preserved=[]
for item in prior['files']:
    if item['path'].startswith('docs/assets/production/city_shop_fittings_02-evidence/'):
        path=R/item['path'];assert path.stat().st_size==item['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'],item['path']
        preserved.append(item['path'])
result=dict(status='PASS',glb_sha256=hashlib.sha256(b).hexdigest(),glb_bytes=len(b),raw_material_flags=flags,only_material_doubleSided_changed=True,binary_positions_normals_uv_indices_byte_identical=True,binary_sha256=old['binary_sha256'],saved_source_reexport_byte_identical=True,unchanged_historical_evidence_files=preserved,immutable_rejected_candidate=old['candidate'])
(E/'raw_delta_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
