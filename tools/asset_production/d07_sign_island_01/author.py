"""Original Broadlot sign-island plinth; pinned Blender CLI builds source/export/evidence."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d07_sign_island_01"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
SEGMENTS = 96
# (height, radius): one continuous solid, including a shallow manufactured side reveal.
PROFILE = [(0, 2.96), (.04, 3), (.06, 3), (.075, 2.985), (.105, 2.985),
           (.12, 3), (.22, 3), (.26, 2.98), (.28, 2.94), (.28, 2.58)]


def material(name, rgb, metallic=0, roughness=.55):
    """Create an opaque exportable Principled surface without texture dependencies."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*rgb, 1)
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return result


def aim(obj, target):
    """Aim studio optics along their local negative Z axis."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    """Construct the monolithic lathed base and retain four isolated review cameras."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    collection = bpy.data.collections.new("export_" + ASSET)
    scene.collection.children.link(collection)
    slate = material("island_body_slate", (.24, .32, .36), .05, .65)
    petrol = material("island_deck_petrol", (.028, .067, .092), .10, .60)
    lime = material("island_wayfinding_lime", (.48, .72, .16), .0, .50)
    vertices = [(r * math.cos(i * math.tau / SEGMENTS),
                 r * math.sin(i * math.tau / SEGMENTS), z)
                for z, r in PROFILE for i in range(SEGMENTS)]
    faces = [tuple(reversed(range(SEGMENTS)))]
    slots = [0]
    for j in range(len(PROFILE) - 1):
        for i in range(SEGMENTS):
            a = j * SEGMENTS + i
            b = j * SEGMENTS + (i + 1) % SEGMENTS
            faces.append((a, b, b + SEGMENTS, a + SEGMENTS))
            # Eight sectors = 30 degrees, centred toward Blender +Y / Godot -Z.
            accent = j >= 6 and 20 <= i < 28
            slots.append(2 if accent else (1 if 2 <= j <= 4 else 0))
    faces.append(tuple(range((len(PROFILE) - 1) * SEGMENTS, len(vertices))))
    slots.append(1)
    mesh = bpy.data.meshes.new("D07SignIsland01_Geometry")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    for mat in (slate, petrol, lime):
        mesh.materials.append(mat)
    obj = bpy.data.objects.new("D07SignIsland01_Mesh", mesh)
    collection.objects.link(obj)
    for polygon, slot in zip(mesh.polygons, slots):
        polygon.material_index = slot
        polygon.use_smooth = abs(polygon.normal.z) < .99
    # Weighted normals keep the broad horizontal deck flat and the circular wall smooth.
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    modifier = obj.modifiers.new("Broad manufactured normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    root = bpy.data.objects.new("D07SignIsland01", None)
    collection.objects.link(root)
    obj.parent = root
    root["asset_id"] = "d07_sign_island.01"
    root["provenance"] = "Original parametric Blender construction; commissioned production worker"
    root["datum"] = "Ground pivot (0,0,0); flat deck z=0.28m; clear centre radius=2.58m"
    root["front_axis"] = "Blender +Y / Godot -Z; lime sector is front"
    # Studio is intentionally excluded from the declared export collection.
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes["Background"]
    background.inputs[0].default_value = (.14, .19, .25, 1)
    background.inputs[1].default_value = .5
    bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, -.012))
    bpy.context.object.name = "STUDIO_ground"
    bpy.context.object.data.materials.append(material("STUDIO_asphalt", (.055, .075, .09)))
    for name, location, energy, size in [
        ("key", (2, 4, 9), 1700, 7), ("fill", (-5, 1, 6), 900, 6),
        ("rim", (1, -5, 7), 1300, 5),
    ]:
        light = bpy.data.lights.new("STUDIO_" + name, "AREA")
        light.energy, light.shape, light.size = energy, "DISK", size
        item = bpy.data.objects.new(light.name, light)
        scene.collection.objects.link(item)
        item.location = location
        aim(item, (0, 0, 0))
    camera_data = bpy.data.cameras.new("STUDIO_camera")
    camera_data.clip_end = 1000
    camera = bpy.data.objects.new("STUDIO_camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 95
    scene.render.dither_intensity = 0
    scene.view_settings.view_transform = "AgX"
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 8.2
    camera.location = (8, 11, 8)
    aim(camera, (0, 0, .1))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export = Path(__file__).with_name("export.py")
    exec(compile(export.read_text(), str(export), "exec"), {"__file__": str(export)})
    for name, location, target, scale in [
        ("hero", (8, 11, 8), (0, 0, .1), 8.2),
        ("side", (24, 0, 4.22), (0, 0, .14), 7.4),
        ("detail", (3, 6, 2.7), (0, 2.55, .15), 3.4),
    ]:
        camera.location = location
        aim(camera, target)
        camera_data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / (name + ".png"))
        bpy.ops.render.render(write_still=True)
    camera.location = (0, 0, 47)
    camera.rotation_euler = (0, 0, 0)
    camera_data.type = "PERSP"
    camera_data.sensor_fit = "VERTICAL"
    camera_data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
