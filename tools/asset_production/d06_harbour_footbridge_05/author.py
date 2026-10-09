"""Author three original two-flight access adaptations using the approved family datum."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d06_harbour_footbridge_05"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
WIDTH = 3.2
RUN = 5.12
RISE = 2.75
STEPS = 16
DEPTH = 0.35
VARIANTS = ("main", "south", "quay")


def material(name, color, roughness):
    """Make a texture-free opaque Principled surface matching the delivered deck family."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*color, 1)
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = roughness
    return result


def sections(variant):
    """Return cross-route centre, travel direction, length, top start and top end in Blender metres."""
    result = [("Upper", (0, 0), (0, 1), WIDTH, 5.5, 5.5),
              ("Flight1", (0, 3.2), (0, 1), RUN, 5.5, 2.75),
              ("Mid", (0, 8.32), (0, 1), WIDTH, 2.75, 2.75)]
    if variant == "main":
        result += [("Flight2", (0, 11.52), (0, 1), RUN, 2.75, 0),
                   ("Apron", (0, 16.64), (0, 1), WIDTH, 0, 0)]
    else:
        sign = 1 if variant == "south" else -1
        result += [("Flight2", (sign * 1.6, 9.92), (sign, 0), RUN, 2.75, 0),
                   ("Apron", (sign * 6.72, 9.92), (sign, 0), WIDTH, 0, 0)]
    return result


def build_section(collection, root, spec, materials):
    """Extrude a closed stair or landing profile; independent shells meet on exact seam planes."""
    name, start, direction, length, high, low = spec
    profile = [(0, high)]
    if high == low:
        profile.append((length, high))
    else:
        for index in range(STEPS):
            distance = (index + 1) * length / STEPS
            profile += [(distance, high - index * RISE / STEPS),
                        (distance, high - (index + 1) * RISE / STEPS)]
    profile += [(length, low - DEPTH), (0, high - DEPTH)]
    across = (direction[1], -direction[0])
    vertices = [(start[0] + direction[0] * s + across[0] * w,
                 start[1] + direction[1] * s + across[1] * w, z)
                for w in (-WIDTH / 2, WIDTH / 2) for s, z in profile]
    count = len(profile)
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    faces += [(i, (i + 1) % count, (i + 1) % count + count, i + count)
              for i in range(count)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.parent = root
    for mat in materials:
        mesh.materials.append(mat)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for face in bm.faces:
        face.material_index = 0 if face.normal.z > 0.9 else (2 if face.normal.z < -0.5 else 1)
    bm.to_mesh(mesh)
    bm.free()
    # Restrained softened tread noses and longitudinal edges. Mating planes stay square.
    weights = mesh.attributes.new("bevel_weight_edge", "FLOAT", "EDGE")
    for edge in mesh.edges:
        a, b = (mesh.vertices[i].co for i in edge.vertices)
        sa = (a.x - start[0]) * direction[0] + (a.y - start[1]) * direction[1]
        sb = (b.x - start[0]) * direction[0] + (b.y - start[1]) * direction[1]
        seam = (abs(sa) < 1e-5 and abs(sb) < 1e-5) or (
            abs(sa - length) < 1e-5 and abs(sb - length) < 1e-5)
        weights.data[edge.index].value = 0 if seam else 1
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bevel = obj.modifiers.new("Soft 8 mm stair edges; square mating planes", "BEVEL")
    bevel.limit_method = "WEIGHT"
    bevel.width = 0.008
    bevel.segments = 2
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=0.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for edge in bm.edges:
        edge.smooth = edge.calc_face_angle() < math.radians(40)
    bm.to_mesh(mesh)
    bm.free()
    for face in mesh.polygons:
        face.use_smooth = True
    normal = obj.modifiers.new("Weighted stair normals", "WEIGHTED_NORMAL")
    normal.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=normal.name)
    obj.select_set(False)
    return obj


