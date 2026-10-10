"""Author an original wall-mounted Crescents porch canopy in isolated pinned Blender."""
import math
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "d02_domestic_details_04"
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
WIDTH = 2.0
DEPTH = 1.15
BACK_ROOF_M = 3.23
FRONT_ROOF_M = 3.0


def material(name, swatch, roughness, metallic=0):
    """Match domestic trim/plinth swatches, using the mailbox sage enamel on the roof."""
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


def slope_prism(name, left, right, rear, front, back_top, front_top, thickness, mat):
    """Author a closed sloping roof or edge section with a constant vertical thickness."""
    section = [(rear, back_top - thickness), (front, front_top - thickness),
               (front, front_top), (rear, back_top)]
    vertices = [(x, y, z) for x in (left, right) for y, z in section]
    faces = [(3, 2, 1, 0), (4, 5, 6, 7)]
    for index in range(4):
        following = (index + 1) % 4
        faces.append((index, following, following + 4, index + 4))
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    finish(obj, mat, .004)


def brace(name, x, start, end):
    """Use a baked sloped rectangular metal strut, with no post in the walking corridor."""
    from mathutils import Vector
    a, b = Vector((x, *start)), Vector((x, *end))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(a + b) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (.08, .08, (b - a).length)
    obj.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    finish(obj, base, .006)


# Front projects Blender +Y; its lower eave sheds away from the wall.
slope_prism("Quiet_sage_roof", -WIDTH / 2, WIDTH / 2, -DEPTH / 2, DEPTH / 2,
            BACK_ROOF_M, FRONT_ROOF_M, .075, paint)
# Fascias tuck inside the metal skin to avoid coplanar exterior faces.
box("Ivory_front_fascia", (0, .54, 2.92), (1.98, .05, .12), trim, .006)
for side in (-1, 1):
    x = side * .955
    slope_prism("Ivory_side_fascia", x - .03, x + .03, -.55, .54,
                3.16, 2.942, .10, trim)
box("Wall_flashing", (0, -.535, 3.225), (1.94, .08, .05), base, .003)
for side in (-1, 1):
    x = side * .72
    box("Wall_mount_plate", (x, -.55, 2.88), (.12, .05, .56), base, .006)
    brace("Cantilever_brace", x, (-.52, 2.68), (.45, 2.925))

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "D02DomesticDetails04_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("D02DomesticDetails04", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "d02_domestic_details.04"
root["provenance"] = "Original Blender construction; no external meshes, textures or artwork"
root["datum"] = "Ground-projected footprint centre; wall Blender Y=-.575; lowest mesh Z=2.6"
root["state"] = "Static overhead canopy; no posts, collision, light, interior or interaction"
bpy.ops.mesh.primitive_cube_add(size=1, location=(3, 0, .5))
reference = bpy.context.object
reference.name = "authoring_1m_reference"
reference.hide_render = True
bpy.context.preferences.filepaths.save_version = 0
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
