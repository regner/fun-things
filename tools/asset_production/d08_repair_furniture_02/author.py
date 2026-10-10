"""Author the original static Ironreach tyre rack; pinned Blender, metres, no external assets."""
from pathlib import Path

import math

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d08_repair_furniture_02"
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


def beam(name, start, end, width, depth, mat):
    """Place a solid square-ended brace between its authored attachment centres."""
    direction = Vector(end) - Vector(start)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(Vector(start) + Vector(end)) / 2)
    obj = bpy.context.object
    obj.dimensions = (width, depth, direction.length)
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return finish(obj, name, mat, .006)


def tyre(name, centre):
    """Revolve an original hollow tyre section around X, including two broad tread channels."""
    # Axial distance/radius in metres. The inner wall closes the section without a filled hub.
    profile = [(-.115,.20),(-.14,.225),(-.15,.28),(-.138,.325),(-.10,.355),
               (-.055,.36),(-.048,.35),(-.032,.35),(-.025,.36),(.025,.36),
               (.032,.35),(.048,.35),(.055,.36),(.10,.355),(.138,.325),
               (.15,.28),(.14,.225),(.115,.20)]
    segments = 40
    vertices = [(centre[0] + axial, centre[1] + radius * math.sin(2 * math.pi * i / segments),
                 centre[2] + radius * math.cos(2 * math.pi * i / segments))
                for axial, radius in profile for i in range(segments)]
    faces = []
    for ring in range(len(profile)):
        following = (ring + 1) % len(profile)
        for index in range(segments):
            after = (index + 1) % segments
            faces.append((ring * segments + index, ring * segments + after,
                          following * segments + after, following * segments + index))
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    finish(obj, name, rubber)
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj


# Two grounded runners and four stout uprights; no wheels or movable repair equipment.
for side in (-1, 1):
    x = side * 1.0
    box("Ground runner", (x, 0, .02), (.20, .82, .04), frame, .007)
    for end in (-1, 1):
        box("Square upright", (x, end * .32, .94), (.07, .07, 1.80), enamel, .006)
        box("Foot collar", (x, end * .32, .085), (.10, .10, .09), frame, .005)
    box("Upper side tie", (x, 0, 1.805), (.07, .64, .07), frame, .006)
    for level in (.19, 1.03):
        box("Side rail", (x, 0, level), (.07, .64, .09), frame, .006)
# Tyres cradle across paired front/rear rails, not across a solid shelf.
for level in (.19, 1.03):
    for end in (-1, 1):
        mat = amber if level > 1 and end > 0 else frame
        box("Cradle rail", (0, end * .255, level), (2.0, .07, .12), mat, .008)
    for side in (-1, 1):
        box("Rail attachment plate", (side * .965, .296, level), (.14, .018, .14), enamel, .005)
        box("Exposed broad fastener", (side * .965, .310, level), (.031, .014, .031), steel, .006)
# Back brace stiffens the silhouette but leaves both ends and top open.
beam("Rear diagonal brace", (-.98, -.321, .28), (.98, -.321, 1.78), .048, .033, frame)
for level in (.50, 1.34):
    for index, x in enumerate((-.72, -.36, 0, .36, .72)):
        tyre("Integral tyre %02d at %.2f" % (index, level), (x, 0, level))
# Sparse worn edges remain the family finish, not a new grunge treatment.
wear_patch("Lower rail rust", [(-.78,.151),(-.50,.151),(-.54,.166),
           (-.65,.169),(-.71,.181),(-.78,.174)], .2901, rust)
wear_patch("Amber rail rubbed edge", [(.37,.981),(.75,.981),(.75,.995),
           (.63,1.004),(.58,.997),(.45,1.002)], .2901, steel)
wear_patch("Front post rust", [(.974,.16),(1.026,.16),(1.026,.29),
           (1.01,.273),(.999,.22),(.974,.207)], .3551, rust)
wear_patch("Left post scuff", [(-1.026,1.60),(-1.006,1.61),(-.984,1.75),
           (-1.026,1.77)], .3551, steel)
wear_patch("Runner worn corner", [(.925,.22),(.952,.245),(.965,.385),
           (1.035,.39),(1.035,.398),(.925,.398)], .0401, steel, "top")

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "D08RepairFurniture02_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D08RepairFurniture02", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "d08_repair_furniture.02"
root["authorship"] = "Original Blender construction by commissioned production worker"
root["front_axis"] = "Blender +Y -> Godot -Z"
root["pivot"] = "Ground-centred footprint (0,0,0)"
root["state"] = "Static two-tier rack with ten integral tyres; no interaction or moving parts"
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
print("D08_REPAIR_FURNITURE_02_AUTHORED")
