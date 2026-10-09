"""Resolve observed panel depth and normal artifacts in the saved Astra car sources."""
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[4]
for record_path in sorted((ROOT/'docs/assets/vehicle_car_evidence').glob('car_*_a_source.json')):
    record=json.loads(record_path.read_text())
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/record['source']))
    scene=bpy.context.scene
    assert not scene.get('panel_depth_revision',False),'One-time source refinement already applied'
    col=bpy.data.collections[record['collection']]
    length=record['source_spec']['length']
    for name,offset in [('FrontBumper',.012),('RearBumper',-.012),
                        ('HeadlampLeft',.04),('HeadlampRight',.04)]:
        bpy.data.objects[name].location.y+=offset
    hood=bpy.data.objects['HoodInset']
    slope=-.04/(length/2-.92)
    hood.location.z=1.04+slope*(hood.location.y-.70)+.003
    hood.rotation_euler.x=math.atan(slope)
    bpy.context.view_layer.objects.active=hood
    hood.select_set(True)
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    hood.select_set(False)
    shader=next(n for n in bpy.data.materials['glass'].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    shader.inputs['Roughness'].default_value=.42
    for obj in col.all_objects:
        if obj.type!='MESH':
            continue
        bpy.context.view_layer.objects.active=obj
        for face in obj.data.polygons:
            face.use_smooth=True
        if hasattr(obj.data,'set_sharp_from_angle'):
            obj.data.set_sharp_from_angle(angle=math.radians(35))
        mod=obj.modifiers.new('final_surface_normals','WEIGHTED_NORMAL')
        mod.keep_sharp=True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    scene['panel_depth_revision']=True
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/record['source']))
    settings=json.loads((ROOT/'tools/assets/export_settings.json').read_text())
    settings.update(export_animations=False,export_skins=False,collection=col.name,
        filepath=str(ROOT/record['export']))
    bpy.ops.export_scene.gltf(**settings)
    points=[o.matrix_world@Vector(c) for o in col.all_objects if o.type=='MESH' for c in o.bound_box]
    lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
    record.update(godot_aabb_min=[lo[0],lo[2],-hi[1]],godot_aabb_max=[hi[0],hi[2],-lo[1]],
        panel_depth_revision=1)
    record_path.write_text(json.dumps(record,indent=2)+'\n')
    print('SURFACE_REFINEMENT',record['id'],flush=True)
