"""Trace actual source fixtures, immutable inputs, reverse consumers and candidate bytes."""
from run_checks import CANDIDATE, IDS, REVIEW, SNAPSHOT, REPO, index, run
import hashlib
import json
from pathlib import Path

payloads=json.loads((REVIEW/'candidate-payload-index.json').read_text())
blob_errors=[]
for row in payloads:
    data=(SNAPSHOT/row['path']).read_bytes()
    actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if actual!=row['git_blob']:
        blob_errors.append(row['path'])
assert not blob_errors
tree=json.loads((REVIEW/'retention-check.json').read_text())
assert all(not r['omitted'] and not r['extra'] and not r['mismatches'] for r in tree)
refs=[]
for asset in IDS:
    ep=SNAPSHOT/f'docs/assets/production/{asset}-evidence'
    for name in ('reference_inputs.json','input_references.json'):
        p=ep/name
        if not p.exists():
            continue
        document=json.loads(p.read_text())
        rows=document if isinstance(document,list) else document.get('reference_files',document.get('inputs',[]))
        for row in rows:
            if not isinstance(row,dict) or 'path' not in row or 'sha256' not in row:
                continue
            target=SNAPSHOT/row['path']
            actual=index(target) if target.is_file() else None
            refs.append({'asset':asset,'receipt':str(p.relative_to(SNAPSHOT)),
                         'path':row['path'],'recorded':row,'candidate_actual':actual,
                         'matches_candidate':actual is not None and actual['sha256']==row['sha256']})
result={'revision':CANDIDATE,'candidate_payload_git_blob_errors':blob_errors,
        'source_gdignore':index(SNAPSHOT/'art/source/.gdignore'),'producer_reference_checks':refs}
run('reverse-consumers',['rg','-n',r'city_(planting_0[345]|roof_details_0[12]|shop_fittings_01)',
    'scenes','scripts','art/materials','art/textures','docs/asset-catalogue.md'])
run('owned-authoring-provenance',['rg','-n',r'provenance|from_pydata|primitive_|import_scene|libraries|load\(|bpy.ops.wm.save',
    *[f'tools/asset_production/{asset}/author.py' for asset in IDS]])
run('mounting-and-calibration-claims',['rg','-n',r'reference|camera|lens|sensor|dimensions|hash|location|scale',
    *[f'tools/asset_production/{asset}/'+('assembly_preview.py' if asset in ('city_planting_03','city_planting_04') else 'preview.py') for asset in IDS]])
(REVIEW/'reference-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('REFERENCE_AUDIT_COMPLETE',len(refs),'receipts',sum(not r['matches_candidate'] for r in refs),'historical differences')
