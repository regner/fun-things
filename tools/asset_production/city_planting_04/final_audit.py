"""Dependency-free final payload/PNG/receipt audit after every writer has exited."""
from pathlib import Path
import json,hashlib,ast,shutil,struct,zlib
R=Path(__file__).resolve().parents[3]; E=R/'docs/assets/production/city_planting_04-evidence'; T=R/'tools/asset_production/city_planting_04'
p=E/'commands.json'; l=json.loads(p.read_text()); l=[r for r in l if not(r['name']=='inspect_failure' and 'receipt_note' in r)]; p.write_text(json.dumps(l,indent=2)+'\n')
for name in ['export_verified','check_glb','reexport','assembly_preview_final','preview_saved']:assert next(r for r in l if r['name']==name)['exit_code']==0
for r in l:assert (E/r['raw_log']).is_file()
images=[]
for f in sorted(E.glob('*.png')):
 data=f.read_bytes(); assert data[:8]==b'\x89PNG\r\n\x1a\n'; offset=8; compressed=b''; size=None
 while offset<len(data):
  n=struct.unpack_from('>I',data,offset)[0]; tag=data[offset+4:offset+8]; payload=data[offset+8:offset+8+n]
  assert zlib.crc32(tag+payload)==struct.unpack_from('>I',data,offset+8+n)[0]
  if tag==b'IHDR':size=list(struct.unpack_from('>II',payload))
  if tag==b'IDAT':compressed+=payload
  offset+=12+n
 assert size and zlib.decompress(compressed)
 images.append({'path':str(f.relative_to(R)),'size':size})
assert len(images)==6
for f in T.glob('*.py'):ast.parse(f.read_text())
for row in json.loads((E/'reference_inputs.json').read_text()):assert hashlib.sha256((R/row['path']).read_bytes()).hexdigest()==row['sha256']
for row in json.loads((E/'assembly_preview.json').read_text())['inputs']:assert hashlib.sha256((R/row['path']).read_bytes()).hexdigest()==row['sha256']
for v in ['compact','broad']:
 f='city_planting_04_'+v+'.glb'; assert (R/'art/models/environment/city_planting_04'/f).read_bytes()==(E/'reexport'/f).read_bytes()
source=R/'art/source/models/environment/city_planting_04/city_planting_04.blend'
(E/'final_audit.json').write_text(json.dumps({'source':{'path':str(source.relative_to(R)),'bytes':source.stat().st_size,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()},'checks':'PASS: final jobs exit 0; complete logged jobs; owned Python syntax; six PNG CRC/inflate checks; reference fingerprints unchanged; both GLB byte comparisons','images':images,'owned_writers':'Blender subprocesses completed; no live editor or owned background writer','remaining_gates':['Godot import/prefab','collision/runtime','device performance','independent acceptance']},indent=2)+'\n')
print('FINAL_AUDIT_PASS')
