"""Read exported glTF triangles without an importer, welding or asset mutations."""

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import struct

import numpy as np

# glTF/Godot Y-up -> the brief's Blender Z-up, in metres.
Z_UP = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float)
DTYPES = {5120: 'i1', 5121: 'u1', 5122: '<i2', 5123: '<u2', 5125: '<u4', 5126: '<f4'}
WIDTHS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


@dataclass
class Part:
    """One instantiated exported primitive; indices retain exported face identity."""

    name: str
    vertices: np.ndarray
    indices: np.ndarray
    material: str
    double_sided: bool = False
    opaque: bool = True
    source: str = ''
    instance: str = ''
    attributes: dict = field(default_factory=dict)


def transform_points(points, matrix):
    """Apply one affine transform without changing index/vertex multiplicity."""
    return points @ matrix[:3, :3].T + matrix[:3, 3]


def node_matrix(node):
    """Decode column-major glTF matrix or TRS (including negative/nonuniform scale)."""
    if 'matrix' in node:
        return np.array(node['matrix'], float).reshape(4, 4).T
    x, y, z, w = node.get('rotation', [0, 0, 0, 1])
    result = np.eye(4)
    result[:3, :3] = np.array([
        [1-2*y*y-2*z*z, 2*x*y-2*z*w, 2*x*z+2*y*w],
        [2*x*y+2*z*w, 1-2*x*x-2*z*z, 2*y*z-2*x*w],
        [2*x*z-2*y*w, 2*y*z+2*x*w, 1-2*x*x-2*y*y],
    ]) @ np.diag(node.get('scale', [1, 1, 1]))
    result[:3, 3] = node.get('translation', [0, 0, 0])
    return result


class Glb:
    """Strict GLB 2 reader for the repository's uncompressed triangle exports."""

    def __init__(self, path):
        self.path = Path(path)
        raw = self.path.read_bytes()
        self.sha256 = hashlib.sha256(raw).hexdigest()
        if len(raw) < 20 or struct.unpack_from('<4sII', raw) != (b'glTF', 2, len(raw)):
            raise ValueError(f'{path}: invalid GLB 2 header')
        chunks = {}
        cursor = 12
        while cursor < len(raw):
            length, kind = struct.unpack_from('<I4s', raw, cursor)
            if cursor + 8 + length > len(raw) or kind in chunks:
                raise ValueError(f'{path}: invalid GLB chunks')
            chunks[kind] = raw[cursor+8:cursor+8+length]
            cursor += 8 + length
        self.doc = json.loads(chunks[b'JSON'])
        self.binary = chunks.get(b'BIN\0', b'')
        if self.doc.get('extensionsRequired'):
            raise ValueError(f'{path}: unsupported required extension')
        if any('uri' in b for b in self.doc.get('buffers', [])):
            raise ValueError(f'{path}: external buffers are unsupported')
        self.dynamic = bool(self.doc.get('animations') or self.doc.get('skins'))

    def accessor(self, index):
        """Read offsets, strides, normalized and sparse accessors with bounds checks."""
        a = self.doc['accessors'][index]
        dtype = np.dtype(DTYPES[a['componentType']])
        width = WIDTHS[a['type']]

        def view_data(view_index, offset, count, columns, item_type):
            view = self.doc['bufferViews'][view_index]
            if view.get('buffer', 0) != 0:
                raise ValueError('only the GLB binary buffer is supported')
            stride = view.get('byteStride', columns * item_type.itemsize)
            needed = offset + max(0, count-1)*stride + (columns*item_type.itemsize if count else 0)
            start = view.get('byteOffset', 0)
            if needed > view['byteLength'] or start + needed > len(self.binary):
                raise ValueError('accessor exceeds buffer view')
            return np.ndarray((count, columns), dtype=item_type, buffer=self.binary,
                              offset=start+offset, strides=(stride, item_type.itemsize)).copy()

        if 'bufferView' in a:
            values = view_data(a['bufferView'], a.get('byteOffset', 0), a['count'], width, dtype)
        else:
            values = np.zeros((a['count'], width), dtype=dtype)
        if 'sparse' in a:
            sparse = a['sparse']
            ids, vals = sparse['indices'], sparse['values']
            indices = view_data(ids['bufferView'], ids.get('byteOffset', 0), sparse['count'],
                                1, np.dtype(DTYPES[ids['componentType']])).ravel()
            if np.any(indices >= a['count']):
                raise ValueError('sparse index out of bounds')
            values[indices] = view_data(vals['bufferView'], vals.get('byteOffset', 0),
                                       sparse['count'], width, dtype)
        if a.get('normalized') and dtype.kind in 'iu':
            values = np.maximum(values.astype(float) / np.iinfo(dtype).max, -1)
        if not np.all(np.isfinite(values)):
            raise ValueError('nonfinite accessor')
        return values

    def nodes(self):
        """Return active-scene nodes in parent-first order, not orphaned mesh data."""
        nodes = self.doc.get('nodes', [])
        scenes = self.doc.get('scenes', [])
        roots = scenes[self.doc.get('scene', 0)]['nodes'] if scenes else [
            i for i in range(len(nodes)) if not any(i in n.get('children', []) for n in nodes)]
        output = []

        def visit(index, parent, ancestors):
            if index in ancestors:
                raise ValueError('cyclic glTF node hierarchy')
            node = nodes[index]
            name = node.get('name', f'node_{index}')
            path = f'{parent}/{name}' if parent else name
            output.append((path, parent, node_matrix(node), node))
            for child in node.get('children', []):
                visit(child, path, ancestors | {index})

        for root in roots:
            visit(root, '', set())
        return output

    def primitives(self, node, name, matrix, instance=''):
        """Load render primitives only; reject unhandled modes instead of silently skipping."""
        if 'mesh' not in node:
            return []
        if any(segment.lower().endswith(('-colonly', '-convcolonly')) for segment in name.split('/')):
            return []
        mesh = self.doc['meshes'][node['mesh']]
        parts = []
        for number, primitive in enumerate(mesh['primitives']):
            if primitive.get('mode', 4) != 4:
                raise ValueError(f'{self.path}: non-triangle primitive')
            attrs = {k: self.accessor(v) for k, v in primitive['attributes'].items()}
            vertices = transform_points(attrs['POSITION'].astype(float), matrix)
            indices = (self.accessor(primitive['indices']).ravel() if 'indices' in primitive
                       else np.arange(len(vertices)))
            if len(indices) % 3 or np.any(indices < 0) or np.any(indices >= len(vertices)):
                raise ValueError('invalid triangle indices')
            indices = indices.astype(int).reshape(-1, 3)
            # Reflections reverse winding; preserve the source's outward-facing orientation.
            if np.linalg.det(matrix[:3, :3]) < 0:
                indices = indices[:, [0, 2, 1]]
            mat = self.doc.get('materials', [])[primitive['material']] if 'material' in primitive else {}
            parts.append(Part(f'{name}/primitive_{number}', vertices, indices,
                              mat.get('name', '<default>'), mat.get('doubleSided', False),
                              mat.get('alphaMode', 'OPAQUE') == 'OPAQUE',
                              self.path.as_posix(), instance, attrs))
        return parts

    def parts(self):
        """Return Z-up geometry with each active node's full transform applied once."""
        matrices = {'': Z_UP}
        parts = []
        for path, parent, local, node in self.nodes():
            matrices[path] = matrices[parent] @ local
            parts.extend(self.primitives(node, path, matrices[path]))
        return parts
