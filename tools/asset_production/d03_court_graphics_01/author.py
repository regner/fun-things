"""Construct the original flush annular artwork carrier and a source-linked review studio."""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_court_graphics_01"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
TEXTURE = ROOT / f"art/textures/environment/{NID}/communal_circle_albedo.png"
SEGMENTS = 128
INNER_RADIUS_M = 4.4
OUTER_RADIUS_M = 7.0
LIFT_M = .015


def material(name, hex_color, roughness=.94):
    """Create matte Principled material using explicitly converted sRGB swatches."""
    rgb = [int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    shader = result.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*linear, 1)
    shader.inputs["Roughness"].default_value = roughness
    result.diffuse_color = (*linear, 1)
    return result


def build_motif(scene):
    """Author only an open planar annulus; existing ground owns the open centre and collision."""
    collection = bpy.data.collections.new("export_" + NID)
    scene.collection.children.link(collection)
    root = bpy.data.objects.new("D03CourtGraphics01", None)
    collection.objects.link(root)
    root["asset_id"] = "d03_court_graphics.01"
    root["authorship"] = "Original commissioned Blender carrier and reproducible Pillow artwork"
    root["surface_contract"] = "14 m circle, 8.8 m open centre, 15 mm above external ground"
    vertices = [(r * math.cos(i * math.tau / SEGMENTS),
                 r * math.sin(i * math.tau / SEGMENTS), LIFT_M)
                for r in (INNER_RADIUS_M, OUTER_RADIUS_M) for i in range(SEGMENTS)]
    faces = [(i, i + SEGMENTS, (i + 1) % SEGMENTS + SEGMENTS, (i + 1) % SEGMENTS)
             for i in range(SEGMENTS)]
    data = bpy.data.meshes.new("D03CourtGraphics01_Geometry")
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new("D03CourtGraphics01_Mesh", data)
    collection.objects.link(obj)
    obj.parent = root
    uv = data.uv_layers.new(name="UVMap")
    for loop in data.loops:
        point = data.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = ((point.x + 7) / 14, (point.y + 7) / 14)
    paint = material("communal_circle", "9BA8A2")
    image = paint.node_tree.nodes.new("ShaderNodeTexImage")
    image.name = "CommittedAlbedo"
    image.image = bpy.data.images.load(str(TEXTURE))
    image.image.colorspace_settings.name = "sRGB"
    image.extension = "EXTEND"
    paint.node_tree.links.new(image.outputs["Color"],
                             paint.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    data.materials.append(paint)


def aim(obj, target):
    """Aim review objects only; source root and mesh transforms stay identity."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def linked_context(scene, path, collection_name, placements):
    """Instance existing Blender sources without copying or exporting their geometry."""
    with bpy.data.libraries.load(str(ROOT / path), link=True) as (_, linked):
        linked.collections = [collection_name]
    for name, position, yaw in placements:
        instance = bpy.data.objects.new("STUDIO_" + name, None)
        instance.instance_type = "COLLECTION"
        instance.instance_collection = linked.collections[0]
        instance.location = position
        instance.rotation_euler.z = math.radians(yaw)
        scene.collection.objects.link(instance)


def studio(scene):
    """Make an isolated context with reused benches and people, never new prop geometry."""
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.24, .29, .37, 1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = .7
    bpy.ops.mesh.primitive_plane_add(size=200)
    ground = bpy.context.object
    ground.name = "STUDIO_ground_not_exported"
    ground.data.materials.append(material("STUDIO_quiet_paving", "859591"))
    linked_context(scene, "art/source/models/environment/city_seating_01/city_seating_01.blend",
                   "export_city_seating_01", [
                       ("bench_north", (0, 6.65, 0), 180),
                       ("bench_east", (6.65, 0, 0), 90)])
    linked_context(scene, "art/source/models/characters/coral_courier/coral_courier.blend",
                   "export_coral_courier", [
                       ("person_centre", (-.6, -.3, 0), -25),
                       ("person_ring", (-4.9, 2.7, 0), 40),
                       ("person_edge", (3.2, -5.6, 0), 10)])
    data = bpy.data.lights.new("STUDIO_sun", "SUN")
    data.energy, data.angle = 2.0, math.radians(18)
    sun = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(20), math.radians(-25), math.radians(-20))
    data = bpy.data.cameras.new("STUDIO_camera")
    camera = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.location = (12, -18, 24)
    aim(camera, (0, 0, 0))
    data.type, data.ortho_scale = "ORTHO", 24
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 95
    scene.render.dither_intensity = 0
    scene.view_settings.view_transform = "AgX"
    return camera


def main():
    """Save editable source with relative dependencies, export and render four bounded views."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    build_motif(scene)
    camera = studio(scene)
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    sys.path.insert(0, str(Path(__file__).parent))
    from export import export_motif
    export_motif(ROOT / f"art/models/environment/{NID}")
    for name, location, target, scale in [
        ("hero", (12, -18, 24), (0, 0, 0), 25),
        ("side", (0, -22, 13), (0, 0, .1), 24),
        ("detail", (-4, -12, 15), (-2, -4.5, 0), 11),
    ]:
        camera.location = location
        aim(camera, target)
        camera.data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / (name + ".png"))
        bpy.ops.render.render(write_still=True)
    camera.location, camera.rotation_euler = (0, 0, 47), (0, 0, 0)
    camera.data.type = "PERSP"
    camera.data.sensor_fit = "VERTICAL"
    camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
