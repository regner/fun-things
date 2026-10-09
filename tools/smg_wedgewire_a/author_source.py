"""Original Wedgewire source bootstrap, following Regner's approved C concept.

Run once in a fresh private Blender process. Subsequent edits belong in the saved
source; export.py reexports that source without rebuilding any geometry.
"""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = 'smg_wedgewire_a'
SOURCE = ROOT / 'art/source/models/weapons_smg' / (ASSET + '.blend')
assert bpy.app.version_string == '5.2.2 LTS'
assert not SOURCE.exists(), 'Do not overwrite an existing authored source'
assert (ROOT / 'art/source/.gdignore').exists()
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0


def material(name, srgb, roughness=0.65, metallic=0.0):
    """Assign stable opaque flat-color materials with explicit linear values."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    rgb = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in srgb]
    bsdf.inputs['Base Color'].default_value = (*rgb, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    m.diffuse_color = (*rgb, 1.0)
    return m


MATS = {
    'coral_shell': material('smg_wedgewire_coral_shell', (0.96, 0.36, 0.34)),
    'cyan_band': material('smg_wedgewire_cyan_band', (0.13, 0.85, 0.88)),
    'charcoal_body': material('smg_wedgewire_charcoal_body', (0.22, 0.25, 0.29)),
    'grip_rubber': material('smg_wedgewire_grip_rubber', (0.105, 0.135, 0.16), 0.85),
    'muzzle_metal': material('smg_wedgewire_muzzle_metal', (0.30, 0.34, 0.37), 0.45, 0.35),
    'pad_petrol': material('smg_wedgewire_review_petrol', (0.075, 0.13, 0.17), 0.9),
    'pad_concrete': material('smg_wedgewire_review_concrete', (0.30, 0.35, 0.36), 0.95),
}


def collection(name):
    """Separate explicit model, preview geometry and nonexported measurement scope."""
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c


MODEL = collection('export_' + ASSET)
PAD = collection('export_smg_wedgewire_review_pad')
REFERENCE = collection('source_measurement_reference')


def move(obj, group):
    """Keep each object in exactly its declared authoring collection."""
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    group.objects.link(obj)


def finish(obj, name, mat, group=MODEL, bevel=0.006):
    """Bake smooth broad bevels, explicit triangles and positive static transforms."""
    obj.name = name
    move(obj, group)
    obj.data.materials.append(MATS[mat])
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel:
        mod = obj.modifiers.new('AuthoredRoundedEdges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    for face in obj.data.polygons:
        face.use_smooth = True
    mod = obj.modifiers.new('AuthoredFaceNormals', 'WEIGHTED_NORMAL')
    mod.keep_sharp = True
    mod.weight = 50
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mod = obj.modifiers.new('ExplicitTriangles', 'TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.select_set(False)
    return obj


def box(name, size, pos, mat, bevel=0.006, angle=0.0, group=MODEL):
    """Create an authored beveled solid with front along Blender +Y."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    obj = bpy.context.object
    obj.dimensions = size
    obj.rotation_euler.x = angle
    return finish(obj, name, mat, group, bevel)


def prism(name, outline, bottom, top, mat, bevel=0.006):
    """Build the concept's planar wedge silhouette as a closed source mesh."""
    n = len(outline)
    verts = [(x, y, z) for z in (bottom, top) for x, y in outline]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    MODEL.objects.link(obj)
    return finish(obj, name, mat, bevel=bevel)


def ring(name, start, end, centre_z, outer, inner):
    """Author a short decorative muzzle ring, with no mechanical or firing behavior."""
    segments = 24
    verts = [(r * math.cos(i * math.tau / segments), y,
              centre_z + r * math.sin(i * math.tau / segments))
             for r, y in [(outer, start), (outer, end), (inner, start), (inner, end)]
             for i in range(segments)]
    faces = []
    for i in range(segments):
        j = (i + 1) % segments
        faces += [(i, i + segments, j + segments, j),
                  (i + 2 * segments, j + 2 * segments, j + 3 * segments, i + 3 * segments),
                  (i + segments, i + 3 * segments, j + 3 * segments, j + segments),
                  (i, j, j + 2 * segments, i + 2 * segments)]
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    MODEL.objects.link(obj)
    return finish(obj, name, 'muzzle_metal', bevel=0.001)


