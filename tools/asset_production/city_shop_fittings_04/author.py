"""Author the original static shop shutter with the pinned, isolated Blender CLI."""
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_shop_fittings_04"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
WIDTH, HEIGHT = 3.2, 2.48
SLATS, SLAT_PITCH = 14, .15
assert bpy.app.version_string == "5.2.2 LTS"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new("export_" + ASSET)
scene.collection.children.link(collection)
parts = []


def material(name, swatch, metallic, roughness):
    """Use the sibling frontage palette with opaque, single-sided Principled materials."""
    srgb = [int(swatch[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in srgb]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*linear, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*linear, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


frame = material("shutter_slate_petrol", "405B68", .25, .46)
curtain = material("shutter_satin_curtain", "70888D", .40, .48)
gasket = material("shutter_dark_rebate", "23333B", .05, .70)
hardware = material("shutter_satin_hardware", "929D9F", .65, .38)


def finish(obj, name, mat, bevel):
    """Apply restrained bevels and weighted normals to each closed manufactured solid."""
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Soft folded edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    bmesh.ops.remove_doubles(mesh, verts=list(mesh.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(mesh, edges=list(mesh.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(mesh, faces=list(mesh.faces))
    mesh.to_mesh(obj.data)
    mesh.free()
    obj.data.update()
    for face in obj.data.polygons:
        face.use_smooth = True
    modifier = obj.modifiers.new("Weighted manufactured normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    parts.append(obj)
    return obj


def box(name, position, dimensions, mat, bevel):
    """Construct an editable solid from explicit metre dimensions."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.dimensions = dimensions
    return finish(obj, name, mat, bevel)


def extrude_profile(name, profile, width, mat, bevel):
    """Extrude an original Y/Z folded sheet outline across the frontage width."""
    count = len(profile)
    vertices = [(x, y, z) for x in (-width / 2, width / 2) for y, z in profile]
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for index in range(count):
        following = (index + 1) % count
        faces.append((index, following, count + following, count + index))
    mesh = bpy.data.meshes.new(name + "_topology")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, name, mat, bevel)


# Continuous closed corrugated curtain: shallow folds, not floating individual strips.
# The back is flat; visible slat rhythm is deliberately broad rather than micro-ribbed.
profile = [(.045, .10), (.10, .10)]
for index in range(SLATS):
    bottom = .10 + index * SLAT_PITCH
    profile.extend([(.125, bottom + .022), (.125, bottom + .116),
                    (.10, bottom + .142), (.10, bottom + SLAT_PITCH)])
profile.append((.045, .10 + SLATS * SLAT_PITCH))
extrude_profile("Closed folded curtain", profile, 2.98, curtain, .003)
for sign in (-1, 1):
    box("Guide shadow rebate", (sign * 1.478, .078, 1.12),
        (.06, .092, 2.24), gasket, .006)
    box("Vertical guide casing", (sign * 1.54, .105, 1.115),
        (.12, .19, 2.23), frame, .012)
# Header is a shallow chamfered roll cover, not a fascia/artwork carrier.
extrude_profile("Folded headbox", [(.01, 2.21), (.22, 2.21), (.28, 2.27),
                (.28, 2.42), (.22, HEIGHT), (.01, HEIGHT)], WIDTH, frame, .010)
box("Headbox lower lip", (0, .23, 2.223), (2.99, .028, .027), hardware, .004)
box("Ground contact seal", (0, .095, .015), (2.98, .12, .03), gasket, .004)
box("Weighted bottom rail", (0, .105, .072), (2.98, .13, .096), hardware, .008)
# Two simple recessed-looking grip plates on the weighted rail; no lock/interaction API.
for x in (-.78, .78):
    box("Bottom rail grip recess", (x, .172, .075), (.19, .008, .045), gasket, .008)
    box("Bottom rail grip lip", (x, .179, .085), (.15, .014, .014), frame, .004)

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.object
obj.name = "CityShopFittings04_Mesh"
scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
root = bpy.data.objects.new("CityShopFittings04", None)
collection.objects.link(root)
obj.parent = root
root["asset_id"] = "city_shop_fittings.04"
root["authorship"] = "Original Blender construction; commissioned implementation specialist"
root["front_axis"] = "Blender +Y maps to Godot -Z"
root["datum"] = "Facade plane and finished-floor centre at origin; wall at Blender Y=0"
root["state"] = "Static closed frontage closure; no opening animation or interaction"
root["interface"] = "Provisional 3.2 x 2.48 m; standalone closed bay, not a window overlay"
# An excluded metre fixture makes the source scale independently inspectable.
reference = bpy.data.collections.new("authoring_excluded")
scene.collection.children.link(reference)
bpy.ops.mesh.primitive_cube_add(size=1, location=(5, 0, .5))
metre = bpy.context.object
metre.name = "authoring_1m_reference"
for owner in list(metre.users_collection):
    owner.objects.unlink(metre)
reference.objects.link(metre)
metre.hide_render = True
metre.hide_set(True)
SOURCE.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
exec(compile((Path(__file__).parent / "export.py").read_text(),
             str(Path(__file__).parent / "export.py"), "exec"))
print("CITY_SHOP_FITTINGS_04_AUTHORED")
