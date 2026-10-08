"""Independent export-byte, hierarchy, accessor, topology and overhead-gap checks."""
import hashlib
import json
import math
import struct
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
path = ROOT / 'art/models/spikes/s05_explosion_carrier.glb'
raw = path.read_bytes()
assert struct.unpack_from('<4sII', raw) == (b'glTF', 2, len(raw))
json_length, chunk_type = struct.unpack_from('<II', raw, 12)
assert chunk_type == 0x4E4F534A
model = json.loads(raw[20:20 + json_length])
bin_offset = 20 + json_length
bin_length, chunk_type = struct.unpack_from('<II', raw, bin_offset)
assert chunk_type == 0x004E4942 and bin_offset + 8 + bin_length == len(raw)
data = raw[bin_offset + 8:]
assert model['asset'] == {'generator': 'Khronos glTF Blender I/O v5.2.40', 'version': '2.0'}
assert model['nodes'] == [{'mesh': 0, 'name': 'ExplosionCarrier'}]
assert model['scenes'] == [{'name': 'export_s05_explosion_carrier', 'nodes': [0]}]
assert model['scene'] == 0 and len(model['meshes']) == 1
for key in ('images', 'textures', 'skins', 'animations', 'cameras',
            'extensionsUsed', 'extensionsRequired'):
    assert not model.get(key), key
assert model['buffers'] == [{'byteLength': len(data)}]
assert [m['name'] for m in model['materials']] == ['flash_amber', 'burst_coral', 'flash_ivory']
for mat in model['materials']:
    assert mat.get('alphaMode', 'OPAQUE') == 'OPAQUE'
    assert mat['pbrMetallicRoughness']['baseColorFactor'][3] == 1
    assert mat.get('emissiveFactor', [0, 0, 0]) == [0, 0, 0]
    assert not mat.get('extensions')


def accessor(index):
    """Decode complete tightly packed exporter attributes, with bounded byte ranges."""
    item = model['accessors'][index]
    view = model['bufferViews'][item['bufferView']]
    assert view['buffer'] == 0 and 'sparse' not in item
    width = {'VEC3': 3, 'SCALAR': 1}[item['type']]
    code = {5126: 'f', 5123: 'H'}[item['componentType']]
    length = struct.calcsize('<' + code * width)
    assert view.get('byteStride', length) == length
    start = view.get('byteOffset', 0) + item.get('byteOffset', 0)
    assert start + length * item['count'] <= len(data)
    assert length * item['count'] <= view['byteLength']
    values = [struct.unpack_from('<' + code * width, data, start + i * length)
              for i in range(item['count'])]
    assert all(math.isfinite(v) for row in values for v in row)
    if 'min' in item:
        assert list(item['min']) == [min(row[i] for row in values) for i in range(width)]
        assert list(item['max']) == [max(row[i] for row in values) for i in range(width)]
    return values


triangles = []
vertices = set()
primitive_counts = []
for primitive in model['meshes'][0]['primitives']:
    assert primitive.get('mode', 4) == 4
    assert set(primitive['attributes']) == {'POSITION', 'NORMAL'}
    positions = accessor(primitive['attributes']['POSITION'])
    normals = accessor(primitive['attributes']['NORMAL'])
    assert len(positions) == len(normals)
    assert all(abs(sum(v * v for v in n) - 1) <= .0001 for n in normals)
    indices = [v[0] for v in accessor(primitive['indices'])]
    assert len(indices) % 3 == 0 and max(indices) < len(positions)
    vertices.update(positions)
    for start in range(0, len(indices), 3):
        face = tuple(positions[i] for i in indices[start:start + 3])
        assert len(set(face)) == 3
        triangles.append(face)
    primitive_counts.append(dict(material=primitive['material'], vertices=len(positions),
                                 triangles=len(indices) // 3))
assert len(vertices) == 684 and len(triangles) == 1344
edges = Counter()
for face in triangles:
    for index in range(3):
        edges[tuple(sorted((face[index], face[(index + 1) % 3])))] += 1
assert set(edges.values()) == {2}, 'Export remains closed after welding material seams'
minimum = [min(v[i] for v in vertices) for i in range(3)]
maximum = [max(v[i] for v in vertices) for i in range(3)]
probe = json.loads((HERE / 'source-probe.json').read_text())
assert minimum == probe['min_godot'] and maximum == probe['max_godot']


def covered(point):
    """Test point coverage of exported triangles in the vertical XZ projection."""
    for face in triangles:
        signs = []
        for index in range(3):
            a, b = face[index], face[(index + 1) % 3]
            signs.append((b[0] - a[0]) * (point[1] - a[2]) -
                         (b[2] - a[2]) * (point[0] - a[0]))
        if max(signs) - min(signs) > 1e-8 and (min(signs) >= 0 or max(signs) <= 0):
            return True
    return False


# Literal independent probes in clear radial corridors and inside the flash/lobes.
clear = [(-.88, -1.21), (-1.43, .46), (0, 1.5), (1.43, .46), (.88, -1.21)]
solid = [(0, 0), (0, -1.22), (-1.16, -.38), (-.72, .99), (.72, .99), (1.16, -.38)]
assert not any(covered(point) for point in clear)
assert all(covered(point) for point in solid)
receipt = dict(export_sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
               min_godot=minimum, max_godot=maximum,
               size_m=[maximum[i] - minimum[i] for i in range(3)],
               welded_vertices=len(vertices), triangles=len(triangles),
               primitives=primitive_counts, clear_xz_probes=clear, solid_xz_probes=solid,
               double_sided=[m.get('doubleSided', False) for m in model['materials']],
               note='Static projected gaps only; no rendered camera/readability/cost evidence',
               checks='PASS')
(HERE / 'glb-check.json').write_text(json.dumps(receipt, indent=2) + '\n')
(HERE / 'glb-structure.json').write_text(json.dumps(model, indent=2) + '\n')
print(json.dumps(receipt, sort_keys=True))
