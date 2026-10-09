import bpy, json, hashlib
from pathlib import Path
root=Path('/home/regner/.paseo/worktrees/0u71f39f/brackett-greybox')
out=Path('/tmp/brackett-height-review/exports')
assert bpy.app.version_string=='5.2.2 LTS'
bpy.ops.wm.open_mainfile(filepath=str(root/'art/source/models/brackett_greybox/district_04_kit.blend'))
settings=json.loads((root/'tools/s01/export_settings.json').read_text())
settings['export_animations']=False
manifest=next(e for e in json.loads((root/'art/source/models/brackett_greybox/source_manifest.json').read_text()) if e['source'].endswith('district_04_kit.blend'))
receipts=[]
for asset in ('office','tower_mid','tower_high'):
 col=bpy.data.collections['export_'+asset]
 assert sorted(o.name for o in col.all_objects)==manifest['collections'][col.name]
 objects=[]
 for obj in col.all_objects:
  assert tuple(obj.scale)==(1,1,1)
  assert all(abs(x)<1e-6 for x in obj.rotation_euler)
  points=[obj.matrix_world @ v.co for v in obj.data.vertices]
  objects.append({'name':obj.name,'source_bounds_xyz':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)],'materials':[m.name for m in obj.data.materials]})
 path=out/(asset+'.glb')
 bpy.ops.export_scene.gltf(**settings,collection=col.name,filepath=str(path))
 same=path.read_bytes()==(root/'art/models/brackett_greybox'/path.name).read_bytes()
 assert same
 receipts.append({'asset':asset,'byte_identical':same,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_objects':objects})
(out.parent/'fresh_export.json').write_text(json.dumps({'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'unit_scale':bpy.context.scene.unit_settings.scale_length,'exports':receipts},indent=2)+'\n')
print('INDEPENDENT_THREE_EXPORTS_IDENTICAL')
