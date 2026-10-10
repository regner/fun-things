"""Build the original closed service dumpster with the pinned Blender CLI."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_waste_03"
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


def material(name, color, metallic, roughness):
    """Create opaque, back-culled Principled surfaces without external dependencies."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*color, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


# Faded steel stays in the established muted waste palette; rust is localized, not noise.
body = material("waste_body_petrol", (.060, .115, .115), .25, .64)
lid = material("waste_lid_sage", (.100, .165, .155), .20, .57)
recess = material("waste_recess_charcoal", (.016, .025, .029), .15, .68)
metal = material("waste_hardware_slate", (.170, .215, .225), .50, .42)


def finish(obj, name, mat, bevel, smooth=True):
    """Apply soft manufactured edges and preserve closed, consistently wound subparts."""
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Manufactured edge radius", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    bmesh.ops.remove_doubles(mesh, verts=list(mesh.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(mesh, edges=list(mesh.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(mesh, faces=list(mesh.faces))
    mesh.to_mesh(obj.data)
    mesh.free()
    obj.data.update()
    for polygon in obj.data.polygons:
        polygon.use_smooth = smooth
    if smooth:
        modifier = obj.modifiers.new("Weighted manufactured normals", "WEIGHTED_NORMAL")
        modifier.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    parts.append(obj)
    return obj


def box(name, position, dimensions, mat, bevel):
    """Author one editable solid with literal metre dimensions."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.dimensions = dimensions
    return finish(obj, name, mat, bevel)


rust = material("waste_localized_rust", (.115, .058, .034), 0, .86)

# The wide tapered steel container is closed; no inaccessible interior is modeled.
vertices = [(x * width / 2, y * depth / 2, z)
            for z, width, depth in ((.20, 1.90, 1.05), (1.36, 2.10, 1.26))
            for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
faces = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4),
         (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
mesh = bpy.data.meshes.new("Tapered service steel shell")
mesh.from_pydata(vertices, [], faces)
mesh.update()
obj = bpy.data.objects.new("Service body", mesh)
collection.objects.link(obj)
finish(obj, "Closed service body", body, .025)
# Two full-depth skids contact the ground; no wheels or movable physics parts.
for x in (-.73, .73):
    box("Ground skid", (x, 0, .09), (.18, 1.12, .18), recess, .022)
    box("Skid mounting saddle", (x, 0, .20), (.24, .94, .08), metal, .016)
box("Folded base rail", (0, 0, .27), (1.98, 1.13, .14), body, .020)
box("Reinforced rim", (0, 0, 1.345), (2.20, 1.36, .09), body, .022)
box("Closed lid shadow seam", (0, 0, 1.396), (2.17, 1.37, .036), recess, .012)
# Twin broad shallow lids give the service member an unmistakable wide roof rhythm.
for x in (-.5525, .5525):
    box("Closed split lid", (x, 0, 1.45), (1.075, 1.42, .10), lid, .030)
    for dx in (-.24, .24):
        box("Wide lid stiffener", (x + dx, -.04, 1.512), (.075, .96, .076), lid, .018)
    box("Front lid grip", (x, .645, 1.478), (.28, .10, .055), lid, .020)
    box("Rear hinge barrel", (x, -.665, 1.426), (.40, .075, .075), metal, .025)
# Paired open fork sleeves are built as four closed bars, not black painted fake holes.
for side in (-1, 1):
    x = side * 1.07
    for z in (.69, .89):
        box("Fork sleeve flange", (x, 0, z), (.18, .88, .055), body, .012)
    for xx in (x - .0675, x + .0675):
        box("Fork sleeve side", (xx, 0, .79), (.045, .88, .16), body, .010)
# Sparse vertical pressings strengthen the front/back panels without dense repeated detail.
for side in (-1, 1):
    for x in (-.62, .62):
        rib = box("Panel pressing", (x, side * .59, .82), (.065, .06, .78), body, .020)
        rib.rotation_euler.x = -side * .0903
        bpy.context.view_layer.objects.active = rib
        rib.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        rib.select_set(False)


def wear_patch(name, outline):
    """Author a thin closed rust island following the front panel's actual taper."""
    verts = [(x, .525 + (z - .20) * .105 / 1.16 + depth, z)
             for depth in (.0005, .0025) for x, z in outline]
    count = len(outline)
    faces = [tuple(reversed(range(count))), tuple(range(count, 2 * count))]
    faces += [(i, (i + 1) % count, (i + 1) % count + count, i + count)
              for i in range(count)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    # Thin paint-loss edges need flat face normals; averaging across the two sides flips them.
    finish(obj, name, rust, 0, smooth=False)


# Broad sparse chipped areas: no dirt texture, random speckle, labels or hazard stripes.
wear_patch("Lower front paint loss", [(-.48, .37), (-.29, .37), (-.25, .40),
           (-.31, .415), (-.40, .40), (-.49, .42)])
wear_patch("Front corner paint loss", [(.79, .42), (.87, .43), (.90, .51),
           (.87, .53), (.83, .48), (.78, .47)])
# Local sleeve-edge wear stays muted and away from the lid's gameplay silhouette.
for side in (-1, 1):
    box("Fork contact wear", (side * 1.145, .445, .885), (.026, .008, .043), rust, .003)
bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "CityWaste03_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityWaste03", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "city_waste.03"
root["authorship"] = "Original Blender construction; commissioned implementation specialist"
root["front_axis"] = "Blender +Y maps to Godot -Z; lid grips face front"
root["state"] = "Closed static; no collection, loot, destruction or moving parts"
root["ground_datum"] = "Ground-centered body footprint; two fixed skids contact Z=0"
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
print("CITY_WASTE_03_AUTHORED")
