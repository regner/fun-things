"""Build the original compact road-sign support and blank artwork carrier in isolated pinned Blender."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_traffic_fixtures_03"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
SEGMENTS = 24
PARTS = []


def material(name, rgb, metallic, roughness):
    """Use the accepted street-light neutral metal family, without textures or emission."""
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


def lathe(name, rings, mat, y=0):
    """Make a capped rotational metal component from a metre-scale profile."""
    verts = [(radius * math.cos(i * math.tau / SEGMENTS),
              y + radius * math.sin(i * math.tau / SEGMENTS), height)
             for height, radius in rings for i in range(SEGMENTS)]
    faces = [tuple(reversed(range(SEGMENTS)))]
    for ring in range(len(rings) - 1):
        for i in range(SEGMENTS):
            a = ring * SEGMENTS + i
            b = ring * SEGMENTS + (i + 1) % SEGMENTS
            faces.append((a, b, b + SEGMENTS, a + SEGMENTS))
    faces.append(tuple(range((len(rings) - 1) * SEGMENTS, len(verts))))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return finish(obj, name, mat)


def box(name, location, size, mat, bevel):
    """Create a shallow service-access detail with softened edges."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = size
    return finish(obj, name, mat, bevel)


def panel(trim, face):
    """Sweep a rounded square into a closed thin plate with a face-only UV/material interface."""
    corner_steps = 6
    center_height = 2.90
    vertices = []
    # Outer back/front edge and a shallow bevel to the inset, smaller artwork plane.
    profiles = [(.350, .045, .080), (.350, .045, .125), (.340, .035, .135)]
    for half, radius, depth in profiles:
        for cx, cz, start in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
            for step in range(corner_steps + 1):
                angle = math.radians(start + step * 90 / corner_steps)
                vertices.append((cx * (half - radius) + radius * math.cos(angle), depth,
                                 center_height + cz * (half - radius) + radius * math.sin(angle)))
    count = 4 * (corner_steps + 1)
    faces = [tuple(reversed(range(count)))]
    for ring in range(len(profiles) - 1):
        for i in range(count):
            a = ring * count + i
            b = ring * count + (i + 1) % count
            faces.append((a, b, b + count, a + count))
    faces.append(tuple(range(2 * count, 3 * count)))
    mesh = bpy.data.meshes.new("Rounded road-sign plate")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(mesh.name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    finish(obj, mesh.name, trim)
    mesh.materials.append(face)
    uv = mesh.uv_layers.new(name="UVMap")
    for polygon in mesh.polygons:
        # The front plane alone receives artwork; sides/back remain neutral metal.
        front = all(abs(mesh.vertices[mesh.loops[i].vertex_index].co.y - .135) < 1e-6
                    for i in polygon.loop_indices)
        if front:
            polygon.material_index = 1
            polygon.use_smooth = False
        for loop in polygon.loop_indices:
            co = mesh.vertices[mesh.loops[loop].vertex_index].co
            uv.data[loop].uv = ((.340 - co.x) / .680, (co.z - 2.560) / .680)
    # Keep the artwork truly planar instead of inheriting weighted bevel-edge normals.
    front_loops = {loop for polygon in mesh.polygons if polygon.material_index == 1
                   for loop in polygon.loop_indices}
    mesh.normals_split_custom_set([(0, 1, 0) if index in front_loops else normal.vector
                                   for index, normal in enumerate(mesh.corner_normals)])
    return obj


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
    face = material("road_sign_face", (.62, .66, .64), 0, .52)
    lathe("Small cast shoe", [(0, .130), (.012, .140), (.045, .140),
                              (.065, .126), (.160, .095), (.190, .070)], petrol)
    lathe("Slim upright", [(.12, .065), (3.20, .065)], petrol)
    lathe("Foot collar", [(.165, .074), (.18, .081), (.205, .081), (.215, .070)], trim)
    lathe("Post cap", [(3.18, .068), (3.21, .068), (3.22, .055)], trim)
    for height in (2.70, 3.10):
        lathe("Rear clamp band", [(height - .05, .070), (height + .05, .070)], trim)
        box("Plate clamp bridge", (0, .055, height), (.20, .10, .09), petrol, .012)
    panel(trim, face)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in PARTS:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = PARTS[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = "CityTrafficFixtures03_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new("CityTrafficFixtures03", None)
    collection.objects.link(root)
    obj.parent = root
    root["asset_id"] = "city_traffic_fixtures.03"
    root["authorship"] = "Original Blender construction by commissioned production specialist"
    root["front_axis"] = "Blender +Y maps to Godot -Z; ground shoe centre pivot"
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes["Background"]
    background.inputs[0].default_value = (.19, .24, .29, 1)
    background.inputs[1].default_value = .5
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.008))
    bpy.context.object.name = "STUDIO_ground"
    bpy.context.object.data.materials.append(material("STUDIO_slate", (.15, .19, .22), 0, .65))
    for name, position, energy, size in [
        ("key", (4, 4, 6), 1100, 5), ("rim", (-4, -3, 5), 1300, 4),
        ("fill", (1, 5, 2), 350, 4),
    ]:
        data = bpy.data.lights.new("STUDIO_" + name, "AREA")
        data.energy, data.size = energy, size
        light = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(light)
        light.location = position
        aim(light, (0, 0, 1.6))
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
    camera.location = (8, 10, 7)
    aim(camera, (0, 0, 1.65))
    data.type, data.ortho_scale = "ORTHO", 6.6
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export = Path(__file__).parent / "export.py"
    exec(compile(export.read_text(), str(export), "exec"), {"__file__": str(export)})
    for name, position, target, scale in [
        ("hero", (8, 10, 7), (0, 0, 1.65), 6.6),
        ("side", (10, -3, 3.8), (0, 0, 1.65), 6.6),
        ("detail", (2, -3, 3.8), (0, .04, 2.88), 1.8),
    ]:
        camera.location = position
        aim(camera, target)
        data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location, camera.rotation_euler = (0, 0, 47), (0, 0, 0)
    data.type, data.sensor_fit = "PERSP", "VERTICAL"
    data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
