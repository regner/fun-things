import json,pathlib,hashlib,subprocess
O=pathlib.Path(__file__).resolve().parent;r=json.loads((O/'candidate-file-index.json').read_text());root=pathlib.Path.cwd();src=json.loads((root/'docs/assets/production/batch_03-evidence/source-readback.json').read_text());historical=json.loads(subprocess.check_output(['git','show',r['initial']+':docs/assets/production/batch_03-evidence/source-readback.json']));assert src==historical
checks=dict(historical_source_receipt_unchanged=True,current594_payloads601_with_manifests=True,engine300_index297_delta3_unchanged_receipts=True,initial_pack_bytes_preserved=True)
for rows in ['producer_files','engine_files']:
 assert all(e['working_matches'] and e.get('expected_matches',True) for e in r[rows])
assert len(r['producer_files'])==601 and len(r['engine_files'])==300
assert not r['engine_delta_missing'] and len(r['engine_delta_extra'])==3
assert set(src['exact_frozen_paths']).issubset(set(r['producer_expected_paths']))
for e in r['initial_immutable_references']:
 b=(root/e['path']).read_bytes();assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
(O/'readback-confirmation.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks))
