"""Original long dock container: closed corrugated steel, restrained identification faces."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d09_storage_01"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
PARTS = []


def material(name, color, metallic, roughness):
    """Create untextured, opaque steel/paint with stable family material names."""
    result = bpy.data.materials.new(name)
    result.diffuse_color = (*color, 1)
    result.use_nodes = True
    result.use_backface_culling = True
    shader = result.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return result


def finish(obj, name, surface, bevel=.015):
    """Keep each manufactured component closed, bevelled and transform-applied."""
    obj.name = name
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    bpy.data.collections["export_" + ASSET].objects.link(obj)
    obj.data.materials.append(surface)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Soft folded steel edges", "BEVEL")
        modifier.width, modifier.segments = bevel, 2
        modifier.limit_method = "ANGLE"  # Do not bevel coplanar corrugation cap strips.
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    for face in obj.data.polygons:
        face.use_smooth = True
    modifier = obj.modifiers.new("Weighted manufactured normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    PARTS.append(obj)
    return obj


def box(name, location, size, surface, bevel=.015):
    """Author one rounded frame, casting, or closed door component."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = size
    return finish(obj, name, surface, bevel)


def folded_panel(name, length, width, depth, surface, location, rotation):
    """Extrude a closed trapezoidal corrugation profile, with no overlapping rib boxes."""
    count = round(length / .48)
    pitch = length / count
    profile = []
    for rib in range(count):
        for fraction, height in ((0, 0), (.18, 0), (.32, depth), (.68, depth), (.82, 0)):
            profile.append((-length / 2 + (rib + fraction) * pitch, height))
    profile.append((length / 2, 0))
    # Quad strips avoid tessellating a long concave end cap across collinear folds.
    vertices = [(x, y, height) for x, z in profile
                for y, height in ((-width / 2, z), (width / 2, z),
                                  (-width / 2, -.04), (width / 2, -.04))]
    faces = [(0, 1, 3, 2)]
    for i in range(len(profile) - 1):
        a = i * 4
        faces.extend(((a, a + 4, a + 5, a + 1), (a + 2, a + 3, a + 7, a + 6),
                      (a, a + 2, a + 6, a + 4), (a + 1, a + 5, a + 7, a + 3)))
    a = (len(profile) - 1) * 4
    faces.append((a, a + 2, a + 3, a + 1))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.location, obj.rotation_euler = location, rotation
    return finish(obj, name, surface, .008)


def identification_face(side, half_length, amber, frame):
    """Expose only the outward quad as a UV0 artwork slot; all backing stays steel."""
    center_y = half_length - 1.35
    obj = box("Blank identification carrier", (side * 1.212, center_y, 1.96),
              (.036, 1.4, .46), frame, 0)
    obj.data.materials.append(amber)
    uv = obj.data.uv_layers.active
    for polygon in obj.data.polygons:
        if polygon.normal.x * side > .9:
            polygon.material_index = 1
            for loop in polygon.loop_indices:
                vertex = obj.data.vertices[obj.data.loops[loop].vertex_index].co
                # Read left-to-right when viewed from outside either long side.
                uv.data[loop].uv = (.5 + side * vertex.y / 1.4, .5 + vertex.z / .46)
    return obj


