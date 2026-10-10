"""Small serialized GLBs exercise every finding and its non-finding control."""

import json
from pathlib import Path
import struct
import tempfile
import unittest

import numpy as np

from .audit import analyze, gate_failures, policy_reason
from .geometry import closed_islands, fully_covered, points_inside
from .glb import Glb, Z_UP
from .prefab import Prefabs
from .run import main

TRIANGLE = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]])


def write_glb(path, parts, *, nodes=None, animations=False):
    """Serialize tiny in-memory geometry to real GLB buffers, not mocked loader results."""
    data = bytearray()
    doc = {'asset': {'version': '2.0'}, 'buffers': [], 'bufferViews': [], 'accessors': [],
           'meshes': [], 'materials': [], 'nodes': [], 'scenes': [{'nodes': []}], 'scene': 0}

    def accessor(values, kind, component):
        values = np.asarray(values, dtype='<f4' if component == 5126 else '<u4')
        while len(data) % 4:
            data.append(0)
        view = len(doc['bufferViews'])
        doc['bufferViews'].append({'buffer': 0, 'byteOffset': len(data), 'byteLength': values.nbytes})
        data.extend(values.tobytes())
        index = len(doc['accessors'])
        doc['accessors'].append({'bufferView': view, 'componentType': component,
                                 'count': len(values), 'type': kind})
        return index

    for i, part in enumerate(parts):
        vertices = np.asarray(part['vertices']) @ Z_UP[:3, :3]
        attrs = {'POSITION': accessor(vertices, 'VEC3', 5126)}
        if 'uv' in part:
            attrs['TEXCOORD_0'] = accessor(part['uv'], 'VEC2', 5126)
        primitive = {'attributes': attrs, 'indices': accessor(np.array(part['indices']).ravel(),
                                                             'SCALAR', 5125), 'material': i}
        doc['materials'].append({'name': part.get('material', f'material_{i}'),
                                  'doubleSided': part.get('double', False),
                                  'alphaMode': part.get('alpha', 'OPAQUE')})
        doc['meshes'].append({'primitives': [primitive]})
        doc['nodes'].append({'name': f'part_{i}', 'mesh': i})
        doc['scenes'][0]['nodes'].append(i)
    if nodes is not None:
        doc['nodes'] = nodes
        doc['scenes'][0]['nodes'] = [0]
    if animations:
        doc['animations'] = [{'name': 'rest_fixture'}]
    doc['buffers'] = [{'byteLength': len(data)}]
    write_document(path, doc, data)
    return path


def write_document(path, doc, binary):
    """Write correct chunk alignment so accessor and header validation are exercised."""
    encoded = json.dumps(doc).encode()
    encoded += b' ' * (-len(encoded) % 4)
    binary = bytes(binary) + b'\0' * (-len(binary) % 4)
    payload = struct.pack('<I4s', len(encoded), b'JSON') + encoded
    payload += struct.pack('<I4s', len(binary), b'BIN\0') + binary
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(struct.pack('<4sII', b'glTF', 2, len(payload)+12) + payload)


def triangle(vertices=TRIANGLE, **kwargs):
    """Provide one source-named triangle primitive for positive/negative controls."""
    return {'vertices': vertices, 'indices': [[0, 1, 2]], **kwargs}


def cube(size=2):
    """Use independently specified outward box faces around the origin."""
    vertices = np.array([[-1,-1,-1], [1,-1,-1], [1,1,-1], [-1,1,-1],
                         [-1,-1,1], [1,-1,1], [1,1,1], [-1,1,1]], float)*size/2
    faces = [[0,2,1], [0,3,2], [4,5,6], [4,6,7], [0,1,5], [0,5,4],
             [1,2,6], [1,6,5], [2,3,7], [2,7,6], [3,0,4], [3,4,7]]
    return {'vertices': vertices, 'indices': faces}


