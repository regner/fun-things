import pathlib,json,hashlib,subprocess
O=pathlib.Path(__file__).resolve().parent;R=pathlib.Path.cwd();E=R/'docs/assets/production/batch_03-retention-evidence'
C='dbcbd8e60dfe7da1bd15a77d87cb908d446b11c3';P='1031a3e1e66a404f67fa1a3857c4888d05f10d1e'
def git(*a):return subprocess.check_output(['git',*a])
def blob(p,rev=C):return git('show',rev+':'+p)
def sha(b):return hashlib.sha256(b).hexdigest()
def row(p,e=None,old=False):
 b=blob(p);w=(R/p).read_bytes();r=dict(path=p,bytes=len(b),sha256=sha(b),working_bytes=len(w),working_sha256=sha(w),working_matches=b==w)
 if e:r['expected_matches']=len(b)==e['bytes'] and sha(b)==e['sha256']
 if old:a=blob(p,P);r['parent_identical']=a==b;r['parent_bytes']=len(a);r['parent_sha256']=sha(a)
 return r
head=git('rev-parse','HEAD').decode().strip();parent=git('rev-parse',C+'^').decode().strip();assert head==C and parent==P
delta=[dict(status=l.split('\t')[0],path=l.split('\t')[1]) for l in git('diff','--name-status',P,C).decode().splitlines()];assert len(delta)==223 and all(d['status']=='A' for d in delta)
ip='docs/assets/production/batch_03-retention-evidence/artifact-index.json';idx=json.loads(blob(ip));assert idx['delta_base']==P;assert len(idx['files'])==222 and idx['self_exclusions']==[ip]
expected={e['path'] for e in idx['files']}|{ip};assert len(expected)==223 and expected=={d['path'] for d in delta}
add=[row(e['path'],e) for e in idx['files']]+[row(ip)];assert all(e['working_matches'] and e.get('expected_matches',True) for e in add)
engine_index='docs/assets/production/batch_03-evidence/engine-artifact-index.json';ei=json.loads(blob(engine_index,P));es=ei['files'];assert len(es)==299
old=[row(e['path'],e,True) for e in es]+[row(engine_index,old=True)];assert len(old)==300 and all(e['working_matches'] and e.get('expected_matches',True) and e['parent_identical'] for e in old)
fp='docs/reviews/asset-production/batch_03/final/';ri=json.loads(blob(fp+'review-file-index.json'));sign=json.loads(blob(fp+'review-index-readback.json'));assert len(ri['files'])==193 and len(ri['self_exclusions'])==5
review=[row(fp+e['path'],e) for e in ri['files']]+[row(fp+n) for n in ri['self_exclusions']];assert len(review)==198
assert sha(blob(fp+'review-file-index.json'))==sign['index_sha256']=='aa642c9597ef61f07be1c50d2535a81fb7088b263b626e9cca03961ef07a38e6';assert len(blob(fp+'review-file-index.json'))==sign['index_bytes'];assert all(e['working_matches'] and e.get('expected_matches',True) for e in review)
assert {e['path'] for e in review}=={e['path'] for e in add if e['path'].startswith(fp)}
ret={e['path'] for e in add if e['path'].startswith('docs/assets/production/batch_03-retention-evidence/')};assert len(ret)==25;assert expected==ret|{e['path'] for e in review}
# Cross-check producer retention receipt without accepting its conclusions.
read=json.loads(blob('docs/assets/production/batch_03-retention-evidence/retention-readback.json'));assert {r['path'] for r in read['complete_engine_expected_set']}=={r['path'] for r in old};assert {r['path'] for r in read['final_review_expected_set']}=={r['path'] for r in review}
for k,rs in [('complete_engine_expected_set',old),('final_review_expected_set',review)]:
 by={r['path']:r for r in rs}
 for e in read[k]:assert all(e[a]==by[e['path']][a] for a in ['bytes','sha256'])
full=blob('docs/assets/production/batch_03-retention-evidence/complete-editor-through-shutdown.log');frozen=blob('docs/assets/production/batch_03-retention-evidence/frozen-candidate-editor.log');append=blob('docs/assets/production/batch_03-retention-evidence/append-after-frozen-prefix.log');review_append=blob(fp+'owned-editor-appended.log');assert full==frozen+append;assert frozen==blob('docs/assets/production/batch_03-evidence/editor-restart.log',P);assert sha(frozen)=='ab20ecf69a33eb2d58617c724bda4bc695247fac82e98057b596144ea44df509';assert append.startswith(review_append);assert [len(x) for x in [full,frozen,append,review_append]]==[34074,29204,4870,4490];assert len(append[len(review_append):])==380
isolation=json.loads(blob('docs/assets/production/batch_03-retention-evidence/isolation.json'));assert isolation['old_editor_stopped'] and isolation['old_os_exit']=='not observed; stopped/zombie PID verified after SIGTERM'
for key,b in [('complete',full),('frozen',frozen),('append',append),('reviewer_append',review_append)]:assert isolation[key+'_bytes']==len(b) and isolation[key+'_sha256']==sha(b)
prior=json.loads(blob(fp+'candidate-file-index.json'));producer=[row(e['path'],e,True) for e in prior['producer_files']];initial=[row(e['path'],e,True) for e in prior['initial_immutable_references']];assert len(producer)==601 and all(e['working_matches'] and e['expected_matches'] and e['parent_identical'] for e in producer);assert all(e['working_matches'] and e['expected_matches'] and e['parent_identical'] for e in initial)
untracked=git('ls-files','--others','--exclude-standard').decode().splitlines();sidecars=[p for p in untracked if p.endswith(('.import','.uid'))];assert len(sidecars)==46;assert not set(sidecars)&expected
r=dict(candidate=C,parent=P,actual_head=head,actual_parent=parent,actual_delta=delta,retention_expected_paths=sorted(expected),retention_files=add,old_engine_expected_paths=sorted(e['path'] for e in old),old_engine_files=old,review193_plus5_expected_paths=sorted(e['path'] for e in review),review_files=review,producer601_unchanged_files=producer,initial_review_unchanged_files=initial,logs=dict(complete_bytes=len(full),complete_sha256=sha(full),frozen_bytes=len(frozen),frozen_sha256=sha(frozen),append_bytes=len(append),append_sha256=sha(append),reviewer_append_bytes=len(review_append),reviewer_append_sha256=sha(review_append),integrator_postreview_append_bytes=380,exact_concatenation=True,old_exit_unobserved=True),artifact_index_self_exclusion=ip,excluded_untracked_importer_metadata=sidecars,tracked_diff=git('diff','--name-status').decode().splitlines(),index_diff=git('diff','--cached','--name-status').decode().splitlines())
assert not r['tracked_diff'] and not r['index_diff'];(O/'verified-file-index.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(candidate=C,parent=P,added_delta=len(delta),retention_payloads=len(add)-1,retention_with_self=len(add),old_engine_paths=len(old),review_payloads=len(ri['files']),review_metadata=len(ri['self_exclusions']),producer_paths=len(producer),initial_review_paths=len(initial),logs=r['logs'],excluded_importer_sidecars=len(sidecars),all_expected_git_and_working_bytes_sha_match=True),indent=2))
