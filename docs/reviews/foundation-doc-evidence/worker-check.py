from pathlib import Path
import re,sys,hashlib,json,tomllib
from urllib.parse import unquote
paths=[Path(p) for p in sys.argv[1:]]
def slug(s):
 s=re.sub(r'[`*_]','',s).lower()
 return re.sub(r'[^\w\- ]','',s).replace(' ','-')
count=0
for source in paths:
 content=source.read_text(); assert '\r' not in content,source
 assert not re.search(r'[ \t]+$',content,re.M),source
 for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)',content):
  if re.match(r'\w+://',target): continue
  path,_,anchor=unquote(target).partition('#'); dest=source.parent/path if path else source
  assert dest.exists(),(source,target)
  if anchor: assert anchor in [slug(x) for x in re.findall(r'^#{1,6} (.+)$',dest.read_text(),re.M)],(source,target)
  count+=1
print(f'PASS {len(paths)} documents, {count} local links/anchors, LF and trailing whitespace')
config=tomllib.loads(Path('mise.toml').read_text())
for task in ('gdstyle:check','gdscript:check','resources:check','s01:clean','s01:reexport','spike:s03','tools:check'):
 assert task in config['tasks'],task
 for path in re.findall(r'tools/[\w/]+\.py',config['tasks'][task]['run']): assert Path(path).exists(),path
print('PASS seven named mise tasks and direct tool targets exist (static scope inspection only)')
s01=json.loads(Path('docs/spikes/s01-evidence/fingerprints.json').read_text())
for name,row in s01.items():
 for label,path in [('source_sha256',f'art/source/models/spikes/{name}.blend'),('export_sha256',f'art/models/spikes/{name}.glb')]:
  assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==row[label],path
s03=json.loads(Path('docs/spikes/s03-evidence/reviewed-fix-result.json').read_text())
for path,digest in s03['fixture_sha256'].items(): assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,path
assert s03['ok'] and all(x['ok'] for x in s03['results'].values())
compiled=json.loads(Path('docs/spikes/s03-evidence/reviewed-fix-compilation.json').read_text())
assert len(compiled)==10 and all(x['ok'] for x in compiled)
print('PASS retained S01 4 hashes, S03 17 hashes and accepted 10-script/result records; no runtime rerun')