class MeshAuditTests(unittest.TestCase):
    """Run production APIs against scratch GLB/scene bytes and independent expectations."""

    def setUp(self):
        """Keep fixtures and audit output outside the repository."""
        self.temp = tempfile.TemporaryDirectory(prefix='mesh-audit-tests-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root/'art/models/fixture.glb'

    def audit(self, parts, **kwargs):
        """Exercise the actual exported-file read and analysis pipeline."""
        write_glb(self.path, parts)
        return analyze(Glb(self.path).parts(), **kwargs)

    def test_downward_datum_elevated_and_upward_negative(self):
        """Datum is asset zero, not the lowest point or glTF's Z coordinate."""
        result = self.audit([triangle(TRIANGLE[[0,2,1]]),
                             triangle(TRIANGLE[[0,2,1]]+[0,0,.03]),
                             triangle(TRIANGLE+[2,0,0])])['summary']
        self.assertEqual((result['bottoms'], result['elevated_undersides']), (1, 1))
        self.assertEqual(result['removable_candidates'], 2)

    def test_double_sided_downward_is_visible_not_removable(self):
        """A back-wound double-sided artwork carrier is not an invisible bottom."""
        result = self.audit([triangle(TRIANGLE[[0,2,1]], double=True)])['summary']
        self.assertEqual(result['unseen_sampled'], 0)
        self.assertEqual(result['removable_candidates'], 0)

    def test_exception_and_dynamic_keep(self):
        """Keep rules exclude underside savings without hiding measured findings."""
        for kwargs in ({'keep_reason': 'keep, exception: water'}, {'dynamic': True}):
            result = self.audit([triangle(TRIANGLE[[0,2,1]])], **kwargs)['summary']
            self.assertEqual(result['bottoms'], 1)
            self.assertEqual(result['removable_candidates'], 0)
        policy = {'keep_undersides': [{'glob': 'art/models/water/*', 'reason': 'water'}]}
        self.assertEqual(policy_reason('art/models/water/deck.glb', policy), 'water')
        self.assertEqual(policy_reason('art/models/building.glb', policy), '')

    def test_water_exception_keeps_sloping_undersides_outside_downward_threshold(self):
        """An underside with Z normal -0.85 can reflect even though check 1 selects <-0.9."""
        slope = np.array([[0,0,0], [0,1,0], [.85,0,.5267827]])
        bare = self.audit([triangle(slope)])['summary']
        kept = self.audit([triangle(slope)], keep_reason='keep, exception: water')['summary']
        self.assertEqual(bare['elevated_undersides'], 0)
        self.assertEqual(bare['removable_candidates'], 1)
        self.assertEqual(kept['keep_exception'], 1)
        self.assertEqual(kept['removable_candidates'], 0)

    def test_coplanar_same_facing_and_threshold_negatives(self):
        """Agreement requires plane, area, angle and projected intersection, not AABB alone."""
        for offset, expected in (([0,0,0], 1), ([0,0,.0009], 1), ([0,0,.0011], 0),
                                 ([2,0,0], 0), ([.999,0,0], 0)):
            result = self.audit([triangle(), triangle(TRIANGLE+offset)])
            self.assertEqual(result['summary']['z_fighting_pairs'], expected)
        rotated = TRIANGLE.copy()
        rotated[2, 2] = .01
        self.assertEqual(self.audit([triangle(), triangle(rotated)])['summary']['z_fighting_pairs'], 0)

    def test_adjacent_triangles_and_aabb_overlap_are_not_z_fights(self):
        """Touching edges and disjoint triangles with overlapping bounds have zero area."""
        other = np.array([[1,0,0], [1,1,0], [0,1,0]], float)
        self.assertEqual(self.audit([triangle(), triangle(other)])['summary']['z_fighting_pairs'], 0)
        self.assertEqual(self.audit([triangle(), triangle(other+[.1,.1,0])])['summary']['z_fighting_pairs'], 0)

    def test_angle_tolerance_independent_of_plane_and_area(self):
        """A relaxed plane tolerance does not bypass the normal-angle contract."""
        tilted = TRIANGLE.copy()
        tilted[2, 2] = .01
        result = self.audit([triangle(), triangle(tilted)], plane=.02)
        self.assertEqual(result['summary']['z_fighting_pairs'], 0)
        result = self.audit([triangle(), triangle(tilted)], plane=.02, angle=1)
        self.assertEqual(result['summary']['z_fighting_pairs'], 1)

    def test_opposite_double_sided_positive_single_sided_negative(self):
        """Only double-sided opposite coplanar triangles meet the z-fighting contract."""
        for double, count in ((False, 0), (True, 1)):
            result = self.audit([triangle(), triangle(TRIANGLE[[0,2,1]], double=double)])
            self.assertEqual(result['summary']['z_fighting_pairs'], count)

    def test_sealed_full_contact_partial_and_thin_shell_negatives(self):
        """Full opposing flush cover is sealed; a partial contact or thin solid is not."""
        left, right = cube(), cube()
        left['vertices'] = left['vertices'] + [-1,0,0]
        right['vertices'] = right['vertices'] + [1,0,0]
        self.assertEqual(self.audit([left, right])['summary']['sealed'], 4)
        vertical = TRIANGLE[:, [2,0,1]]
        self.assertEqual(self.audit([triangle(vertical), triangle(vertical[[0,2,1]])])['summary']['sealed'], 0)
        self.assertEqual(self.audit([triangle(), triangle(TRIANGLE[[0,2,1]]+[.2,0,0])])['summary']['sealed'], 0)
        self.assertEqual(self.audit([triangle(), triangle(TRIANGLE[[0,2,1]]-[0,0,.0008])])['summary']['sealed'], 0)
        tilted = TRIANGLE[[0,2,1]].copy()
        tilted[1, 2] = .0005
        self.assertEqual(self.audit([triangle(), triangle(tilted)])['summary']['sealed'], 0)

    def test_contact_union_covers_without_duplicate_area_inflation(self):
        """Two half covers seal a face; two copies of one half cannot seal the remainder."""
        left = np.array([[0,0,0], [0,1,0], [.5,0,0]], float)
        right = np.array([[.5,0,0], [0,1,0], [1,0,0]], float)
        result = self.audit([triangle(TRIANGLE[[0,2,1]]), triangle(left[[0,2,1]]),
                             triangle(right[[0,2,1]])])
        self.assertEqual(result['groups'][0]['faces']['sealed'], [0])
        result = self.audit([triangle(TRIANGLE[[0,2,1]]), triangle(left[[0,2,1]]),
                             triangle(left[[0,2,1]])])
        self.assertEqual(result['groups'][0]['faces']['sealed'], [])

    def test_dense_flush_contacts_discard_zero_area_fragments(self):
        """Repeated coplanar boundaries remain bounded and do not inflate covered area."""
        left = np.array([[0,0,0], [0,1,0], [.5,0,0]], float)
        self.assertFalse(fully_covered(TRIANGLE, np.tile(left, (128,1,1)), np.array([0,0,1])))
        self.assertTrue(fully_covered(TRIANGLE, np.tile(TRIANGLE, (128,1,1)), np.array([0,0,1])))

    def test_interior_closed_island_positive_and_exposed_negative(self):
        """An internal triangle is occluded/contained; the same triangle outside is visible."""
        inner = TRIANGLE*.2
        result = self.audit([cube(), triangle(inner)])
        self.assertEqual(result['groups'][1]['faces']['inside_closed_island'], [0])
        self.assertEqual(result['groups'][1]['faces']['unseen_sampled'], [0])
        outside = self.audit([cube(), triangle(inner+[0,0,2])])
        self.assertEqual(outside['groups'][1]['faces']['inside_closed_island'], [])
        self.assertEqual(outside['groups'][1]['faces']['unseen_sampled'], [])

    def test_open_island_and_transparent_shell_do_not_certify_interior(self):
        """Missing roof and alpha geometry cannot hide an upward inner face."""
        box = cube()
        box['indices'] = box['indices'][:2]+box['indices'][4:]
        result = self.audit([box, triangle(TRIANGLE*.2)])
        self.assertEqual(result['summary']['inside_closed_island'], 0)
        self.assertEqual(result['groups'][1]['faces']['unseen_sampled'], [])
        box = cube()
        box['alpha'] = 'BLEND'
        result = self.audit([box, triangle(TRIANGLE*.2)])
        self.assertEqual(result['summary']['inside_closed_island'], 0)
        self.assertEqual(result['groups'][1]['faces']['unseen_sampled'], [])

    def test_inside_out_shell_is_not_an_opaque_container(self):
        """Closed topology with inward normals does not hide contents behind culled faces."""
        box = cube()
        box['indices'] = np.array(box['indices'])[:, [0,2,1]]
        result = self.audit([box, triangle(TRIANGLE*.2)])
        self.assertEqual(result['summary']['inside_closed_island'], 0)
        self.assertEqual(result['groups'][1]['faces']['unseen_sampled'], [])

    def test_closed_mesh_parity_deduplicates_shared_edge_hits(self):
        """Known inside/outside points and the twelve-face closed island are independent oracles."""
        box = cube()
        triangles = box['vertices'][box['indices']]
        self.assertEqual(len(closed_islands(triangles)), 1)
        np.testing.assert_array_equal(points_inside(np.array([[0,0,0], [3,0,0]]), triangles), [True, False])

    def test_occlusion_samples_more_than_centroid(self):
        """A small roof over only a face center cannot make the whole triangle unseen."""
        result = self.audit([triangle(), triangle(TRIANGLE*.3+[.25,.25,.001])])
        self.assertEqual(result['groups'][0]['faces']['unseen_sampled'], [])

    def test_duplicate_loose_zero_area_and_uv_seam_negative(self):
        """Exact duplicates are split from legitimate attribute seams, per material."""
        bad = {'vertices': np.vstack([TRIANGLE, TRIANGLE[0], [2,2,2]]),
               'indices': [[0,1,2], [0,3,0]], 'material': 'bad'}
        result = self.audit([bad, triangle(TRIANGLE+[4,0,0], material='clean')])
        group = result['groups'][0]
        self.assertEqual((group['duplicate_vertices'], group['loose_vertices']), (1,1))
        self.assertEqual(group['faces']['zero_area'], [1])
        self.assertEqual(result['groups'][1]['faces']['zero_area'], [])
        seam = {'vertices': np.vstack([TRIANGLE, TRIANGLE[0]]), 'indices': [[0,1,2], [3,1,2]],
                'uv': [[0,0], [1,0], [0,1], [1,1]]}
        self.assertEqual(self.audit([seam])['summary']['duplicate_vertices'], 0)

    def test_glb_hierarchy_mirror_nonuniform_scale_and_unindexed(self):
        """Node matrices convert axes once and preserve outward winding under reflection."""
        nodes = [{'name': 'root', 'translation': [2,3,4], 'children': [1]},
                 {'name': 'child', 'mesh': 0, 'scale': [-2,1,3]}]
        write_glb(self.path, [triangle()], nodes=nodes)
        glb = Glb(self.path)
        part = glb.parts()[0]
        np.testing.assert_allclose(part.vertices[0], [2,-4,3])
        self.assertEqual(analyze([part])['summary']['bottoms'], 0)
        doc = glb.doc
        del doc['meshes'][0]['primitives'][0]['indices']
        write_document(self.path, doc, glb.binary)
        self.assertEqual(len(Glb(self.path).parts()[0].indices), 1)

    def test_strided_accessor_and_sparse_positions(self):
        """Byte offsets/strides and sparse overlays are not silently misread as packed arrays."""
        write_glb(self.path, [triangle()])
        glb = Glb(self.path)
        doc, binary = glb.doc, bytearray(glb.binary)
        start = len(binary)
        binary += np.array([[99,0,0,0], [99,1,0,0], [99,0,0,-1]], dtype='<f4').tobytes()
        doc['bufferViews'].append({'buffer': 0, 'byteOffset': start, 'byteLength': 48, 'byteStride': 16})
        doc['accessors'][0].update(bufferView=len(doc['bufferViews'])-1, byteOffset=4)
        doc['buffers'][0]['byteLength'] = len(binary)
        write_document(self.path, doc, binary)
        np.testing.assert_allclose(Glb(self.path).parts()[0].vertices, TRIANGLE)
        glb = Glb(self.path)
        doc, binary = glb.doc, bytearray(glb.binary)
        start = len(binary)
        binary += struct.pack('<Ifff', 1, 2, 0, 0)
        doc['bufferViews'] += [{'buffer': 0, 'byteOffset': start, 'byteLength': 4},
                               {'buffer': 0, 'byteOffset': start+4, 'byteLength': 12}]
        doc['accessors'][0]['sparse'] = {'count': 1,
            'indices': {'bufferView': len(doc['bufferViews'])-2, 'componentType': 5125},
            'values': {'bufferView': len(doc['bufferViews'])-1}}
        write_document(self.path, doc, binary)
        self.assertEqual(Glb(self.path).parts()[0].vertices[1,0], 2)

    def test_collision_only_node_and_children_are_excluded(self):
        """Collision-only exports cannot inflate render geometry counts."""
        nodes = [{'name': 'shape-colonly', 'mesh': 0, 'children': [1]},
                 {'name': 'child', 'mesh': 0}]
        write_glb(self.path, [triangle()], nodes=nodes)
        self.assertEqual(Glb(self.path).parts(), [])
        nodes[0]['name'] = 'visible-col'
        write_glb(self.path, [triangle()], nodes=nodes)
        self.assertEqual(len(Glb(self.path).parts()), 2)

    def test_invalid_glb_fails_closed(self):
        """Unknown primitive mode, malformed index and truncated GLB are explicit failures."""
        for mode in ('mode', 'index', 'truncated'):
            write_glb(self.path, [triangle()])
            glb = Glb(self.path)
            if mode == 'mode':
                glb.doc['meshes'][0]['primitives'][0]['mode'] = 1
                write_document(self.path, glb.doc, glb.binary)
            elif mode == 'index':
                binary = bytearray(glb.binary)
                struct.pack_into('<I', binary, 36, 100)
                write_document(self.path, glb.doc, binary)
            else:
                self.path.write_bytes(self.path.read_bytes()[:-1])
            with self.assertRaises(ValueError):
                Glb(self.path).parts()

    def write_scene(self, name, text):
        """Create scratch-only static scene text to test read-only resolution, not authored art."""
        path = self.root/'scenes/prefabs'/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def test_prefab_repeated_glb_transform_positive_negative(self):
        """Repeated same-GLB instances are checked; parent translation separates the control."""
        write_glb(self.path, [triangle()])
        scene = '''[gd_scene format=3]
[ext_resource type="PackedScene" path="res://art/models/fixture.glb" id="glb"]
[node name="Root" type="Node3D"]
[node name="A" parent="." instance=ExtResource("glb")]
[node name="Group" type="Node3D" parent="."]
TRANSFORM
[node name="B" parent="Group" instance=ExtResource("glb")]
'''
        for transform, count in (('', 1), ('transform = Transform3D(1,0,0,0,1,0,0,0,1,2,0,0)', 0)):
            path = self.write_scene('assembly.tscn', scene.replace('TRANSFORM', transform))
            parts = Prefabs(self.root).parts(path)
            self.assertEqual(analyze(parts, cross_instance=True)['summary']['z_fighting_pairs'], count)

    def test_nested_prefab_inherited_transform_and_material_override(self):
        """Inheritance overrides the target node, including double-sided material culling."""
        write_glb(self.path, [triangle(), triangle(TRIANGLE[[0,2,1]])])
        self.write_scene('base.tscn', '''[gd_scene format=3]
[ext_resource type="PackedScene" path="res://art/models/fixture.glb" id="glb"]
[node name="Base" type="Node3D"]
[node name="Model" parent="." instance=ExtResource("glb")]
''')
        material = self.root/'material.tres'
        material.write_text('[gd_resource type="StandardMaterial3D" format=3]\n[resource]\ncull_mode = 2\n')
        path = self.write_scene('inherited.tscn', '''[gd_scene format=3]
[ext_resource type="PackedScene" path="res://scenes/prefabs/base.tscn" id="base"]
[ext_resource type="Material" path="res://material.tres" id="mat"]
[node name="Inherited" instance=ExtResource("base")]
transform = Transform3D(0,0,-1,0,2,0,3,0,0,5,0,0)
[node name="part_1" parent="Model"]
surface_material_override/0 = ExtResource("mat")
''')
        parts = Prefabs(self.root).parts(path)
        self.assertTrue(parts[1].double_sided)
        self.assertEqual(analyze(parts)['summary']['z_fighting_pairs'], 1)
        np.testing.assert_allclose(parts[0].vertices[0], [5,0,0])

    def test_prefab_import_material_remap_and_hidden_inheritance(self):
        """Import remaps affect culling; an override without visible=true stays hidden."""
        write_glb(self.path, [triangle()])
        material = self.root/'material.tres'
        material.write_text('[gd_resource type="StandardMaterial3D" format=3]\n[resource]\ncull_mode = 2\n')
        remaps = {'materials': {'material_0': {'use_external/enabled': True,
                                              'use_external/fallback_path': 'res://material.tres'}}}
        Path(str(self.path)+'.import').write_text('_subresources='+json.dumps(remaps)+'\n')
        base = self.write_scene('base.tscn', '''[gd_scene format=3]
[ext_resource type="PackedScene" path="res://art/models/fixture.glb" id="glb"]
[node name="Root" type="Node3D"]
[node name="Model" parent="." instance=ExtResource("glb")]
''')
        self.assertTrue(Prefabs(self.root).parts(base)[0].double_sided)
        base.write_text(base.read_text()+'visible = false\n')
        derived = self.write_scene('derived.tscn', '''[gd_scene format=3]
[ext_resource type="PackedScene" path="res://scenes/prefabs/base.tscn" id="base"]
[node name="Root" instance=ExtResource("base")]
[node name="Model" parent="."]
transform = Transform3D(1,0,0,0,1,0,0,0,1,2,0,0)
''')
        self.assertEqual(Prefabs(self.root).parts(derived), [])

    def test_prefab_unsupported_transform_fails_instead_of_identity_fallback(self):
        """Future unimplemented serialization cannot silently pass as an identity transform."""
        path = self.write_scene('unsupported.tscn', '[gd_scene format=3]\n[node name="Root" type="Node3D"]\nscale = Vector3(2,2,2)\n')
        with self.assertRaises(ValueError):
            Prefabs(self.root).parts(path)

    def test_gate_positive_negative_and_read_only_cli(self):
        """Audit completion and a clean gate are separate statuses; input bytes never change."""
        write_glb(self.path, [triangle(), triangle()])
        before = self.path.read_bytes()
        code = main(['--root', str(self.root), '--output', str(self.root/'../mesh-audit-gate-output'/self.root.name),
                     '--no-prefabs', '--jobs', '1', '--fail-on', 'z_fighting_pairs'])
        output = self.root/'../mesh-audit-gate-output'/self.root.name
        self.addCleanup(__import__('shutil').rmtree, output)
        self.assertEqual(code, 1)
        report = json.loads((output/'audit.json').read_text())
        self.assertTrue(report['complete'])
        self.assertFalse(report['gate_passed'])
        self.assertEqual(gate_failures(report, ['zero_area']), [])
        self.assertEqual(self.path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
