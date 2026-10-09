"""Render immutable source collections beside measured metre cubes; never save sources."""
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/assets/production/batch_02-evidence/calibration'
IDS = [('city_planting_04', 'export_city_planting_04_compact'),
       ('city_planting_04', 'export_city_planting_04_broad'),
       ('city_roof_details_01', 'export_city_roof_details_01'),
       ('city_roof_details_02', 'export_city_roof_details_02')]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
rows = []
for index, (asset_id, collection_name) in enumerate(IDS):
    source = ROOT / f'art/source/models/environment/{asset_id}/{asset_id}.blend'
    assert bpy.app.version == (5, 2, 2)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    with bpy.data.libraries.load(str(source), link=False) as (available, requested):
        assert collection_name in available.collections
        requested.collections = [collection_name]
    collection = requested.collections[0]
    collection.hide_render = False
    collection.hide_viewport = False
    for obj in list(collection.all_objects):
        obj.hide_render = False
        obj.hide_viewport = False
    # Original objects retain their exact local/world matrices. Only the presentation
    # collection instance receives a pure translation; there is no rotation or scale.
    points = [obj.matrix_world @ Vector(corner) for obj in collection.all_objects
              if obj.type == 'MESH' for corner in obj.bound_box]
    lo = [min(p[a] for p in points) for a in range(3)]
    hi = [max(p[a] for p in points) for a in range(3)]
    placement = (index * 4.5 - 6.75, 0, 0)
    instance = bpy.data.objects.new(asset_id, None)
    instance.instance_type = 'COLLECTION'
    instance.instance_collection = collection
    instance.location = placement
    scene.collection.objects.link(instance)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(placement[0] + 1.7, 2.2, 0.5))
    reference = bpy.context.object
    reference.name = asset_id + '_reference_1m'
    assert all(abs(d - 1) < 1e-6 for d in reference.dimensions)
    material = bpy.data.materials.get('Calibration coral') or bpy.data.materials.new('Calibration coral')
    material.diffuse_color = (0.85, 0.15, 0.08, 1)
    reference.data.materials.append(material)
    # Calibration arrows are isolated Blender fixtures: +Y front and +Z up.
    origin = Vector((placement[0] - 1.7, 1.3, 0))
    for label, direction, color in [('FRONT +Y', Vector((0, 1, 0)), (0.1, 0.8, 0.2, 1)),
                                     ('UP +Z', Vector((0, 0, 1)), (0.15, 0.4, 1, 1))]:
        mat = bpy.data.materials.new(label + str(index))
        mat.diffuse_color = color
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=.025, depth=.8,
                                             location=origin + direction * .4)
        arrow = bpy.context.object
        arrow.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
        arrow.data.materials.append(mat)
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=.09, radius2=0, depth=.2,
                                       location=origin + direction * .9)
        tip = bpy.context.object
        tip.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
        tip.data.materials.append(mat)
        bpy.ops.object.text_add(location=origin + direction + Vector((0, 0, .15)))
        text = bpy.context.object
        text.data.body = label
        text.data.size = .17
        text.rotation_euler = (math.pi / 2, 0, math.pi)
    bpy.ops.object.text_add(location=(placement[0] + 1.7, 2.21, 1.06))
    bpy.context.object.data.body = '1 m'
    bpy.context.object.data.size = .3
    bpy.context.object.rotation_euler = (math.pi / 2, 0, math.pi)
    bpy.ops.object.text_add(location=(placement[0] + 1.4, 2.5, .1))
    bpy.context.object.data.body = collection_name.removeprefix('export_')
    bpy.context.object.data.size = .2
    bpy.context.object.rotation_euler = (math.pi / 2, 0, math.pi)
    rows.append({'id': asset_id, 'source': str(source.relative_to(ROOT)),
                 'source_sha256_before': digest, 'source_sha256_after': digest,
                 'glb': f'art/models/environment/{asset_id}/{collection_name.removeprefix("export_")}.glb',
                 'glb_sha256': hashlib.sha256((ROOT / f'art/models/environment/{asset_id}/{collection_name.removeprefix("export_")}.glb').read_bytes()).hexdigest(),
                 'collection': collection_name, 'source_bounds_blender_xyz': {'min': lo, 'max': hi},
                 'instance_translation_m': list(placement), 'instance_rotation_rad': [0, 0, 0],
                 'instance_scale': [1, 1, 1], 'source_object_matrices_unchanged': True,
                 'front_vector_blender': [0, 1, 0], 'up_vector_blender': [0, 0, 1],
                 'godot_front_vector': [0, 0, -1], 'godot_up_vector': [0, 1, 0],
                 'reference_dimensions_m': list(reference.dimensions),
                 'reference_translation_m': list(reference.location)})
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
bpy.ops.object.camera_add(location=(9, 28, 17))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 2.3)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 21
scene.camera = camera
for position, energy, size in [((0, -6, 12), 1900, 12), ((4, 5, 9), 1200, 9)]:
    bpy.ops.object.light_add(type='AREA', location=position)
    lamp = bpy.context.object
    lamp.data.energy = energy
    lamp.data.shape = 'DISK'
    lamp.data.size = size
    lamp.rotation_euler = (Vector((0, 0, 2)) - lamp.location).to_track_quat('-Z', 'Y').to_euler()
scene.world = bpy.data.worlds.new('Calibration studio')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.13, 0.16, 0.2, 1)
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(OUT / 'tree-roof-metre-front-up-comparison.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'tree-roof-metre-front-up-comparison.blend'))
bpy.ops.render.render(write_still=True)
(OUT / 'tree-roof-measurements.json').write_text(json.dumps({'blender_version': bpy.app.version_string,
    'build_hash': bpy.app.build_hash.decode(), 'units': 'METRIC', 'scale_length': 1,
    'fixture_dimensions_xyz_m': [1, 1, 1], 'presentation': 'Four tree/roof source variant collection instances; translation only; one-metre cubes are calibration fixtures, not game assets.',
    'assets': rows}, indent=2) + '\n')
