"""Resolve saved static prefab composition without running scripts or importing assets."""

from dataclasses import dataclass, field
import json
from pathlib import Path
import re

import numpy as np

from .glb import Glb, Z_UP

HEADER = re.compile(r'^\[(\w+)(.*?)\]\s*$', re.M)
QUOTED = re.compile(r'(\w+)="([^"]*)"')
REFERENCE = re.compile(r'ExtResource\("([^"]+)"\)')


def sections(path):
    """Read section headers and raw properties; never evaluate scene text as code."""
    text = Path(path).read_text(encoding='utf-8')
    matches = list(HEADER.finditer(text))
    result = []
    for index, match in enumerate(matches):
        end = matches[index+1].start() if index+1 < len(matches) else len(text)
        properties = dict(re.findall(r'^([\w/]+)\s*=\s*(.*)$', text[match.end():end], re.M))
        result.append((match[1], dict(QUOTED.findall(match[2])), properties, match[2]))
    return result


@dataclass
class Node:
    """Expanded local node with inherited properties and optional exported mesh."""

    parent: str
    matrix: np.ndarray = field(default_factory=lambda: np.eye(4))
    glb: object = None
    mesh_node: dict = field(default_factory=dict)
    instance: str = ''
    materials: dict = field(default_factory=dict)
    hidden: bool = False
    collision: bool = False


