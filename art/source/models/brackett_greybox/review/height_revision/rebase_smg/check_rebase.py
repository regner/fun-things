import subprocess,json,hashlib
from pathlib import Path
root=Path('/home/regner/.paseo/worktrees/0u71f39f/brackett-greybox');out=Path('/tmp/brackett-height-review/rebase_smg')
def git(*args):return subprocess.check_output(['git',*args],cwd=root)
def resolve(x):return git('rev-parse',x).decode().strip()
def tree(rev):
 entries={}
 for line in git('ls-tree','-r','-z',rev).split(b'\0'):
  if not line:continue
  meta,path=line.split(b'\t');entries[path.decode()]=meta.decode()
 return entries
old=resolve('615ccf89fb1baa3fb885250e8d9d2ae4808267c4');new=resolve('708b59e5edfbf17d67deb3b16914dd22495dd682');base=resolve('4f2ed147de3a10a0a9c197dd3f7b0ba5cca59252')
prefixes=['art/models/brackett_greybox/','art/source/models/brackett_greybox/','scenes/world/brackett_greybox/','tools/brackett_greybox/','docs/assets/brackett_greybox.md']
a,b=tree(old),tree(new);owned=lambda p:any(p.startswith(x) for x in prefixes)
owned_old={p:v for p,v in a.items() if owned(p)};owned_new={p:v for p,v in b.items() if owned(p)}
assert owned_old==owned_new
main=tree(base);assert all(b[p]==v for p,v in main.items())
assert all(owned(p) for p in set(b)-set(main))
pairs=[('0def968','cbe11b1'),('310bf79','7b33ee1'),('93904df','6e72540'),('1f69653','8f65a03'),('615ccf8','708b59e')];checks=[]
for x,y in pairs:
 x,y=resolve(x),resolve(y)
 xd=git('diff','--binary',x+'^',x);yd=git('diff','--binary',y+'^',y);assert xd==yd
 checks.append({'original':x,'rebased':y,'binary_patch_byte_identical':True,'binary_patch_sha256':hashlib.sha256(xd).hexdigest()})
ancestry=subprocess.run(['git','merge-base','--is-ancestor',base,new],cwd=root).returncode;assert ancestry==0
chain=git('rev-list','--parents',base+'..'+new).decode().splitlines();assert len(chain)==5 and all(len(x.split())==2 for x in chain)
assert resolve('main')==base and resolve('HEAD')==new
assert git('status','--short')==b''
report={'reviewed_asset_candidate':'21fd536aa4415488d2d06b05ee0a8e3b7cf5227f','pre_rebase_with_retained_review':old,'rebased_candidate':new,'latest_main_base':base,'owned_blob_and_mode_count':len(owned_old),'all_owned_sources_exports_scenes_docs_and_evidence_byte_identical_across_rebase':True,'all_latest_main_blobs_and_modes_preserved':True,'only_new_owned_paths_added_to_main':True,'commit_pairs':checks,'base_ancestor_exit':ancestry,'linear_single_parent_commits_above_base':5,'main_matches_base_and_head_matches_candidate':True,'fast_forward_eligible_from_verified_main':True,'worktree_clean':True,'limitations':'Read-only git/tree checks only; no engine rerun required for byte-identical asset. Prior technical acceptance and integration limits carry forward unchanged. No model/scene/ref mutation.'}
(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
