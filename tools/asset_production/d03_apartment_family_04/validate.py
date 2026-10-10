"""Validate the saved reference, original dependencies, actual GLB surfaces and stepped-bar geometry."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import runpy
import struct

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.geometry import intersect_ray_tri

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_04"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SCRATCH = Path(f"C:/tmp/ft/assets/{NID}")
PREFAB = ROOT / f"scenes/prefabs/environment/{NID}.tscn"
assert bpy.app.version_string == "5.2.2 LTS"
engine = json.loads((SCRATCH / "prefab-check.json").read_text())
assert engine["ok"] and engine["roundtrip"]["byte_stable"]
assert hashlib.sha256(PREFAB.read_bytes()).hexdigest() == engine["roundtrip"]["normalized_sha256"]
# Independent inventory includes four complete steps, never duplicate upper walls/caps.
assert Counter(Path(item['path']).stem for item in engine['models']) == {
    'd03_apartment_family_05': 12, 'd03_apartment_family_07': 8,
    'd03_apartment_family_08': 2, 'd03_apartment_family_09': 4,
    'd03_apartment_family_10_straight': 5, 'd03_apartment_family_10_end': 6,
    'd03_apartment_family_11': 4,
}
expected_steps = [
    ('WestLowerStep', [-9.12, 3.2, 0], 180),
    ('WestUpperStep', [-3.12, 6.4, 0], 180),
    ('EastUpperStep', [3.12, 6.4, 0], 0),
    ('EastLowerStep', [9.12, 3.2, 0], 0),
]
for name, position, yaw in expected_steps:
    item = next(item for item in engine['placements'] if item['name'] == name)
    assert max(abs(a-b) for a,b in zip(item['position'], position)) < .001
    assert abs(abs(item['yaw_degrees']) - yaw) < .001
    assert item['prefab'].endswith('d03_apartment_family_11.tscn')
for name, position in [('WestMidL0', [-6, 0, 0]), ('EastMidL0', [6, 0, 0]),
                       ('CrownUpperBalcony', [0, 3.2, -6])]:
    item = next(item for item in engine['placements'] if item['name'] == name)
    assert max(abs(a-b) for a,b in zip(item['position'], position)) < .001
    assert item['yaw_degrees'] == 0


def receipt(path):
    """Pin original dependencies and the final saved scene, without copying their payloads."""
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def read_glb(path):
    """Read binary indexed triangles/normals, not just declared glTF accessor bounds."""
    raw = path.read_bytes()
    assert struct.unpack_from('<4sII', raw) == (b'glTF', 2, len(raw))
    length, kind = struct.unpack_from('<II', raw, 12)
    assert kind == 0x4E4F534A
    asset = json.loads(raw[20:20 + length])
    binary_size, kind = struct.unpack_from('<II', raw, 20 + length)
    assert kind == 0x004E4942
    binary = raw[28 + length:28 + length + binary_size]

    def values(index):
        """Decode each packed accessor with its actual component width and stride."""
        accessor = asset['accessors'][index]
        view = asset['bufferViews'][accessor['bufferView']]
        code = {5126: 'f', 5125: 'I', 5123: 'H', 5121: 'B'}[accessor['componentType']]
        count = {'SCALAR': 1, 'VEC3': 3}[accessor['type']]
        fmt = '<' + code * count
        offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
        stride = view.get('byteStride', struct.calcsize(fmt))
        return [struct.unpack_from(fmt, binary, offset + i * stride)
                for i in range(accessor['count'])]

    assert len(asset['meshes']) == 1
    assert not any(asset.get(key) for key in ('images', 'skins', 'animations', 'cameras'))
    triangles, vertices = [], []
    for primitive in asset['meshes'][0]['primitives']:
        points = [Vector(p) for p in values(primitive['attributes']['POSITION'])]
        normals = [Vector(n) for n in values(primitive['attributes']['NORMAL'])]
        assert all(abs(n.length - 1) < .0001 for n in normals)
        assert all(math.isfinite(v) for p in points for v in p)
        indices = [i[0] for i in values(primitive['indices'])]
        for offset in range(0, len(indices), 3):
            triangle = tuple(points[i] for i in indices[offset:offset + 3])
            a, b, c = triangle
            assert (b - a).cross(c - a).length > 2e-10
            triangles.append(triangle)
        vertices.extend(points)
    return triangles, vertices, len(asset['meshes'][0]['primitives'])


# Original exports are reproduced, not replaced or flattened into another building mesh.
runpy.run_path(str(Path(__file__).with_name('export.py')), run_name='__main__')
paths = sorted({item['path'].removeprefix('res://') for item in engine['models']})
dependencies, geometry = [], {}
for relative in paths:
    path = ROOT / relative
    sibling = path.parent.name
    source = ROOT / f'art/source/models/environment/{sibling}/{sibling}.blend'
    fresh = SCRATCH / 'reexport' / sibling / path.name
    assert path.read_bytes() == fresh.read_bytes(), path
    bpy.ops.wm.open_mainfile(filepath=str(source))
    collection = bpy.data.collections['export_' + path.stem]
    meshes = [o for o in collection.objects if o.type == 'MESH']
    assert len(meshes) == 1
    obj = meshes[0]
    assert not obj.modifiers and obj.matrix_world == Matrix.Identity(4)
    mesh = obj.data
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    bm.free()
    assert nonmanifold == 0 and all(p.area > 1e-10 for p in mesh.polygons)
    assert all(abs(n.vector.length - 1) < .0001 for n in mesh.corner_normals)
    triangles, vertices, surfaces = read_glb(path)
    assert len(triangles) == len(mesh.loop_triangles)
    geometry[relative] = (triangles, vertices, surfaces, len(mesh.vertices))
    dependencies.append({'source': receipt(source), 'export': receipt(path),
        'import': receipt(path.with_suffix('.glb.import')), 'triangles': len(triangles),
        'source_vertices': len(mesh.vertices), 'export_vertices': len(vertices),
        'meshes': 1, 'surfaces': surfaces, 'nonmanifold_edges': nonmanifold,
        'degenerate_faces': 0, 'degenerate_glb_triangles': 0, 'unit_normals': True,
        'fresh_reexport_byte_identical': True})

all_triangles, all_vertices = [], []
totals = Counter()
for item in engine['models']:
    triangles, vertices, surfaces, source_vertices = geometry[item['path'].removeprefix('res://')]
    matrix = Matrix.Translation(Vector(item['position'])) @ Matrix.Rotation(
        math.radians(item['yaw_degrees']), 4, 'Y')
    all_triangles.extend(tuple(matrix @ point for point in tri) for tri in triangles)
    all_vertices.extend(matrix @ point for point in vertices)
    totals.update(triangles=len(triangles), source_vertices=source_vertices,
                  export_vertices=len(vertices), meshes=1, surfaces=surfaces)
minimum = [min(p[i] for p in all_vertices) for i in range(3)]
maximum = [max(p[i] for p in all_vertices) for i in range(3)]
assert max(abs(a - b) for a, b in zip(minimum, [-15.34, 0, -7.5])) < .001
assert max(abs(a - b) for a, b in zip(maximum, [15.34, 13.12, 6.18])) < .001
assert totals['meshes'] == engine['mesh_count'] and totals['surfaces'] == engine['surface_count']


def top_at(x, z):
    """Measure the first actual triangle surface hit from above, including visual-only caps."""
    origin, direction = Vector((x, 20, z)), Vector((0, -1, 0))
    hits = [hit.y for a, b, c in all_triangles
            if (hit := intersect_ray_tri(a, b, c, direction, origin, True)) is not None
            and hit.y <= 20]
    return max(hits) if hits else None


# Literal height profile checks all five fields, four step caps and their adjacent roofs.
roof_samples = []
for x, z, expected in [(-12, 0, 6.62), (-6, 0, 9.82), (0, 0, 13.02),
                        (6, 0, 9.82), (12, 0, 6.62),
                        (-9.75, 0, 6.62), (-9.12, 0, 9.92), (-8.999, 0, 9.82),
                        (-3.75, 0, 9.82), (-3.12, 0, 13.12), (-2.999, 0, 13.02),
                        (2.999, 0, 13.02), (3.12, 0, 13.12), (3.75, 0, 9.82),
                        (8.999, 0, 9.82), (9.12, 0, 9.92), (9.75, 0, 6.62),
                        (-15.12, 0, 6.72), (15.12, 0, 6.72),
                        (-14.999, 0, 6.62), (14.999, 0, 6.62),
                        (-12, -5.9, 6.72), (-6, -5.9, 9.92), (0, -5.9, 13.12),
                        (6, 5.9, 9.92), (12, 5.9, 6.72)]:
    actual = top_at(x, z)
    assert actual is not None and abs(actual - expected) < .001, (x, z, actual, expected)
    roof_samples.append({'xz': [x, z], 'expected_y': expected, 'actual_y': actual})
# Both 4m side reservations and the front link remain clear of all visual geometry.
clear_samples = []
for z in range(-12, 13, 2):
    for x in (-21, -19, -17, 17, 19, 21):
        assert top_at(x, z) is None, (x, z)
        clear_samples.append([x, z])
for x in range(-21, 22, 2):
    for z in (-12, -10, -8):
        assert top_at(x, z) is None, (x, z)
        clear_samples.append([x, z])

# Seven ground rectangles prove the bay pitch and the two terminal extensions.
expected_ground = [(-15, -6, -9, 6), (-9, -6, -3, 6), (-3, -6, 3, 6),
                   (3, -6, 9, 6), (9, -6, 15, 6),
                   (-15.24, -6, -15, 6), (15, -6, 15.24, 6)]
ground_boxes = [box for box in engine['collision_boxes'] if abs(box['min'][1]) < .001]
assert len(ground_boxes) == len(expected_ground)
for x0, z0, x1, z1 in expected_ground:
    assert any(max(abs(a-b) for a,b in zip(box['min'] + box['max'],
               [x0, 0, z0, x1, 3.2, z1])) < .001 for box in ground_boxes)
footprint_area = sum((x1-x0)*(z1-z0) for x0,z0,x1,z1 in expected_ground)
assert abs(footprint_area - 365.76) < .001
# Actual core stack counts and step-wall boxes independently enforce only one-storey drops.
for prefix, levels in [('WestLow', [0, 3.2]), ('WestMid', [0, 3.2, 6.4]),
                       ('Crown', [0, 3.2, 6.4, 9.6]), ('EastMid', [0, 3.2, 6.4]),
                       ('EastLow', [0, 3.2])]:
    boxes = [box for box in engine['collision_boxes'] if box['path'].startswith(prefix+'L')]
    assert len(boxes) == len(levels)
    assert all(abs(box['max'][1] - box['min'][1] - 3.2) < .001 for box in boxes)
    assert max(abs(a-b) for a,b in zip(sorted(box['min'][1] for box in boxes), levels)) < .001
for name, low_y, high_y in [('WestLowerStep', 6.4, 9.6), ('WestUpperStep', 9.6, 12.8),
                           ('EastUpperStep', 9.6, 12.8), ('EastLowerStep', 6.4, 9.6)]:
    boxes = [box for box in engine['collision_boxes'] if box['path'].startswith(name+'/')]
    assert len(boxes) == 1
    assert abs(boxes[0]['min'][1] - low_y) < .001
    assert abs(boxes[0]['max'][1] - high_y) < .001

prefabs = sorted({ROOT / item['prefab'].removeprefix('res://') for item in engine['placements']})
report = {'asset_id': 'd03_apartment_family.04', 'output_type': 'Assembly reference',
    'new_meshes': 0, 'new_source_or_glb': 'Not applicable: existing-prefab composition only',
    'blender': bpy.app.version_string, 'blender_build': bpy.app.build_hash.decode(),
    'prefab': receipt(PREFAB), 'dependencies': dependencies,
    'linked_prefabs': [receipt(p) for p in sorted(set(prefabs))],
    'instance_totals': dict(totals), 'actual_glb_aabb_min': minimum, 'actual_glb_aabb_max': maximum,
    'ground_footprint_area_m2': footprint_area,
    'ground_solid_rectangles_xz': expected_ground, 'roof_first_hit_samples': roof_samples, 'unroofed_link_samples': clear_samples,
    'godot': engine, 'renders': json.loads((SCRATCH / 'renders.json').read_text()),
    'ok': True}
(EVIDENCE / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', newline='\n')
print('PASS:', json.dumps(dict(totals)), ';', len(roof_samples), 'roof hits;', len(clear_samples),
      'open visual-link samples; 7 dependency GLBs byte-identical')
