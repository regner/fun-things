"""Original modular Terrace Ward flat-roof caps; exact sibling connector footprints."""
import math
import runpy
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_apartment_family_10"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
STOREY_HEIGHT = 3.2
assert bpy.app.version_string == "5.2.2 LTS", bpy.app.version_string
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1
collection = None
parts = []


def material(name, swatch, roughness, metallic=0):
    """Match the straight bay's opaque sRGB swatches using linear Principled inputs."""
    srgb = [int(swatch[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    rgb = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in srgb]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*rgb, 1)
    shader = mat.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    return mat


wall = material("terrace_bluegrey_render", "829398", .76)
trim = material("terrace_pale_frame", "C5CABF", .53)
roof = material("terrace_bluegrey_roof", "526B7B", .80)


def prism(name, footprint, bottom, top, mat):
    """Extrude a documented Godot X/Z footprint as a watertight Blender solid."""
    count = len(footprint)
    verts = [(x, -z, y) for y in (bottom, top) for x, z in footprint]
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    faces.extend((i, (i + 1) % count, (i + 1) % count + count, i + count)
                 for i in range(count))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(mat)
    parts.append(obj)
    return obj


# Footprints use Godot X/Z. No cap/eave projects across a mating plane.
CAPS = {
    "straight": {
        "slab": [(-3, -6), (3, -6), (3, 6), (-3, 6)],
        "field": [(-3, -5.76), (3, -5.76), (3, 5.76), (-3, 5.76)],
        "rims": [[(-3, -6), (3, -6), (3, -5.76), (-3, -5.76)],
                 [(-3, 5.76), (3, 5.76), (3, 6), (-3, 6)]],
    },
    "end": {
        "slab": [(-.12, -6), (.12, -6), (.12, 6), (-.12, 6)],
        "field": None,
        "rims": [[(-.12, -6), (.12, -6), (.12, 6), (-.12, 6)]],
    },
    "outside": {
        "slab": [(-6, -6), (6, -6), (6, 6), (-6, 6)],
        "field": [(-5.76, -5.76), (6, -5.76), (6, 5.76),
                  (5.76, 5.76), (5.76, 6), (-5.76, 6)],
        "rims": [[(-6, -6), (6, -6), (6, -5.76), (-5.76, -5.76),
                  (-5.76, 6), (-6, 6)],
                 [(5.76, 5.76), (6, 5.76), (6, 6), (5.76, 6)]],
    },
    "inside": {
        "slab": [(-9, -9), (9, -9), (9, 3), (3, 3), (3, 9), (-9, 9)],
        "field": [(-8.76, -8.76), (9, -8.76), (9, 2.76),
                  (2.76, 2.76), (2.76, 9), (-8.76, 9)],
        "rims": [[(-9, -9), (9, -9), (9, -8.76), (-8.76, -8.76),
                  (-8.76, 9), (-9, 9)],
                 [(2.76, 2.76), (9, 2.76), (9, 3), (3, 3), (3, 9), (2.76, 9)]],
    },
}
roots = {}
for variant, spec in CAPS.items():
    collection = bpy.data.collections.new(f"export_{NID}_{variant}")
    scene.collection.children.link(collection)
    parts = []
    prism("Roof_slab", spec["slab"], STOREY_HEIGHT, 3.40, wall)
    if spec["field"]:
        prism("Recessed_roof_field", spec["field"], 3.40, 3.42, roof)
    for index, footprint in enumerate(spec["rims"]):
        prism(f"Continuous_coping_{index}", footprint, 3.40, 3.52, trim)
    bpy.ops.object.select_all(action="DESELECT")
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    model = bpy.context.object
    name = "D03ApartmentFamily10" + variant.title()
    model.name = name + "_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    old_slots = list(model.data.materials)
    ordered = [wall, trim] if variant == "end" else [wall, trim, roof]
    indices = [ordered.index(old_slots[face.material_index]) for face in model.data.polygons]
    model.data.materials.clear()
    for mat in ordered:
        model.data.materials.append(mat)
    for face, index in zip(model.data.polygons, indices):
        face.material_index = index
    root = bpy.data.objects.new(name, None)
    collection.objects.link(root)
    model.parent = root
    root["asset_id"] = "d03_apartment_family.10"
    root["provenance"] = "Original Blender construction; no external geometry or textures"
    root["interface"] = "Ground reference pivot; roof underside 3.2m; 6m pitch / 12m depth"
    root["state"] = "Overhead-only inaccessible flat roof; no roof gameplay or collision"
    roots[variant] = root

# Studio is excluded from all named export collections.
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.24, .29, .37, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .65
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.025))
ground = bpy.context.object
ground.name = "STUDIO_ground"
ground.data.materials.append(material("STUDIO_slate", "667783", .8))
bpy.ops.mesh.primitive_cube_add(size=1, location=(25, 0, .5))
reference = bpy.context.object
reference.name = "STUDIO_one_metre_reference"
reference.hide_render = True


