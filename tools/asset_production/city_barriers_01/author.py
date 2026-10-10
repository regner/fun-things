"""Author the original short bollard in pinned Blender; studio objects never export."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_barriers_01"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
# Metres: ground shoe, gently tapered shaft, rolled amber shoulder, shallow dark cap.
# Each interval takes its material from the lower ring: 0 metal, 1 safety amber.
PROFILE = [
    (0.000, 0.170, 0), (0.008, 0.180, 0), (0.045, 0.180, 0),
    (0.060, 0.173, 0), (0.100, 0.155, 0), (0.140, 0.150, 0),
    (0.710, 0.145, 0), (0.728, 0.158, 0), (0.740, 0.160, 1),
    (0.840, 0.160, 1), (0.865, 0.150, 1), (0.880, 0.135, 0),
    (0.894, 0.120, 0), (0.900, 0.105, 0),
]
SEGMENTS = 32


def material(name, rgb, metallic, roughness):
    """Use exportable opaque Principled surfaces without external dependencies."""
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
    """Point a studio camera/light at a fixed inspection target."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def area_light(name, position, energy, size):
    """Add broad studio fill outside the export collection."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (0, 0, 0.4))


def main():
    """Build editable closed topology, save the source, export and render four views."""
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
    metal = material("barrier_dark_metal", (0.025, 0.075, 0.090), 0.45, 0.46)
    amber = material("barrier_safety_amber", (1.0, 0.527, 0.102), 0.0, 0.42)
    vertices = [(radius * math.cos(i * math.tau / SEGMENTS),
                 radius * math.sin(i * math.tau / SEGMENTS), height)
                for height, radius, _slot in PROFILE for i in range(SEGMENTS)]
    faces = [tuple(reversed(range(SEGMENTS)))]
    slots = [0]
    for ring in range(len(PROFILE) - 1):
        for i in range(SEGMENTS):
            lower = ring * SEGMENTS
            faces.append((lower + i, lower + (i + 1) % SEGMENTS,
                          lower + SEGMENTS + (i + 1) % SEGMENTS, lower + SEGMENTS + i))
            slots.append(PROFILE[ring][2])
    faces.append(tuple(range((len(PROFILE) - 1) * SEGMENTS, len(vertices))))
    slots.append(0)
    mesh = bpy.data.meshes.new("CityBarriers01_Geometry")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(metal)
    mesh.materials.append(amber)
    mesh.update()
    for polygon, slot in zip(mesh.polygons, slots):
        polygon.material_index = slot
        polygon.use_smooth = len(polygon.vertices) == 4
    obj = bpy.data.objects.new("CityBarriers01_Mesh", mesh)
    collection.objects.link(obj)
    root = bpy.data.objects.new("CityBarriers01", None)
    collection.objects.link(root)
    obj.parent = root
    root["asset_id"] = "city_barriers.01"
    root["authorship"] = "Original Blender construction by commissioned production specialist"
    root["ground_datum_m"] = 0.0
    root["front_axis"] = "Rotationally symmetric; Blender +Y maps to Godot -Z"
    # Continuous watertight rings avoid overlapping shells, bevel slivers and hidden caps.
    # No UV map is needed: both surfaces are uniform opaque colors.
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes["Background"]
    background.inputs[0].default_value = (0.19, 0.24, 0.29, 1)
    background.inputs[1].default_value = 0.5
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.002))
    ground = bpy.context.object
    ground.name = "STUDIO_ground"
    ground.data.materials.append(material("STUDIO_slate", (0.15, 0.19, 0.22), 0, 0.65))
    area_light("STUDIO_key", (3, 4, 6), 650, 5)
    area_light("STUDIO_rim", (-3, -2, 4), 850, 4)
    area_light("STUDIO_fill", (1, 3, 1.5), 100, 3)
    data = bpy.data.cameras.new("STUDIO_camera")
    camera = bpy.data.objects.new("STUDIO_camera", data)
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
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 100
    scene.view_settings.view_transform = "AgX"
    camera.location = (2, 3, 1.8)
    aim(camera, (0, 0, 0.44))
    data.type = "ORTHO"
    data.ortho_scale = 2.35
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    exec(compile((Path(__file__).parent / "export.py").read_text(),
                 str(Path(__file__).parent / "export.py"), "exec"), {"__file__": __file__})
    for name, location, target, scale in [
        ("hero", (2, 3, 1.8), (0, 0, 0.44), 2.35),
        ("side", (3, 0, 0.45), (0, 0, 0.45), 2.2),
        ("detail", (1.2, 1.8, 1.7), (0, 0, 0.79), 0.90),
    ]:
        camera.location = location
        aim(camera, target)
        data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location = (0, 0, 47)
    camera.rotation_euler = (0, 0, 0)
    data.type = "PERSP"
    data.sensor_fit = "VERTICAL"
    data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