class Prefabs:
    """Flatten PackedScene instances and overrides; unknown placement forms fail closed."""

    def __init__(self, root):
        self.root = Path(root).resolve()
        self.glbs = {}
        self.material_remaps = {}
        self.dependencies = set()

    def resource(self, path):
        """Resolve project-local resources only, retaining the complete dependency inventory."""
        if not path.startswith('res://'):
            raise ValueError(f'non-project resource: {path}')
        result = (self.root / path[6:]).resolve()
        if not result.is_relative_to(self.root):
            raise ValueError('resource escapes project')
        self.dependencies.add(result)
        return result

    def load_glb(self, path):
        """Cache decoded source bytes, not geometry transformed by another prefab."""
        if path not in self.glbs:
            self.glbs[path] = Glb(path)
            self.material_remaps[path] = {}
            sidecar = Path(str(path)+'.import')
            if sidecar.exists():
                self.dependencies.add(sidecar)
                text = sidecar.read_text(encoding='utf-8')
                values = dict(re.findall(r'^([\w/]+)=(.*)$', text, re.M))
                if float(values.get('nodes/root_scale', '1')) != 1:
                    raise ValueError(f'{path}: nonunit import root scale is unsupported')
                if values.get('import_script/path', '""') != '""':
                    raise ValueError(f'{path}: import script requires engine evaluation')
                subtext = text.split('_subresources=', 1)[1] if '_subresources=' in text else '{}'
                subresources, _ = json.JSONDecoder().raw_decode(subtext)
                for name, settings in subresources.get('materials', {}).items():
                    if settings.get('use_external/enabled'):
                        target = settings.get('use_external/fallback_path', settings.get('use_external/path'))
                        self.material_remaps[path][name] = self.resource(target)
        return self.glbs[path]

    def expand(self, path, ancestors=()):
        """Build an inherited tree before evaluating any parent/world transforms."""
        path = Path(path).resolve()
        self.dependencies.add(path)
        if path in ancestors:
            raise ValueError(f'cyclic PackedScene reference: {path}')
        if path.suffix == '.glb':
            glb = self.load_glb(path)
            nodes = {'': Node('')}
            for name, parent, matrix, source in glb.nodes():
                nodes[name] = Node(parent, matrix, glb, source)
            return nodes
        if path.suffix != '.tscn':
            raise ValueError(f'unsupported scene: {path}')
        blocks = sections(path)
        resources = {attrs['id']: self.resource(attrs['path'])
                     for kind, attrs, _, _ in blocks if kind == 'ext_resource'}
        nodes = {}
        for kind, attrs, props, raw in blocks:
            if kind != 'node':
                continue
            parent = attrs.get('parent', '')
            parent = '' if parent == '.' else parent
            name = f"{parent}/{attrs['name']}".strip('/') if 'parent' in attrs else ''
            instance = re.search(r'instance=(ExtResource\("[^"]+"\))', raw)
            if instance:
                child_path = resources[REFERENCE.fullmatch(instance[1])[1]]
                children = self.expand(child_path, ancestors+(path,))
                for child_name, node in children.items():
                    destination = '/'.join(p for p in (name, child_name) if p)
                    node.parent = '/'.join(p for p in (name, node.parent) if p) if child_name else parent
                    if child_path.suffix == '.glb':
                        node.instance = name or '<root>'
                    elif node.instance:
                        node.instance = '/'.join(p for p in (name, node.instance) if p)
                    nodes[destination] = node
            elif name not in nodes:
                if 'type' not in attrs and name:
                    raise ValueError(f'{path}: unresolved inherited node {name}')
                nodes[name] = Node(parent)
            node = nodes[name]
            if any(k in props for k in ('position', 'rotation', 'rotation_degrees', 'scale',
                                        'quaternion', 'top_level')):
                raise ValueError(f'{path}: unsupported transform representation on {name}')
            if 'transform' in props:
                match = re.fullmatch(r'Transform3D\(([^)]+)\)', props['transform'])
                if match is None:
                    raise ValueError(f'{path}: invalid Transform3D')
                values = [float(n) for n in match[1].split(',')]
                if len(values) != 12 or not np.isfinite(values).all():
                    raise ValueError('invalid Transform3D elements')
                node.matrix = np.eye(4)
                node.matrix[:3, :] = np.array(values).reshape(4, 3).T
            if 'visible' in props:
                node.hidden = props['visible'] == 'false'
            node.collision |= attrs.get('type', '') in ('CollisionShape3D', 'CollisionPolygon3D')
            for key, value in props.items():
                if key.startswith('surface_material_override/') or key == 'material_override':
                    slot = int(key.split('/')[-1]) if '/' in key else -1
                    if value == 'null':
                        node.materials.pop(slot, None)
                        continue
                    ref = REFERENCE.fullmatch(value)
                    if not ref:
                        raise ValueError(f'{path}: unsupported material override {value}')
                    node.materials[slot] = resources[ref[1]]
        return nodes

    def material(self, path):
        """Use saved StandardMaterial culling/alpha; shaders cannot certify occlusion."""
        blocks = sections(path)
        resource = next((props for kind, _, props, _ in blocks if kind == 'resource'), {})
        if 'shader' in resource:
            return str(path.relative_to(self.root)), True, False
        cull = int(resource.get('cull_mode', '0'))
        if cull == 1:
            raise ValueError(f'{path}: front-cull material needs explicit support')
        return (path.relative_to(self.root).as_posix(), cull == 2,
                int(resource.get('transparency', '0')) == 0)

    def parts(self, path):
        """Apply saved prefab transforms and material overrides to every render instance."""
        nodes = self.expand(path)
        matrices, hidden = {}, {}
        parts = []
        pending = dict(nodes)
        while pending:
            progressed = False
            for name, node in list(pending.items()):
                if name and node.parent not in matrices:
                    continue
                matrices[name] = (matrices[node.parent] if name else Z_UP) @ node.matrix
                hidden[name] = node.hidden or (hidden[node.parent] if name else False)
                if node.glb and not hidden[name] and not node.collision:
                    loaded = node.glb.primitives(node.mesh_node, name, matrices[name], node.instance)
                    for i, part in enumerate(loaded):
                        remap = self.material_remaps[node.glb.path].get(part.material)
                        override = node.materials.get(-1, node.materials.get(i, remap))
                        if override:
                            part.material, part.double_sided, part.opaque = self.material(override)
                    parts.extend(loaded)
                del pending[name]
                progressed = True
            if not progressed:
                raise ValueError(f'{path}: unresolved parent nodes {list(pending)}')
        return parts
