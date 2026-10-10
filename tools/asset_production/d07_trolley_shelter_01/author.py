"""Original short trolley shelter, authored with the pinned isolated Blender CLI."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d07_trolley_shelter_01"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
ROOF_HALF_WIDTH = 1.45
ROOF_EDGE_HEIGHT = 2.70
ROOF_RISE = .32
ROOF_THICKNESS = .09
ROOF_SEGMENTS = 16


def material(name, rgb, metallic=0, roughness=.46):
    """Create opaque flat-colour Principled surfaces, with no image dependencies."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*rgb, 1)
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


def finish(obj, collection, mat, bevel=0):
    """Apply manufacture-scale bevels and normals; retain closed editable mesh islands."""
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
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
    for face in obj.data.polygons:
        face.use_smooth = True
    modifier = obj.modifiers.new("Broad face normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    return obj


def box(collection, name, position, size, mat, bevel=.015):
    """Create one closed frame member with applied rotation and scale."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    return finish(obj, collection, mat, bevel)


def roof_strip(collection, name, front, back, mat):
    """Extrude a closed shallow barrel profile along the shelter's depth."""
    profile = []
    for i in range(ROOF_SEGMENTS + 1):
        x = -ROOF_HALF_WIDTH + 2 * ROOF_HALF_WIDTH * i / ROOF_SEGMENTS
        z = ROOF_EDGE_HEIGHT + ROOF_RISE * (1 - (x / ROOF_HALF_WIDTH) ** 2)
        profile.append((x, z))
    outline = profile + [(x, z + ROOF_THICKNESS) for x, z in reversed(profile)]
    count = len(outline)
    vertices = [(x, y, z) for y in (back, front) for x, z in outline]
    faces = [tuple(reversed(range(count))), tuple(range(count, 2 * count))]
    for i in range(count):
        j = (i + 1) % count
        faces.append((i, j, j + count, i + count))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return finish(obj, collection, mat)


def aim(obj, target):
    """Aim only evidence cameras and lights, never exported geometry."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def studio(scene):
    """Use a neutral isolated stage outside the named export collection."""
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes["Background"]
    background.inputs[0].default_value = (.19, .24, .29, 1)
    background.inputs[1].default_value = .5
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.005))
    floor = bpy.context.object
    floor.name = "STUDIO_ground"
    floor.data.materials.append(material("STUDIO_slate", (.15, .19, .22), roughness=.65))
    for name, location, energy, size in [
        ("key", (4, 6, 9), 1500, 7), ("rim", (-4, -3, 6), 1700, 5),
        ("fill", (1, 6, 3), 500, 4),
    ]:
        data = bpy.data.lights.new("STUDIO_" + name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(light)
        light.location = location
        aim(light, (0, 0, 1.4))
    data = bpy.data.cameras.new("STUDIO_camera")
    camera = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.location = (6, 8, 5)
    aim(camera, (0, 0, 1.5))
    data.type = "ORTHO"
    data.ortho_scale = 8.1
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 100
    scene.view_settings.view_transform = "AgX"
    return camera


def main():
    """Build, save, export and render the shelter without trolley or placement geometry."""
    assert bpy.app.version_string == "5.2.2 LTS"
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    collection = bpy.data.collections.new("export_" + ASSET)
    scene.collection.children.link(collection)
    petrol = material("shelter_frame_petrol", (.025, .075, .09), .45)
    pale = material("shelter_roof_ivory", (.76, .82, .78), .12, .52)
    coral = material("shelter_entry_coral", (1.0, .168, .11), .1, .48)
    parts = []
    for x in (-1.24, 1.24):
        # Low continuous skids and guard rails make the side collision legible.
        parts.append(box(collection, "Side skid", (x, 0, .075), (.22, 3.16, .15), petrol))
        for y in (-1.47, 1.47):
            parts.append(box(collection, "Upright", (x, y, 1.39), (.14, .14, 2.68), petrol))
        for z in (.57, 1.10):
            parts.append(box(collection, "Side trolley guard", (x, 0, z), (.12, 3.08, .12), petrol))
        parts.append(box(collection, "Side eave beam", (x, 0, 2.68), (.16, 3.18, .14), petrol))
        parts.append(box(collection, "Entry colour collar", (x, 1.47, 1.19), (.15, .15, .18), coral))
    for z in (.075, .57, 1.10):
        parts.append(box(collection, "Rear trolley stop", (0, -1.47, z),
                         (2.48, .14, .15 if z == .075 else .12), petrol))
    parts.append(roof_strip(collection, "Pale barrel canopy", 1.68, -1.68, pale))
    parts.append(roof_strip(collection, "Front canopy rim", 1.80, 1.68, petrol))
    parts.append(roof_strip(collection, "Rear canopy rim", -1.68, -1.80, petrol))
    # No signs, glazing, bolts, seating or faux trolley geometry: the other records own trolleys.
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = "D07TrolleyShelter01_Mesh"
    obj.data.name = "D07TrolleyShelter01_Geometry"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new("D07TrolleyShelter01", None)
    collection.objects.link(root)
    obj.parent = root
    root["asset_id"] = "d07_trolley_shelter.01"
    root["authorship"] = "Original Blender construction by commissioned production specialist"
    root["front_axis"] = "Open entry Blender +Y maps to Godot -Z"
    root["ground_datum_m"] = 0.0
    root["provisional_dimensions_godot_m"] = [2.9, 3.11, 3.6]
    camera = studio(scene)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export_script = Path(__file__).parent / "export.py"
    exec(compile(export_script.read_text(), str(export_script), "exec"), {"__file__": __file__})
    for name, position, target, scale in [
        ("hero", (6, 8, 5), (0, 0, 1.5), 8.1),
        ("side", (8, 0, 3.6), (0, 0, 1.5), 7.0),
        ("detail", (4, 5, 3.8), (1.18, 1.40, 2.2), 3.1),
    ]:
        camera.location = position
        aim(camera, target)
        camera.data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location = (0, 0, 47)
    camera.rotation_euler = (0, 0, 0)
    camera.data.type = "PERSP"
    camera.data.sensor_fit = "VERTICAL"
    camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
