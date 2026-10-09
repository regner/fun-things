"""Astra-authored visual refinement of the saved approved Wedgewire source.

This is a one-time source edit, not a regeneration step. The saved .blend is the
source of truth; export.py remains the reproducible export path.
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'art/source/models/weapons_smg/smg_wedgewire_a.blend'
assert Path(bpy.data.filepath).resolve() == SOURCE
assert bpy.app.version_string == '5.2.2 LTS'
assert not bpy.context.scene.get('astra_visual_refinement_01', False)


def replace_mesh(name, vertices, faces, bevel=0.0):
    """Replace only the selected source geometry while preserving object/material identity."""
    obj = bpy.data.objects[name]
    old_mesh = obj.data
    mesh = bpy.data.meshes.new(name + '_refined_mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    for mat in old_mesh.materials:
        mesh.materials.append(mat)
    obj.data = mesh
    bpy.data.meshes.remove(old_mesh)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if bevel:
        mod = obj.modifiers.new('RoundedSourceEdges', 'BEVEL')
        mod.width = bevel
        mod.segments = 4
        bpy.ops.object.modifier_apply(modifier=mod.name)
    mod = obj.modifiers.new('ExplicitTriangles', 'TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.select_set(False)


def wedge(name, bottom, top, bevel):
    """Add the selected concept's rising front profile without changing contact surfaces."""
    outline = [(-0.105, 0.025), (0.105, 0.025), (0.135, 0.175),
               (0.066, 0.435), (-0.066, 0.435), (-0.135, 0.175)]
    if name == 'Wedgewire_Underbody':
        # A cross-section at the support contact preserves its flat measured surface.
        width = (0.135 - (0.31 - 0.175) * 0.069 / 0.26) * 0.94
        outline = [(-0.105 * 0.94, 0.025), (0.105 * 0.94, 0.025),
                   (0.135 * 0.94, 0.175), (width, 0.31), (0.066 * 0.94, 0.435),
                   (-0.066 * 0.94, 0.435), (-width, 0.31), (-0.135 * 0.94, 0.175)]
    n = len(outline)
    vertices = [(x, y, bottom(y)) for x, y in outline]
    vertices += [(x, y, top(y)) for x, y in outline]
    faces = [tuple(reversed(range(n))), tuple(range(n, n * 2))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    replace_mesh(name, vertices, faces, bevel)


# Keep the roof plane flat for the approved broad stripe, taper the lower front edge.
wedge('Wedgewire_CoralShell', lambda y: 0.105 + max(0, y - 0.175) * 0.025 / 0.26,
      lambda y: 0.20, 0.008)
wedge('Wedgewire_Underbody', lambda y: 0.055 + max(0, y - 0.31) * 0.035 / 0.125,
      lambda y: 0.125 + max(0, y - 0.31) * 0.01 / 0.125, 0.004)

# The source name is retained for import stability; this single mesh now holds both side bands.
vertices = []
faces = []
for side, rear, front in [(-1, 0.259, 0.311), (1, 0.325, 0.378)]:
    points = [(rear, 0.192), (rear + 0.025, 0.135),
              (front + 0.025, 0.135), (front, 0.192)]
    start = len(vertices)
    vertices += [(side * (0.135 - (y - 0.175) * 0.069 / 0.26 + 0.0005), y, z)
                 for y, z in points]
    order = (0, 1, 2, 3) if side == 1 else (3, 2, 1, 0)
    faces.append(tuple(start + i for i in order))
side_obj = bpy.data.objects['Wedgewire_CyanSideLeft']
side_obj.location = (0, 0, 0)
replace_mesh(side_obj.name, vertices, faces)


def set_source_normals(obj, flat=False):
    """Set explicit post-triangulation corner normals, avoiding stale modifier loop mappings."""
    mesh = obj.data
    mesh.update()
    adjacent = [[] for _ in mesh.vertices]
    for face in mesh.polygons:
        face.use_smooth = not flat
        for index in face.vertices:
            adjacent[index].append(face)
    normals = [None] * len(mesh.loops)
    threshold = math.cos(math.radians(35))
    for face in mesh.polygons:
        for loop in face.loop_indices:
            normal = face.normal.copy()
            if not flat:
                normal = Vector((0, 0, 0))
                for other in adjacent[mesh.loops[loop].vertex_index]:
                    if face.normal.dot(other.normal) >= threshold:
                        normal += other.normal * other.area
                normal.normalize()
            normals[loop] = tuple(normal)
    mesh.normals_split_custom_set(normals)
    mesh.update()


for obj in bpy.data.collections['export_smg_wedgewire_a'].all_objects:
    if obj.type == 'MESH':
        set_source_normals(obj)
for obj in bpy.data.collections['export_smg_wedgewire_review_pad'].all_objects:
    set_source_normals(obj, flat=True)
bpy.context.scene['astra_visual_refinement_01'] = True
bpy.context.scene['refinement_authorship'] = (
    'Codex gpt-6-astra/high, verified active runtime codex-turn-9 on 9 October 2026; '
    'side band wrap, tapered lower front and explicit post-triangulation corner normals')
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
print('SMG_ASTRA_REFINEMENT_SAVED', SOURCE)
