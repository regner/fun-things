"""Construct the original low wheel stop in Blender; export only its named collection."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_parking_furniture_01"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
# Metres, Blender Y/Z section: a low skirt and two tire-facing sloped shoulders.
SECTION = [(-.15, 0), (.15, 0), (.15, .025), (.085, .16), (-.085, .16), (-.15, .025)]
STATIONS = [-.90, -.72, -.42, .42, .72, .90]
BEVEL_M = .008


def material(name, rgb, roughness):
    """Create plain opaque exportable Principled material, without procedural textures."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*rgb, 1)
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Roughness"].default_value = roughness
    return result


def aim(obj, target):
    """Orient a studio camera or broad light toward an inspection target."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def area_light(name, location, power, size):
    """Keep studio lights outside the export collection."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    aim(obj, (0, 0, .08))


def main():
    """Build a closed segmented extrusion with flush safety bands, then export and render."""
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
    body = material("parking_rubber_petrol", (.025, .075, .090), .78)
    amber = material("parking_safety_amber", (1.0, .527, .102), .58)
    vertices = [(x, y, z) for x in STATIONS for y, z in SECTION]
    count = len(SECTION)
    faces = [tuple(reversed(range(count)))]
    slots = [0]
    for station in range(len(STATIONS) - 1):
        for side in range(count):
            a = station * count + side
            b = station * count + (side + 1) % count
            faces.append((a, b, b + count, a + count))
            slots.append(int(station in (1, 3) and side in (2, 3, 4)))
    faces.append(tuple(range((len(STATIONS) - 1) * count, len(vertices))))
    slots.append(0)
    mesh = bpy.data.meshes.new("CityParkingFurniture01_Geometry")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(body)
    mesh.materials.append(amber)
    mesh.update()
    for polygon, slot in zip(mesh.polygons, slots):
        polygon.material_index = slot
    obj = bpy.data.objects.new("CityParkingFurniture01_Mesh", mesh)
    collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    # Only geometric corners bevel: flush bands remain part of the watertight body,
    # avoiding floating plates, z-fighting and decorative collision snag points.
    bevel = obj.modifiers.new("Soft molded edges", "BEVEL")
    bevel.width = BEVEL_M
    bevel.segments = 3
    bevel.limit_method = "ANGLE"
    bevel.angle_limit = .25
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    weighted = obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    weighted.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=weighted.name)
    root = bpy.data.objects.new("CityParkingFurniture01", None)
    collection.objects.link(root)
    obj.parent = root
    root["asset_id"] = "city_parking_furniture.01"
    root["authorship"] = "Original Blender construction by commissioned production specialist"
    root["ground_datum_m"] = 0.0
    root["front_axis"] = "Symmetric tire-facing shoulders; Blender +Y maps to Godot -Z"
    root["provisional_dimensions_godot_m"] = [1.8, .16, .30]
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes["Background"]
    background.inputs[0].default_value = (.19, .24, .29, 1)
    background.inputs[1].default_value = .5
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.002))
    ground = bpy.context.object
    ground.name = "STUDIO_ground"
    ground.data.materials.append(material("STUDIO_slate", (.15, .19, .22), .65))
    area_light("STUDIO_key", (1, 3, 5), 650, 5)
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
    camera.location = (2.3, 3.2, 1.9)
    aim(camera, (0, 0, .08))
    data.type = "ORTHO"
    data.ortho_scale = 2.65
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export_script = Path(__file__).parent / "export.py"
    exec(compile(export_script.read_text(), str(export_script), "exec"), {"__file__": __file__})
    for name, location, target, scale in [
        ("hero", (2.3, 3.2, 1.9), (0, 0, .08), 2.65),
        ("side", (3, 0, .3), (0, 0, .08), .85),
        ("detail", (1.4, 1.9, 1.5), (.59, 0, .09), .95),
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
