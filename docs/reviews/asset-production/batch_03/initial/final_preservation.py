"""Verify frozen buffers and retain context identity before the one final callback."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
OUT=Path(__file__).resolve().parent
CANDIDATE='028775618c4493ca672646e6e37fdc3c83e0e313'
sha=lambda b:hashlib.sha256(b).hexdigest()
index=json.loads((OUT/'frozen-file-index.json').read_text())
changed=[]
for e in index['files']:
    b=Path(e['path']).read_bytes()
    if len(b)!=e['bytes'] or sha(b)!=e['sha256']:changed.append(e['path'])
frozen_changed=[]
for e in index['files']:
    p=Path('/tmp/batch03-independent/frozen')/e['path']
    if p.exists() and (p.stat().st_size!=e['bytes'] or sha(p.read_bytes())!=e['sha256']):frozen_changed.append(e['path'])
contracts=['AGENTS.md','.agents/skills/art-review/SKILL.md',
 '.agents/skills/paseo-orchestrator/references/reviewer.md',
 'docs/assets/production/commission.md','docs/assets.md','docs/art-direction.md',
 'docs/world-layout.md','docs/scene-structure.md','docs/spikes/s01.md',
 'docs/assets/city_shop_fittings.md','docs/assets/city_small_shop_shells.md',
 'docs/assets/d06_commercial_graphics.md','docs/assets/d06_southern_shopping_parade.md',
 'docs/concepts/districts-v1/brief-contract.md','docs/concepts/districts-v1/the-crescents.md',
 'docs/concepts/districts-v1/old-quay.md','docs/concepts/districts-v1/broadlot.md',
 'docs/concepts/districts-v1/signal-row.md','docs/concepts/districts-v1/signal-row-assets.md',
 'docs/concepts/world-v1/stage-03-district-identities/README.md','mise.toml',
 'art/source/.gdignore','docs/assets/production/batch_03-evidence/source-readback.json']
images=['docs/concepts/districts-v1/'+n for n in ['06-signal-row-v03.png','02-the-crescents-v02.png','05-old-quay-v03.png']]
selected={'city_shop_fittings_02':['artwork_interface.png','rear_mounts.png'],
 'city_shop_fittings_03':['front_elevation.png'],
 'city_shop_fittings_05':['attachment_opening.png','rear_attachment.png'],
 'city_shop_fittings_06':['fitted_front.png'],
 'city_shop_fittings_07':['hero.png','mounting_detail.png'],
 'city_shop_fittings_08':['uv_positive_x.png','uv_negative_x.png','bracket_detail.png','elevation_design.png'],
 'city_small_shop_shells_01':['mounted_hero.png','rear_roof.png']}
for ident,names in selected.items():
    for n in names+['measured_1m_comparison.png']:images.append(f'docs/assets/production/{ident}-evidence/{n}')
context=[]
for p in contracts+images:
    b=subprocess.check_output(['git','show',CANDIDATE+':'+p])
    context.append(dict(path=p,bytes=len(b),sha256=sha(b),working_matches=Path(p).read_bytes()==b))
(OUT/'context-file-index.json').write_text(json.dumps(context,indent=2)+'\n')
env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
def git(*args):return subprocess.check_output(['git',*args],env=env).decode()
result=dict(candidate=CANDIDATE,actual_head=git('rev-parse','HEAD').strip(),actual_branch=git('rev-parse','--abbrev-ref','HEAD').strip(),
 reviewed_files=len(index['files']),changed_working_frozen_paths=changed,changed_scratch_frozen_paths=frozen_changed,
 tracked_working_diff=git('diff','--name-status'),status_short=git('status','--short'),
 process_inventory=subprocess.check_output(['ps','-eo','pid,args']).decode())
(OUT/'final-preservation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='process_inventory'},indent=2))
assert not changed and not frozen_changed
assert all(e['working_matches'] for e in context)
assert not result['tracked_working_diff']
