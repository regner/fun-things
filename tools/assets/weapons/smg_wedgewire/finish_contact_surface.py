"""Astra source correction: keep the support contact on a deliberate planar underside.

The earlier tapered n-gon triangulated through the contact patch. Explicit loft
sections preserve a flat support surface and a separate rising front section.
"""
import ast
from pathlib import Path

import bpy
from mathutils import Vector
import math

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'art/source/models/weapons/smg_wedgewire/smg_wedgewire_a.blend'
assert Path(bpy.data.filepath).resolve() == SOURCE
assert bpy.context.scene.get('astra_visual_refinement_01', False)
assert not bpy.context.scene.get('support_surface_finished', False)
# Reuse only the already-authored mesh/normal helpers, never rerun the source edit.
tree = ast.parse(Path(__file__).with_name('refine_source.py').read_text())
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in ['replace_mesh', 'set_source_normals']:
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<source helpers>', 'exec'))

vertices = []
for y, bottom, top in [(0.025, 0.055, 0.125), (0.175, 0.055, 0.125),
                       (0.335, 0.055, 0.125), (0.435, 0.09, 0.135)]:
    width = (0.105 + (y - 0.025) * 0.03 / 0.15) if y <= 0.175 else (
        0.135 - (y - 0.175) * 0.069 / 0.26)
    width *= 0.94
    vertices += [(-width, y, bottom), (width, y, bottom),
                 (width, y, top), (-width, y, top)]
faces = [(0, 1, 2, 3), (15, 14, 13, 12)]
for section in range(3):
    for edge in range(4):
        i = section * 4 + edge
        j = section * 4 + (edge + 1) % 4
        faces.append((i, i + 4, j + 4, j))
replace_mesh('Wedgewire_Underbody', vertices, faces, 0.004)
set_source_normals(bpy.data.objects['Wedgewire_Underbody'])
bpy.context.scene['support_surface_finished'] = True
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
print('SMG_SUPPORT_SURFACE_SAVED', SOURCE)
