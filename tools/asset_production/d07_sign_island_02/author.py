"""Original low Broadlot directory support; run only in isolated pinned Blender CLI."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d07_sign_island_02"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
FACE_WIDTH = 3.84
FACE_HEIGHT = 1.84
FACE_BOTTOM = .50


def material(name, rgb, metallic=0, roughness=.55):
    """Create an opaque Principled material matching the delivered island palette."""
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
    """Aim studio optics along negative local Z without export-axis corrections."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def finish(obj, collection, materials, slot, bevel=0):
    """Apply static transforms and soft manufactured edges, retaining closed topology."""
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    for mat in materials:
        obj.data.materials.append(mat)
    for face in obj.data.polygons:
        face.material_index = slot
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Soft manufactured edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        modifier.limit_method = "ANGLE"
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    for face in obj.data.polygons:
        face.use_smooth = True
    modifier = obj.modifiers.new("Weighted broad planes", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    return obj


def box(name, centre, dimensions, collection, materials, slot, bevel):
    """Make one editable closed box component in metre units."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=centre)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    return finish(obj, collection, materials, slot, bevel)


def main():
    """Build a squat monolith, UV artwork face and flush lime cap in one linked export."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    collection = bpy.data.collections.new("export_" + ASSET)
    scene.collection.children.link(collection)
    materials = [
        material("sign_island_artwork_face", (.028, .067, .092), .10, .60),
        material("island_body_slate", (.24, .32, .36), .05, .65),
        material("island_deck_petrol", (.028, .067, .092), .10, .60),
        material("island_wayfinding_lime", (.48, .72, .16), 0, .50),
    ]
    parts = [
        box("Low mounting shoe", (0, 0, .12), (4.4, .8, .24),
            collection, materials, 2, .06),
        box("Broad quiet casing", (0, 0, 1.37), (4.2, .56, 2.26),
            collection, materials, 1, .06),
    ]
    # Longitudinal cap divisions permit a flush colour sector without overlay z-fighting.
    xs = [-2.1, 1.14, 1.8, 2.1]
    vertices = [(x, y, z) for x in xs for y, z in
                [(-.3, 2.5), (.3, 2.5), (.3, 2.6), (-.3, 2.6)]]
    faces = [(3, 2, 1, 0)]
    for section in range(3):
        for edge in range(4):
            a = section * 4 + edge
            b = section * 4 + (edge + 1) % 4
            faces.append((a, b, b + 4, a + 4))
    faces.append((12, 13, 14, 15))
    mesh = bpy.data.meshes.new("Flush divided cap")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    cap = bpy.data.objects.new("Quiet cap with lime sector", mesh)
    collection.objects.link(cap)
    cap = finish(cap, collection, materials, 2, .025)
    # Material only: the main upper face between x=1.14 and 1.80 becomes lime.
    for polygon in cap.data.polygons:
        if polygon.normal.z > .99 and 1.14 < polygon.center.x < 1.8:
            polygon.material_index = 3
    parts.append(cap)
    panel = box("Replaceable front artwork carrier", (0, .282, 1.42),
                (FACE_WIDTH, .016, FACE_HEIGHT), collection, materials, 2, 0)
    # Exactly one rectangular front quad owns slot 0. Sides/rear never receive artwork.
    uv = panel.data.uv_layers.active
    for face in panel.data.polygons:
        if face.normal.y > .99:
            face.material_index = 0
            for loop_index in face.loop_indices:
                vertex = panel.data.vertices[panel.data.loops[loop_index].vertex_index].co
                uv.data[loop_index].uv = (.5 - vertex.x / FACE_WIDTH,
                                          vertex.z / FACE_HEIGHT + .5)
    parts.append(panel)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = "D07SignIsland02_Mesh"
    obj.data.name = "D07SignIsland02_Geometry"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new("D07SignIsland02", None)
    collection.objects.link(root)
    obj.parent = root
    root["asset_id"] = "d07_sign_island.02"
    root["provenance"] = "Original parametric Blender construction; commissioned worker"
    root["datum"] = "Mount at island-base Y=0.28m; foot radius 2.2361m fits clear radius 2.58m"
    root["front_axis"] = "Blender +Y maps once to Godot -Z"
    root["artwork"] = "Slot0 front only, 3.84x1.84m; UV(0,0) bottom-left from front"
    # Studio only: no shared sources or live sessions are modified.
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
        aim(item, (0, 0, 1.3))
    data = bpy.data.cameras.new("STUDIO_camera")
    data.clip_end = 1000
    camera = bpy.data.objects.new("STUDIO_camera", data)
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
    data.type = "ORTHO"
    data.ortho_scale = 7.5
    camera.location = (8, 12, 7)
    aim(camera, (0, 0, 1.25))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    exporter = Path(__file__).with_name("export.py")
    exec(compile(exporter.read_text(), str(exporter), "exec"), {"__file__": str(exporter)})
    for name, location, target, scale in [
        ("hero", (8, 12, 7), (0, 0, 1.25), 7.5),
        ("side", (12, 2, 4.5), (0, 0, 1.3), 7.4),
        ("detail", (3.8, 6, 4.5), (1.2, .05, 2.2), 3.2),
    ]:
        camera.location = location
        aim(camera, target)
        data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / (name + ".png"))
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
