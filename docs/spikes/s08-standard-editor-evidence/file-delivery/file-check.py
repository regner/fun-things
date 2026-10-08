"""Offline full-byte request test; no engine/editor/client connection."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'tools/s08'))
from request_file import read_request
scope=Path('/tmp/s08-standard-555e0330');d=scope/'requests-run04';d.mkdir()
source=Path('/tmp/s08-entrypoint-read/release_boot.gd.draft').read_text()
req={'method':'script.write','params':{'file_path':'res://tests/fixtures/s08/release_boot.gd','content':source}}
raw=(json.dumps(req)+'\n').encode();p=d/'boot-write.json';p.write_bytes(raw)
control={'request_file':str(p),'sha256':hashlib.sha256(raw).hexdigest()}
actual,readback=read_request(control,scope)
assert len(raw)>4095 and readback==raw and actual==req and actual['params']['content']==source
for bad in [{**control,'sha256':'0'*64},{'request_file':str(Path.cwd()/'project.godot'),'sha256':'0'*64}]:
 try:read_request(bad,scope)
 except ValueError:pass
 else:raise AssertionError('invalid control accepted')
(d/'boot-write-control.json').write_text(json.dumps(control)+'\n')
print(json.dumps({'ok':True,'bytes':len(raw),'sha256':control['sha256'],'source_bytes':len(source.encode()),'exact_readback':True,'wrong_hash_rejected':True,'outside_scope_rejected':True,'terminal_control_bytes':len(json.dumps(control))}))
