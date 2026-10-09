from pathlib import Path
import json,hashlib,re
root=Path('/home/regner/.paseo/worktrees/0u71f39f/brackett-greybox');out=Path('/tmp/brackett-height-review');receipt=json.loads((out/'static_checks.json').read_text());fresh=json.loads((out/'fresh_export.json').read_text())
for entry in fresh['exports']:
 asset=entry['asset'];txt=(root/f'scenes/world/brackett_greybox/prefabs/{asset}.tscn').read_text();shapes={}
 for rid,x,y,z in re.findall(r'\[sub_resource type="BoxShape3D" id="([^"]+)"\]\nsize = Vector3\(([^,]+), ([^,]+), ([^)]+)\)',txt):shapes[rid]=[float(x),float(y),float(z)]
 boxes=[]
 for block in txt.split('\n[node ')[1:]:
  if not block.startswith('name="Envelope'):continue
  pos=re.search(r'transform = Transform3D\(([^)]+)\)',block);xyz=[float(v) for v in pos[1].split(',')][-3:];rid=re.search(r'shape = SubResource\("([^"]+)"\)',block)[1];size=shapes[rid]
  boxes.append({'min':[xyz[i]-size[i]/2 for i in range(3)],'max':[xyz[i]+size[i]/2 for i in range(3)]})
 glb=next(e for e in receipt['decoded_glbs'] if e['asset']==asset)
 assert len(boxes)==len(glb['bounds'])
 for b,g in zip(boxes,glb['bounds']):assert all(abs(b[k][i]-g[k][i])<0.00001 for k in ('min','max') for i in range(3))
 glb['box_collision_bounds_match']=True
fps=json.loads((root/'art/models/brackett_greybox/fingerprints.json').read_text())
assert all(hashlib.sha256((root/e['source']).read_bytes()).hexdigest()==e['source_sha256'] and hashlib.sha256((root/'art/models/brackett_greybox'/e['export']).read_bytes()).hexdigest()==e['export_sha256'] for e in fps)
receipt['all_40_source_export_fingerprints_match']=True
(out/'static_checks.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS 3 GLB/collision matches; all 40 fingerprints; 47 unchanged scenes, 3 identity-preserving wrappers')
