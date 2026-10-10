"""Build the original three-lens signal head with a top-centred attachment pivot in isolated pinned Blender."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_traffic_fixtures_02"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
CYLINDER_SEGMENTS = 32
VISOR_SEGMENTS = 16
PARTS = []


def material(name, rgb, metallic, roughness):
    """Use opaque Principled colors without textures, emission or traffic phase logic."""
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


def box(name, location, size, mat, bevel):
    """Create a closed housing or face component with softened edges."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = size
    return finish(obj, name, mat, bevel)


def cylinder(name, location, radius, depth, mat, front=False):
    """Make a capped lens or mounting boss, never an open single-sided disk."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=CYLINDER_SEGMENTS, radius=radius, depth=depth,
                                      location=location)
    obj = bpy.context.object
    if front:
        obj.rotation_euler.x = math.pi / 2
    return finish(obj, name, mat, .006)


def visor(height, mat):
    """Create a closed thick upper half-shell that shades a recessed lens."""
    steps = VISOR_SEGMENTS
    vertices = []
    for y in (.17, .38):
        for radius in (.157, .177):
            for i in range(steps + 1):
                angle = math.pi * i / steps
                vertices.append((radius * math.cos(angle), y,
                                 height + radius * math.sin(angle)))
    n = steps + 1
    faces = []
    for i in range(steps):
        faces.extend([(i, i+1, n+i+1, n+i),
                      (2*n+i, 3*n+i, 3*n+i+1, 2*n+i+1),
                      (i, 2*n+i, 2*n+i+1, i+1),
                      (n+i, n+i+1, 3*n+i+1, 3*n+i)])
    faces.extend([(0, n, 3*n, 2*n), (n-1, 3*n-1, 4*n-1, 2*n-1)])
    mesh = bpy.data.meshes.new("Thick sun visor")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("Thick sun visor", mesh)
    bpy.context.scene.collection.objects.link(obj)
    finish(obj, "Thick sun visor", mat, .003)


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
    box("Rounded housing", (0, 0, -.70), (.44, .32, 1.24), petrol, .045)
    cylinder("Top mounting boss", (0, 0, -.05), .12, .10, trim)
    box("Face frame", (0, .16, -.70), (.50, .04, 1.24), trim, .018)
    box("Recessed face", (0, .185, -.70), (.45, .02, 1.18), recess, .009)
    lenses = [material("signal_red_unlit", (.25, .022, .018), .05, .30),
              material("signal_amber_unlit", (.34, .17, .018), .05, .30),
              material("signal_green_unlit", (.018, .20, .065), .05, .30)]
    for height, lens in zip((-.32, -.70, -1.08), lenses):
        cylinder("Lens rim", (0, .202, height), .151, .028, trim, front=True)
        cylinder("Recessed colored lens", (0, .216, height), .134, .012,
                 lens, front=True)
        visor(height, petrol)
    box("Rear service cover", (0, -.155, -.73), (.32, .01, .92), recess, .004)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in PARTS:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = PARTS[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = "CityTrafficFixtures02_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new("CityTrafficFixtures02", None)
    collection.objects.link(root)
    obj.parent = root
    root["asset_id"] = "city_traffic_fixtures.02"
    root["authorship"] = "Original Blender construction by commissioned production specialist"
    root["front_axis"] = "Blender +Y maps to Godot -Z; top-centred attachment pivot"
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes["Background"]
    background.inputs[0].default_value = (.19, .24, .29, 1)
    background.inputs[1].default_value = .5
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -1.328))
    bpy.context.object.name = "STUDIO_ground"
    bpy.context.object.data.materials.append(material("STUDIO_slate", (.15, .19, .22), 0, .65))
    for name, position, energy, size in [
        ("key", (3, 4, 5), 800, 5), ("rim", (-3, -3, 3), 1100, 4),
        ("fill", (1, 4, 0), 180, 3),
    ]:
        data = bpy.data.lights.new("STUDIO_" + name, "AREA")
        data.energy, data.size = energy, size
        light = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(light)
        light.location = position
        aim(light, (0, 0, -.6))
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
    camera.location = (3, 6, 2)
    aim(camera, (0, .1, -.65))
    data.type, data.ortho_scale = "ORTHO", 2.8
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export = Path(__file__).parent / "export.py"
    exec(compile(export.read_text(), str(export), "exec"), {"__file__": str(export)})
    for name, position, target, scale in [
        ("hero", (3, 6, 2), (0, .1, -.65), 2.8),
        ("side", (6, 0, -.3), (0, .1, -.65), 2.8),
        ("detail", (2, 5, .6), (0, .15, -.32), 1.25),
    ]:
        camera.location = position
        aim(camera, target)
        data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    pole_source = ROOT / "art/source/models/environment/city_traffic_fixtures_01/city_traffic_fixtures_01.blend"
    with bpy.data.libraries.load(str(pole_source), link=False) as (available, requested):
        requested.collections = ["export_city_traffic_fixtures_01"]
    scene.collection.children.link(requested.collections[0])
    root.location = (0, 1.4, 4.2)
    bpy.data.objects["STUDIO_ground"].location.z = -.008
    for name, position, energy in [
        ("key", (4, 4, 8), 1300), ("rim", (-4, -3, 6), 1600),
        ("fill", (1, 5, 2), 350),
    ]:
        light = bpy.data.objects["STUDIO_" + name]
        light.location = position
        light.data.energy = energy
        aim(light, (0, .3, 2.2))
    camera.location, camera.rotation_euler = (0, 0, 47), (0, 0, 0)
    data.type, data.sensor_fit = "PERSP", "VERTICAL"
    data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
