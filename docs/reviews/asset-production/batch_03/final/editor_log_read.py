from pathlib import Path
import os,json,hashlib
O=Path(__file__).resolve().parent;rows=[]
for fd in [1,2]:
 target=os.readlink('/proc/254275/fd/'+str(fd));p=Path(target);print('VERIFIED_FD_TARGET',target);assert (target.startswith('/tmp/asset-register-production-editor/') or target==str(Path.cwd()/'docs/assets/production/batch_03-evidence/editor-restart.log')) and p.is_file();b=p.read_bytes();rows.append(dict(fd=fd,path=target,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()));print('OWNED_EDITOR_STREAM_FD',fd,target);print(b.decode(errors='replace'))
(O/'editor-log-references.json').write_text(json.dumps(rows,indent=2)+'\n')
