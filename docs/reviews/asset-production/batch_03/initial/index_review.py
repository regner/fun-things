"""Hash the complete retained review packet, excluding its self-referential index."""
import hashlib
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
files=[]
for p in sorted(OUT.rglob('*')):
    if not p.is_file() or p.name=='review-file-index.json':continue
    b=p.read_bytes()
    files.append(dict(path=str(p.relative_to(OUT)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
(OUT/'review-file-index.json').write_text(json.dumps(dict(scope='All current retained review files except this index itself',files=files),indent=2)+'\n')
print('REVIEW_PACKET_INDEX',len(files))