def aim(obj, target):
    """Aim studio cameras/lights without changing exported transforms."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


for name, location, power, size in [("key", (-12, 18, 25), 10000, 18),
                                   ("fill", (18, 12, 20), 8500, 16),
                                   ("rim", (-4, -18, 25), 9000, 16)]:
    data = bpy.data.lights.new("STUDIO_" + name, "AREA")
    data.energy, data.size = power, size
    light = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(light)
    light.location = location
    aim(light, (0, 0, 1.5))
data = bpy.data.cameras.new("STUDIO_camera")
camera = bpy.data.objects.new(data.name, data)
scene.collection.objects.link(camera)
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.compression = 95
scene.render.dither_intensity = 0
scene.view_settings.view_transform = "AgX"
data.type, data.ortho_scale = "ORTHO", 55
camera.location = (-30, 42, 35)
aim(camera, (0, 0, 1.6))
SOURCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
runpy.run_path(str(Path(__file__).with_name("export.py")), run_name="__main__")
# Evidence-only display offsets and unchanged sibling context never enter the saved source.
# Three completed roof samples: straight with two end caps, outside and inside elbows.
roots["straight"].location = (-18, 0, 0)
roots["end"].location = (-14.88, 0, 0)
roots["outside"].location = (-5, 0, 0)
roots["inside"].location = (13, 0, 0)
end_copy = bpy.data.objects.new("EVIDENCE_west_end", None)
scene.collection.objects.link(end_copy)
end_copy.instance_type = "COLLECTION"
end_copy.instance_collection = bpy.data.collections[f"export_{NID}_end"]
# The original collection root already has a display offset; compensate for this instance.
end_copy.location = (-6.24, 0, 0)


def context(sibling, variant, location):
    """Append unchanged sibling geometry as render-only mounting context after saving."""
    source = ROOT / f"art/source/models/environment/{sibling}/{sibling}.blend"
    collection_name = f"export_{sibling}" + ("_" + variant if variant else "")
    with bpy.data.libraries.load(str(source), link=False) as (available, loaded):
        loaded.collections = [collection_name]
    item = bpy.data.objects.new("EVIDENCE_" + sibling + variant, None)
    scene.collection.objects.link(item)
    item.instance_type = "COLLECTION"
    item.instance_collection = loaded.collections[0]
    item.location = location
    return item


contexts = [context("d03_apartment_family_05", "", (-18, 0, 0)),
            context("d03_apartment_family_07", "", (-14.88, 0, 0)),
            context("d03_apartment_family_07", "", (-21.12, 0, 0)),
            context("d03_apartment_family_06", "outside", (-5, 0, 0)),
            context("d03_apartment_family_06", "inside", (13, 0, 0))]
contexts[2].rotation_euler.z = math.pi
for name, location, target, scale in [
    ("hero", (-32, 48, 42), (0, 0, 1.8), 57),
    ("side", (30, -48, 34), (0, 0, 1.8), 57),
    ("roof_detail", (-10, 13, 13), (-15, 0, 3.35), 14),
]:
    camera.location = location
    aim(camera, target)
    data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / (name + ".png"))
    bpy.ops.render.render(write_still=True)
camera.location = (0, 0, 47)
camera.rotation_euler = (0, 0, 0)
data.type = "PERSP"
data.sensor_fit = "VERTICAL"
data.angle = math.radians(42)
scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
bpy.ops.render.render(write_still=True)
