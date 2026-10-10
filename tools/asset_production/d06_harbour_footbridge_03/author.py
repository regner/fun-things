"""Author the southern span using .02's approved parametric slab recipe and family materials."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_harbour_footbridge_03"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
WIDTH = 3.2
LENGTH = 12.0
DEPTH = 0.35
BEVEL = 0.025
PROVISIONAL_PLACED_HEIGHT = 5.5


def material(name, color, roughness):
    """Create an opaque, back-culling, texture-free Principled surface."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*color, 1)
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = roughness
    return result


def aim(obj, target):
    """Aim a studio light or camera without introducing export geometry."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    """Build, save and export one slab; retain four isolated presentation views."""
    assert bpy.app.version_string == "5.2.2 LTS"
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    collection = bpy.data.collections.new(f"export_{NID}")
    scene.collection.children.link(collection)
    root = bpy.data.objects.new("D06HarbourFootbridge03", None)
    collection.objects.link(root)
    root["asset_id"] = "d06_harbour_footbridge.03"
    root["datum"] = "Incoming portal surface centre; Blender Z=0 / Godot Y=0, NOT ground"
    root["provenance"] = "Original commissioned Blender construction; no external assets"
    root["interface_status"] = "Provisional family contract approved by supervisor"

    half = WIDTH / 2
    # CCW footprint along Blender +Y / Godot -Z; incoming surface datum at origin.
    points = [(half, LENGTH), (-half, LENGTH), (-half, 0), (half, 0)]
    count = len(points)
    vertices = [(x, y, z) for z in (-DEPTH, 0) for x, y in points]
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    faces += [(i, (i + 1) % count, (i + 1) % count + count, i + count)
              for i in range(count)]
    mesh = bpy.data.meshes.new("D06HarbourFootbridge03_Slab")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    slab = bpy.data.objects.new("D06HarbourFootbridge03_Mesh", mesh)
    collection.objects.link(slab)
    slab.parent = root
    for mat in (
        material("deck_warm_pale", (0.72, 0.73, 0.66), 0.78),
        material("deck_pale_fascia", (0.49, 0.59, 0.59), 0.56),
        material("deck_petrol_underside", (0.075, 0.16, 0.18), 0.65),
    ):
        mesh.materials.append(mat)
    mesh.polygons[0].material_index = 2
    mesh.polygons[1].material_index = 0
    for face in mesh.polygons[2:]:
        face.material_index = 1

    # Bevel only exposed boundaries: every portal perimeter remains square and flush.
    portals = ({0, 1, count, count + 1}, {2, 3, count + 2, count + 3})
    weights = mesh.attributes.new("bevel_weight_edge", "FLOAT", "EDGE")
    for edge in mesh.edges:
        weights.data[edge.index].value = 0 if any(
            set(edge.vertices).issubset(portal) for portal in portals) else 1
    bpy.context.view_layer.objects.active = slab
    slab.select_set(True)
    bevel = slab.modifiers.new("Soft exposed slab edges; square mating faces", "BEVEL")
    bevel.limit_method = "WEIGHT"
    bevel.width = BEVEL
    bevel.segments = 3
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=0.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    # Square portal edges must not inherit rounded interpolated shading from the slab top.
    for edge in bm.edges:
        edge.smooth = edge.calc_face_angle() < math.radians(45)
    bm.to_mesh(mesh)
    bm.free()
    for face in mesh.polygons:
        face.use_smooth = True
    normal = slab.modifiers.new("Weighted slab normals", "WEIGHTED_NORMAL")
    normal.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=normal.name)
    slab.select_set(False)

    for name, location, yaw in (
        ("socket_incoming", (0, 0, 0), math.pi),
        ("socket_outgoing", (0, LENGTH, 0), 0),
    ):
        socket = bpy.data.objects.new(name, None)
        collection.objects.link(socket)
        socket.parent = root
        socket.location = location
        socket.rotation_euler.z = yaw
        socket.empty_display_type = "ARROWS"
        socket.empty_display_size = 0.4
        socket["forward"] = "Local Blender +Y / Godot -Z points outward; local up is deck normal"

    world = scene.world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.17, 0.23, 0.28, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -DEPTH - 0.012))
    ground = bpy.context.object
    ground.name = "STUDIO_ground_not_exported"
    ground.data.materials.append(material("STUDIO_slate", (0.055, 0.105, 0.13), 0.8))
    for name, position, energy, size in (
        ("STUDIO_key", (2, 9, 11), 2200, 9),
        ("STUDIO_fill", (-5, 3, 7), 1600, 8),
        ("STUDIO_rim", (4, -2, 5), 1200, 7),
    ):
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.size = energy, size
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = position
        aim(light, (0, LENGTH / 2, 0))
    data = bpy.data.cameras.new("STUDIO_camera")
    camera = bpy.data.objects.new("STUDIO_camera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.compression = 95
    # Disable film dithering so quiet gradients compress without lossy palette conversion.
    scene.render.dither_intensity = 0
    scene.view_settings.view_transform = "AgX"
    camera.location = (11, -10, 12)
    aim(camera, (0, LENGTH / 2, -0.1))
    data.type, data.ortho_scale = "ORTHO", 18.5
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    exec(compile((Path(__file__).parent / "export.py").read_text(),
                 str(Path(__file__).parent / "export.py"), "exec"), {"__file__": __file__})
    for name, position, target, scale in (
        ("hero", (11, -10, 12), (0, LENGTH / 2, -0.1), 18.5),
        ("side", (14, 3, 2.8), (0, LENGTH / 2, -0.1), 15.0),
        ("portal_detail", (4, -4, 2.8), (0, 0.6, -0.15), 5.5),
    ):
        camera.location = position
        aim(camera, target)
        data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    # Evidence-only elevation: source/export retain the deck-surface datum at zero.
    root.location.z = PROVISIONAL_PLACED_HEIGHT
    # Render-only southern orientation; the saved reusable span still runs along local -Z.
    root.rotation_euler.z = math.radians(-135)
    # Keep the broad studio emitters above the elevated deck, not intersecting its surface.
    rotation = root.rotation_euler.to_matrix()
    for light in (obj for obj in scene.objects if obj.type == "LIGHT"):
        light.location = rotation @ light.location + root.location
        light.rotation_euler = (rotation @ light.rotation_euler.to_matrix()).to_euler()
    ground.location.z = -0.015
    camera.location = (LENGTH / (2 * math.sqrt(2)), -LENGTH / (2 * math.sqrt(2)), 47)
    camera.rotation_euler = (0, 0, 0)
    data.type = "PERSP"
    data.sensor_fit = "VERTICAL"
    data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
