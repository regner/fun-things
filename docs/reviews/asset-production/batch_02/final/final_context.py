"""Record quiescence, exact revision, immutable inputs and final stage receipts."""
import hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path('/home/regner/.paseo/worktrees/0u71f39f/asset-register-production')
OUT=Path(__file__).resolve().parent
C='10ddb64d16e6cb2f137923a31d3ca14991468f7d'
S='5e94cc0ea4155219285db49c64b5728e0882b093'
B='66400c26a01bf917dfe631af4762c2b444d9c48f'
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT)
inputs=['AGENTS.md','.agents/skills/art-review/SKILL.md','docs/assets/production/commission.md',
 'docs/assets.md','docs/art-direction.md','docs/world-layout.md','docs/scene-structure.md',
 'docs/assets/production/batch_02-integration.md',
 'docs/assets/production/batch_02-evidence/engine-artifact-index.json',
 'docs/reviews/asset-production/batch_02/initial/artifact-index.json',
 'docs/reviews/asset-production/batch_02/initial/artifact-expected-set.json',
 'docs/reviews/asset-production/batch_02/initial/artifact-verification.json',
 'docs/reviews/asset-production/batch_02/initial/shared-input-index.json']
rows=[]
for p in inputs:
    data=git('show',C+':'+p)
    rows.append(dict(path=p,revision=C,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
(OUT/'shared-input-index.json').write_text(json.dumps(rows,indent=2)+'\n')
# Reproduce and verify the parsed numerical receipt from its retained raw output.
raw=(OUT/'resource-query-audit.stdout').read_text()
actual=json.loads(raw.split('INDEPENDENT_BATCH02 ')[1].splitlines()[0])
assert actual==json.loads((OUT/'resource-query-audit.json').read_text())
# Local namespace process inventory: do not claim host/global process discovery.
active=[]
for p in Path('/proc').iterdir():
    if not p.name.isdigit(): continue
    try:
        argv=[v.decode(errors='replace') for v in (p/'cmdline').read_bytes().split(b'\0') if v]
    except (FileNotFoundError,PermissionError,ProcessLookupError): continue
    if argv and Path(argv[0]).name in ['godot','blender']:
        active.append(dict(namespace_pid=int(p.name),argv=argv))
assert not active,active
initial=ROOT/'docs/reviews/asset-production/batch_02/initial'
expected=json.loads((initial/'artifact-expected-set.json').read_text())['paths']
assert sorted(x.name for x in initial.iterdir())==sorted(expected)
for name in expected: assert (initial/name).read_bytes()==git('show',C+':docs/reviews/asset-production/batch_02/initial/'+name)
historical=git('show',C+':docs/assets/production/batch_02-evidence/transport/final-context-results.jsonl').decode()
receipt=dict(candidate=C,source_delta_base=S,original_base=B,observed_HEAD=git('rev-parse','HEAD').decode().strip(),
 source_and_initial_unchanged=True,initial_file_count=len(expected),supplied_private_pid=195352,
 supplied_private_pid_visible=Path('/proc/195352').exists(),private_session_accessed=False,
 reviewer_editor_saves=0,historical_final_context=json.loads(historical),
 reviewer_processes_running_in_namespace=active,all_owned_check_commands_completed=True,
 editor_lease='released; supplied PID absent, no live session accessed; no current synchronization claim',
 disposition=dict(source_export='accepted production, initial evidence unchanged',C1='accepted bounded source-linked comparison',
 prefab='accepted bounded production integration',fixture_collision='accepted scoped static movement/query/aim',
 native_views='accepted recorded fixtures only',world_device_sustained_performance_full_game='pending existing owners'))
(OUT/'final-context.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
