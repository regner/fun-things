"""Author the original static Ironreach low parts trolley; pinned Blender, metres, no external assets."""
from pathlib import Path

import math

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d08_repair_furniture_03"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new("export_" + ASSET)
scene.collection.children.link(collection)
parts = []


def material(name, swatch, roughness, metallic):
    """Retain the existing Ironreach swatches as opaque, back-culled workshop finishes."""
    rgb = [int(swatch[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*linear, 1)
    shader = result.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*linear, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return result


enamel = material("ironreach_faded_petrol", "627D7B", .64, .25)
frame = material("ironreach_roof_petrol", "294E58", .60, .30)
steel = material("ironreach_replacement_sheet", "7D9190", .52, .55)
rust = material("ironreach_local_rust", "A7653E", .9, 0)
rubber = material("ironreach_tyre_rubber", "293437", .86, 0)
amber = material("ironreach_working_amber", "F5BA55", .65, .10)


def finish(obj, name, mat, bevel=0):
    """Bake soft manufactured edges and normals; keep each solid component manifold."""
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Manufactured edge", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    if bevel:
        for face in obj.data.polygons:
            face.use_smooth = True
        modifier = obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
        modifier.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    parts.append(obj)
    return obj


def box(name, location, dimensions, mat, bevel=.008):
    """Construct an editable closed steel component, facing Blender +Y / Godot -Z."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    return finish(obj, name, mat, bevel)


def wear_patch(name, outline, plane, mat, axis="front"):
    """Use sparse closed 0.8mm paint-loss prisms, not floating decals or noisy texture grids."""
    vertices = []
    for depth in (plane - .0004, plane + .0004):
        for u, v in outline:
            if axis == "front":
                vertices.append((u, depth, v))
            elif axis == "side":
                vertices.append((depth, u, v))
            else:
                vertices.append((u, v, depth))
    count = len(outline)
    faces = [tuple(reversed(range(count))), tuple(range(count, 2 * count))]
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, next_index, next_index + count, index + count))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, name, mat)


def cylinder(name, centre, radius, width, mat):
    """Make one closed static caster or axle cap along X."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=width,
                                       location=centre, rotation=(0, math.pi / 2, 0))
    return finish(bpy.context.object, name, mat, .004)


def handle():
    """Sweep a closed U-shaped push bar; static geometry, not an interaction socket."""
    path = [(-.27, .39), (-.27, .775)]
    for i in range(1, 5):
        angle = math.pi - i * math.pi / 8
        path.append((-.21 + .06 * math.cos(angle), .775 + .06 * math.sin(angle)))
    path.append((.21, .835))
    for i in range(1, 5):
        angle = math.pi / 2 - i * math.pi / 8
        path.append((.21 + .06 * math.cos(angle), .775 + .06 * math.sin(angle)))
    path.append((.27, .39))
    vertices, faces = [], []
    segments = 12
    for index, (y, z) in enumerate(path):
        before = Vector((0, *path[max(0, index - 1)]))
        after = Vector((0, *path[min(len(path) - 1, index + 1)]))
        tangent = (after - before).normalized()
        across = Vector((1, 0, 0))
        other = tangent.cross(across)
        for i in range(segments):
            angle = i * 2 * math.pi / segments
            vertices.append(tuple(Vector((.655, y, z)) + .025 *
                                  (math.cos(angle) * across + math.sin(angle) * other)))
    for j in range(len(path) - 1):
        for i in range(segments):
            faces.append((j * segments + i, j * segments + (i + 1) % segments,
                          (j + 1) * segments + (i + 1) % segments,
                          (j + 1) * segments + i))
    faces.extend([tuple(reversed(range(segments))),
                  tuple(range((len(path) - 1) * segments, len(path) * segments))])
    mesh = bpy.data.meshes.new("Bent push handle")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("Bent push handle", mesh)
    collection.objects.link(obj)
    finish(obj, "Bent push handle", frame)
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4


# Four small caster assemblies are part of the joined stationary visual, not physics wheels.
for x in (-.51, .39):
    for y in (-.255, .255):
        cylinder("Integral caster tyre", (x, y, .09), .09, .06, rubber)
        cylinder("Caster axle", (x, y, .09), .031, .108, steel)
        for side in (-1, 1):
            box("Caster fork", (x + side * .043, y, .145), (.018, .065, .135),
                frame, .005)
        box("Caster swivel plate", (x, y, .205), (.13, .12, .025), steel, .006)
# Two broad shallow trays, an airy gap, and four connected corner posts.
for z in (.235, .545):
    box("Tray floor", (-.06, 0, z), (1.24, .70, .03), enamel, .010)
    for y in (-.335, .335):
        finish_mat = amber if z > .5 and y > 0 else enamel
        box("Retaining long rim", (-.06, y, z + .0575), (1.24, .03, .085),
            finish_mat, .006)
    for x in (-.665, .545):
        box("Retaining end rim", (x, 0, z + .0575), (.03, .64, .085), enamel, .006)
for x in (-.615, .495):
    for y in (-.285, .285):
        box("Corner upright", (x, y, .405), (.045, .045, .43), frame, .006)
# A restrained integral closed parts case below, two covered sorting tins above.
for name, centre, dims in (
    ("Lower parts case", (-.22, -.02, .33), (.49, .40, .16)),
    ("Upper broad tin", (-.30, -.01, .61), (.38, .43, .10)),
    ("Upper small tin", (.15, -.03, .599), (.29, .35, .078)),
):
    box(name, centre, dims, frame, .012)
    lid_z = centre[2] + dims[2] / 2
    box(name + " fitted lid", (centre[0], centre[1], lid_z),
        (dims[0] + .015, dims[1] + .015, .018), steel, .007)
    box(name + " lid grip", (centre[0], centre[1], lid_z + .018),
        (.13, .035, .028), frame, .008)
handle()
for y in (-.27, .27):
    box("Handle mounting lug", (.585, y, .45), (.18, .07, .075), steel, .008)
# Sparse irregular wear is placed on actual rim faces and one top corner.
wear_patch("Lower rim rust", [(-.58,.269),(-.40,.269),(-.435,.285),
           (-.50,.280),(-.55,.292),(-.58,.283)], .3501, rust)
wear_patch("Amber rim abrasion", [(-.10,.579),(.20,.579),(.17,.591),
           (.09,.587),(.04,.600),(-.04,.592)], .3501, steel)
wear_patch("End rim rust", [(-.23,.568),(-.10,.568),(-.12,.581),
           (-.19,.578),(-.23,.590)], -.6801, rust, "side")
wear_patch("Lower rim rubbed corner", [(-.61,.292),(-.54,.302),(-.48,.311),
           (-.51,.323),(-.61,.323)], .3501, steel)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "D08RepairFurniture03_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D08RepairFurniture03", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "d08_repair_furniture.03"
root["authorship"] = "Original Blender construction by commissioned production worker"
root["front_axis"] = "Blender +Y -> Godot -Z"
root["pivot"] = "Ground-centred footprint (0,0,0)"
root["state"] = "Static low parts trolley with integral closed storage and casters; no interaction"
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
print("D08_REPAIR_FURNITURE_03_AUTHORED")
