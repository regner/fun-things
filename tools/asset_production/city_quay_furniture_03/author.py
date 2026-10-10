"""Author the original non-climbable quay-edge ladder and isolated studio evidence."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_quay_furniture_03"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
RAIL_X = .36
FRONT_Y = .30
RETURN_Y = -.27
BEND_RADIUS = .285
TUBE_RADIUS = .045


def material(name, color, metallic, roughness):
    """Match the delivered quay family's quiet opaque Principled metals and paint."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*color, 1)
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return result


def box(collection, parts, name, location, dimensions, surface, bevel=.008):
    """Create one closed seated hardware shell, with applied soft-edge modifiers."""
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    for previous in list(obj.users_collection):
        previous.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(surface)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    modifier = obj.modifiers.new("Soft manufactured edges", "BEVEL")
    modifier.width, modifier.segments = bevel, 2
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    modifier = obj.modifiers.new("Hardware face normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    parts.append(obj)


def stile(collection, parts, x, metal, amber):
    """Sweep a continuous hooked stile; amber is assigned, not overlaid geometry."""
    path = [(x, FRONT_Y, -2.4), (x, FRONT_Y, .65)]
    path += [(x, .015 + BEND_RADIUS * math.cos(i * math.pi / 16),
              .65 + BEND_RADIUS * math.sin(i * math.pi / 16)) for i in range(1, 17)]
    path += [(x, RETURN_Y, .55), (x, RETURN_Y, .30), (x, RETURN_Y, .04)]
    vertices = []
    count = 16
    for index, point in enumerate(path):
        # Exact circular tangents keep the full bend radius and avoid kinked joins.
        if index <= 1:
            tangent = Vector((0, 0, 1))
        elif index <= 17:
            angle = (index - 1) * math.pi / 16
            tangent = Vector((0, -math.sin(angle), math.cos(angle)))
        else:
            tangent = Vector((0, 0, -1))
        across = Vector((1, 0, 0))
        other = tangent.cross(across).normalized()
        for ring in range(count):
            angle = ring * math.tau / count
            vertices.append(tuple(Vector(point) + TUBE_RADIUS * (
                math.cos(angle) * across + math.sin(angle) * other)))
    faces = [tuple(reversed(range(count)))]
    for index in range(len(path) - 1):
        for ring in range(count):
            a = index * count + ring
            b = index * count + (ring + 1) % count
            faces.append((a, b, b + count, a + count))
    faces.append(tuple(range((len(path) - 1) * count, len(path) * count)))
    mesh = bpy.data.meshes.new("Hooked tubular stile")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(metal)
    mesh.materials.append(amber)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    for polygon in mesh.polygons:
        polygon.use_smooth = len(polygon.vertices) == 4
        # Return grip band between .30 and .55 m, continuous with the dark tube.
        if len(polygon.vertices) == 4:
            coords = [mesh.vertices[v].co for v in polygon.vertices]
            if max(v.y for v in coords) < -.20 and all(.299 < v.z < .551 for v in coords):
                polygon.material_index = 1
    obj = bpy.data.objects.new("Hooked tubular stile", mesh)
    collection.objects.link(obj)
    parts.append(obj)


def aim(obj, target):
    """Point only studio lights and cameras, never the export hierarchy."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    """Save editable metre-scale source, export its collection, and render four views."""
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
    amber = material("quay_working_amber", (1, .527, .102), 0, .42)
    slate = material("quay_hardware_slate", (.115, .165, .185), .55, .40)
    parts = []
    for x in (-RAIL_X, RAIL_X):
        stile(collection, parts, x, metal, amber)
        box(collection, parts, "Quay top anchor plate", (x, RETURN_Y, .03),
            (.22, .24, .06), metal)
        for y in (RETURN_Y - .075, RETURN_Y + .075):
            box(collection, parts, "Deck anchor head", (x, y, .065),
                (.034, .034, .022), slate, .004)
        for height in (-.65, -1.85):
            box(collection, parts, "Wall anchor plate", (x, .02, height),
                (.18, .04, .22), metal)
            box(collection, parts, "Wall stand-off", (x, .165, height),
                (.075, .29, .075), slate)
            for z in (height - .075, height + .075):
                box(collection, parts, "Wall anchor head", (x, .045, z),
                    (.034, .022, .034), slate, .004)
    for index in range(8):
        box(collection, parts, "Broad flat rung", (0, FRONT_Y, -.15 - index * .30),
            (.72, .105, .065), slate, .012)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = "CityQuayFurniture03_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    for uv_layer in list(mesh.data.uv_layers):
        mesh.data.uv_layers.remove(uv_layer)
    root = bpy.data.objects.new("CityQuayFurniture03", None)
    collection.objects.link(root)
    mesh.parent = root
    root["asset_id"] = "city_quay_furniture.03"
    root["authorship"] = "Original Blender construction; commissioned implementation specialist"
    root["datum"] = "Quay top Y=0 / wall Z=0 in Godot; ladder projects toward water -Z"
    root["axes"] = "Blender +Y to Godot -Z, Blender +Z to Godot +Y"
    root["gameplay"] = "Static decorative ladder; no climbing or swimming; not a shore boundary"
    # The ground plane is below the ladder for unobstructed isolated inspection.
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes["Background"]
    background.inputs[0].default_value = (.19, .24, .29, 1)
    background.inputs[1].default_value = .5
    bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, -2.405))
    bpy.context.object.name = "STUDIO_ground_below_ladder"
    studio_floor = material("STUDIO_slate", (.15, .19, .22), 0, 1)
    studio_floor.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0
    bpy.context.object.data.materials.append(studio_floor)
    for name, position, energy, size in [("key", (3, 4, 5), 1100, 7),
                                         ("rim", (-4, -3, 4), 1200, 5),
                                         ("fill", (2, 4, 1.5), 400, 3.5)]:
        data = bpy.data.lights.new("STUDIO_" + name, "AREA")
        data.energy, data.size = energy, size
        obj = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(obj)
        obj.location = position
        obj.visible_camera = False
        aim(obj, (0, 0, -.5))
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
    camera.location = (4, 7, 3)
    aim(camera, (0, 0, -.65))
    data.type, data.ortho_scale = "ORTHO", 6.8
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export_script = Path(__file__).parent / "export.py"
    exec(compile(export_script.read_text(), str(export_script), "exec"), {"__file__": __file__})
    for name, location, target, scale in [
        ("hero", (4, 7, 3), (0, 0, -.65), 6.8),
        ("side", (7, .4, .1), (0, 0, -.70), 6.8),
        ("detail", (2.5, 4, 2.5), (0, 0, .38), 2.7),
    ]:
        camera.location = location
        aim(camera, target)
        data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location = (0, 0, 47)
    camera.rotation_euler = (0, 0, 0)
    data.type, data.sensor_fit, data.angle = "PERSP", "VERTICAL", math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