def aim(obj, target):
    """Aim studio objects independently of exported transforms."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    """Save metre-based source/export collections and four lean isolated presentation renders."""
    assert bpy.app.version_string == "5.2.2 LTS"
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    materials = [material("deck_warm_pale", (0.72, 0.73, 0.66), 0.78),
                 material("deck_pale_fascia", (0.49, 0.59, 0.59), 0.56),
                 material("deck_petrol_underside", (0.075, 0.16, 0.18), 0.65)]
    roots = {}
    for variant in VARIANTS:
        collection = bpy.data.collections.new(f"export_{NID}_{variant}")
        scene.collection.children.link(collection)
        root = bpy.data.objects.new(f"D06HarbourFootbridge05_{variant}", None)
        collection.objects.link(root)
        roots[variant] = root
        root["asset_id"] = "d06_harbour_footbridge.05"
        root["datum"] = "Ground below incoming upper landing; upper surface Blender Z=5.5"
        root["provenance"] = "Original commissioned Blender construction; no external assets"
        parts = [build_section(collection, root, spec, materials) for spec in sections(variant)]
        bpy.ops.object.select_all(action="DESELECT")
        for obj in parts:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]
        bpy.ops.object.join()
        obj = bpy.context.object
        obj.name = f"D06HarbourFootbridge05_{variant}_Mesh"
        scene.cursor.location = (0, 0, 0)
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        obj.select_set(False)
        end = {"main": (0, 19.84, 0), "south": (9.92, 9.92, 0),
               "quay": (-9.92, 9.92, 0)}[variant]
        for name, position, yaw in (("incoming", (0, 0, 5.5), math.pi),
                                    ("ground", end, {"main": 0, "south": -math.pi / 2,
                                                     "quay": math.pi / 2}[variant])):
            socket = bpy.data.objects.new(f"socket_{name}_{variant}", None)
            collection.objects.link(socket)
            socket.parent = root
            socket.location = position
            socket.rotation_euler.z = yaw
            socket.empty_display_type = "ARROWS"
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.17, 0.23, 0.28, 1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    bpy.ops.mesh.primitive_plane_add(size=1000, location=(0, 0, -0.36))
    ground = bpy.context.object
    ground.name = "STUDIO_ground_not_exported"
    ground.data.materials.append(material("STUDIO_slate", (0.055, 0.105, 0.13), 0.8))
    for name, position, energy, size in (
        ("key", (5, 2, 24), 6500, 16), ("fill", (-20, 5, 16), 5000, 14),
        ("rim", (16, 20, 18), 6500, 16),
    ):
        data = bpy.data.lights.new("STUDIO_" + name, "AREA")
        data.energy, data.size = energy, size
        light = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(light)
        light.location = position
        aim(light, (0, 10, 2.75))
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
    scene.render.image_settings.compression = 95
    # Disable film dithering so quiet gradients compress without lossy palette conversion.
    scene.render.dither_intensity = 0
    scene.view_settings.view_transform = "AgX"
    camera.location = (25, 42, 30)
    aim(camera, (-2, 9, 2.75))
    data.type, data.ortho_scale = "ORTHO", 48
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    script = Path(__file__).parent / "export.py"
    exec(compile(script.read_text(), str(script), "exec"), {"__file__": str(script)})
    # All display offsets/visibility below are render-only; source collections stay at origin.
    for variant, offset in (("main", -18), ("south", -9), ("quay", 16)):
        roots[variant].location.x = offset
    scene.render.filepath = str(EVIDENCE / "hero.png")
    bpy.ops.render.render(write_still=True)
    camera.location = (0, 9.92, 47)
    camera.rotation_euler = (0, 0, 0)
    data.type = "PERSP"
    data.sensor_fit = "VERTICAL"
    data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)
    for variant in VARIANTS:
        roots[variant].location.x = 0
        for child in roots[variant].children:
            child.hide_render = variant != "main"
    data.type = "ORTHO"
    camera.location = (25, 7, 12)
    aim(camera, (0, 9.92, 2.6))
    data.ortho_scale = 24
    scene.render.filepath = str(EVIDENCE / "side.png")
    bpy.ops.render.render(write_still=True)
    for variant in VARIANTS:
        for child in roots[variant].children:
            child.hide_render = variant != "south"
    camera.location = (9, 18, 9)
    aim(camera, (1, 8.5, 2.9))
    data.ortho_scale = 10
    scene.render.filepath = str(EVIDENCE / "landing_detail.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
