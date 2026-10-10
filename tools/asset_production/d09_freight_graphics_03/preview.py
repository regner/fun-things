"""Isolated Blender previews of original artwork on unchanged shared sign sources; never save."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d09_freight_graphics_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
assert bpy.app.version_string == "5.2.2 LTS"


def aim(obj, target):
    """Aim a studio camera or light along its negative Z axis."""
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z", "Y").to_euler()


def attach_artwork(mesh_name, variant):
    """Change only the front slot in transient memory, never a source or exported material."""
    material = bpy.data.materials.new(f"loading_{variant}_preview")
    material.use_nodes = True
    material.use_backface_culling = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = .62
    texture = material.node_tree.nodes.new("ShaderNodeTexImage")
    texture.image = bpy.data.images.load(
        str(ROOT / f"art/textures/environment/{NID}/loading_{variant}_albedo.png"))
    texture.extension = "EXTEND"
    material.node_tree.links.new(texture.outputs["Color"], bsdf.inputs["Base Color"])
    bpy.data.objects[mesh_name].data.materials[0] = material


def studio(number):
    """Open one original carrier read-only and configure bounded evidence lighting/rendering."""
    carrier = f"city_sign_supports_{number:02d}"
    source = ROOT / f"art/source/models/environment/{carrier}/{carrier}.blend"
    bpy.ops.wm.open_mainfile(filepath=str(source))
    scene = bpy.context.scene
    collection = bpy.data.collections[f"export_{carrier}"]
    for obj in list(bpy.data.objects):
        if obj.name not in collection.all_objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    world = bpy.data.worlds.new("Freight loading evidence world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (.14, .18, .22, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = .8
    scene.world = world
    for name, location, energy, size in [
        ("key", (-3, 4, 6), 750, 5), ("fill", (4, 2, 2), 450, 4)
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = location
        aim(light, (0, 0, .5))
    data = bpy.data.cameras.new("Freight loading evidence camera")
    camera = bpy.data.objects.new("Freight loading evidence camera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.compression = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    return scene, camera


def render(scene, camera, name, location, target, scale):
    """Render a fixed useful close view without scaling, tilting or duplicating carrier geometry."""
    camera.location = location
    aim(camera, target)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = scale
    scene.render.filepath = str(EVIDENCE / f"{name}.png")
    bpy.ops.render.render(write_still=True)


def main():
    """Produce wall hero/detail, complete low sign side and both carriers at gameplay distance."""
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    scene, camera = studio(1)
    attach_artwork("artwork_carrier", "wall")
    render(scene, camera, "hero", (-.65, 4, 1.0), (0, 0, 0), 2.3)
    render(scene, camera, "detail", (.36, 3, .36), (.28, .088, -.12), 1.18)
    scene, camera = studio(2)
    attach_artwork("CitySignSupports02_ArtworkCarrier", "low")
    render(scene, camera, "side", (2.1, 4, 1.95), (0, 0, .675), 3.0)
    # Load only the existing wall export collection for the side-by-side overhead proof.
    wall = ROOT / "art/source/models/environment/city_sign_supports_01/city_sign_supports_01.blend"
    with bpy.data.libraries.load(str(wall), link=False) as (available, loaded):
        loaded.collections = ["export_city_sign_supports_01"]
    scene.collection.children.link(loaded.collections[0])
    attach_artwork("artwork_carrier", "wall")
    bpy.data.objects["CitySignSupports01"].location = (-1.5, 0, 1.6)
    bpy.data.objects["CitySignSupports02"].location = (1.5, 0, 0)
    camera.location = (0, 8, 47)
    camera.rotation_euler = (0, 0, 0)
    camera.data.type = "PERSP"
    camera.data.sensor_fit = "VERTICAL"
    camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)
    print("LOADING_PREVIEW_PASS: four 1280x720 renders; both shared sources never saved")


if __name__ == "__main__":
    main()
