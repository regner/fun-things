import pathlib,json,hashlib,subprocess,os
O=pathlib.Path(__file__).resolve().parent;r=json.loads((O/'verified-file-index.json').read_text());paths={}
for group in ['retention_files','old_engine_files','review_files','producer601_unchanged_files','initial_review_unchanged_files']:
 for e in r[group]:paths[e['path']]=dict(bytes=e['bytes'],sha256=e['sha256'])
checks=[]
for p,e in sorted(paths.items()):
 b=pathlib.Path(p).read_bytes();a=dict(path=p,bytes=len(b),sha256=hashlib.sha256(b).hexdigest());a['matches']=a['bytes']==e['bytes'] and a['sha256']==e['sha256'];checks.append(a)
assert all(e['matches'] for e in checks)
rs=[json.loads(l) for l in (O/'editor_context_dedicated.stdout').read_text().splitlines()];assert 'res://tools/asset_production/integration/inspector.tscn' in str(rs[0]);assert rs[1]['result']['result']['was_running']==False;ctx=rs[2]['result']['result']['result'];assert ctx['pid']==277464 and ctx['engine']=='4.8-dev7 (official)' and ctx['project']==str(pathlib.Path.cwd())+'/' and ctx['unsaved']=='PackedStringArray()'
fds={str(i):os.readlink('/proc/277464/fd/'+str(i)) for i in [1,2]};assert set(fds.values())=={'/tmp/asset-register-production-editor/f3/editor-live.log'};log=pathlib.Path(fds['1']);logmeta=dict(path=str(log),current_bytes=log.stat().st_size,live_unsnapshotted=True,outside_workspace=True)
head=subprocess.check_output(['git','rev-parse','HEAD']).decode().strip();diff=subprocess.check_output(['git','diff','--name-status']).decode().splitlines();index=subprocess.check_output(['git','diff','--cached','--name-status']).decode().splitlines();assert head==r['candidate'] and not diff and not index
out=dict(candidate=head,parent=r['parent'],all_working_expected_bytes_sha_match_after_editor_calls=True,files=checks,current_fd_targets=fds,private_live_log=logmeta,context=ctx,saved_inspector_selected=True,runtime_stopped=True,lease_released=True,tracked_diff=diff,index_diff=index)
(O/'final-readback.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['files','context']},indent=2))
