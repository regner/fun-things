"""Construct the original flush stepping artwork carrier and a source-linked review studio."""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d03_court_graphics_02"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
TEXTURE = ROOT / f"art/textures/environment/{NID}/play_steps_albedo.png"
CELL_WIDTH_M = .9
CELL_LENGTH_M = .8
CORNER_CUT_M = .08
CELLS = [(0, -2.25), (0, -1.35), (-.5, -.45), (.5, -.45),
         (0, .45), (-.5, 1.35), (.5, 1.35), (0, 2.25)]
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
    """Author eight disconnected flush painted faces; existing paving owns ground and collision."""
    collection = bpy.data.collections.new("export_" + NID)
    scene.collection.children.link(collection)
    root = bpy.data.objects.new("D03CourtGraphics02", None)
    collection.objects.link(root)
    root["asset_id"] = "d03_court_graphics.02"
    root["authorship"] = "Original commissioned Blender carrier and reproducible Pillow artwork"
    root["surface_contract"] = "1.9 x 5.3 m stepping motif, 15 mm above external collision-bearing ground"
    vertices, faces = [], []
    x, y, cut = CELL_WIDTH_M / 2, CELL_LENGTH_M / 2, CORNER_CUT_M
    for cx, cy in CELLS:
        start = len(vertices)
        vertices.extend((cx + dx, cy + dy, LIFT_M) for dx, dy in [
            (-x + cut, -y), (x - cut, -y), (x, -y + cut), (x, y - cut),
            (x - cut, y), (-x + cut, y), (-x, y - cut), (-x, -y + cut)])
        faces.append(tuple(range(start, start + 8)))
    data = bpy.data.meshes.new("D03CourtGraphics02_Geometry")
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new("D03CourtGraphics02_Mesh", data)
    collection.objects.link(obj)
    obj.parent = root
    uv = data.uv_layers.new(name="UVMap")
    for loop in data.loops:
        point = data.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = ((point.x + 1.5) / 3, (point.y + 3) / 6)
    paint = material("play_steps", "587D7C")
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
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-3.5, 0, .5))
    reference = bpy.context.object
    reference.name = "STUDIO_one_metre_reference"
    reference.hide_render = True
    linked_context(scene, "art/source/models/environment/city_seating_01/city_seating_01.blend",
                   "export_city_seating_01", [
                       ("bench_side", (2.7, 1.3, 0), 90)])
    linked_context(scene, "art/source/models/characters/coral_courier/coral_courier.blend",
                   "export_coral_courier", [
                       ("person_on_step", (0, .45, 0), -25),
                       ("person_beside", (1.5, -1.6, 0), 40)])
    data = bpy.data.lights.new("STUDIO_sun", "SUN")
    data.energy, data.angle = 2.0, math.radians(18)
    sun = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(20), math.radians(-25), math.radians(-20))
    data = bpy.data.cameras.new("STUDIO_camera")
    camera = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.location = (7, -10, 15)
    aim(camera, (0, 0, 0))
    data.type, data.ortho_scale = "ORTHO", 12
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
        ("hero", (7, -10, 15), (.4, 0, 0), 12),
        ("side", (8, -6, 8), (.4, 0, .1), 12),
        ("detail", (0, -4, 7), (0, -.8, 0), 5),
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
