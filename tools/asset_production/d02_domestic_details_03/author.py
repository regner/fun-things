"""Author an original quiet painted-metal Crescents mailbox in isolated pinned Blender."""
import math
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_domestic_details_03"
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
# Provisional metre envelope; front is Blender +Y / Godot -Z.
BODY_RADIUS = .24
BODY_SHOULDER = 1.11
BODY_BASE = .85


def material(name, swatch, roughness, metallic=0):
    """Match domestic trim/plinth swatches, adding quiet sage enamel and a dark recess."""
    rgb = [int(swatch[i:i+2], 16) / 255 for i in (0, 2, 4)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*linear, 1)
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*linear, 1)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    return mat


paint = material("crescents_sage_enamel", "526B65", .42, .25)
base = material("crescents_slate_plinth", "58636B", .75)
trim = material("crescents_ivory_trim", "D4CEBB", .55)
recess = material("mailbox_recess", "293B40", .7)


def finish(obj, mat, bevel):
    """Bake small manufactured bevels and weighted normals into closed editable geometry."""
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Soft manufactured edges", "BEVEL")
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
    for face in obj.data.polygons:
        face.use_smooth = True
    modifier = obj.modifiers.new("Broad plane normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    parts.append(obj)


def box(name, location, dimensions, mat, bevel):
    """Create one closed authored hardware part, never a runtime primitive."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    finish(obj, mat, bevel)


def arched_box(name, radius, shoulder, bottom, rear, front, mat, bevel):
    """Extrude a semicircular X/Z roof profile along the mailbox depth."""
    section = [(-radius, bottom), (radius, bottom)]
    for index in range(17):
        angle = index * math.pi / 16
        section.append((radius * math.cos(angle), shoulder + radius * math.sin(angle)))
    count = len(section)
    vertices = [(x, y, z) for y in (rear, front) for x, z in section]
    faces = [tuple(reversed(range(count))), tuple(range(count, 2 * count))]
    for index in range(count):
        following = (index + 1) % count
        faces.append((index, following, following + count, index + count))
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    finish(obj, mat, bevel)


# Body goes first to preserve the documented surface order after joining.
arched_box("Rolled_arch_housing", BODY_RADIUS, BODY_SHOULDER, BODY_BASE,
           -.21, .17, paint, .004)
box("Ground_shoe", (0, 0, .03), (.24, .24, .06), base, .008)
box("Square_support_post", (0, 0, .465), (.12, .12, .81), base, .008)
# Static front seam and closed access leaf; no interior or operable door is commissioned.
arched_box("Door_perimeter_reveal", .218, 1.11, .868, .166, .183, recess, .002)
arched_box("Closed_front_leaf", .207, 1.11, .878, .180, .196, paint, .002)
box("Letter_slot_shadow", (0, .198, 1.12), (.292, .008, .027), recess, .002)
box("Ivory_rain_lip", (0, .197, 1.145), (.32, .026, .022), trim, .003)
box("Quiet_pull_tab", (0, .198, .974), (.085, .024, .026), trim, .003)
box("Lower_hinge_bar", (0, .192, .881), (.26, .026, .020), base, .003)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "D02DomesticDetails03_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D02DomesticDetails03", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "d02_domestic_details.03"
root["provenance"] = "Original Blender construction; no external meshes, textures or artwork"
root["datum"] = "Ground-centred foot and AABB; front Blender +Y maps to Godot -Z"
root["state"] = "Static intact mailbox; no interior, working door, flag, text or interaction"
bpy.ops.mesh.primitive_cube_add(size=1, location=(3, 0, .5))
reference = bpy.context.object
reference.name = "authoring_1m_reference"
reference.hide_render = True
bpy.context.preferences.filepaths.save_version = 0
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
