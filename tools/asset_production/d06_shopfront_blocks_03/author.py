"""Author the original chamfered corner shell; pinned Blender CLI, no live sessions."""
from pathlib import Path

import math

import bmesh
import bpy
import io_scene_gltf2
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d06_shopfront_blocks_03"
WIDTH, DEPTH, WALL_HEIGHT, DECK = 16.0, 12.8, 4.95, 4.3
# Clockwise structural boundary: front, clipped corner, east, rear, west.
FOOTPRINT = [(-8, 6.4), (3.2, 6.4), (8, 1.6), (8, -6.4), (-8, -6.4)]
assert bpy.app.version_string == "5.2.2 LTS"
assert io_scene_gltf2.bl_info["version"] == (5, 2, 40)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for collection in list(bpy.data.collections):
    bpy.data.collections.remove(collection)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new("export_" + ASSET)
scene.collection.children.link(collection)
root = bpy.data.objects.new(ASSET, None)
collection.objects.link(root)
root["provenance"] = "Original commissioned Blender construction; no external geometry"
root["datum"] = "Ground-centred 16 x 12.8 m structural bounding rectangle; Blender +Y front, +Z up"


def material(name, swatch, metallic, roughness):
    """Retain the accepted inline shell's opaque, linearized palette."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    rgb = [int(swatch[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    rgba = tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
                 for v in rgb) + (1,)
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = rgba
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    mat.diffuse_color = rgba
    return mat


wall = material("shell_muted_plum_render", "81777C", 0, .78)
roof = material("shell_quiet_blue_roof", "405B68", .12, .65)
trim = material("shell_warm_structural_trim", "BBB6A8", 0, .70)
plinth = material("shell_slate_plinth", "4A5358", 0, .78)
coping = material("shell_dark_drain_coping", "334950", .35, .48)
CUBE_FACES = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
              (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]


def corners(low, high):
    """Return consistently ordered corners for a closed rectangular component."""
    a, b, c = low
    d, e, f = high
    return [(a, b, c), (d, b, c), (d, e, c), (a, e, c),
            (a, b, f), (d, b, f), (d, e, f), (a, e, f)]


def mesh(name, vertices, faces, mat, bevel=0):
    """Build editable manifold geometry with applied broad highlight bevels."""
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.parent = root
    data.materials.append(mat)
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if bevel:
        mod = obj.modifiers.new("soft_architectural_edges", "BEVEL")
        mod.width, mod.segments = bevel, 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
        for polygon in data.polygons:
            polygon.use_smooth = True
        mod = obj.modifiers.new("broad_plane_normals", "WEIGHTED_NORMAL")
        mod.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.select_set(False)
    return obj


def box(name, low, high, mat, bevel=.012):
    """Author a closed shell component without unapplied object transforms."""
    return mesh(name, corners(low, high), CUBE_FACES, mat, bevel)


def offset_polygon(distance):
    """Miter the convex footprint by a signed outward distance, retaining each facade plane."""
    points = [Vector(p) for p in FOOTPRINT]
    result = []
    for i, point in enumerate(points):
        before = (point - points[i - 1]).normalized()
        after = (points[(i + 1) % len(points)] - point).normalized()
        n0, n1 = Vector((-before.y, before.x)), Vector((-after.y, after.x))
        bisector = n0 + n1
        result.append(point + bisector * (distance / bisector.dot(n1)))
    return result


def prism(name, polygon, bottom, top, mat, bevel=.012):
    """Extrude an authored planar boundary into a closed Blender mesh."""
    count = len(polygon)
    vertices = [(p[0], p[1], z) for z in (bottom, top) for p in polygon]
    faces = [tuple(range(count)), tuple(range(count, count * 2))]
    faces += [(i, (i + 1) % count, (i + 1) % count + count, i + count)
              for i in range(count)]
    return mesh(name, vertices, faces, mat, bevel)


outer = offset_polygon(0)
inner = offset_polygon(-.28)
for index in range(5):
    start, end = outer[index], outer[(index + 1) % 5]
    tangent = (end - start).normalized()
    normal = Vector((-tangent.y, tangent.x))
    length = (end - start).length
    centre = length / 2
    # Three differently oriented facades share the unchanged 6.4 m fitting interface.
    holes = ([(centre - 2.47, centre + .57, .54, 2.42),
              (centre + 1.24, centre + 2.66, 0, 2.45)] if index < 3 else [])
    xs = sorted({0, length} | {x for h in holes for x in h[:2]})
    zs = sorted({0, WALL_HEIGHT} | {z for h in holes for z in h[2:]})
    vertices, indices, faces = [], {}, {}
    for left, right in zip(xs, xs[1:]):
        for bottom, top in zip(zs, zs[1:]):
            x, z = (left + right) / 2, (bottom + top) / 2
            if any(l < x < r and b < z < t for l, r, b, t in holes):
                continue
            ids = []
            for u, depth, height in corners((left, 0, bottom), (right, .28, top)):
                point = start + tangent * u - normal * depth
                if depth and u == 0:
                    point = inner[index]
                elif depth and u == length:
                    point = inner[(index + 1) % 5]
                vertex = (point.x, point.y, height)
                if vertex not in indices:
                    indices[vertex] = len(vertices)
                    vertices.append(vertex)
                ids.append(indices[vertex])
            for face in CUBE_FACES:
                value = tuple(ids[i] for i in face)
                key = tuple(sorted(value))
                if key in faces:
                    del faces[key]
                else:
                    faces[key] = value
    mesh(f'facade_{index}_wall', vertices, list(faces.values()), wall)
    for label, outside, inside, bottom, top, mat in (
            ('coping', .08, -.36, 4.95, 5.05, coping),
            ('head_course', .035, -.02, 4.48, 4.61, trim)):
        a, b = offset_polygon(outside), offset_polygon(inside)
        prism(f'{label}_{index}', [a[index], a[(index + 1) % 5],
                                   b[(index + 1) % 5], b[index]], bottom, top, mat)
    # Plinth has true door cut-outs; simple runs avoid decor across the closed door leaf.
    intervals = [(0, centre + 1.10), (centre + 2.8, length)] if index < 3 else [(0, length)]
    for run, (left, right) in enumerate(intervals):
        a, b = start + tangent * left, start + tangent * right
        prism(f'plinth_{index}_{run}', [a + normal * .04, b + normal * .04,
                                      b - normal * .01, a - normal * .01], 0, .30,
              plinth, .008)
    if index >= 3:
        continue
    rotation = math.atan2(tangent.y, tangent.x)
    for kind, u, height in (('entrance_single', 1.95, 0), ('door_single', 1.95, 0),
                           ('display_window', -.95, .48), ('canopy', -.95, 3),
                           ('fascia', -.95, 3.8)):
        point = start + tangent * (centre + u)
        obj = bpy.data.objects.new(f'mount_{index}_{kind}', None)
        collection.objects.link(obj)
        obj.parent = root
        obj.location = (point.x, point.y, height)
        obj.rotation_euler.z = rotation
        obj.empty_display_size = .2
    # Broad warm jamb piers mark the change in frontage direction, not more sign clutter.
    for side, u in (('left', centre - 3.18), ('right', centre + 3.00)):
        a, b = start + tangent * u, start + tangent * (u + .18)
        prism(f'frontage_pier_{index}_{side}', [a + normal * .065, b + normal * .065,
                                              b - normal * .01, a - normal * .01],
              .30, 4.48, trim, .012)
prism('quiet_pentagonal_roof', offset_polygon(-.275), 4.14, DECK, roof)
# Two quiet rear seam bands make the deep roof scale legible without rooftop equipment.
for i, y in enumerate((-2.2, -4.3)):
    box(f'roof_seam_{i}', (-7.69, y - .018, DECK - .004),
        (7.69, y + .018, DECK + .022), roof, .005)
excluded = bpy.data.collections.new('authoring_excluded')
scene.collection.children.link(excluded)
reference = box('authoring_1m_reference', (-11, 0, 0), (-10, 1, 1), trim, 0)
collection.objects.unlink(reference)
excluded.objects.link(reference)
reference.parent = None
reference.hide_render = True
reference.hide_set(True)
root['structural_footprint_blender_xy_m'] = [v for p in FOOTPRINT for v in p]
scene['scope'] = 'Clipped-corner exterior; shared fitted closures; no interiors, paving or roof access'
scene['provisional_structural_envelope_m'] = [16, 12.8, 5.05]
bpy.context.preferences.filepaths.save_version = 0
source = ROOT / f'art/source/models/environment/{ASSET}/{ASSET}.blend'
source.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print('SOURCE_SAVED', source)
