import json,hashlib,subprocess,datetime
from pathlib import Path
O=Path(__file__).resolve().parent;C='c4067ff3abe1384301471d9a64e94e84201235e2';S='390377dc6530e101eddcbf38b2946a1b235137c7';B='66400c26a01bf917dfe631af4762c2b444d9c48f'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==C
checks=json.loads((O/'commands.json').read_text())
for c in checks:
 assert (O/(c['label']+'.stdout.log')).is_file() and (O/(c['label']+'.stderr.log')).is_file(),c['label']
expected_failures={'private-context','calibration','calibration-adapted','private-prefabs'}
assert {c['label'] for c in checks if c['exit']!=0}==expected_failures
assert all(c['exit']==0 for c in checks if c['label'] not in expected_failures)
for index in ['candidate-scope-file-index.json','artifact-index.json']:
 data=json.loads((O.parent/index).read_text());rows=data['files'] if isinstance(data,dict) else data
 for r in rows:assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']
identity=dict(candidate=C,actual_delta_base=S,original_base=B,branch='art/register-production-20261009',workspace=str(Path.cwd()),workspace_id='wks_59891ad7a05813e5',reviewer='same independent Codex GPT-6.1 Sol high reviewer',review_start_utc='2026-10-09 16:53:50 UTC',review_completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),initial_cap_minutes=60,report='report.md',initial_review='../report.md',scope_ids=['city_lights.01','city_lights.02','city_lights.04','city_sign_supports.01','city_planting.01','city_planting.02'],source_stage='accepted bounded production source/export',calibration_G1='accepted; closed',prefab_stage='accepted production linked-prefab handoff',native_engine_stage='accepted bounded native standalone fixture checks',overall_game_ready_stage='pending downstream world/combat/network/export/platform/performance acceptance',actionable_asset_findings=[],implementation_fixes_requested=[],residual_tooling='disclosed editor progress-dialog/task errors; no asset runtime/UID warning observed',writes='only final reviewer directory and isolated /tmp scratch; no implementation/index/commit/subagent operations',editor_handoff=dict(pid=195352,runtime_stopped=True,unsaved_scenes=[],ownership='saved quiescent private editor returned with final completion'))
(O/'review-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
files=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name!='artifact-index.json':
  data=p.read_bytes();files.append(dict(path=str(p.relative_to(Path.cwd())),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
index=dict(candidate=C,actual_delta_base=S,original_base=B,self_hash_exclusion='artifact-index.json excludes itself; all other final report/check/result/raw diagnostic/request/script/image files, including .gdignore, are indexed',original_review_preservation='original 180 candidate-scope rows and 67 reviewer artifacts reverified; referenced without copying their payload',file_count=len(files),files=files)
(O/'artifact-index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Sealed',len(files),'review files;',len(checks),'check argv/exits with paired raw streams; all four own failure exits explicitly retained; original payload preserved; HEAD',C)
