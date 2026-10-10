"""Construct the original Northpoint lighthouse in Blender; dimensions are provisional metres."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d01_lighthouse_01"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
SEGMENTS = 64
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new("export_" + ASSET)
scene.collection.children.link(collection)
parts = []


def material(name, color, roughness, metal=0, emission=0):
    """Use original opaque Principled colors; warm glazing is appearance, not a beam/light."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Emission Color"].default_value = (*color, 1)
    shader.inputs["Emission Strength"].default_value = emission
    return mat


ivory = material("lighthouse_ivory_masonry", (.82, .79, .68), .72)
red = material("lighthouse_muted_red_band", (.48, .065, .045), .57)
stone = material("lighthouse_pale_stone", (.51, .55, .51), .73)
metal = material("lighthouse_petrol_metal", (.018, .055, .062), .4, .45)
recess = material("lighthouse_door_window_recess", (.013, .032, .037), .58)
glass = material("lighthouse_warm_glazing", (.95, .49, .115), .25, .1, .65)


def finish(obj, name, mat, bevel=0, smooth=True, weighted=True):
    """Apply transforms and local edge treatment; each overlapping piece remains a closed solid."""
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Soft crafted edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=0.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    for polygon in obj.data.polygons:
        polygon.use_smooth = smooth
    if smooth and weighted:
        modifier = obj.modifiers.new("Weighted architectural normals", "WEIGHTED_NORMAL")
        modifier.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    parts.append(obj)
    return obj