def marker(name, pos, normal=None):
    """Store measured contacts in the weapon frame; normals are separate metadata."""
    obj = bpy.data.objects.new(name, None)
    MODEL.objects.link(obj)
    obj.location = pos
    obj.empty_display_type = 'ARROWS'
    obj.empty_display_size = 0.045
    if normal:
        obj['contact_normal_blender'] = normal
    return obj


outline = [(-0.105, 0.025), (0.105, 0.025), (0.135, 0.175),
           (0.066, 0.435), (-0.066, 0.435), (-0.135, 0.175)]
prism('Wedgewire_CoralShell', outline, 0.105, 0.20, 'coral_shell', 0.008)
prism('Wedgewire_Underbody', [(x * 0.94, y) for x, y in outline],
      0.055, 0.125, 'charcoal_body', 0.005)
box('Wedgewire_RearBody', (0.095, 0.14, 0.105), (0, -0.012, 0.1275), 'charcoal_body')
box('Wedgewire_Stock', (0.066, 0.16, 0.067), (0, -0.157, 0.132), 'charcoal_body')
box('Wedgewire_ShoulderPad', (0.105, 0.045, 0.17), (0, -0.2575, 0.128),
    'grip_rubber', 0.01)
box('Wedgewire_MainGrip', (0.064, 0.07, 0.19), (0, 0, 0),
    'grip_rubber', 0.009, math.radians(-12))
box('Wedgewire_Magazine', (0.053, 0.063, 0.175), (0, 0.18, -0.033),
    'charcoal_body', 0.004)
box('Wedgewire_MagazineFoot', (0.068, 0.079, 0.02), (0, 0.18, -0.121),
    'grip_rubber', 0.004)
box('Wedgewire_TriggerGuardBottom', (0.025, 0.104, 0.018), (0, 0.081, -0.031),
    'charcoal_body', 0.004)
box('Wedgewire_TriggerGuardFront', (0.025, 0.018, 0.087), (0, 0.127, 0.0035),
    'charcoal_body', 0.004)
box('Wedgewire_TriggerAccent', (0.017, 0.018, 0.041), (0, 0.057, 0.011),
    'coral_shell', 0.004, math.radians(-16))
# Slight positive thickness avoids coplanar flicker while retaining the concept roof stripe.
prism('Wedgewire_CyanRoofBand', [(-0.113, 0.259), (0.094, 0.325),
      (0.080, 0.378), (-0.100, 0.311)], 0.199, 0.2015, 'cyan_band', 0.0005)
box('Wedgewire_CyanSideLeft', (0.002, 0.049, 0.06), (-0.112, 0.259, 0.158),
    'cyan_band', 0.0005)
box('Wedgewire_FrontCollar', (0.092, 0.034, 0.082), (0, 0.436, 0.14),
    'charcoal_body', 0.005)
ring('Wedgewire_Muzzle', 0.449, 0.52, 0.14, 0.026, 0.014)
# A dark end cap deep behind the rim is decoration, never a projectile origin.
box('Wedgewire_ApertureShadow', (0.027, 0.002, 0.027), (0, 0.45, 0.14),
    'grip_rubber', 0.0005)
marker('socket_grip', (0, 0, 0))
marker('socket_muzzle', (0, 0.52, 0.14))
marker('socket_grip_contact', (0.032, 0, 0), (1, 0, 0))
marker('socket_support_hand', (0, 0.31, 0.055), (0, 0, -1))
marker('socket_shoulder', (0, -0.28, 0.128), (0, -1, 0))

box('Review_PetrolPad', (65, 45, 0.10), (0, 0, -0.075), 'pad_petrol',
    bevel=0.0, group=PAD)
box('Review_ConcreteStrip', (65, 8, 0.018), (0, 8, -0.016), 'pad_concrete',
    bevel=0.0, group=PAD)
box('Reference_OneMetre', (1, 0.02, 0.02), (1, 0, 0), 'cyan_band',
    bevel=0.0, group=REFERENCE)
REFERENCE.hide_render = True
REFERENCE.hide_viewport = True
scene['asset_id'] = ASSET
scene['authorship'] = 'Original Codex SMG lead; Regner approved option C on 9 October 2026'
scene['axes'] = 'Blender +Y front, +Z up, +X right; glTF maps to Godot -Z,+Y,+X'
scene['grip_cross_section_m'] = [0.064, 0.070]
scene['animation_contract'] = 'Rigid static visual; player owns holding clips; no weapon clips required'
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
print('SMG_SOURCE', SOURCE)
