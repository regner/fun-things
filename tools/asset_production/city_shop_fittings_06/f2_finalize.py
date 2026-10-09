"""Validate bounded F2 delta, immutable interfaces and unchanged non-ring GLB payloads."""
import json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[3];E=R/'docs/assets/production/city_shop_fittings_06-evidence/fix_f2'
before=json.loads((E/'preservation_before.json').read_text())
for path,h in (before['immutable_03_inputs']|before['importer_sidecars']).items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h,path
old=json.loads((E/'before/manifest.json').read_text());changed=[];unchanged=[]
for row in old['files']:
    p=R/row['path'];assert p.exists(),row['path']
    (unchanged if hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'] else changed).append(row['path'])
allowed={'art/source/models/environment/city_shop_fittings_06/city_shop_fittings_06.blend','art/models/environment/city_shop_fittings_06/city_shop_fittings_06_single.glb','art/models/environment/city_shop_fittings_06/city_shop_fittings_06_double.glb','docs/assets/production/city_shop_fittings_06.md','docs/assets/production/city_shop_fittings_06-evidence/fitted_comparison.blend'}|{'tools/asset_production/city_shop_fittings_06/'+f for f in ['author.py','export.py','check_glb.py','assembly.py','preview.py','manifest.py']}
assert set(changed)<=allowed,changed

def decode(p):
    data=p.read_bytes();size=struct.unpack_from('<I',data,12)[0];d=json.loads(data[20:20+size]);binary=data[28+size:]
    def acc(i):
        a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];n={'SCALAR':1,'VEC3':3}[a['type']];fmt={5123:'H',5125:'I',5126:'f'}[a['componentType']]*n;step=struct.calcsize('<'+fmt);start=v.get('byteOffset',0)+a.get('byteOffset',0)
        return [struct.unpack_from('<'+fmt,binary,start+j*v.get('byteStride',step)) for j in range(a['count'])]
    payload={}
    for node in d['nodes']:
        if 'mesh' not in node:continue
        payload[node['name']]=[dict(attributes={k:acc(v) for k,v in prim['attributes'].items()},indices=acc(prim['indices']),material=d['materials'][prim['material']]) for prim in d['meshes'][node['mesh']]['primitives']]
    return d,payload
variants=[]
for v in ['single','double']:
    name='city_shop_fittings_06_'+v+'.glb'
    prior=R/'docs/reviews/asset-production/batch_03/initial/reexports'/name
    current=R/'art/models/environment/city_shop_fittings_06'/name
    a,ap=decode(prior);b,bp=decode(current);assert a['materials']==b['materials']
    stable=[n for n in ap if not n.endswith('_stiles_rails')]
    for n in stable:assert ap[n]==bp[n],n
    assert current.read_bytes()==(E/'reexports'/name).read_bytes()
    variants.append(dict(variant=v,unchanged_mesh_payloads=stable,materials_identical=True,byte_identical_saved_source_reexport=True,bytes=current.stat().st_size,sha256=hashlib.sha256(current.read_bytes()).hexdigest()))
source=R/'art/source/models/environment/city_shop_fittings_06/city_shop_fittings_06.blend'
(E/'preservation_after.json').write_text(json.dumps(dict(immutable_candidate=before['immutable_candidate'],source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),changed_prior_paths=changed,unchanged_prior_paths=unchanged,no_historical_payload_removed=True,immutable_03_and_sidecars_unchanged=True,variants=variants),indent=2)+'\n')
print('BOUNDED_DELTA_IMMUTABLE_03_SIDECARS_AND_NONRING_PAYLOADS_PASS')
