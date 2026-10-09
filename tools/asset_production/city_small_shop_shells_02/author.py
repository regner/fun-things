"""Author the original wide standalone shell; pinned Blender CLI, no live sessions."""
from pathlib import Path

import bmesh
import bpy
import io_scene_gltf2

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_small_shop_shells_02"
WIDTH, DEPTH = 12.8, 9.0
FRONT, DECK = DEPTH / 2, 4.3
BAYS = (-3.2, 3.2)
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
root["datum"] = "Ground-centred 12.8 x 9 m footprint; Blender +Y front, +Z up"


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


# One welded cell facade, not stacked cubes: four actual fitting apertures.
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
mesh("front_wall_four_openings", vertices, list(faces.values()), wall)
box("side_wall_left", (-6.4, -4.5, 0), (-6.12, 4.22, 4.6), wall, 0)
box("side_wall_right", (6.12, -4.5, 0), (6.4, 4.22, 4.6), wall, 0)
box("rear_wall", (-6.12, -4.5, 0), (6.12, -4.22, 4.6), wall, 0)
box("flat_roof_deck", (-6.12, -4.22, 4.14), (6.12, 4.22, DECK), roof)
# Broad transverse roof rhythm distinguishes this shallow/wide mass from .01.
for label, y in (("front", 1.45), ("rear", -1.45)):
    box("roof_fold_" + label, (-6.02, y - .018, 4.296),
        (6.02, y + .018, 4.322), roof, .006)
box("front_parapet_coping", (-6.48, 4.15, 4.95), (6.48, 4.62, 5.05), coping, .022)
box("rear_coping", (-6.48, -4.58, 4.6), (6.48, -4.15, 4.7), coping, .015)
for label, x in (("left", -6.48), ("right", 6.08)):
    box("side_coping_" + label, (x, -4.15, 4.6), (x + .40, 4.22, 4.7), coping)
# Wrapped plinth/head course make the formerly party-wall sides intentional elevations.
for label, low, high in (
    ("left", (-6.445, -4.5, 0), (-6.395, 4.5, .3)),
    ("right", (6.395, -4.5, 0), (6.445, 4.5, .3)),
    ("rear", (-6.4, -4.545, 0), (6.4, -4.495, .3)),
):
    box("plinth_" + label, low, high, plinth, .01)
for label, x in (("left", -6.43), ("right", 6.39)):
    box("side_head_course_" + label, (x, -4.5, 4.48), (x + .04, 4.5, 4.60), trim)
box("rear_head_course", (-6.4, -4.53, 4.48), (6.4, -4.49, 4.60), trim)
box("front_head_course", (-6.4, 4.5, 4.48), (6.4, 4.56, 4.61), trim)
for label, x in (("left", -6.4), ("centre", -.18), ("right", 6.03)):
    box("front_pier_" + label, (x, 4.49, 0), (x + .37, 4.565, 4.55), trim, .015)
for label, bay in zip(("left", "right"), BAYS):
    box("front_plinth_" + label, (bay - 3.2, 4.501, 0),
        (bay + 1.10, 4.545, .30), plinth, .01)
    box("front_plinth_end_" + label, (bay + 2.80, 4.501, 0),
        (bay + 3.2, 4.545, .30), plinth, .01)
    for kind, x, z in (("entrance_single", 1.95, 0), ("door_single", 1.95, 0),
                       ("display_window", -.95, .48), ("canopy", -.95, 3),
                       ("fascia", -.95, 3.8)):
        obj = bpy.data.objects.new("mount_" + label + "_" + kind, None)
        collection.objects.link(obj)
        obj.parent = root
        obj.location = (bay + x, FRONT, z)
        obj.empty_display_size = .2
obj = bpy.data.objects.new("mount_roof_detail", None)
collection.objects.link(obj)
obj.parent = root
obj.location = (0, 0, DECK)
excluded = bpy.data.collections.new("authoring_excluded")
scene.collection.children.link(excluded)
reference = box("authoring_1m_reference", (-8, 0, 0), (-7, 1, 1), trim, 0)
collection.objects.unlink(reference)
excluded.objects.link(reference)
reference.parent = None
reference.hide_render = True
reference.hide_set(True)
scene["scope"] = "Static exterior shell; fittings remain separate linked assets; no interiors"
scene["approved_envelope_m"] = [12.8, 9, 5.05]
bpy.context.preferences.filepaths.save_version = 0
source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
source.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print("SOURCE_SAVED", source)
