"""Owner-requested Latch front-door/rear-quarter split in its saved Blender source.

Authored with verified Astra/high, 9 October 2026. Run once on the first checkpoint.
The approved Latch concept keeps rear-quarter glazing and body fixed above the axle.
"""
import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / 'docs/assets/vehicle_car_evidence/car_latch_a_source.json'
SEAM_Y = -.62
GAP = .012


def retain_half(obj, plane_y, front):
    """Bisect a closed saved mesh and cap the new seam in its own local coordinates."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    inverse = obj.matrix_world.inverted()
    plane = inverse @ Vector((0, plane_y, 0))
    normal = obj.matrix_world.to_3x3().transposed() @ Vector((0, 1, 0))
    result = bmesh.ops.bisect_plane(
        bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
        dist=0.000001, plane_co=plane, plane_no=normal,
        clear_inner=front, clear_outer=not front)
    cut_edges = [e for e in result['geom_cut'] if isinstance(e, bmesh.types.BMEdge)
                 and e.is_boundary]
    bmesh.ops.holes_fill(bm, edges=cut_edges, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    assert len(obj.data.polygons) > 0, obj.name


def parent_in_place(obj, parent):
    """Preserve the assembled rest pose when changing only the rigid-part owner."""
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world


def source_bounds(obj):
    """Measure actual transformed vertices for the new front/rear seam evidence."""
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return {'min': [min(v[i] for v in points) for i in range(3)],
            'max': [max(v[i] for v in points) for i in range(3)]}


record = json.loads(RECORD.read_text())
source = (ROOT / record['source']).resolve()
assert source.parent == ROOT / 'art/source/models/vehicles/car_latch_a'
bpy.ops.wm.open_mainfile(filepath=str(source))
assert Path(bpy.data.filepath).resolve() == source
assert not bpy.context.scene.get('latch_short_door_revision', False)
col = bpy.data.collections[record['collection']]
root = bpy.data.objects['car_latch_a']
evidence = {}
for side, sign in [('Left', -1), ('Right', 1)]:
    for kind, fixed_name in [('Panel', 'QuarterPanel'), ('Window', 'QuarterGlass')]:
        moving = bpy.data.objects['Door' + kind + 'Front' + side]
        fixed = moving.copy()
        fixed.data = moving.data.copy()
        fixed.name = fixed_name + side
        col.objects.link(fixed)
        bpy.context.view_layer.update()
        parent_in_place(fixed, root)
        bpy.context.view_layer.update()
        retain_half(moving, SEAM_Y + GAP / 2, True)
        retain_half(fixed, SEAM_Y - GAP / 2, False)
        evidence[moving.name] = source_bounds(moving)
        evidence[fixed.name] = source_bounds(fixed)
        assert evidence[moving.name]['min'][1] >= SEAM_Y + GAP / 2 - .00001
        assert evidence[fixed.name]['max'][1] <= SEAM_Y - GAP / 2 + .00001
    pillar = bpy.data.objects['Pillar' + side]
    pillar.location = (sign * .72, SEAM_Y, 1.27)
    pillar.rotation_euler.y = -sign * math.atan(.10 / .445)
    pillar.data.materials.clear()
    pillar.data.materials.append(bpy.data.materials['trim'])
    bpy.ops.object.select_all(action='DESELECT')
    pillar.select_set(True)
    bpy.context.view_layer.objects.active = pillar
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    handle = bpy.data.objects['DoorHandleFront' + side]
    world = handle.matrix_world.copy()
    world.translation.y = SEAM_Y + .18
    handle.matrix_world = world

bpy.context.view_layer.update()
for name in evidence:
    obj = bpy.data.objects[name]
    bpy.context.view_layer.objects.active = obj
    # New caps must not interpolate shading across the cut seam.
    obj.data.set_sharp_from_angle(angle=math.radians(35))
    mod = obj.modifiers.new('split_panel_normals', 'WEIGHTED_NORMAL')
    mod.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.context.scene['latch_short_door_revision'] = 1
bpy.ops.wm.save_as_mainfile(filepath=str(source))
settings = json.loads((ROOT / 'tools/s01/export_settings.json').read_text())
settings.update(export_animations=False, export_skins=False, collection=col.name,
                filepath=str(ROOT / record['export']))
bpy.ops.export_scene.gltf(**settings)
record.update(members=sorted(o.name for o in col.all_objects),
              triangles=sum(len(o.data.polygons) for o in col.all_objects if o.type == 'MESH'),
              latch_short_door_revision=1,
              door_seam_blender_y_m=SEAM_Y,
              rear_quarter_nodes=['QuarterPanelLeft', 'QuarterPanelRight',
                                  'QuarterGlassLeft', 'QuarterGlassRight'],
              door_split_bounds_blender_m=evidence)
RECORD.write_text(json.dumps(record, indent=2) + '\n')
print('LATCH_SHORT_DOORS_SAVED', json.dumps(evidence), flush=True)
