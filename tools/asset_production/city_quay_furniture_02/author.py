"""Build the original low-rail spans and three surface-mounted post variants in Blender."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_quay_furniture_02"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
COMPONENTS = ("straight", "corner", "end", "post_quay", "post_deck", "post_landward")
MOUNTS = {"quay": (.30, .30, .06), "deck": (.22, .34, .04), "landward": (.32, .32, .05)}
POSTS = {"straight": [(-1.5, 0), (1.5, 0)],
         "corner": [(-.75, -.75), (.691421356, -.691421356), (.75, .75)],
         "end": [(0, 0)], "post": [(0, 0)]}


def material(name, color, metallic, roughness):
    """Match the preceding mooring bollard's uniform, opaque material language."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*color, 1)
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return result


def hardware(collection, parts, name, location, dimensions, surface, cylinder=False):
    """Make closed, softly bevelled rail hardware with applied transforms."""
    bpy.ops.object.select_all(action="DESELECT")
    if cylinder:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.5, depth=1, location=location)
    else:
        bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    for previous in list(obj.users_collection):
        previous.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(surface)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bevel = obj.modifiers.new("Soft metal edges", "BEVEL")
    bevel.width = min(.009, min(dimensions) / 5)
    bevel.segments = 2
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    normal = obj.modifiers.new("Hardware face normals", "WEIGHTED_NORMAL")
    normal.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=normal.name)
    parts.append(obj)


