import json,sys,time
from pathlib import Path
run=Path('/tmp/s05-author-56eb6b28-run01')
def call(name,args=None):
 n=len(list((run/'requests').glob('*.json')))+1
 target=run/'requests'/('%03d.json'%n)
 request={'name':name,'args':args or {}}
 temporary=target.with_suffix('.tmp');temporary.write_text(json.dumps(request));temporary.rename(target)
 response=run/'responses'/target.name
 deadline=time.monotonic()+36
 while not response.exists():
  if time.monotonic()>deadline:raise RuntimeError('no response '+str(n))
  time.sleep(.05)
 data=json.loads(response.read_text())
 for c in data.get('content',[]):
  if c.get('type')=='text':
   try:
    d=json.loads(c['text'])
    if d.get('success') is False:raise RuntimeError(c['text'])
   except json.JSONDecodeError:pass
 return data
if __name__=='__main__':print(json.dumps(call(sys.argv[1],json.loads(sys.argv[2]) if len(sys.argv)>2 else {})))
