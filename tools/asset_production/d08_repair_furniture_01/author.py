"""Author the original static Ironreach tool cabinet; pinned Blender, metres, no external assets."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d08_repair_furniture_01"
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
recess = material("ironreach_dark_recess", "20363F", .78, .05)
steel = material("ironreach_replacement_sheet", "7D9190", .52, .55)
rust = material("ironreach_local_rust", "A7653E", .9, 0)
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


# Stationary recessed plinth, not wheels: the later trolley owns the mobile-looking silhouette.
box("Ground plinth", (0, -.015, .065), (1.32, .60, .13), frame, .018)
box("Sealed carcass", (0, -.015, .78), (1.40, .65, 1.32), frame, .018)
for side in (-1, 1):
    box("Pressed side panel", (side * .699, -.02, .81), (.018, .53, 1.18), enamel, .008)
box("Top seam", (0, 0, 1.429), (1.42, .75, .022), recess, .006)
box("Rounded top cap", (0, 0, 1.45), (1.44, .80, .06), enamel, .012)
box("Recessed rubber top pad", (0, -.014, 1.488), (1.27, .62, .024), recess, .012)
box("Warm front rim", (0, .341, 1.481), (1.23, .055, .010), amber, .003)
# Closed lower double cupboard, with a dark narrow meeting seam and matching short pulls.
for side in (-1, 1):
    x = side * .318
    box("Closed lower door", (x, .322, .444), (.616, .026, .55), enamel, .008)
    box("Door pull backing", (side * .08, .344, .475), (.042, .025, .22), recess, .005)
    box("Vertical lower pull", (side * .08, .365, .475), (.025, .028, .19), steel, .006)
# Four shallow drawers and one deeper lowest drawer make this a tool chest, not a utility enclosure.
for index, (height, depth) in enumerate(((.80, .13), (.938, .112), (1.064, .112),
                                        (1.19, .112), (1.316, .112))):
    mat = amber if index == 3 else enamel
    box("Closed drawer %02d" % index, (0, .322, height), (1.254, .026, depth), mat, .006)
    for side in (-1, 1):
        box("Handle foot", (side * .474, .345, height + .012), (.045, .039, .032), frame, .004)
    box("Broad drawer grip", (0, .365, height + .012), (1.012, .026, .033), steel, .007)
# No text, logo, glowing status or lock gameplay. Two quiet closed hinge plates establish function.
for x in (-.619, .619):
    box("Door hinge", (x, .339, .47), (.025, .018, .115), frame, .004)
# Localized abrasion follows touched edges: closed solids intersect their supporting surface slightly.
wear_patch("Lower left paint loss", [(-.595,.193),(-.39,.193),(-.405,.209),
           (-.49,.221),(-.54,.217),(-.595,.239)], .3351, rust)
wear_patch("Lower right paint loss", [(.41,.188),(.596,.188),(.596,.229),
           (.55,.216),(.528,.218),(.512,.201)], .3351, rust)
wear_patch("Drawer edge scuff", [(-.57,1.28),(-.34,1.28),(-.39,1.292),
           (-.48,1.294),(-.56,1.3)], .3351, steel)
wear_patch("Warm drawer rubbed edge", [(.32,1.145),(.596,1.145),(.596,1.162),
           (.53,1.158),(.50,1.166),(.43,1.159)], .3351, steel)
wear_patch("Side lower rust", [(-.25,.237),(.12,.237),(.135,.252),
           (.01,.261),(-.08,.252),(-.15,.28),(-.25,.267)], .7081, rust, "side")
wear_patch("Side shallow scuff", [(-.19,.84),(.12,.82),(.18,.831),
           (-.10,.86)], .7081, steel, "side")
wear_patch("Top corner wear", [(-.696,.275),(-.655,.282),(-.649,.355),
           (-.582,.362),(-.58,.375),(-.696,.371)], 1.4801, steel, "top")

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "D08RepairFurniture01_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D08RepairFurniture01", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "d08_repair_furniture.01"
root["authorship"] = "Original Blender construction by commissioned production worker"
root["front_axis"] = "Blender +Y -> Godot -Z"
root["pivot"] = "Ground-centred footprint (0,0,0)"
root["state"] = "Static closed tool cabinet; no interaction, interior or moving parts"
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
print("D08_REPAIR_FURNITURE_01_AUTHORED")
