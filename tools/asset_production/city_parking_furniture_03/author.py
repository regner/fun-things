"""Author the original cycle hoop in Blender, retaining an editable source and lean renders."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_parking_furniture_03"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
TUBE_RADIUS_M = .04
LEG_CENTRE_X_M = .44
BEND_RADIUS_M = .14
BEND_CENTRE_HEIGHT_M = .72
TUBE_SIDES = 16
BEND_SEGMENTS = 8


def material(name, rgb, metallic, roughness):
    """Use the family's plain opaque petrol/amber Principled palette."""
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
    """Point an isolated studio camera or light at a measured inspection target."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def hoop(collection, materials):
    """Sweep one capped circular tube through two tangent quarter-circle shoulders."""
    # Each path point carries an exact tangent, keeping the bends circular and smooth.
    path = [(-LEG_CENTRE_X_M, .02, 0.0, 1.0)]
    for i in range(BEND_SEGMENTS + 1):
        angle = math.pi - i * math.pi / (2 * BEND_SEGMENTS)
        path.append((-.30 + BEND_RADIUS_M * math.cos(angle),
                     BEND_CENTRE_HEIGHT_M + BEND_RADIUS_M * math.sin(angle),
                     math.sin(angle), -math.cos(angle)))
    # Flush material bands use real section stations, not floating decal geometry.
    path.extend((x, .86, 1.0, 0.0) for x in (-.22, -.12, .12, .22))
    for i in range(BEND_SEGMENTS + 1):
        angle = math.pi / 2 - i * math.pi / (2 * BEND_SEGMENTS)
        path.append((.30 + BEND_RADIUS_M * math.cos(angle),
                     BEND_CENTRE_HEIGHT_M + BEND_RADIUS_M * math.sin(angle),
                     math.sin(angle), -math.cos(angle)))
    path.append((LEG_CENTRE_X_M, .02, 0.0, -1.0))
    vertices = []
    for x, z, tx, tz in path:
        for i in range(TUBE_SIDES):
            angle = i * 2 * math.pi / TUBE_SIDES
            vertices.append((x - tz * TUBE_RADIUS_M * math.sin(angle),
                             TUBE_RADIUS_M * math.cos(angle),
                             z + tx * TUBE_RADIUS_M * math.sin(angle)))
    faces = [tuple(reversed(range(TUBE_SIDES)))]
    slots = [0]
    for station in range(len(path) - 1):
        midpoint_x = (path[station][0] + path[station + 1][0]) / 2
        is_band = .12 < abs(midpoint_x) < .22
        for side in range(TUBE_SIDES):
            a = station * TUBE_SIDES + side
            b = station * TUBE_SIDES + (side + 1) % TUBE_SIDES
            faces.append((a, b, b + TUBE_SIDES, a + TUBE_SIDES))
            slots.append(int(is_band))
    faces.append(tuple(range((len(path) - 1) * TUBE_SIDES, len(vertices))))
    slots.append(0)
    mesh = bpy.data.meshes.new("CycleHoop_Geometry")
    mesh.from_pydata(vertices, [], faces)
    for mat in materials:
        mesh.materials.append(mat)
    mesh.update()
    for polygon, slot in zip(mesh.polygons, slots):
        polygon.material_index = slot
        polygon.use_smooth = polygon.index not in (0, len(mesh.polygons) - 1)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("Continuous cycle hoop", mesh)
    collection.objects.link(obj)
    return obj


def mounting_shoe(collection, x, mat):
    """Create a low rounded ground-contact shoe without bolt-scale visual clutter."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, .0125))
    obj = bpy.context.object
    obj.name = "Ground mounting shoe"
    obj.dimensions = (.16, .18, .025)
    for source_collection in list(obj.users_collection):
        source_collection.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bevel = obj.modifiers.new("Rounded cast edges", "BEVEL")
    bevel.width = .009
    bevel.segments = 3
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    weighted = obj.modifiers.new("Broad face normals", "WEIGHTED_NORMAL")
    weighted.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=weighted.name)
    return obj


def studio(scene):
    """Prepare isolated evidence lights and ground outside the export collection."""
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes["Background"]
    background.inputs[0].default_value = (.19, .24, .29, 1)
    background.inputs[1].default_value = .5
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.002))
    floor = bpy.context.object
    floor.name = "STUDIO_ground"
    floor.data.materials.append(material("STUDIO_slate", (.15, .19, .22), 0, .65))
    for name, location, power, size in [
        ("key", (1, 3, 5), 650, 5), ("rim", (-3, -2, 4), 850, 4),
        ("fill", (1, 3, 1.5), 100, 3),
    ]:
        data = bpy.data.lights.new("STUDIO_" + name, "AREA")
        data.energy = power
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(light)
        light.location = location
        aim(light, (0, 0, .45))
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
    camera.location = (1.8, 3.2, 1.8)
    aim(camera, (0, 0, .43))
    data.type = "ORTHO"
    data.ortho_scale = 2.3
    return camera


def main():
    """Build one static mesh with identity transforms, save source, export and render."""
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
    petrol = material("parking_metal_petrol", (.025, .075, .09), .45, .46)
    amber = material("parking_safety_amber", (1.0, .527, .102), 0, .58)
    parts = [hoop(collection, [petrol, amber])]
    parts.extend(mounting_shoe(collection, x, petrol) for x in (-.44, .44))
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = "CityParkingFurniture03_Mesh"
    obj.data.name = "CityParkingFurniture03_Geometry"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new("CityParkingFurniture03", None)
    collection.objects.link(root)
    obj.parent = root
    root["asset_id"] = "city_parking_furniture.03"
    root["authorship"] = "Original Blender construction by commissioned production specialist"
    root["ground_datum_m"] = 0.0
    root["front_axis"] = "Symmetric hoop; Blender +Y maps to Godot -Z"
    root["provisional_dimensions_godot_m"] = [1.04, .90, .18]
    camera = studio(scene)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export_script = Path(__file__).parent / "export.py"
    exec(compile(export_script.read_text(), str(export_script), "exec"), {"__file__": __file__})
    for name, location, target, scale in [
        ("hero", (1.8, 3.2, 1.8), (0, 0, .43), 2.3),
        ("side", (0, 4, .6), (0, 0, .45), 2.0),
        ("detail", (1.2, 2.2, 1.6), (.23, 0, .80), .85),
    ]:
        camera.location = location
        aim(camera, target)
        camera.data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location = (0, 0, 47)
    camera.rotation_euler = (0, 0, 0)
    camera.data.type = "PERSP"
    camera.data.sensor_fit = "VERTICAL"
    camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
