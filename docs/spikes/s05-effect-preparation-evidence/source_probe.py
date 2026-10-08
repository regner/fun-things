"""Inspect committed Blender source topology and dependencies without saving it."""
import hashlib
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
import io_scene_gltf2

output = Path(sys.argv[sys.argv.index('--') + 1])
assert bpy.app.version_string == '5.2.2 LTS'
assert bpy.app.build_hash == b'd13f752e3b9c'
assert io_scene_gltf2.bl_info['version'] == (5, 2, 40)
assert not bpy.data.libraries and not bpy.data.images and not bpy.data.actions
assert list(bpy.data.objects.keys()) == ['ExplosionCarrier']
assert list(bpy.data.collections.keys()) == ['export_s05_explosion_carrier']
obj = bpy.data.objects['ExplosionCarrier']
assert not obj.parent and not obj.modifiers and not obj.animation_data
assert tuple(obj.location) == (0, 0, 0) and tuple(obj.scale) == (1, 1, 1)
assert tuple(obj.rotation_euler) == (0, 0, 0)
assert [m.name for m in obj.data.materials] == ['flash_amber', 'burst_coral', 'flash_ivory']
bm = bmesh.new()
bm.from_mesh(obj.data)
assert all(e.is_manifold and e.is_contiguous for e in bm.edges)
assert all(f.calc_area() > 1e-7 and len(f.verts) == 3 for f in bm.faces)
assert all(math.isfinite(v) for vert in bm.verts for v in vert.co)
todo = set(bm.verts)
components = []
while todo:
    component, stack = set(), [next(iter(todo))]
    while stack:
        vert = stack.pop()
        if vert in component:
            continue
        component.add(vert)
        stack.extend(e.other_vert(vert) for e in vert.link_edges)
    todo -= component
    faces = {f for vert in component for f in vert.link_faces}
    volume = sum(f.verts[0].co.dot(f.verts[1].co.cross(f.verts[2].co)) / 6 for f in faces)
    assert volume > .01, 'Outward winding required for each closed surface'
    minimum = [min(v.co[axis] for v in component) for axis in range(3)]
    maximum = [max(v.co[axis] for v in component) for axis in range(3)]
    components.append(dict(vertices=len(component), triangles=len(faces),
                           min_blender=minimum, max_blender=maximum, volume_m3=volume))
assert len(components) == 6
assert len(bm.verts) == 684 and len(bm.faces) == 1344
minimum = [min(v.co[axis] for v in bm.verts) for axis in range(3)]
maximum = [max(v.co[axis] for v in bm.verts) for axis in range(3)]
assert minimum[2] >= 0 and maximum[2] <= 2
assert maximum[0] - minimum[0] <= 4 and maximum[1] - minimum[1] <= 4
geometry = dict(vertices=[list(v.co) for v in obj.data.vertices],
                triangles=[list(f.vertices) for f in obj.data.polygons],
                material_indices=[f.material_index for f in obj.data.polygons])
materials = []
for mat in obj.data.materials:
    node = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    assert len(mat.node_tree.nodes) == 2 and not mat.library
    assert node.inputs['Alpha'].default_value == 1
    assert node.inputs['Emission Strength'].default_value == 0
    materials.append(dict(name=mat.name, base_color=list(node.inputs['Base Color'].default_value),
                          roughness=node.inputs['Roughness'].default_value))
receipt = dict(blender=bpy.app.version_string, build_hash=bpy.app.build_hash.decode(),
               exporter=list(io_scene_gltf2.bl_info['version']), source=bpy.data.filepath,
               source_sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
               collection='export_s05_explosion_carrier', members=['ExplosionCarrier'],
               vertices=len(bm.verts), triangles=len(bm.faces), components=components,
               min_godot=[minimum[0], minimum[2], -maximum[1]],
               max_godot=[maximum[0], maximum[2], -minimum[1]],
               geometry_sha256=hashlib.sha256(json.dumps(geometry, sort_keys=True).encode()).hexdigest(),
               materials=materials, external_dependencies=[], checks='PASS')
output.write_text(json.dumps(receipt, indent=2) + '\n')
bm.free()
print('S05_SOURCE_PROBE_PASS', json.dumps(receipt, sort_keys=True))
