"""Author the original cast mooring bollard in Blender; studio objects never export."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_quay_furniture_01"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
SEGMENTS = 40
# Height, X/Y radii, material on the interval above: dark casting=0, amber paint=1.
# The broad oval mushroom head and rope waist distinguish this from a road bollard.
PROFILE = [
    (.070, .245, .225, 0), (.100, .245, .225, 0), (.140, .225, .205, 0),
    (.200, .195, .185, 0), (.500, .180, .170, 0), (.545, .205, .185, 0),
    (.580, .310, .225, 0), (.605, .410, .270, 0), (.640, .444, .287, 0),
    (.670, .450, .290, 0), (.715, .450, .290, 1), (.737, .442, .284, 1),
    (.755, .425, .270, 0), (.775, .370, .235, 0), (.780, .320, .200, 0),
]


def material(name, rgb, metallic, roughness):
    """Make a uniform opaque Principled surface with no texture dependencies."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*rgb, 1)
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return result


def finish_hardware(obj, collection, surface, bevel):
    """Apply small manufactured bevels and normals before joining the static mesh."""
    for previous in list(obj.users_collection):
        previous.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(surface)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    modifier = obj.modifiers.new("Cast edge round", "BEVEL")
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
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    modifier = obj.modifiers.new("Weighted hardware normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    return obj


def aim(obj, target):
    """Aim an isolated studio camera or light at the inspection target."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def area_light(name, position, energy, size):
    """Add broad studio fill outside the declared export collection."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (0, 0, .4))


def main():
    """Save editable original source, export the named collection and render four views."""
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
    metal = material("quay_dark_metal", (.025, .075, .090), .45, .46)
    amber = material("quay_working_amber", (1.0, .527, .102), 0, .42)
    slate = material("quay_hardware_slate", (.115, .165, .185), .55, .40)
    vertices = [(rx * math.cos(i * math.tau / SEGMENTS),
                 ry * math.sin(i * math.tau / SEGMENTS), height)
                for height, rx, ry, _slot in PROFILE for i in range(SEGMENTS)]
    faces = [tuple(reversed(range(SEGMENTS)))]
    slots = [0]
    for ring in range(len(PROFILE) - 1):
        for i in range(SEGMENTS):
            lower = ring * SEGMENTS
            faces.append((lower + i, lower + (i + 1) % SEGMENTS,
                          lower + SEGMENTS + (i + 1) % SEGMENTS, lower + SEGMENTS + i))
            slots.append(PROFILE[ring][3])
    faces.append(tuple(range((len(PROFILE) - 1) * SEGMENTS, len(vertices))))
    slots.append(0)
    mesh = bpy.data.meshes.new("CityQuayFurniture01_Geometry")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(metal)
    mesh.materials.append(amber)
    mesh.update()
    for polygon, slot in zip(mesh.polygons, slots):
        polygon.material_index = slot
        # Smooth the crown into its flat top; only the hidden casting underside is sharp.
        polygon.use_smooth = polygon.index != 0
    casting = bpy.data.objects.new("Oval mushroom casting", mesh)
    collection.objects.link(casting)
    parts = [casting]
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, .04))
    plate = bpy.context.object
    plate.name = "Rounded anchor plate"
    plate.dimensions = (.68, .60, .08)
    parts.append(finish_hardware(plate, collection, metal, .018))
    # Four restrained hex anchors; no threads, labels, ropes or interaction sockets.
    for x in (-.26, .26):
        for y in (-.22, .22):
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=.038, depth=.03,
                                               location=(x, y, .091))
            bolt = bpy.context.object
            bolt.name = "Slate anchor bolt"
            parts.append(finish_hardware(bolt, collection, slate, .004))
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = casting
    bpy.ops.object.join()
    casting.name = "CityQuayFurniture01_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new("CityQuayFurniture01", None)
    collection.objects.link(root)
    casting.parent = root
    root["asset_id"] = "city_quay_furniture.01"
    root["authorship"] = "Original Blender construction by commissioned implementation specialist"
    root["ground_datum_m"] = 0.0
    root["axes"] = "Long head along X; Blender +Y maps to Godot -Z; +Z maps to +Y"
    root["interaction"] = "Static intact fixture; no mooring, climbing or water gameplay"
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes["Background"]
    background.inputs[0].default_value = (.19, .24, .29, 1)
    background.inputs[1].default_value = .5
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.002))
    ground = bpy.context.object
    ground.name = "STUDIO_ground"
    ground.data.materials.append(material("STUDIO_slate", (.15, .19, .22), 0, .65))
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
    camera.location = (2, 3, 1.7)
    aim(camera, (0, 0, .38))
    data.type = "ORTHO"
    data.ortho_scale = 2.25
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export_script = Path(__file__).parent / "export.py"
    exec(compile(export_script.read_text(), str(export_script), "exec"), {"__file__": __file__})
    for name, location, target, scale in [
        ("hero", (2, 3, 1.7), (0, 0, .38), 2.25),
        ("side", (0, 3, .40), (0, 0, .40), 2.10),
        ("detail", (1.4, 2, 2.2), (0, 0, .57), 1.55),
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
