"""Retain exact new run04/finite-check payloads without replacing prior dictionaries."""
import gzip,hashlib,json,subprocess
from pathlib import Path
root=Path.cwd();out=root/'docs/spikes/s05-saved-presentation-evidence';run=Path('/tmp/s05-author-56eb6b28-run04');net=Path('/tmp/s05-effect-network-56eb6b28-run01')
expected={}
for p in run.iterdir():
 if p.is_file() and (p.name.startswith('call-') or p.name in ['commands-before-engine.json','lifecycle.json','observe.stdout','observe.stderr','observe.engine.log','connector.stderr','client.mjs','context.gd','call.py','author_batch.py','fixtures_batch.py','roundtrip_batch.py','roundtrip_stable.py','roundtrip.json','resource-check.json','import-inspection-node_call_method.json','import-inspection-execute_code.json']):expected['run04/'+p.name]=p
expected['network/result.json']=net/'result.json'
for role in ['host','client','late']:
 for stream in ['stdout','stderr','engine.log']:expected['network/'+role+'/'+stream]=net/role/stream
for name,args in [('format',['fmt','--check']),('lint',['--max-warnings','0'])]:
 command=['/home/regner/.local/share/mise/installs/github-atelico-gdstyle/0.3.0/gdstyle',*args,*map(str,sorted((root/'tests/fixtures/s05_effect').glob('*.gd')))]
 result=subprocess.run(command,capture_output=True)
 assert result.returncode==0
 for ext,data in [('stdout',result.stdout),('stderr',result.stderr)]:
  path=run/(name+'-final.'+ext);path.write_bytes(data);expected['checks/'+path.name]=path
 path=run/(name+'-final.command.json');path.write_text(json.dumps({'argv':command,'exit':result.returncode},indent=2)+'\n');expected['checks/'+path.name]=path
metadata=[]
for logical,source in sorted(expected.items()):
 data=source.read_bytes();stored=logical+'.gz';target=out/stored;target.parent.mkdir(parents=True,exist_ok=True)
 assert not target.exists()
 payload=gzip.compress(data,mtime=0);target.write_bytes(payload)
 assert gzip.decompress(target.read_bytes())==data
 metadata.append({'path':stored,'decoded_path':logical,'source':str(source),'decoded_bytes':len(data),'decoded_sha256':hashlib.sha256(data).hexdigest(),'stored_bytes':len(payload),'stored_sha256':hashlib.sha256(payload).hexdigest()})
(out/'run04-expected-set.json').write_text(json.dumps([p+'.gz' for p in sorted(expected)],indent=2)+'\n')
(out/'run04-manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
assert set(p+'.gz' for p in expected)==set(r['path'] for r in metadata)
mirror=[]
for row in json.loads(Path('/tmp/s05-author-56eb6b28-run01/inputs.json').read_text()):
 data=(Path('/tmp/s05-author-56eb6b28-run01/project')/row['path']).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256'];mirror.append(row['path'])
(out/'run04-final-mirror-preservation.json').write_text(json.dumps({'count':len(mirror),'unchanged_paths':mirror},indent=2)+'\n')
session=Path('/home/regner/.codex/sessions/2026/10/08/rollout-2026-10-08T09-37-15-01a11aa8-d994-7832-989e-29f10b183857.jsonl')
recovered=[];steering=[]
for line in session.open():
 item=json.loads(line);v=item.get('payload',{})
 if v.get('type')=='message' and v.get('role')=='user':
  text='\n'.join(p.get('text','') for p in v.get('content',[]))
  if text.startswith(('ROOT new evidence:', 'ROOT relay concrete S08')):steering.append(text)
 if v.get('type')=='custom_tool_call_output':
  for b in v.get('output',[]):
   try:d=json.loads(b.get('text',''))
   except(ValueError,TypeError):continue
   if not isinstance(d,dict):continue
   s=d.get('output','')
   if any(term in s for term in ['roundtrip bytes changed boot','diff -u','canonicalized burst','PackedStringArray()','virtual/override method','object allocation', '"pid": 561303', '"pid\\": 561303', 'roundtrip stable', 'readiness engine diagnostics']):recovered.append({'original_tool_result_text':b['text'],'decoded':d})
(out/'run04-supplemental-root-steering.json').write_text(json.dumps(steering,indent=2)+'\n')
(out/'run04-recovered-tool-results.json').write_text(json.dumps(recovered,indent=2)+'\n')
print(json.dumps({'payloads':len(metadata),'decoded_bytes':sum(r['decoded_bytes'] for r in metadata),'stored_bytes':sum(r['stored_bytes'] for r in metadata),'mirrored_originals_unchanged':len(mirror),'steering':len(steering)}))
