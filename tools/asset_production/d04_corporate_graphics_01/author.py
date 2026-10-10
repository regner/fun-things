"""Author one original full-size facade carrier, not a scaled small-sign derivative."""
from pathlib import Path
import runpy

import bpy
import bmesh

ROOT = Path(__file__).resolve().parents[3]
NID = "d04_corporate_graphics_01"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new(f"export_{NID}")
scene.collection.children.link(collection)
root = bpy.data.objects.new("D04CorporateGraphics01", None)
collection.objects.link(root)


def material(name, color, metal=0.0, roughness=.5):
    """Create an opaque named Principled material; Godot remaps only sign_face."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = roughness
    mat.diffuse_color = (*color, 1)
    return mat


frame = material("glassward_frame", (.055, .10, .145), .55, .38)
recess = material("recess_gasket", (.012, .021, .030), 0, .64)
face = material("sign_face", (.6, .65, .65), 0, .56)
metal = material("mount_metal", (.09, .13, .16), .65, .46)
parts = []


def box(name, location, dimensions, mat, bevel):
    """Make a closed bevelled part at actual metre scale, with identity object transforms."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Manufactured edge radius", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    mod = obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.parent = root
    parts.append(obj)
    return obj


# Thin back tray and a continuous dark perimeter; no enlarged fasteners or deep lightbox.
box("Back tray", (0, .063, 0), (5.6, .086, 4.0), frame, .02)
box("Recess bed", (0, .112, 0), (5.43, .020, 3.83), recess, .018)
for z in (-1.35, 1.35):
    box("Concealed mounting rail", (0, .019, z), (4.8, .038, .10), metal, .008)
for x in (-2.75, 2.75):
    box("Side return", (x, .104, 0), (.10, .072, 3.93), frame, .018)
for z in (-1.95, 1.95):
    box("Horizontal return", (0, .104, z), (5.50, .072, .10), frame, .018)
# Consolidate hardware only; keep the front material independently addressable.
bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
hardware = bpy.context.object
hardware.name = "D04CorporateGraphics01_Hardware"
hardware.data.name = hardware.name + "_Mesh"
parts.clear()
carrier = box("D04CorporateGraphics01_ArtworkCarrier", (0, .113, 0),
              (5.36, .030, 3.76), face, .006)
carrier.data.name = carrier.name + "_Mesh"
carrier.data.materials.append(metal)
for polygon in carrier.data.polygons:
    polygon.material_index = 0 if polygon.normal.y > .999 else 1
uv = carrier.data.uv_layers.active
uv.name = "UVMap"
for polygon in carrier.data.polygons:
    for li in polygon.loop_indices:
        position = carrier.data.vertices[carrier.data.loops[li].vertex_index].co
        uv.data[li].uv = ((2.68-position.x)/5.36, (position.z+1.88)/3.76)
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
print("CORPORATE_AUTHOR_PASS")
