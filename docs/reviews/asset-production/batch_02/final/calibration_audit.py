"""Read actual saved calibration and compare every source mesh/material/matrix."""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path('/tmp/batch02-final-10ddb64/snapshot')
OUT=Path('/home/regner/.paseo/worktrees/0u71f39f/asset-register-production/docs/reviews/asset-production/batch_02/final')
META=ROOT/'docs/assets/production/batch_02-evidence/calibration/tree-roof-measurements.json'
meta=json.loads(META.read_text())
assert bpy.app.version==(5,2,2)
assert bpy.app.build_hash.decode()=='d13f752e3b9c'
scene=bpy.context.scene
assert scene.unit_settings.system=='METRIC' and scene.unit_settings.scale_length==1
def material(m):
    values=dict(color=list(m.diffuse_color),use_nodes=m.use_nodes)
    if m.use_nodes:
        values['nodes']=[dict(type=n.type,inputs={i.name: list(i.default_value) if hasattr(i.default_value,'__iter__') else i.default_value
          for i in n.inputs if hasattr(i,'default_value') and i.type in ('RGBA','VECTOR','VALUE','INT','BOOLEAN')}) for n in m.node_tree.nodes]
    return values
def shape(o):
    data=dict(type=o.type,matrix=[list(r) for r in o.matrix_world])
    if o.type=='MESH':
        data.update(vertices=[list(v.co) for v in o.data.vertices],
          polygons=[dict(vertices=list(p.vertices),material=p.material_index,smooth=p.use_smooth) for p in o.data.polygons],
          materials=[material(m) if m else None for m in o.data.materials],
          modifiers=[dict(type=m.type,name=m.name) for m in o.modifiers])
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
instances=[o for o in scene.objects if o.instance_type=='COLLECTION' and o.instance_collection]
assert len(instances)==4
rows=[]
for row in meta['assets']:
    matches=[o for o in instances if o.instance_collection.name==row['collection']]
    assert len(matches)==1, row['collection']
    instance=matches[0]; embedded=instance.instance_collection
    observed=sorted(shape(o) for o in embedded.all_objects)
    source=ROOT/row['source']; sourcehash=hashlib.sha256(source.read_bytes()).hexdigest()
    assert sourcehash==row['source_sha256_before']==row['source_sha256_after']
    assert hashlib.sha256((ROOT/row['glb']).read_bytes()).hexdigest()==row['glb_sha256']
    with bpy.data.libraries.load(str(source),link=False) as (available,requested):
        requested.collections=[row['collection']]
    original=requested.collections[0]
    assert observed==sorted(shape(o) for o in original.all_objects),row['collection']
    assert all(abs(x-y)<1e-6 for x,y in zip(instance.location,row['instance_translation_m']))
    assert instance.rotation_euler.length<1e-6
    assert (instance.scale-Vector((1,1,1))).length<1e-6
    points=[o.matrix_world@Vector(c) for o in embedded.all_objects if o.type=='MESH' for c in o.bound_box]
    bounds=dict(min=[min(p[a] for p in points) for a in range(3)],max=[max(p[a] for p in points) for a in range(3)])
    assert all(abs(bounds[k][a]-row['source_bounds_blender_xyz'][k][a])<1e-6 for k in bounds for a in range(3))
    refs=[o for o in scene.objects if 'reference_1m' in o.name and (o.location-Vector(row['reference_translation_m'])).length<1e-6]
    assert len(refs)==1 and all(abs(d-1)<1e-6 for d in refs[0].dimensions)
    ref=refs[0]
    assert ref.type=='MESH' and len(ref.data.vertices)==8 and len(ref.data.polygons)==6
    coords=[ref.matrix_world@v.co for v in ref.data.vertices]
    assert abs(min(p.z for p in coords))<1e-6 and abs(max(p.z for p in coords)-1)<1e-6
    rows.append(dict(collection=row['collection'],mesh_matrix_material_fingerprints=observed,
      bounds=bounds,instance_translation=list(instance.location),reference_dimensions=list(ref.dimensions),
      reference_translation=list(ref.location),source_sha256=sourcehash,glb_sha256=row['glb_sha256']))
# Arrow stems use their actual mesh's local axial extent transformed into world.
arrows=[]
for o in scene.objects:
    if o.type!='MESH' or not o.data.materials: continue
    label=o.data.materials[0].name
    if not (label.startswith('FRONT +Y') or label.startswith('UP +Z')): continue
    direction=(o.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
    expected=Vector((0,1,0) if label.startswith('FRONT') else (0,0,1))
    assert (direction-expected).length<1e-6
    arrows.append(dict(object=o.name,label=label,actual_direction=list(direction)))
assert len(arrows)==16
assert scene.camera.data.type=='ORTHO'
result=dict(blender=bpy.app.version_string,build=bpy.app.build_hash.decode(),units=scene.unit_settings.system,
 scale_length=scene.unit_settings.scale_length,source_identity_verified=True,rows=rows,arrows=arrows,
 image_render_dimensions=[scene.render.resolution_x,scene.render.resolution_y],camera=scene.camera.name)
(OUT/'calibration-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(passed=True,source_collections=len(rows),arrows=len(arrows),units='METRIC',scale_length=1)))
