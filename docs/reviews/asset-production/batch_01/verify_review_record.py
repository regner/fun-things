"""Check retained review record completeness and declared numeric conclusions."""
import json
from pathlib import Path
p=Path(__file__).resolve().parent
fresh=json.loads((p/'fresh-export-comparison.json').read_text())
assert len(fresh)==9 and all(x['byte_identical'] and x['export_exit']==0 for x in fresh)
assert len(json.loads((p/'independent-source-inspection.json').read_text())['assets'])==6
manifests=json.loads((p/'independent-manifest-check.json').read_text())
assert sum(x['declared_count'] for x in manifests)==171
assert all(not x['hash_byte_mismatches'] and x['readback_count_matches'] and x['readback_manifest_hash_matches'] for x in manifests)
assert len(json.loads((p/'candidate-scope-file-index.json').read_text()))==180
assert all(x['max_contract_deviation_m']<=.001 for x in json.loads((p/'independent-model-bounds.json').read_text()))
for c in json.loads((p/'commands.json').read_text()):
 for suffix in ['stdout.log','stderr.log']:assert (p/(c['label']+'.'+suffix)).exists()
print('PASS: 6 sources, 9 exact reexports, 171 declared retained files, 180 scoped candidate files, all bounds within tolerance, all recorded check streams present.')