def lathe(name, profile, mat, count=SEGMENTS, bevel=0):
    """Create a capped radial profile; section tuples are height/radius, never zero-radius rings."""
    verts = [(radius * math.cos(i * math.tau / count),
              radius * math.sin(i * math.tau / count), height)
             for height, radius in profile for i in range(count)]
    faces = [tuple(reversed(range(count)))]
    for row in range(len(profile) - 1):
        for i in range(count):
            a, b = row * count + i, row * count + (i + 1) % count
            faces.append((a, b, b + count, a + count))
    faces.append(tuple(range((len(profile) - 1) * count, len(profile) * count)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    finish(obj, name, mat, bevel, weighted=False)
    # Large end caps must not bend the adjacent cone/cornice normals inward.
    for polygon in obj.data.polygons:
        if len(polygon.vertices) > 4:
            polygon.use_smooth = False
    return obj


def box(name, location, dimensions, mat, bevel=.015):
    """Create a small closed manufactured fitting, not a runtime-built hierarchy."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    return finish(obj, name, mat, bevel)


def rod(name, start, end, radius, mat):
    """Fit a closed round rail or lantern mullion between authored endpoints."""
    start, end = Vector(start), Vector(end)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius,
                                      depth=(end - start).length, location=(start + end) / 2)
    obj = bpy.context.object
    obj.rotation_euler = (end - start).to_track_quat("Z", "Y").to_euler()
    return finish(obj, name, mat, .006)


def hoop(name, radius, height, tube, mat):
    """Build an unbroken circumference rail with a modest, smooth closed torus."""
    bpy.ops.mesh.primitive_torus_add(major_segments=64, minor_segments=8,
                                    major_radius=radius, minor_radius=tube,
                                    location=(0, 0, height))
    return finish(bpy.context.object, name, mat)


def arch(name, width, bottom, spring, y_back, y_front, mat, bevel=.012):
    """Extrude an arched closed face; doorway relief is sealed against the solid tower."""
    radius = width / 2
    profile = [(-radius, bottom), (radius, bottom), (radius, spring)]
    profile += [(radius * math.cos(i * math.pi / 16),
                 spring + radius * math.sin(i * math.pi / 16)) for i in range(1, 17)]
    verts = [(x, y, z) for y in (y_back, y_front) for x, z in profile]
    count = len(profile)
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for i in range(count):
        j = (i + 1) % count
        faces.append((i, j, j + count, i + count))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, name, mat, bevel)


# Compact masonry body. Color is a face assignment on one continuous taper, not a floating sleeve.
lathe("Ground contact plinth", [(0, 2.05), (.12, 2.05), (.30, 1.91), (.34, 1.78)], stone)
shaft = lathe("Continuous tapered masonry shaft", [(.26, 1.75), (8.35, 1.294),
              (10.45, 1.176), (10.8, 1.156)], ivory)
shaft.data.materials.append(red)
for polygon in shaft.data.polygons:
    if 8.35 < polygon.center.z < 10.45:
        polygon.material_index = 1
lathe("Masonry neck cornice", [(10.45, 1.18), (10.52, 1.28), (10.67, 1.28),
      (10.8, 1.55), (10.9, 1.65)], ivory)
lathe("Gallery corbel flare", [(10.64, 1.27), (10.80, 1.72), (10.89, 2.12),
      (10.94, 2.2), (11.04, 2.2), (11.10, 2.12)], stone)
lathe("Gallery dark deck rim", [(11.04, 2.18), (11.10, 2.18)], metal)
# The non-accessible gallery has a dedicated circular railing, not the boardwalk's shared rail.
for i in range(24):
    angle = i * math.tau / 24
    x, y = 2.10 * math.cos(angle), 2.10 * math.sin(angle)
    rod(f"Gallery upright {i:02d}", (x, y, 11.07), (x, y, 12.12), .037, metal)
hoop("Gallery handrail", 2.10, 12.12, .05, metal)
hoop("Gallery middle rail", 2.10, 11.61, .028, metal)
hoop("Gallery toe rail", 2.10, 11.19, .033, metal)
# Octagonal lantern, warm opaque pane appearance avoids depth-sorted overlapping transparency.
lathe("Lantern lower drum", [(11.09, 1.20), (11.45, 1.20), (11.49, 1.25)], metal, 8)
lathe("Warm glazed lantern", [(11.45, 1.145), (13.22, 1.145)], glass, 8)
for i in range(8):
    angle = i * math.tau / 8
    x, y = 1.155 * math.cos(angle), 1.155 * math.sin(angle)
    rod(f"Lantern mullion {i:02d}", (x, y, 11.45), (x, y, 13.28), .047, metal)
lathe("Lantern upper frame", [(13.19, 1.20), (13.31, 1.20)], metal, 8)
# Hipped cap is deliberately dark and compact; broad roof ribs add overhead recognition.
lathe("Roof eave and cap", [(13.28, 1.23), (13.34, 1.50), (13.43, 1.50),
      (14.54, .20), (14.63, .15)], metal, 32)
for i in range(8):
    angle = i * math.tau / 8
    rod(f"Roof folded seam {i:02d}",
        (1.46 * math.cos(angle), 1.46 * math.sin(angle), 13.44),
        (.18 * math.cos(angle), .18 * math.sin(angle), 14.59), .018, metal)
lathe("Finial", [(14.58, .14), (14.75, .14), (14.80, .08), (15.0, .025)], metal, 24)
# Sealed entry with readable arched pale surround, dark timber/metal leaf and restrained fittings.
arch("Pale arch surround", 1.34, .25, 2.04, 1.37, 1.83, stone, .025)
arch("Door shadow reveal", 1.10, .31, 2.03, 1.77, 1.86, recess)
arch("Closed petrol door", .94, .34, 2.015, 1.84, 1.89, metal)
box("Door inset upper", (0, 1.919, 1.78), (.65, .04, .62), recess, .055)
box("Door inset lower", (0, 1.919, .84), (.65, .04, .63), recess, .025)
box("Door latch", (.29, 1.96, 1.31), (.06, .04, .23), stone, .012)
# Only two small window rhythms, sized as broad accents rather than dense masonry noise.
for height, depth in ((4.70, 1.54), (6.88, 1.42)):
    arch(f"Window surround {height}", .55, height - .56, height + .25,
         depth - .12, depth + .045, stone)
    arch(f"Window recess {height}", .34, height - .43, height + .25,
         depth + .043, depth + .065, recess)
    box(f"Window sill {height}", (0, depth + .035, height - .52),
        (.68, .24, .10), stone, .018)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "D01Lighthouse01_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D01Lighthouse01", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "d01_lighthouse.01"
root["authorship"] = "Original commissioned Blender construction; no external geometry or textures"
root["front_axis"] = "Blender +Y / Godot -Z; ground-centred pivot"
root["scope"] = "Closed coastal landmark; no interior, climbing, beacon rotation or beam"
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
print("D01_LIGHTHOUSE_01_SOURCE_SAVED", SOURCE)
