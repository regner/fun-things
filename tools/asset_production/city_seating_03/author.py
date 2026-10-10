"""Author the original corner seat; all dimensions are provisional metres."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_seating_03"
OUTER_HALF, ARM_WIDTH = 1.05, .65
SEAT_HEIGHT, SEAT_THICKNESS = .46, .09
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new("export_" + ASSET)
scene.collection.children.link(collection)
parts = []


def material(name, color, metallic, roughness):
    """Define the seating family's quiet opaque ivory, slate and petrol finishes."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


ivory = material("seating_ivory", (.82, .80, .67), 0, .48)
slate = material("seating_slate", (.23, .30, .34), .15, .48)
petrol = material("seating_petrol_trim", (.045, .10, .115), .35, .40)


def corner_prism(name, inset, bottom, height, mat, bevel):
    """Extrude one continuous L outline; no overlapping elbow or diagonal seat seam."""
    outer = OUTER_HALF - inset
    inner = -OUTER_HALF + ARM_WIDTH - inset
    outline = [(-outer, -outer), (outer, -outer), (outer, inner),
               (inner, inner), (inner, outer), (-outer, outer)]
    vertices = [(x, y, z) for z in (bottom, bottom + height) for x, y in outline]
    faces = [tuple(reversed(range(6))), tuple(range(6, 12))]
    faces.extend((i, (i + 1) % 6, (i + 1) % 6 + 6, i + 6) for i in range(6))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for parent in list(obj.users_collection):
        parent.objects.unlink(obj)
    collection.objects.link(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.materials.append(mat)
    modifier = obj.modifiers.new("Soft civic roundover", "BEVEL")
    modifier.width, modifier.segments = bevel, 3
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    modifier = obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    parts.append(obj)


# The equal arms wrap an open corner, sharing the sibling's slab height and finishes.
corner_prism("Continuous L seat", 0, SEAT_HEIGHT - SEAT_THICKNESS,
             SEAT_THICKNESS, ivory, .035)
corner_prism("Recessed L rim", .04, .33, .045, petrol, .018)
corner_prism("Slate L plinth", .10, 0, .34, slate, .045)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
mesh = bpy.context.object
mesh.name = "CitySeating03_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CitySeating03", None)
collection.objects.link(root)
mesh.parent = root
root["asset_id"] = "city_seating.03"
root["authorship"] = "Original Blender construction; commissioned production specialist"
root["datum"] = "Bounding-footprint centre at ground Z=0; open corner +X/+Y; seat top .46 m"
root["axes"] = "Front Blender +Y maps to Godot -Z; up +Z maps to +Y"
source = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
source.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(source))
print("SOURCE_SAVED", source)
