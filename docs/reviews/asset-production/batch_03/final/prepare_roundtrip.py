import json,pathlib,hashlib,subprocess
O=pathlib.Path(__file__).resolve().parent;paths=list(json.load(open('docs/assets/production/batch_03-evidence/roundtrip-stable-before.json')));before={};requests=[];C='1031a3e1e66a404f67fa1a3857c4888d05f10d1e'
for p in paths:
 f=p.removeprefix('res://');b=pathlib.Path(f).read_bytes();assert b==subprocess.check_output(['git','show',C+':'+f]);before[p]=hashlib.sha256(b).hexdigest()
 requests += [dict(method='scene.open',params={'file_path':p}),dict(method='editor.save_scene',params={}),dict(method='scene.close',params={'file_path':p}),dict(method='scene.open',params={'file_path':p}),dict(method='editor.save_scene',params={})]
requests += json.loads((O/'editor-context-requests.json').read_text())
(O/'review-roundtrip-before.json').write_text(json.dumps(before,indent=2)+'\n');(O/'review-roundtrip-requests.json').write_text(json.dumps(requests,indent=2)+'\n')
audit=[dict(method='node.call_method',params={'node_path':'.','method_name':'inspect_prefab','arguments':[p]}) for p in paths[:9]];(O/'editor-audit-requests.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(dict(scenes=len(paths),requests=len(requests),audit=len(audit))))
