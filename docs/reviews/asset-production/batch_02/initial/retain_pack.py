"""Retain the complete expected review set and verify bytes without copying old evidence."""
import hashlib
import json
from pathlib import Path

R=Path(__file__).resolve().parent
S=Path('/tmp/batch02-review-5e94cc0/snapshot')
C='5e94cc0ea4155219285db49c64b5728e0882b093'
assets=['city_planting_03','city_planting_04','city_planting_05',
        'city_roof_details_01','city_roof_details_02','city_shop_fittings_01']
roots=['city_planting_03','city_planting_04_compact','city_planting_04_broad',
       'city_planting_05_short_tuft','city_planting_05_spreading_clump',
       'city_roof_details_01','city_roof_details_02','city_shop_fittings_01']


def fingerprint(path):
    data=path.read_bytes()
    return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def git_blob(path):
    data=path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


shared=set(['AGENTS.md','.agents/skills/art-review/SKILL.md',
    '.agents/skills/paseo-orchestrator/SKILL.md',
    '.agents/skills/paseo-orchestrator/references/reviewer.md',
    'docs/assets/production/commission.md','docs/assets.md','docs/art-direction.md',
    'docs/world-layout.md','docs/scene-structure.md','docs/design.md','TODO.md',
    'docs/spikes/s01.md','docs/asset-catalogue.md','art/source/.gdignore',
    'docs/assets/city_planting.md','docs/assets/city_roof_details.md',
    'docs/assets/city_shop_fittings.md','docs/assets/city_small_shop_shells.md',
    'docs/assets/production/city_planting_01.md','docs/assets/production/city_planting_02.md',
    'docs/assets/production/batch_02-evidence/source-readback.json',
    'docs/concepts/districts-v1/brief-contract.md',
    'docs/concepts/world-v1/stage-03-district-identities/README.md',
    'docs/concepts/p0-04/f-roof-shapes.png','docs/concepts/districts-v1/06-signal-row-v03.png',
    'docs/concepts/districts-v1/08-ironreach-v02.png',
    'art/models/environment/city_planting_01/city_planting_01.glb',
    'art/models/environment/city_planting_02/city_planting_02.glb',
    'art/models/characters/coral_courier/coral_courier.glb',
    'art/models/brackett_greybox/shop.glb'])
for name in ('signal-row','ironreach','glassward','broadlot','old-quay','the-crescents','northpoint'):
    shared.update([f'docs/concepts/districts-v1/{name}.md',
                   f'docs/concepts/districts-v1/{name}-assets.md'])
for row in json.loads((R/'reference-audit.json').read_text())['producer_reference_checks']:
    shared.add(row['path'])
(R/'shared-input-index.json').write_text(json.dumps([
    {'revision':C,'path':p,'git_blob':git_blob(S/p),**fingerprint(S/p)}
    for p in sorted(shared)],indent=2)+'\n')

commands=['candidate-tree','parent-tree','delta-parent','delta-original-base',
          'candidate-whitespace','blender-pin','binary-audit','binary-audit-adapted',
          'reference-audit','calibration-source','reverse-consumers',
          'owned-authoring-provenance','mounting-and-calibration-claims']
commands += [asset+'-source' for asset in assets]
commands += [asset+'-source-adapted' for asset in assets[1:]]
executions=[]
for name in commands:
    receipt=json.loads((R/(name+'.command.json')).read_text())
    sources=[]
    if '-source' in name and name not in ('calibration-source',):
        sources=['source_audit.py' if 'adapted' in name else 'source_audit-first.py']
    elif name.startswith('binary-audit'):
        sources=['glb_audit.py']
    elif name=='calibration-source':
        sources=['calibration_source.py']
    elif name=='reference-audit':
        sources=['reference_audit.py','run_checks.py']
    executions.append({'command':name,'receipt':name+'.command.json',
        'exit':receipt['exit'],'check_sources':[{'path':p,**fingerprint(R/p)} for p in sources],
        'stdout':{'path':name+'.stdout',**fingerprint(R/(name+'.stdout'))},
        'stderr':{'path':name+'.stderr',**fingerprint(R/(name+'.stderr'))}})
(R/'execution-check-sources.json').write_text(json.dumps(executions,indent=2)+'\n')
(R/'wrapper-invocations.json').write_text(json.dumps([
    {'argv':['python','docs/reviews/asset-production/batch_02/initial/'+script],
     'cwd':'/home/regner/.paseo/worktrees/0u71f39f/asset-register-production',
     'stdout':prefix+'.stdout','stderr':prefix+'.stderr','observed_exit':0,
     'timing':'not captured by outer shell; subprocess receipts retain actual UTC times',
     'note':'outer driver exit does not replace per-check exit inspection'}
    for script,prefix in [('run_checks.py','runner'),('adapt_checks.py','adaptation'),
                          ('final_checks.py','final-checks')]],indent=2)+'\n')

expected=set(['run_checks.py','source_audit.py','source_audit-first.py','glb_audit.py',
    'glb_audit-first.py','adapt_checks.py','reference_audit.py','calibration_source.py',
    'final_checks.py','retain_pack.py','report.md','candidate-payload-index.json',
    'retention-check.json','binary-audit.json','reference-audit.json','calibration-source.json',
    'shared-input-index.json','execution-check-sources.json','wrapper-invocations.json',
    'runner.stdout','runner.stderr','adaptation.stdout','adaptation.stderr',
    'final-checks.stdout','final-checks.stderr','artifact-expected-set.json',
    'artifact-index.json','artifact-verification.json'])
for name in commands:
    expected.update(name+suffix for suffix in ('.command.json','.stdout','.stderr'))
expected.update(asset+'-source.json' for asset in assets)
expected.update(root+suffix for root in roots for suffix in ('-fresh.glb','-fresh-source.png'))
# Bytecode is execution cache, not an evidence payload; remove only this review cache.
for p in R.glob('__pycache__/*.pyc'):
    p.unlink()
cache=R/'__pycache__'
if cache.exists() and not list(cache.iterdir()):
    cache.rmdir()
(R/'artifact-expected-set.json').write_text(json.dumps({'scope':'initial review only',
    'paths':sorted(expected),'self_index_policy':
    'Index excludes itself and its verification receipt; verification hashes both index and expected set.'},indent=2)+'\n')
indexed=expected-{'artifact-index.json','artifact-verification.json'}
missing=sorted(p for p in indexed if not (R/p).is_file())
assert not missing, missing
rows=[{'path':p,**fingerprint(R/p)} for p in sorted(indexed)]
(R/'artifact-index.json').write_text(json.dumps({'candidate':C,'files':rows},indent=2)+'\n')
actual={str(p.relative_to(R)) for p in R.rglob('*') if p.is_file()}
actual.add('artifact-verification.json')
assert actual==expected, {'missing':sorted(expected-actual),'extra':sorted(actual-expected)}
for row in rows:
    assert fingerprint(R/row['path'])=={k:row[k] for k in ('bytes','sha256')}
(R/'artifact-verification.json').write_text(json.dumps({'expected_count':len(expected),
    'indexed_count':len(rows),'complete_expected_set_matches':True,
    'all_indexed_bytes_and_sha256_match':True,'missing':[],'extra':[],
    'artifact_index':fingerprint(R/'artifact-index.json'),
    'artifact_expected_set':fingerprint(R/'artifact-expected-set.json')},indent=2)+'\n')
