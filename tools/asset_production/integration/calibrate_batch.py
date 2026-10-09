"""Render immutable source collections beside measured metre cubes; never save sources."""
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/assets/production/batch_01-evidence/calibration'
IDS = ['city_lights_01', 'city_lights_02', 'city_sign_supports_01',
       'city_planting_01', 'city_planting_02']
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
rows = []
for index, asset_id in enumerate(IDS):
    source = ROOT / f'art/source/models/environment/{asset_id}/{asset_id}.blend'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    collection_name = 'export_' + asset_id
    with bpy.data.libraries.load(str(source), link=False) as (available, requested):
        assert collection_name in available.collections
        requested.collections = [collection_name]
    collection = requested.collections[0]
    # Original objects retain their exact local/world matrices. Only the presentation
    # collection instance receives a pure translation; there is no rotation or scale.
    points = [obj.matrix_world @ Vector(corner) for obj in collection.all_objects
              if obj.type == 'MESH' for corner in obj.bound_box]
    lo = [min(p[a] for p in points) for a in range(3)]
    hi = [max(p[a] for p in points) for a in range(3)]
    placement = (index * 3.0 - 6.0, 0, 0)
    instance = bpy.data.objects.new(asset_id, None)
    instance.instance_type = 'COLLECTION'
    instance.instance_collection = collection
    instance.location = placement
    scene.collection.objects.link(instance)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(placement[0] + 1.2, -1, 0.5))
    reference = bpy.context.object
    reference.name = asset_id + '_reference_1m'
    assert all(abs(d - 1) < 1e-6 for d in reference.dimensions)
    material = bpy.data.materials.get('Calibration coral') or bpy.data.materials.new('Calibration coral')
    material.diffuse_color = (0.85, 0.15, 0.08, 1)
    reference.data.materials.append(material)
    rows.append({'id': asset_id, 'source': str(source.relative_to(ROOT)),
                 'source_sha256_before': digest, 'source_sha256_after': digest,
                 'collection': collection_name, 'source_bounds_blender_xyz': {'min': lo, 'max': hi},
                 'instance_translation_m': list(placement), 'instance_rotation_rad': [0, 0, 0],
                 'instance_scale': [1, 1, 1], 'source_object_matrices_unchanged': True,
                 'reference_dimensions_m': list(reference.dimensions),
                 'reference_translation_m': list(reference.location)})
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
bpy.ops.object.camera_add(location=(10, -24, 13))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 2.3)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 19
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
scene.render.filepath = str(OUT / 'five-source-metre-comparison.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'five-source-metre-comparison.blend'))
bpy.ops.render.render(write_still=True)
(OUT / 'measurements.json').write_text(json.dumps({'blender_version': bpy.app.version_string,
    'build_hash': bpy.app.build_hash.decode(), 'units': 'METRIC', 'scale_length': 1,
    'fixture_dimensions_xyz_m': [1, 1, 1], 'presentation': 'Five source collection instances; translation only; one-metre cubes are calibration fixtures, not game assets.',
    'assets': rows}, indent=2) + '\n')