def tube(collection, parts, name, path, radius, surface, reference):
    """Sweep a closed 16-sided tube; end caps remain inside the receiving post."""
    count = 16
    vertices = []
    for index, point in enumerate(path):
        before = Vector(path[max(0, index - 1)])
        after = Vector(path[min(len(path) - 1, index + 1)])
        tangent = (after - before).normalized()
        across = Vector(reference)
        other = tangent.cross(across).normalized()
        for ring in range(count):
            angle = ring * math.tau / count
            vertices.append(tuple(Vector(point) + radius * (
                math.cos(angle) * across + math.sin(angle) * other)))
    faces = [tuple(reversed(range(count)))]
    for index in range(len(path) - 1):
        for ring in range(count):
            a = index * count + ring
            b = index * count + (ring + 1) % count
            faces.append((a, b, b + count, a + count))
    faces.append(tuple(range((len(path) - 1) * count, len(path) * count)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(surface)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    for polygon in mesh.polygons:
        polygon.use_smooth = len(polygon.vertices) == 4
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    parts.append(obj)


def build_component(component, surfaces):
    """Author one reusable span or mount; no complete-carrier geometry is duplicated."""
    collection = bpy.data.collections.new(f"export_{ASSET}_{component}")
    bpy.context.scene.collection.children.link(collection)
    metal, amber, slate = surfaces
    parts = []
    if component.startswith("post_"):
        mount = component.removeprefix("post_")
        width, depth, height = MOUNTS[mount]
        hardware(collection, parts, "Anchor flange", (0, 0, height / 2),
                 (width, depth, height), metal, mount == "landward")
        hardware(collection, parts, "Upright", (0, 0, .52), (.11, .11, .98), metal)
        hardware(collection, parts, "Base shoe", (0, 0, .115), (.16, .16, .15), slate)
        hardware(collection, parts, "Amber identification collar", (0, 0, .99),
                 (.122, .122, .03), amber)
        hardware(collection, parts, "Capped post", (0, 0, 1.03), (.15, .15, .06), slate)
        # Bolt heads only: coarse hex-free squares remain quiet at gameplay scale.
        anchors = [(x, y) for x in (-width * .32, width * .32)
                   for y in (-depth * .34, depth * .34)]
        if mount == "landward":
            anchors = [(0, -.12), (0, .12), (-.12, 0), (.12, 0)]
        for x, y in anchors:
            hardware(collection, parts, "Anchor head", (x, y, height + .008),
                     (.026, .026, .020), slate)
    elif component == "end":
        # Safe hairpin return joins the upper and lower rails at an access opening.
        path = [(0, 0, .95), (.25, 0, .95)]
        path += [(.25 + .235 * math.sin(i * math.pi / 16), 0,
                  .715 + .235 * math.cos(i * math.pi / 16)) for i in range(1, 17)]
        path.append((0, 0, .48))
        tube(collection, parts, "Continuous terminal return", path, .05, metal, (0, 1, 0))
    else:
        for height, radius in ((.95, .05), (.48, .03)):
            if component == "straight":
                path = [(-1.5, 0, height), (1.5, 0, height)]
            else:
                path = [(-.75, -.75, height), (.55, -.75, height)]
                path += [(.55 + .20 * math.sin(i * math.pi / 16),
                          -.55 - .20 * math.cos(i * math.pi / 16), height)
                         for i in range(1, 9)]
                path.append((.75, .75, height))
            tube(collection, parts, "Handrail" if height > .5 else "Lower rail",
                 path, radius, metal, (0, 0, 1))
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    name = "CityQuayFurniture02_" + component
    mesh.name = name + "_Mesh"
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    for uv_layer in list(mesh.data.uv_layers):
        mesh.data.uv_layers.remove(uv_layer)
    root = bpy.data.objects.new(name, None)
    collection.objects.link(root)
    mesh.parent = root
    root["asset_id"] = "city_quay_furniture.02"
    root["authorship"] = "Original Blender construction; commissioned implementation specialist"
    root["datum"] = "Ground/mounting surface Y=0 in Godot; metre scale"
    root["axes"] = "Blender +Y to Godot -Z, Blender +Z to Godot +Y"
    # Exporters use the explicit collection regardless of render visibility.
    collection.hide_render = True
    return mesh


def aim(obj, target):
    """Point studio cameras and broad lights at the rail display."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def preview(component, position):
    """Link source mesh data into the non-exporting studio, without copying geometry."""
    source = bpy.data.objects["CityQuayFurniture02_" + component + "_Mesh"]
    obj = bpy.data.objects.new("STUDIO_" + component, source.data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = position
    return obj


def main():
    """Save six editable export collections, then make the four lean review views."""
    assert bpy.app.version_string == "5.2.2 LTS"
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    surfaces = [material("quay_dark_metal", (.025, .075, .090), .45, .46),
                material("quay_working_amber", (1, .527, .102), 0, .42),
                material("quay_hardware_slate", (.115, .165, .185), .55, .40)]
    for component in COMPONENTS:
        build_component(component, surfaces)
    # A straight quay run, a deck corner, a landward terminal and three mount samples.
    display = {"straight": [], "corner": [], "end": [], "mounts": []}
    for form, mount, offset in [("straight", "quay", (-.5, -1.4)),
                                ("corner", "deck", (-1.8, 1.0)),
                                ("end", "landward", (1.4, 1.0))]:
        display[form].append(preview(form, (*offset, 0)))
        for x, y in POSTS[form]:
            display[form].append(preview("post_" + mount, (x + offset[0], y + offset[1], 0)))
    for index, mount in enumerate(MOUNTS):
        display["mounts"].append(preview("post_" + mount, (1.0 + index * .60, 2.2, 0)))
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes["Background"]
    background.inputs[0].default_value = (.19, .24, .29, 1)
    background.inputs[1].default_value = .5
    bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, -.002))
    bpy.context.object.name = "STUDIO_ground"
    bpy.context.object.data.materials.append(material("STUDIO_slate", (.15, .19, .22), 0, .65))
    for name, position, energy, size in [("key", (3, -4, 7), 1100, 7),
                                         ("rim", (-4, 3, 6), 1200, 5),
                                         ("fill", (2, 4, 3), 400, 5)]:
        data = bpy.data.lights.new("STUDIO_" + name, "AREA")
        data.energy, data.size = energy, size
        obj = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(obj)
        obj.location = position
        aim(obj, (0, 0, .5))
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
    camera.location = (7, -10, 7)
    aim(camera, (0, .3, .5))
    data.type, data.ortho_scale = "ORTHO", 8
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export_script = Path(__file__).parent / "export.py"
    exec(compile(export_script.read_text(), str(export_script), "exec"), {"__file__": __file__})
    for name, location, target, scale in [
        ("hero", (7, -10, 7), (0, .3, .5), 8),
        ("side", (0, -10, 2.0), (-.5, -1.4, .53), 4.8),
        ("detail", (3.4, 4.2, 2.1), (1.6, 2.2, .52), 2.8),
    ]:
        for group, objects in display.items():
            for obj in objects:
                obj.hide_render = ((name == "side" and group != "straight")
                                   or (name == "detail" and group != "mounts"))
        camera.location = location
        aim(camera, target)
        data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    for objects in display.values():
        for obj in objects:
            obj.hide_render = False
    camera.location = (0, 0, 47)
    camera.rotation_euler = (0, 0, 0)
    data.type, data.sensor_fit, data.angle = "PERSP", "VERTICAL", math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
