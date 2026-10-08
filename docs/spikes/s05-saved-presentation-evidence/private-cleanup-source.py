"""Source-qualified private backing-store cleanup; no process query or engine."""
import hashlib,json,os,time,tempfile
from pathlib import Path
project='/tmp/s05-author-56eb6b28-run01/project';key=hashlib.sha256(project.encode()).hexdigest()[:12]
def clean(folder,allowed):
 entry=folder/'entries'/f'{key}.json';lock=folder/'projects.json.lock'
 assert not lock.exists(),'unknown lock: fail closed'
 if entry.exists():
  row=json.loads(entry.read_text());assert row['_key']==project and row['pid'] in allowed
 else:row=None
 # Toolkit file_lock.gd's documented uncontended pid:timestamp/release contract.
 with lock.open('x') as f:f.write(f'{os.getpid()}:{int(time.time())}')
 try:
  if entry.exists():entry.unlink()
  projection={'by_path':{}}
  for p in (folder/'entries').glob('*.json'):
   r=json.loads(p.read_text());assert not p.name.endswith('.runtime.json')
   projection['by_path'][r['_key']]={k:v for k,v in r.items() if k!='_key'}
  target=folder/'projects.json';temporary=folder/'projects.json.tmp'
  temporary.write_text(json.dumps(projection,indent=2)+'\n');temporary.replace(target)
 finally:lock.unlink()
 return {'entry_before':row,'after':projection,'own_entry_gone':not entry.exists(),'lock_gone':not lock.exists()}
retained=Path('docs/spikes/s05-saved-presentation-evidence')
with tempfile.TemporaryDirectory(prefix='s05-cleanup-offline-') as name:
 folder=Path(name);(folder/'entries').mkdir()
 before=json.loads((retained/'private-stale-entry-before-cleanup.json').read_text())
 (folder/'entries'/f'{key}.json').write_text(json.dumps(before))
 unrelated={'_key':'/tmp/unrelated-private-fixture','pid':777777,'port':6507,'token_path':'synthetic-unused'}
 other=folder/'entries/unrelated.json';other.write_text(json.dumps(unrelated));bytes_before=other.read_bytes()
 result=clean(folder,{555104,558716});assert other.read_bytes()==bytes_before
 assert result['after']['by_path']=={unrelated['_key']:{k:v for k,v in unrelated.items() if k!='_key'}}
 result['unrelated_entry_bytes_preserved']=True
 (retained/'offline-private-cleanup.json').write_text(json.dumps(result,indent=2)+'\n')
actual=clean(Path('/tmp/s05-author-56eb6b28-run01/data/godot-mcp-toolkit'),{555104,558716})
(retained/'supported-private-cleanup-readback.json').write_text(json.dumps(actual,indent=2)+'\n')
print(json.dumps(actual))
