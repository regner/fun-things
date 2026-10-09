"""Export declared Wedgewire collections from saved Blender source, never rebuild them."""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
assert bpy.app.version_string == '5.2.2 LTS'
assert Path(bpy.data.filepath).name == 'smg_wedgewire_a.blend'
assert bpy.context.scene.unit_settings.scale_length == 1
settings = json.loads((ROOT / 'tools/assets/export_settings.json').read_text())
settings.update(export_animations=False, export_skins=False)
rows = {}
for name in ['smg_wedgewire_a']:
    col = bpy.data.collections['export_' + name]
    members = sorted(col.all_objects, key=lambda x: x.name)
    points = []
    for obj in members:
        assert all(abs(v - 1) < 0.0001 for v in obj.scale), obj.name
        assert obj.matrix_world.determinant() > 0, obj.name
        assert all(abs(v) < 0.0001 for v in obj.rotation_euler), obj.name
        if obj.type == 'MESH':
            points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    # glTF's Y-up conversion maps Blender (x,y,z) to Godot (x,z,-y).
    converted = [(p.x, p.z, -p.y) for p in points]
    rows[name] = {'collection': col.name, 'members': [o.name for o in members],
                  'aabb_min': [min(p[i] for p in converted) for i in range(3)],
                  'aabb_max': [max(p[i] for p in converted) for i in range(3)],
                  'triangles': sum(len(o.data.polygons) for o in members if o.type == 'MESH'),
                  'materials': sorted({m.name for o in members if o.type == 'MESH'
                                       for m in o.data.materials})}
    settings.update(collection=col.name, filepath=str(OUT / (name + '.glb')))
    bpy.ops.export_scene.gltf(**settings)
rows['sockets'] = {o.name: {'position_godot': [o.location.x, o.location.z, -o.location.y],
                          'basis_godot': [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                          'contact_normal_godot': [o['contact_normal_blender'][0],
                                                   o['contact_normal_blender'][2],
                                                   -o['contact_normal_blender'][1]]
                          if 'contact_normal_blender' in o else None}
                    for o in bpy.data.collections['export_smg_wedgewire_a'].all_objects
                    if o.type == 'EMPTY'}
rows['settings'] = {k: v for k, v in settings.items() if k not in ['filepath', 'collection']}
rows['blender_version'] = bpy.app.version_string
rows['blender_hash'] = bpy.app.build_hash.decode()
(OUT / 'export_receipt.json').write_text(json.dumps(rows, indent=2) + '\n')
print('SMG_EXPORT_OK', OUT)
