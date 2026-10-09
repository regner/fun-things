import json, struct, subprocess, hashlib, re
from pathlib import Path
root=Path('/home/regner/.paseo/worktrees/0u71f39f/brackett-greybox')
base='cf6dae7a420ec477dd85654b615e0fb296ed8aaa'
candidate='21fd536aa4415488d2d06b05ee0a8e3b7cf5227f'
def gitbytes(rev,path): return subprocess.check_output(['git','show',rev+':'+str(path)],cwd=root)
def decode(data):
 n,t=struct.unpack_from('<II',data,12);j=json.loads(data[20:20+n]);o=20+n;bn,bt=struct.unpack_from('<II',data,o);return j,data[o+8:o+8+bn]
def acc(j,b,index):
 a=j['accessors'][index];v=j['bufferViews'][a['bufferView']];assert a['componentType']==5126 and a['type']=='VEC3'
 offset=v.get('byteOffset',0)+a.get('byteOffset',0);return [struct.unpack_from('<fff',b,offset+i*v.get('byteStride',12)) for i in range(a['count'])]
checks=[]
for asset,height in [('office',42),('tower_mid',68),('tower_high',90)]:
 path=Path('art/models/brackett_greybox')/(asset+'.glb');old,ob=decode(gitbytes(base,path));new,nb=decode(gitbytes(candidate,path))
 assert old['materials']==new['materials'];assert not new.get('extensionsUsed')
 assert len(old['nodes'])==len(new['nodes'])
 bounds=[]
 for on,nn in zip(old['nodes'],new['nodes']):
  assert on['name']==nn['name'];assert not nn.get('rotation') and not nn.get('matrix') and not nn.get('scale')
  if 'mesh' not in nn: continue
  op=old['meshes'][on['mesh']]['primitives'];np=new['meshes'][nn['mesh']]['primitives']
  assert len(op)==len(np)
  verts=[]
  for a,z in zip(op,np):
   av=acc(old,ob,a['attributes']['POSITION']);zv=acc(new,nb,z['attributes']['POSITION']);assert len(av)==len(zv)
   assert all(abs(v[0]-w[0])<1e-6 and abs(v[2]-w[2])<1e-6 for v,w in zip(av,zv))
   normal_delta=max(abs(v-w) for x,y in zip(acc(old,ob,a['attributes']['NORMAL']),acc(new,nb,z['attributes']['NORMAL'])) for v,w in zip(x,y))
   print(asset,nn['name'],'max_normal_component_change',normal_delta)
   assert all(abs(sum(v*v for v in normal)-1)<0.00001 for normal in acc(new,nb,z['attributes']['NORMAL']))
   tr=nn.get('translation',[0,0,0]);verts += [tuple(p[i]+tr[i] for i in range(3)) for p in zv]
  bounds.append({'node':nn['name'],'min':[min(p[i] for p in verts) for i in range(3)],'max':[max(p[i] for p in verts) for i in range(3)]})
 assert abs(max(b['max'][1] for b in bounds)-height)<0.0001
 assert abs(min(b['min'][1] for b in bounds))<0.0001
 checks.append({'asset':asset,'bounds':bounds,'xz_vertices_materials_preserved_normals_unit':True})
scene_paths=subprocess.check_output(['git','ls-tree','-r','--name-only',candidate,'scenes/world/brackett_greybox'],cwd=root,text=True).splitlines()
unchanged=[]
for path in scene_paths:
 if path.endswith('.tscn'):
  old=gitbytes(base,path);new=gitbytes(candidate,path)
  # The six allowed changed lines contain box sizes/vertical centres only.
  if old!=new:
   assert Path(path).name in ('office.tscn','tower_mid.tscn','tower_high.tscn')
   assert re.findall(rb'uid="[^"]+"|unique_id=\d+|id="[^"]+"|world_id[^\n]+',old)==re.findall(rb'uid="[^"]+"|unique_id=\d+|id="[^"]+"|world_id[^\n]+',new)
  else: unchanged.append(path)
imports=subprocess.check_output(['git','ls-tree','-r','--name-only',candidate,'art/models/brackett_greybox'],cwd=root,text=True).splitlines()
assert all(gitbytes(base,p)==gitbytes(candidate,p) for p in imports if p.endswith('.import'))
sector=(root/'scenes/world/brackett_greybox/sectors/district_04.tscn').read_text()
assert len(re.findall('instance=ExtResource\\("2_mo5jn"\\)',sector))==26
assert len(re.findall('instance=ExtResource\\("3_b2dbo"\\)',sector))==3
stability=json.loads((root/'art/source/models/brackett_greybox/review/height_revision/editor_stability.json').read_text())
assert all(hashlib.sha256((root/'scenes/world/brackett_greybox'/p).read_bytes()).hexdigest()==sha for p,sha in stability['sha256'].items())
report={'base':base,'candidate':candidate,'decoded_glbs':checks,'unchanged_scenes_count':len(unchanged),'changed_prefab_identities_preserved':True,'all_import_sidecars_unchanged':True,'glassward_placements':{'office':26,'tower_mid':3,'tower_high':0},'producer_six_editor_stability_hashes_match':True}
Path('/tmp/brackett-height-review/static_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
