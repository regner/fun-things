"""Independently enumerate immutable delta, verify all claimed bytes, and history."""
import hashlib, json, subprocess
from pathlib import Path
ROOT=Path('/home/regner/.paseo/worktrees/0u71f39f/asset-register-production')
SNAP=Path('/tmp/batch02-final-10ddb64/snapshot')
OUT=Path(__file__).resolve().parent
C='10ddb64d16e6cb2f137923a31d3ca14991468f7d'
S='5e94cc0ea4155219285db49c64b5728e0882b093'
B='66400c26a01bf917dfe631af4762c2b444d9c48f'
def git(*args): return subprocess.check_output(['git', *args], cwd=ROOT)
def info(p):
    data=(SNAP/p).read_bytes()
    return dict(path=p,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
delta=git('diff','--name-status',S,C).decode().splitlines()
changes=[dict(status=line.split('\t')[0],path=line.split('\t')[1]) for line in delta]
assert all(x['status'] in ('A','M') for x in changes)
expected={x['path'] for x in changes}
indexpath='docs/assets/production/batch_02-evidence/engine-artifact-index.json'
index=json.loads((SNAP/indexpath).read_text())
actual={x['path'] for x in index['files']}
assert len(actual)==len(index['files'])
shared={'docs/assets/production/batch_02-evidence/source-readback.json'}
assert actual==(expected-{indexpath})|shared, (sorted(expected-{indexpath}-actual),sorted(actual-expected-shared))
for row in index['files']: assert info(row['path'])==row,row['path']
payloads=[info(x['path']) for x in changes]
(OUT/'candidate-delta-index.json').write_text(json.dumps(dict(candidate=C,source=S,base=B,changes=changes,files=payloads),indent=2)+'\n')
initial='docs/reviews/asset-production/batch_02/initial/'
old=json.loads((SNAP/initial/'artifact-index.json').read_text())
initialexpected=json.loads((SNAP/initial/'artifact-expected-set.json').read_text())['paths']
assert len(old['files'])==120
assert len(initialexpected)==122
assert set(p.name for p in (SNAP/initial).iterdir())==set(initialexpected)
for row in old['files']:
    assert info(initial+row['path'])==dict(row,path=initial+row['path'])
for name in initialexpected:
    assert (SNAP/initial/name).read_bytes()==(ROOT/initial/name).read_bytes(),name
# Candidate retains source tree and all prior baseline resources, exactly.
sourcepaths=git('ls-tree','-r','--name-only',S,'art/source/models/environment','art/models/environment','docs/assets/production/batch_02-evidence/source-readback.json').decode().splitlines()
unchanged=[]
for p in sourcepaths:
    if any(s in p for s in ['city_planting_03/','city_planting_04/','city_planting_05/','city_roof_details_01/','city_roof_details_02/','city_shop_fittings_01/']) or p.endswith('/source-readback.json'):
        assert git('show',S+':'+p)==(SNAP/p).read_bytes(),p
        unchanged.append(info(p))
(OUT/'unchanged-source-index.json').write_text(json.dumps(unchanged,indent=2)+'\n')
for sha in [B,S]: assert subprocess.run(['git','merge-base','--is-ancestor',sha,C],cwd=ROOT).returncode==0
# Record raw delta and exact histories independently from report claims.
(OUT/'delta-name-status.txt').write_bytes(git('diff','--name-status',S,C))
(OUT/'delta.patch').write_bytes(git('diff','--no-ext-diff',S,C,'--','scenes','tests','tools','art/models'))
(OUT/'history.txt').write_bytes(git('log','--format=%H %P %s',B+'..'+C))
launch=Path('/tmp/asset-register-production-editor/launch.json')
guard=json.loads(launch.read_text())
pid=guard['pid']; proc=Path('/proc')/str(pid)
guard['process_exists']=proc.exists()
guard['verified_live_ownership']=False
if proc.exists():
    guard['observed_cwd']=str((proc/'cwd').resolve())
    guard['observed_exe']=str((proc/'exe').resolve())
    guard['observed_argv']=(proc/'cmdline').read_bytes().split(b'\0')
    guard['observed_argv']=[x.decode() for x in guard['observed_argv'] if x]
(OUT/'editor-lease-guard.json').write_text(json.dumps(guard,indent=2)+'\n')
summary=dict(candidate=C,source=S,base=B,observed_HEAD=git('rev-parse','HEAD').decode().strip(),delta_files=len(changes),
    indexed_engine_payloads=len(actual),initial_payloads=120,initial_expected_paths=122,
    initial_retained_identically=True,unchanged_source_paths=len(unchanged),editor_process_exists=proc.exists())
(OUT/'static-audit.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
