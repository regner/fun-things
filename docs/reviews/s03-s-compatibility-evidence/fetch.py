from pathlib import Path
import hashlib,json,urllib.request
root=Path('/tmp/s03-s-compatibility-review')
manifest=json.loads(Path('docs/spikes/s03-s-compatibility-evidence/sources.json').read_text())
(root/'sources').mkdir(exist_ok=True)
for e in manifest['files']:
    with urllib.request.urlopen(e['url'],timeout=25) as r: b=r.read(1000000)
    (root/'sources'/e['file']).write_bytes(b)
    h=hashlib.sha256(b).hexdigest()
    print(e['url'],len(b),h,flush=True)
    assert h==e['sha256'] and len(b)==e['bytes']
