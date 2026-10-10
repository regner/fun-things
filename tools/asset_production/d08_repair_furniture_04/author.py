"""Author the original static Ironreach compact workbench; pinned Blender, metres, no external assets."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d08_repair_furniture_04"
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
recess = material("ironreach_dark_recess", "20363F", .78, .05)
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


# Broad low work surface and four fixed feet; no casters or operational equipment.
for x in (-.76, .76):
    for y in (-.27, .27):
        box("Ground foot", (x, y, .02), (.16, .16, .04), frame, .008)
        box("Square bench leg", (x, y, .46), (.08, .08, .84), frame, .008)
for y in (-.29, .29):
    box("Upper long apron", (0, y, .82), (1.52, .06, .12), enamel, .008)
for x in (-.76, .76):
    box("End apron", (x, 0, .82), (.06, .58, .12), enamel, .008)
box("Lower shelf", (0, 0, .21), (1.50, .52, .04), enamel, .008)
for y in (-.24, .24):
    box("Shelf stiffener", (0, y, .18), (1.46, .025, .06), frame, .005)
box("Thick steel worktop", (0, 0, .90), (1.80, .80, .08), steel, .012)
box("Rear worktop stop", (0, -.385, .99), (1.80, .03, .14), enamel, .006)
# A shallow closed double-drawer bank leaves the right knee bay visibly open.
box("Closed drawer housing", (-.34, -.015, .685), (.74, .61, .35), frame, .009)
for index, z in enumerate((.5975, .7575)):
    box("Drawer recess", (-.34, .297, z), (.70, .02, .146), recess, .003)
    box("Closed drawer front", (-.34, .313, z), (.676, .024, .128),
        amber if index == 1 else enamel, .007)
    for x in (-.56, -.12):
        box("Grip standoff", (x, .340, z), (.038, .04, .025), frame, .004)
    box("Drawer grip", (-.34, .361, z), (.51, .028, .028), steel, .006)
# One integral covered bin below keeps storage useful but not cluttered.
box("Closed lower bin", (.37, -.025, .33), (.48, .40, .20), frame, .012)
box("Bin lid", (.37, -.025, .435), (.50, .42, .024), enamel, .007)
box("Bin lid grip", (.37, -.025, .459), (.14, .034, .024), steel, .005)
# Sparse abrasion sits on true painted or worktop surfaces, never a noise field.
wear_patch("Amber drawer rubbed edge", [(-.64,.701),(-.43,.701),(-.46,.711),
           (-.51,.708),(-.58,.717),(-.64,.712)], .3251, steel)
wear_patch("Left leg local rust", [(-.799,.08),(-.750,.08),(-.762,.12),
           (-.788,.14),(-.799,.13)], .3101, rust)
wear_patch("Shelf edge rust", [(.44,.195),(.68,.195),(.66,.208),
           (.57,.203),(.49,.214),(.44,.207)], .2601, rust)
wear_patch("Worktop paint remnant", [(-.70,.348),(-.52,.348),(-.42,.370),
           (-.44,.384),(-.68,.383)], .9401, enamel, "top")

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "D08RepairFurniture04_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D08RepairFurniture04", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "d08_repair_furniture.04"
root["authorship"] = "Original Blender construction by commissioned production worker"
root["front_axis"] = "Blender +Y -> Godot -Z"
root["pivot"] = "Ground-centred footprint (0,0,0)"
root["state"] = "Static compact workbench with integral closed drawers and bin; no interaction"
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
print("D08_REPAIR_FURNITURE_04_AUTHORED")