def build_container(length=12.0):
    """Author the family cross-section and sealed end language at a declared length."""
    half = length / 2
    blue = material("storage_body_blue", (.055, .135, .235), .25, .48)
    frame = material("storage_frame_slate", (.055, .085, .12), .45, .43)
    steel = material("storage_hardware_steel", (.24, .30, .34), .65, .37)
    amber = material("storage_id_face", (.95, .52, .15), .05, .53)
    # The closed belly removes see-through seams; no interior or independent floor access.
    box("Closed steel belly", (0, 0, 1.29), (2.30, length - .26, 2.34), blue, .02)
    for side in (-1, 1):
        folded_panel("Continuous side corrugation", length - .36, 2.20, .045, blue,
                     (side * 1.16, 0, 1.30), (math.pi / 2, 0, side * math.pi / 2))
        for height in (.10, 2.50):
            box("Long perimeter rail", (side * 1.16, 0, height),
                (.16, length - .36, .18), frame, .024)
        for end in (-1, 1):
            box("Full corner post", (side * 1.15, end * (half - .10), 1.30),
                (.18, .18, 2.56), frame, .025)
            for height in (.12, 2.48):
                box("Corner casting", (side * 1.13, end * (half - .12), height),
                    (.24, .24, .24), steel, .028)
        identification_face(side, half, amber, frame)
    folded_panel("Broad low roof folds", length - .36, 2.22, .045, blue,
                 (0, 0, 2.51), (0, 0, math.pi / 2))
    for end in (-1, 1):
        for height in (.10, 2.50):
            box("End perimeter rail", (0, end * (half - .10), height),
                (2.32, .16, .18), frame, .025)
    # Plain rear wall uses the same folded sheet rhythm as the roof/long sides.
    folded_panel("Rear corrugated end", 2.12, 2.20, .045, blue,
                 (0, -half + .13, 1.30), (math.pi / 2, 0, 0))
    for side in (-1, 1):
        box("Closed door leaf", (side * .539, half - .13, 1.30),
            (1.055, .10, 2.20), blue, .035)
        box("Door perimeter inset", (side * .539, half - .073, 1.30),
            (.91, .018, 1.98), frame, .018)
        box("Door inset steel face", (side * .539, half - .058, 1.30),
            (.85, .018, 1.91), blue, .02)
        for x in (.32, .77):
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=.024, depth=1.98,
                                               location=(side * x, half - .036, 1.30))
            finish(bpy.context.object, "Vertical locking bar", steel, .004)
            for height in (.40, 1.10, 2.20):
                box("Bar keeper", (side * x, half - .024, height),
                    (.09, .044, .075), steel, .008)
            box("Closed latch handle", (side * (x - .055), half - .022, 1.0),
                (.19, .044, .045), steel, .008)
        for height in (.48, 1.30, 2.12):
            box("Door hinge", (side * 1.02, half - .045, height),
                (.15, .09, .10), steel, .013)


def aim(obj, target):
    """Point isolated evidence lighting and cameras, never an exported root."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def studio(scene):
    """Render neutral isolated views; none of this studio is part of the export."""
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.19, .24, .29, 1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = .6
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.016))
    bpy.context.object.name = "STUDIO_ground"
    bpy.context.object.data.materials.append(material("STUDIO_slate", (.15, .19, .22), 0, .65))
    for name, location, energy, size in [
        ("key", (6, 8, 14), 4200, 10), ("rim", (-7, -5, 12), 5500, 9),
        ("fill", (0, 12, 5), 1500, 7),
    ]:
        data = bpy.data.lights.new("STUDIO_" + name, "AREA")
        data.energy, data.shape, data.size = energy, "DISK", size
        obj = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(obj)
        obj.location = location
        aim(obj, (0, 0, 1.3))
    data = bpy.data.cameras.new("STUDIO_camera")
    camera = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 100
    scene.view_settings.view_transform = "AgX"
    camera.location = (16, 17, 11)
    data.type, data.ortho_scale = "ORTHO", 16
    aim(camera, (0, 0, 1.2))
    return camera


def main():
    """Save original source, export explicit GLB and capture four lean review views."""
    assert bpy.app.version_string == "5.2.2 LTS"
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system, scene.unit_settings.scale_length = "METRIC", 1
    collection = bpy.data.collections.new("export_" + ASSET)
    scene.collection.children.link(collection)
    build_container()
    bpy.ops.object.select_all(action="DESELECT")
    for obj in PARTS:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = PARTS[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = "D09Storage01_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new("D09Storage01", None)
    collection.objects.link(root)
    mesh.parent = root
    root["asset_id"] = "d09_storage.01"
    root["authorship"] = "Original Blender construction; commissioned implementation specialist"
    root["axes"] = "Ground-centred; closed doors Blender +Y / Godot -Z"
    root["state"] = "Static intact exterior only; no opening doors, freight or stack simulation"
    camera = studio(scene)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export = Path(__file__).with_name("export.py")
    exec(compile(export.read_text(), str(export), "exec"), {"__file__": str(export)})
    for name, location, target, scale in [
        ("hero", (16, 17, 11), (0, 0, 1.2), 16),
        ("side", (20, 0, 6), (0, 0, 1.3), 14.2),
        ("detail", (6, 14, 5.5), (0, 5.5, 1.35), 5.6),
    ]:
        camera.location = location
        aim(camera, target)
        camera.data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location, camera.rotation_euler = (0, 0, 47), (0, 0, 0)
    camera.data.type, camera.data.sensor_fit = "PERSP", "VERTICAL"
    camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
