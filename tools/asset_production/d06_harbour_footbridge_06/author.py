"""Original fitted rail/light and unplaced pier family, authored only in pinned Blender."""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
from layout import NID, VARIANTS, edges, guard_prism

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"
FACES = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
         (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]


def material(name, color, roughness, emission=0):
    """Use quiet opaque Principled swatches; cyan is appearance-only, never a light node."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*color, 1)
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Emission Color"].default_value = (*color, 1)
    shader.inputs["Emission Strength"].default_value = emission
    return result


def solid(collection, name, points, mat, bevel=0.008):
    """Author a closed bevelled solid from a Godot-coordinate prism and apply smooth normals."""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(x, -z, y) for x, y, z in points], [], FACES)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(mat)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    modifier = obj.modifiers.new("Soft manufactured edge", "BEVEL")
    modifier.width, modifier.segments = bevel, 2
    bpy.ops.object.modifier_apply(modifier=modifier.name)
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
    modifier = obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    return obj


def box(collection, name, centre, size, mat):
    """Make a bevelled authored box, not a generated engine render mesh."""
    x, y, z = centre
    w, h, length = size
    return solid(collection, name, guard_prism((x, y, z-length/2),
                 (x, y, z+length/2), -h/2, h/2, w), mat)


def guard(collection, variant, petrol, cyan):
    """Fit sparse manufactured rails and a narrow fascia strip to every exposed boundary."""
    parts = []
    for index, (a, b, height) in enumerate(edges(variant)):
        for name, low, high, width, mat in (
            ("Cap", height-0.12, height, 0.12, petrol),
            ("Mid", 0.57, 0.64, 0.07, petrol),
            ("Toe", 0.10, 0.20, 0.10, petrol),
            ("Cyan", -0.15, -0.09, 0.07, cyan),
        ):
            parts.append(solid(collection, f"{variant}_{index}_{name}",
                               guard_prism(a, b, low, high, width), mat, 0.006))
        length = math.hypot(b[0]-a[0], b[2]-a[2])
        bays = max(1, math.ceil(length / 1.6))
        for post in range(bays + 1):
            t = (0.055 + (length-0.11) * post / bays) / length
            p = tuple(a[i] + (b[i]-a[i]) * t for i in range(3))
            parts.append(box(collection, f"{variant}_{index}_Post{post}",
                             (p[0], p[1]+(height-0.12)/2, p[2]),
                             (0.10, height, 0.10), petrol))
    return parts


def support(collection, variant, pale, fascia, petrol):
    """Build a ground-pivot tapered pier with a broad, quiet bearing head; no site is implied."""
    height = 5.15 if variant == "support_tall" else 2.4
    parts = [box(collection, "Foot", (0, 0.10, 0), (1.2, 0.2, 1.2), pale),
             box(collection, "Collar", (0, 0.275, 0), (0.85, 0.15, 0.85), fascia)]
    lower = guard_prism((0, 0.35, -0.325), (0, 0.35, 0.325), 0, 0, 0.65)[:4]
    upper = guard_prism((0, height-0.30, -0.25), (0, height-0.30, 0.25), 0, 0, 0.5)[:4]
    parts.append(solid(collection, "TaperedPier", lower+upper, pale, 0.018))
    parts.append(box(collection, "BearingHead", (0, height-0.15, 0), (2.4, 0.3, 0.7), petrol))
    return parts


def aim(obj, target):
    """Aim isolated studio objects without modifying export transforms."""
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z", "Y").to_euler()


def reference(source_id, variant, position):
    """Link the existing family Blender collection for render context only, never into exports."""
    source = ROOT / f"art/source/models/environment/{source_id}/{source_id}.blend"
    name = "export_" + source_id + ("_"+variant if variant else "")
    with bpy.data.libraries.load(str(source), link=True) as (_, data):
        data.collections = [name]
    obj = bpy.data.objects.new("STUDIO_reference_"+source_id+variant, None)
    obj.instance_type = "COLLECTION"
    obj.instance_collection = data.collections[0]
    bpy.context.scene.collection.objects.link(obj)
    obj.location = position
    return obj


def main():
    """Save seven clean local collections, export them, and render fitted context plus loose piers."""
    assert bpy.app.version_string == "5.2.2 LTS"
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system, scene.unit_settings.scale_length = "METRIC", 1
    petrol = material("rail_dark_teal", (0.025, 0.075, 0.09), 0.46)
    cyan = material("edge_cyan", (0.12, 0.65, 0.72), 0.38, 0.45)
    pale = material("deck_warm_pale", (0.72, 0.73, 0.66), 0.78)
    fascia = material("deck_pale_fascia", (0.49, 0.59, 0.59), 0.56)
    underside = material("deck_petrol_underside", (0.075, 0.16, 0.18), 0.65)
    roots = {}
    for variant in VARIANTS:
        collection = bpy.data.collections.new(f"export_{NID}_{variant}")
        scene.collection.children.link(collection)
        root = bpy.data.objects.new(f"D06HarbourFootbridge06_{variant}", None)
        collection.objects.link(root)
        roots[variant] = root
        root["asset_id"] = "d06_harbour_footbridge.06"
        root["provenance"] = "Original commissioned Blender construction; provisional components"
        root["datum"] = "Matching slab root for guards; ground-centred foot for unplaced supports"
        parts = (support(collection, variant, pale, fascia, underside)
                 if variant.startswith("support") else guard(collection, variant, petrol, cyan))
        bpy.ops.object.select_all(action="DESELECT")
        for obj in parts:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]
        bpy.ops.object.join()
        obj = bpy.context.object
        obj.name = root.name + "_Mesh"
        obj.parent = root
        scene.cursor.location = (0, 0, 0)
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        obj.select_set(False)
    # Studio is independent of the named export collections. Context references are added AFTER save.
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.17, 0.23, 0.28, 1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.7
    bpy.ops.mesh.primitive_plane_add(size=1000, location=(0, 0, -0.36))
    bpy.context.object.name = "STUDIO_ground"
    bpy.context.object.data.materials.append(material("STUDIO_slate", (0.055, 0.105, 0.13), 0.8))
    for name, position, energy, size in (
        ("key", (5, 2, 24), 7500, 16), ("fill", (-20, 5, 16), 6000, 14),
        ("rim", (16, 20, 18), 7000, 16),
    ):
        data = bpy.data.lights.new("STUDIO_"+name, "AREA")
        data.energy, data.size = energy, size
        light = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(light)
        light.location = position
        aim(light, (0, 6, 2.75))
    data = bpy.data.cameras.new("STUDIO_camera")
    camera = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine, scene.cycles.device, scene.cycles.samples = "CYCLES", "CPU", 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format, scene.render.image_settings.compression = "PNG", 95
    scene.render.dither_intensity = 0
    scene.view_settings.view_transform = "AgX"
    camera.location = (28, 38, 29)
    aim(camera, (1, 4, 2.5))
    data.type, data.ortho_scale = "ORTHO", 60
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    script = Path(__file__).parent / "export.py"
    exec(compile(script.read_text(), str(script), "exec"), {"__file__": str(script)})
    # Exploded catalogue, not road placement: all five fitted pieces plus two detached piers.
    offsets = {"junction": (-19, -4, 5.5), "span": (-12, -6, 5.5),
               "main": (-5, -4, 0), "south": (2, -4, 0), "quay": (25, -4, 0),
               "support_tall": (-19, 5, 0), "support_mid": (-15, 5, 0)}
    refs = {}
    for variant, pos in offsets.items():
        roots[variant].location = pos
        if variant == "junction":
            refs[variant] = reference("d06_harbour_footbridge_01", "", pos)
        elif variant == "span":
            refs[variant] = reference("d06_harbour_footbridge_02", "", pos)
        elif variant in ("main", "south", "quay"):
            refs[variant] = reference("d06_harbour_footbridge_05", variant, pos)
    scene.render.resolution_x, scene.render.resolution_y = 1120, 630
    scene.render.filepath = str(EVIDENCE / "hero.png")
    bpy.ops.render.render(write_still=True)
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    camera.location, camera.rotation_euler = (0, 5, 47), (0, 0, 0)
    data.type, data.sensor_fit, data.angle = "PERSP", "VERTICAL", math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)
    for variant, root in roots.items():
        for child in root.children:
            child.hide_render = variant != "main"
    for variant, obj in refs.items():
        obj.hide_render = variant != "main"
    camera.location = (25, 6, 14)
    aim(camera, (-5, 5.92, 2.6))
    data.type, data.ortho_scale = "ORTHO", 26
    scene.render.filepath = str(EVIDENCE / "side.png")
    bpy.ops.render.render(write_still=True)
    for variant, root in roots.items():
        for child in root.children:
            child.hide_render = variant != "south"
    for variant, obj in refs.items():
        obj.hide_render = variant != "south"
    camera.location = (15, 17, 11)
    aim(camera, (3, 5, 3.2))
    data.ortho_scale = 10
    scene.render.resolution_x, scene.render.resolution_y = 1120, 630
    scene.render.filepath = str(EVIDENCE / "guard_detail.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
