"""Retain immutable review identity, scoped paths and ancestry without index writes."""
import json,hashlib,subprocess
from pathlib import Path
O=Path(__file__).resolve().parent;R=Path('/tmp/six-asset-review-390377d')
C='390377dc6530e101eddcbf38b2946a1b235137c7';B='66400c26a01bf917dfe631af4762c2b444d9c48f'
ids=['city_lights_01','city_lights_02','city_lights_04','city_sign_supports_01','city_planting_01','city_planting_02']
scopes=[f'{prefix}/{a}' for a in ids for prefix in ['art/source/models/environment','art/models/environment','tools/asset_production']]+[f'docs/assets/production/{a}.md' for a in ids]+[f'docs/assets/production/{a}-evidence' for a in ids]+['docs/assets/production/batch_01-evidence/source-readback.json','docs/assets/production/batch_01-evidence/city_planting_01-retention-manifest.json']
argv=['git','diff','--name-status',B,C,'--']+scopes
r=subprocess.run(argv,capture_output=True,text=True);(O/'scoped-changed-paths.stdout.log').write_text(r.stdout);(O/'scoped-changed-paths.stderr.log').write_text(r.stderr)
ancestor=subprocess.run(['git','merge-base','--is-ancestor',B,C],capture_output=True,text=True)
paths=subprocess.run(['git','ls-tree','-r','--name-only',C,'--']+scopes,capture_output=True,text=True)
files=[]
for path in paths.stdout.splitlines():
 p=R/path;b=p.read_bytes();files.append(dict(path=path,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
(O/'candidate-scope-file-index.json').write_text(json.dumps(files,indent=2)+'\n')
# Initial prefabs inspected as static ancestry only.
ancestry=[]
for p in sorted((R/'scenes/prefabs/environment').glob('city_lights_0*.tscn')):
 if not any(a in p.name for a in ['city_lights_01','city_lights_02']):continue
 txt=p.read_text();ancestry.append(dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),has_linked_glb='type="PackedScene"' in txt and 'instance=ExtResource' in txt,has_embedded_render_mesh=any(x in txt for x in ['ArrayMesh','PrimitiveMesh','BoxMesh','SphereMesh']),saved_content=txt))
(O/'initial-ancestry-static.json').write_text(json.dumps(ancestry,indent=2)+'\n')
record=dict(candidate=C,base=B,branch='art/register-production-20261009',workspace='/home/regner/.paseo/worktrees/0u71f39f/asset-register-production',workspace_id='wks_59891ad7a05813e5',snapshot=str(R),snapshot_route='git archive exact candidate into scratch; source/export runs only in independent /tmp/six-review-jobs/<id> copies; no candidate files overwritten',diff_argv=argv,diff_exit=r.returncode,ancestor_exit=ancestor.returncode,ls_tree_exit=paths.returncode,scope_files=len(files),source_gdignore_bytes=(R/'art/source/.gdignore').stat().st_size,production_gdignore_bytes=(R/'docs/assets/production/.gdignore').stat().st_size,model_receipt='Provided user receipt: codex/gpt-6.1-sol high auto-review supported; no profile configured',live_scene_contract_hash_verified='cec8e72f7be1d5d77a82f5a7910b3f67d10cf43efa278067427ab47057f8c9ff',scope_exclusions=['uncommitted integration','city_planting_03','live Blender/Godot/private integrator endpoint','final engine batch','whole-city/device/performance proof'])
(O/'review-identity.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
