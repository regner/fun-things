"""Construct the original flush field artwork carrier in the pinned Blender CLI."""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d01_sports_surface_02"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
TEXTURE = ROOT / f"art/textures/environment/{NID}/field_lines_albedo.png"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
DECAL_LIFT_M = .015


def material(name, color, roughness):
    """Create opaque Principled material with explicit linear fallback colour."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    principled = result.node_tree.nodes["Principled BSDF"]
    principled.inputs["Base Color"].default_value = (*color, 1)
    principled.inputs["Roughness"].default_value = roughness
    result.diffuse_color = (*color, 1)
    return result


def aim(obj, target):
    """Aim studio objects only; production model transforms remain identity."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def build_field(scene):
    """Build a single flush transparent paint carrier, not a grass floor or collider."""
    collection = bpy.data.collections.new("export_" + NID)
    scene.collection.children.link(collection)
    root = bpy.data.objects.new("D01SportsSurface02", None)
    collection.objects.link(root)
    root["asset_id"] = "d01_sports_surface.02"
    root["authorship"] = "Original commissioned Blender construction and PIL field artwork"
    root["surface_contract"] = "Flush artwork +0.015 m above external ground; no floor or collision"
    root["provisional_dimensions"] = "52 x 26 m carrier; 50 x 24 m painted boundary"
    vertices = [(-26, -13, DECAL_LIFT_M), (26, -13, DECAL_LIFT_M),
                (26, 13, DECAL_LIFT_M), (-26, 13, DECAL_LIFT_M)]
    faces = [(0, 1, 2, 3)]
    data = bpy.data.meshes.new("D01SportsSurface02_Geometry")
    data.from_pydata(vertices, [], faces)
    data.update()
    mesh = bpy.data.objects.new("D01SportsSurface02_Mesh", data)
    collection.objects.link(mesh)
    mesh.parent = root
    uv = data.uv_layers.new(name="UVMap")
    for polygon in data.polygons:
        for index in polygon.loop_indices:
            point = data.vertices[data.loops[index].vertex_index].co
            uv.data[index].uv = ((point.x + 26) / 52, (point.y + 13) / 26)
    paint = material("field_lines", (.92158, .87962, .71569), .94)
    image = paint.node_tree.nodes.new("ShaderNodeTexImage")
    image.name = "CommittedAlbedo"
    image.image = bpy.data.images.load(str(TEXTURE))
    image.image.colorspace_settings.name = "sRGB"
    image.extension = "EXTEND"
    paint.node_tree.links.new(image.outputs["Color"],
                             paint.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    paint.node_tree.links.new(image.outputs["Alpha"],
                             paint.node_tree.nodes["Principled BSDF"].inputs["Alpha"])
    data.materials.append(paint)


def studio(scene):
    """Provide neutral quiet-green context only; nothing from this studio is exported."""
    world = scene.world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (.22, .27, .32, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = .7
    bpy.ops.mesh.primitive_plane_add(size=400)
    ground = bpy.context.object
    ground.name = "STUDIO_ground_NOT_FIELD_ASSET"
    grass = material("STUDIO_shared_short_grass", (.08, .18, .1), .96)
    image = grass.node_tree.nodes.new("ShaderNodeTexImage")
    image.image = bpy.data.images.load(str(ROOT /
        "art/textures/environment/city_ground_finishes_04/short_grass_albedo.png"))
    coords = grass.node_tree.nodes.new("ShaderNodeTexCoord")
    mapping = grass.node_tree.nodes.new("ShaderNodeVectorMath")
    mapping.operation = "SCALE"
    mapping.inputs[3].default_value = .25
    grass.node_tree.links.new(coords.outputs["Object"], mapping.inputs[0])
    grass.node_tree.links.new(mapping.outputs[0], image.inputs["Vector"])
    grass.node_tree.links.new(image.outputs["Color"],
                             grass.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    ground.data.materials.append(grass)
    data = bpy.data.lights.new("STUDIO_sun", "SUN")
    data.energy = 2.2
    data.angle = math.radians(15)
    sun = bpy.data.objects.new("STUDIO_sun", data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(20), math.radians(-25), math.radians(-20))
    data = bpy.data.cameras.new("STUDIO_camera")
    camera = bpy.data.objects.new("STUDIO_camera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 95
    scene.render.dither_intensity = 0
    scene.view_settings.view_transform = "AgX"
    camera.location = (40, -60, 75)
    aim(camera, (0, 0, 0))
    data.type = "ORTHO"
    data.ortho_scale = 67
    return camera


def main():
    """Save editable source, export its declared collection and render four isolated views."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    build_field(scene)
    camera = studio(scene)
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    sys.path.insert(0, str(Path(__file__).parent))
    from export import export_field
    export_field(ROOT / f"art/models/environment/{NID}")
    for name, location, target, scale in [
        ("hero", (22, -42, 65), (0, 0, 0), 67),
        ("side", (0, -55, 35), (0, 0, 0), 60),
        ("line_detail", (24, -14, 18), (21, 0, 0), 20),
    ]:
        camera.location = location
        aim(camera, target)
        camera.data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    # Entire 52 x 26 m carrier fits the calibrated approximately 64.1 x 36.1 m view.
    camera.location = (0, 0, 47)
    camera.rotation_euler = (0, 0, 0)
    camera.data.type = "PERSP"
    camera.data.sensor_fit = "VERTICAL"
    camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
