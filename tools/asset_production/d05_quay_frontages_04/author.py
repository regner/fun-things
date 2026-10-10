"""Author the original deep-roof Old Quay corner shell; fittings stay linked separately."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_quay_frontages_04"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new("export_" + NID)
scene.collection.children.link(collection)
parts = []


def material(name, swatch, metal=0, rough=.62):
    """Convert original sRGB swatches to opaque Principled materials."""
    values = [int(swatch[i:i+2], 16)/255 for i in (0, 2, 4)]
    rgb = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in values]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = rough
    mat.diffuse_color = (*rgb, 1)
    return mat


wall = material("quay_ochre_render", "C49A65")
roof = material("quay_slate_roof", "394D62", .12, .52)
trim = material("quay_warm_stone_trim", "C8C2AD", .05, .57)
base = material("quay_petrol_plinth", "405B68", .05, .64)
accent = material("quay_amber_frontage", "DDA653", .05, .5)


def finish(obj, name, mat, bevel=.015):
    """Apply transforms, soft bevels and stable normals to a closed authored solid."""
    obj.name = name
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if bevel:
        mod = obj.modifiers.new("Soft architectural edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
    if name == "Deep_corner_walls":
        # Boolean entrance corners can bevel slightly below the exact ground datum.
        for vertex in bm.verts:
            if vertex.co.z < 0:
                vertex.co.z = 0
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    mod = obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.select_set(False)
    parts.append(obj)
    return obj


def box(name, location, dimensions, mat, bevel=.015):
    """Create a measured Blender solid, never a runtime render primitive."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    return finish(obj, name, mat, bevel)


def pitched_volume(name, half_width, half_depth, eave, ridge, ridge_front, mat):
    """Close an asymmetric three-slope volume: hipped street end and rear gable."""
    corners = [(-half_width, -half_depth), (half_width, -half_depth),
               (half_width, half_depth), (-half_width, half_depth)]
    vertices = [(x, y, 0) for x, y in corners]
    vertices += [(x, y, eave) for x, y in corners]
    vertices += [(0, -half_depth, ridge), (0, ridge_front, ridge)]
    faces = [(3, 2, 1, 0), (4, 8, 5), (5, 8, 9, 6), (6, 9, 7), (7, 9, 8, 4)]
    faces += [(i, (i+1) % 4, (i+1) % 4 + 4, i+4) for i in range(4)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, name, mat, 0)


def roof_skin(name, bottom, mat, thickness):
    """Author a thin closed three-slope roof, including its rear rake edges."""
    points = [(-4.68, -6.28, bottom), (4.68, -6.28, bottom),
              (4.68, 6.28, bottom), (-4.68, 6.28, bottom),
              (0, -6.28, bottom+3.18), (0, 3.4, bottom+3.18)]
    vertices = points + [(x, y, z+thickness) for x, y, z in points]
    slopes = [(1, 2, 5, 4), (2, 3, 5), (3, 0, 4, 5)]
    faces = [tuple(reversed(f)) for f in slopes]
    faces += [tuple(i+6 for i in f) for f in slopes]
    boundary = [0, 4, 1, 2, 3]
    faces += [(i, j, j+6, i+6) for i, j in zip(boundary, boundary[1:]+boundary[:1])]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, name, mat, .012)


# A deep corner building has two active street elevations, not a scaled sibling mesh.
body = pitched_volume("Deep_corner_walls", 4.4, 6, 6.85, 9.88, 3.3, wall)
recesses = [
    ((1.95, 5.775, 1.175), (1.42, .85, 2.55)),
    ((-.95, 5.775, 1.48), (3.04, .85, 1.88)),
    ((0, 5.775, 5.45), (4.68, .85, 1.48)),
    ((0, -5.775, 5.45), (4.68, .85, 1.48)),
    ((4.175, 2, 1.48), (.85, 3.04, 1.88)),
    ((4.175, 2, 5.45), (.85, 4.68, 1.48)),
]
for location, dimensions in recesses:
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    cutter = bpy.context.object
    cutter.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.context.view_layer.objects.active = body
    mod = body.modifiers.new("Shared fitting blind recess", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
parts.remove(body)
body.data.materials.clear()
finish(body, "Deep_corner_walls", wall, .012)
for x in (-4.4, 4.4):
    box("Side_plinth", (x, 0, .22), (.03, 12, .39), base, .006)
box("Rear_plinth", (0, -6, .22), (8.8, .03, .39), base, .006)
for x, width in [(-1.7, 5.4), (3.62, 1.56)]:
    box("Front_plinth", (x, 6.015, .22), (width, .03, .39), base, .006)
box("Front_storey_course", (.055, 6.055, 4.40), (8.91, .11, .18), accent, .018)
box("Return_storey_course", (4.455, 0, 4.40), (.11, 12, .18), accent, .018)
box("Rear_storey_course", (0, -6.035, 4.40), (8.8, .07, .14), trim, .012)
roof_skin("Warm_eave_and_rear_rakes", 6.55, trim, .10)
roof_skin("Deep_slate_three_slope_roof", 6.65, roof, .22)
box("Asymmetric_long_ridge_cap", (0, -1.44, 10.03), (.20, 9.70, .20), roof, .025)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "D05QuayFrontages04_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D05QuayFrontages04", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "d05_quay_frontages.04"
root["provenance"] = "Original Blender construction; shared fittings are separate linked resources"
root["front_axis"] = "Blender +Y maps to Godot -Z"
root["footprint_m"] = "8.8 wide x 12 deep; ground-centred; provisional"
bpy.ops.mesh.primitive_cube_add(size=1, location=(15, 0, .5))
reference = bpy.context.object
reference.name = "authoring_1m_reference"
reference.hide_render = True
bpy.context.preferences.filepaths.save_version = 0
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
