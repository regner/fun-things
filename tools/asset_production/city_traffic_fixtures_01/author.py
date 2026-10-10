"""Build the original signal pole and its mounting datum in isolated pinned Blender."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_traffic_fixtures_01"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
SEGMENTS = 24
PARTS = []


def material(name, rgb, metallic, roughness):
    """Use the accepted street-light neutral metal family, without textures or emission."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*rgb, 1)
    shader = result.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return result


def finish(obj, name, mat, bevel=0):
    """Apply manufactured bevels, weld slivers and retain closed editable components."""
    obj.name = name
    collection = bpy.data.collections["export_" + ASSET]
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
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=0.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    modifier = obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    PARTS.append(obj)
    return obj


def lathe(name, rings, mat, y=0):
    """Make a capped rotational metal component from a metre-scale profile."""
    verts = [(radius * math.cos(i * math.tau / SEGMENTS),
              y + radius * math.sin(i * math.tau / SEGMENTS), height)
             for height, radius in rings for i in range(SEGMENTS)]
    faces = [tuple(reversed(range(SEGMENTS)))]
    for ring in range(len(rings) - 1):
        for i in range(SEGMENTS):
            a = ring * SEGMENTS + i
            b = ring * SEGMENTS + (i + 1) % SEGMENTS
            faces.append((a, b, b + SEGMENTS, a + SEGMENTS))
    faces.append(tuple(range((len(rings) - 1) * SEGMENTS, len(verts))))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return finish(obj, name, mat)


def box(name, location, size, mat, bevel):
    """Create a shallow service-access detail with softened edges."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = size
    return finish(obj, name, mat, bevel)


def arm(mat):
    """Sweep a closed round mast through a quarter elbow into a short horizontal arm."""
    path = [(0, 3.98), (0, 4.13)]
    # Centre (y=.32,z=4.13), radius .32; tangent stays continuous through the elbow.
    for index in range(1, 9):
        angle = index * math.pi / 16
        path.append((.32 - .32 * math.cos(angle), 4.13 + .32 * math.sin(angle)))
    path.extend([(.8, 4.45), (1.40, 4.45)])
    verts = []
    for index, (y, z) in enumerate(path):
        before = Vector((0, *path[max(0, index - 1)]))
        after = Vector((0, *path[min(len(path) - 1, index + 1)]))
        tangent = (after - before).normalized()
        across = Vector((1, 0, 0))
        other = tangent.cross(across)
        for i in range(SEGMENTS):
            angle = i * math.tau / SEGMENTS
            verts.append(tuple(Vector((0, y, z)) + .09 * (
                math.cos(angle) * across + math.sin(angle) * other)))
    faces = [tuple(reversed(range(SEGMENTS)))]
    for ring in range(len(path) - 1):
        for i in range(SEGMENTS):
            a = ring * SEGMENTS + i
            b = ring * SEGMENTS + (i + 1) % SEGMENTS
            faces.append((a, b, b + SEGMENTS, a + SEGMENTS))
    faces.append(tuple(range((len(path) - 1) * SEGMENTS, len(verts))))
    mesh = bpy.data.meshes.new("Swept mast arm")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("Swept mast arm", mesh)
    bpy.context.scene.collection.objects.link(obj)
    finish(obj, "Swept mast arm", mat)


def aim(obj, target):
    """Aim studio objects independently of the export collection."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    """Save the editable production source, explicit export, and four lean review views."""
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
    petrol = material("traffic_dark_metal", (.025, .075, .09), .45, .46)
    trim = material("traffic_fixture_rim", (.07, .13, .15), .50, .42)
    recess = material("traffic_service_recess", (.012, .025, .03), .25, .5)
    lathe("Cast ground shoe", [(0, .205), (.015, .22), (.07, .22),
                              (.10, .205), (.25, .17), (.30, .145)], petrol)
    lathe("Tapered upright", [(.18, .14), (.43, .14), (.60, .11), (4.13, .09)], petrol)
    lathe("Base collar", [(.27, .148), (.285, .156), (.32, .156), (.335, .143)], trim)
    box("Service hatch rim", (0, .12, .78), (.135, .038, .35), recess, .018)
    box("Service hatch cover", (0, .142, .78), (.105, .017, .31), petrol, .012)
    box("Hatch key recess", (0, .153, .86), (.027, .008, .044), recess, .006)
    arm(petrol)
    lathe("Downward head mount", [(4.20, .12), (4.22, .13), (4.27, .13),
                                 (4.29, .10), (4.48, .10), (4.51, .08)], trim, 1.40)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in PARTS:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = PARTS[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = "CityTrafficFixtures01_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new("CityTrafficFixtures01", None)
    collection.objects.link(root)
    obj.parent = root
    root["asset_id"] = "city_traffic_fixtures.01"
    root["authorship"] = "Original Blender construction by commissioned production specialist"
    root["front_axis"] = "Blender +Y maps to Godot -Z; ground shoe centre pivot"
    socket = bpy.data.objects.new("socket_signal_head", None)
    collection.objects.link(socket)
    socket.parent = root
    socket.location = (0, 1.40, 4.20)
    socket.empty_display_type = "ARROWS"
    socket.empty_display_size = .25
    socket["contract"] = "Head top-centre pivot; identity basis; head extends down; front +Y"
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes["Background"]
    background.inputs[0].default_value = (.19, .24, .29, 1)
    background.inputs[1].default_value = .5
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.008))
    bpy.context.object.name = "STUDIO_ground"
    bpy.context.object.data.materials.append(material("STUDIO_slate", (.15, .19, .22), 0, .65))
    for name, position, energy, size in [
        ("key", (4, 4, 8), 1300, 6), ("rim", (-4, -3, 6), 1600, 5),
        ("fill", (1, 5, 2), 350, 4),
    ]:
        data = bpy.data.lights.new("STUDIO_" + name, "AREA")
        data.energy, data.size = energy, size
        light = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(light)
        light.location = position
        aim(light, (0, .3, 2.2))
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
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 100
    scene.view_settings.view_transform = "AgX"
    camera.location = (8, 10, 7)
    aim(camera, (0, .5, 2.25))
    data.type, data.ortho_scale = "ORTHO", 9.2
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export = Path(__file__).parent / "export.py"
    exec(compile(export.read_text(), str(export), "exec"), {"__file__": str(export)})
    for name, position, target, scale in [
        ("hero", (8, 10, 7), (0, .5, 2.25), 9.2),
        ("side", (10, 0, 3.5), (0, .5, 2.25), 9.2),
        ("detail", (3, 4, 5.6), (0, .75, 4.25), 3.1),
    ]:
        camera.location = position
        aim(camera, target)
        data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location, camera.rotation_euler = (0, 0, 47), (0, 0, 0)
    data.type, data.sensor_fit = "PERSP", "VERTICAL"
    data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
