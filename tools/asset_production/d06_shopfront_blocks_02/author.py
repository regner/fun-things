"""Author the original stepped rear-court shell; pinned Blender CLI, no live sessions."""
from pathlib import Path

import bmesh
import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d06_shopfront_blocks_02"
WIDTH, DEPTH = 19.2, 18.0
FRONT, DECK = DEPTH / 2, 4.3
BAYS = (-6.4, 0, 6.4)
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
root["datum"] = "Ground-centred 19.2 x 18 m structural envelope; Blender +Y front, +Z up"


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


# Six real front apertures retain the existing shared fitting installation contract.
holes = []
for bay in BAYS:
    holes.extend([(bay - 2.47, bay + .57, .54, 2.42),
                  (bay + 1.24, bay + 2.66, 0, 2.45)])
xs = sorted({-WIDTH / 2, WIDTH / 2} | {x for h in holes for x in h[:2]})
zs = sorted({0, 4.95} | {z for h in holes for z in h[2:]})
vertices, indices, faces = [], {}, {}
for a, b in zip(xs, xs[1:]):
    for c, d in zip(zs, zs[1:]):
        x, z = (a + b) / 2, (c + d) / 2
        if any(l < x < r and bottom < z < top for l, r, bottom, top in holes):
            continue
        ids = []
        for vertex in corners((a, FRONT - .28, c), (b, FRONT, d)):
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
mesh('front_wall_six_openings', vertices, list(faces.values()), wall)
box('front_bar_rear_wall', (-9.32, 2.6, 0), (9.32, 2.88, 4.6), wall, 0)
for side, x in (('west', -9.6), ('east', 9.32)):
    box('front_bar_' + side, (x, 2.6, 0), (x + .28, 8.72, 4.6), wall, 0)
    box('front_side_plinth_' + side, (x - .035, 2.6, 0),
        (x + .315, 9, .30), plinth, .008)
    box('front_side_course_' + side, (x - .025, 2.6, 4.48),
        (x + .305, 9, 4.6), trim, .008)
box('front_roof_deck', (-9.32, 2.88, 4.14), (9.32, 8.72, 4.3), roof)
box('front_parapet_coping', (-9.68, 8.65, 4.95), (9.68, 9.12, 5.05), coping, .022)
box('front_rear_coping', (-9.68, 2.52, 4.6), (9.68, 2.95, 4.7), coping)
for side, x in (('west', -9.68), ('east', 9.28)):
    box('front_side_coping_' + side, (x, 2.95, 4.6), (x + .4, 8.65, 4.7), coping)
box('front_head_course', (-9.6, 9, 4.48), (9.6, 9.06, 4.61), trim)
# The unequal extensions are exterior masses, not traversable interiors.
# West extends 11.6 m behind the bar; east extends 8.4 m and steps down 0.45 m.
for label, left, right, rear, height in (
        ('west', -9.6, -3.2, -9, 4.6), ('east', 3.2, 9.6, -5.8, 4.15)):
    for edge, x in (('left', left), ('right', right - .28)):
        box(label + '_wall_' + edge, (x, rear, 0), (x + .28, 2.6, height), wall, 0)
        # Butt-jointed caps avoid coplanar overlap at the rear and front-bar corners.
        box(label + '_coping_' + edge, (x - .08, rear + .36, height),
            (x + .36, 2.52, height + .10), coping)
        box(label + '_plinth_' + edge, (x - .035, rear, 0),
            (x + .315, 2.6, .30), plinth, .008)
        box(label + '_head_course_' + edge, (x - .025, rear, height - .12),
            (x + .305, 2.6, height), trim, .008)
    box(label + '_rear_wall', (left + .28, rear, 0),
        (right - .28, rear + .28, height), wall, 0)
    box(label + '_rear_coping', (left - .08, rear - .08, height),
        (right + .08, rear + .36, height + .10), coping)
    box(label + '_rear_plinth', (left, rear - .045, 0),
        (right, rear + .015, .3), plinth, .008)
    deck = height - .30
    box(label + '_deep_roof', (left + .28, rear + .28, deck - .16),
        (right - .28, 2.64, deck), roof)
    # Two broad seam bands only; no repeated rooftop clutter.
    for index, fraction in enumerate((.33, .67)):
        y = rear + (2.6 - rear) * fraction
        box(label + '_roof_seam_' + str(index), (left + .32, y - .018, deck - .004),
            (right - .32, y + .018, deck + .022), roof, .005)
# The broad trim wraps the court back without narrowing its 6.4 m structural opening.
box('court_back_plinth', (-3.2, 2.555, 0), (3.2, 2.605, .30), plinth, .008)
box('court_back_course', (-3.2, 2.55, 4.48), (3.2, 2.61, 4.60), trim, .008)
for index, bay in enumerate(BAYS):
    box('front_pier_' + str(index), (bay - 3.2, 8.99, 0),
        (bay - 2.83, 9.065, 4.55), trim, .015)
    box('front_plinth_' + str(index), (bay - 3.2, 9.001, 0),
        (bay + 1.10, 9.045, .30), plinth, .01)
    box('front_plinth_end_' + str(index), (bay + 2.80, 9.001, 0),
        (bay + 3.2, 9.045, .30), plinth, .01)
    for kind, x, z in (('entrance_single', 1.95, 0), ('door_single', 1.95, 0),
                       ('display_window', -.95, .48), ('canopy', -.95, 3),
                       ('fascia', -.95, 3.8)):
        obj = bpy.data.objects.new(f'mount_{index}_{kind}', None)
        collection.objects.link(obj)
        obj.parent = root
        obj.location = (bay + x, FRONT, z)
        obj.empty_display_size = .2
box('front_end_pier', (9.23, 8.99, 0), (9.6, 9.065, 4.55), trim, .015)
excluded = bpy.data.collections.new('authoring_excluded')
scene.collection.children.link(excluded)
reference = box('authoring_1m_reference', (-12, 0, 0), (-11, 1, 1), trim, 0)
collection.objects.unlink(reference)
excluded.objects.link(reference)
reference.parent = None
reference.hide_render = True
reference.hide_set(True)
scene['scope'] = 'Static exterior U-shell, open unpaved court; no interiors or roof access'
scene['provisional_structural_envelope_m'] = [19.2, 18, 5.05]
bpy.context.preferences.filepaths.save_version = 0
source = ROOT / f'art/source/models/environment/{ASSET}/{ASSET}.blend'
source.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print('SOURCE_SAVED', source)
