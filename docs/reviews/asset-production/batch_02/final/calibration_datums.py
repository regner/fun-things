"""Read only actual metre fixtures, presentation matrices, bounds and arrow axes.

This is a bounded datum inspection, not a retry of the failed full fingerprint audit.
"""
import bpy,json
from pathlib import Path
from mathutils import Vector
scene=bpy.context.scene
out=Path('/home/regner/.paseo/worktrees/0u71f39f/asset-register-production/docs/reviews/asset-production/batch_02/final')
instances=[]; fixtures=[]; arrows=[]
for obj in scene.objects:
    if obj.instance_type=='COLLECTION' and obj.instance_collection:
        points=[mesh.matrix_world@Vector(corner) for mesh in obj.instance_collection.all_objects
          if mesh.type=='MESH' for corner in mesh.bound_box]
        instances.append(dict(name=obj.name,collection=obj.instance_collection.name,
          matrix=[list(r) for r in obj.matrix_world],
          source_bounds=dict(min=[min(p[a] for p in points) for a in range(3)],max=[max(p[a] for p in points) for a in range(3)]),
          object_names=sorted(o.name for o in obj.instance_collection.all_objects)))
    if obj.type=='MESH' and 'reference_1m' in obj.name:
        vertices=[obj.matrix_world@v.co for v in obj.data.vertices]
        fixtures.append(dict(name=obj.name,dimensions=list(obj.dimensions),matrix=[list(r) for r in obj.matrix_world],
          minimum=[min(v[a] for v in vertices) for a in range(3)],maximum=[max(v[a] for v in vertices) for a in range(3)],
          vertices=len(obj.data.vertices),faces=len(obj.data.polygons)))
    if obj.type=='MESH' and obj.data.materials:
        label=obj.data.materials[0].name
        if label.startswith('FRONT +Y') or label.startswith('UP +Z'):
            arrows.append(dict(name=obj.name,label=label,direction=list((obj.matrix_world.to_3x3()@Vector((0,0,1))).normalized())))
result=dict(blender=bpy.app.version_string,build=bpy.app.build_hash.decode(),units=scene.unit_settings.system,
 scale_length=scene.unit_settings.scale_length,instances=instances,fixtures=fixtures,arrows=arrows,
 render=dict(width=scene.render.resolution_x,height=scene.render.resolution_y,percentage=scene.render.resolution_percentage,
   engine=scene.render.engine,samples=scene.cycles.samples),camera_matrix=[list(r) for r in scene.camera.matrix_world],
 camera_type=scene.camera.data.type,camera_ortho_scale=scene.camera.data.ortho_scale)
(out/'calibration-datums.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
