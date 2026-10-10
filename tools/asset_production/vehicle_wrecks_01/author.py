"""Derive the static Sable wreck from its accepted Blender source, never the live GLB."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "vehicle_wrecks_01"
LIVE = ROOT / "art/source/models/vehicles/car_sable_a/car_sable_a.blend"
SOURCE = ROOT / f"art/source/models/vehicles/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"


def material(name, rgb, metal=0.0, rough=0.75):
    """Create a quiet, opaque, exportable wreck surface without texture noise."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.diffuse_color = (*rgb, 1)
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = rough
    return mat


def clean(obj):
    """Weld inherited boolean coincidences and recompute closed-shell normals."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    obj.data.set_sharp_from_angle(angle=math.radians(38))
    for face in obj.data.polygons:
        face.use_smooth = True
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new("Wreck weighted normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=mod.name)


def shard(collection, name, points, normal, mat):
    """Author a solid triangular remnant of glazing over a sealed black aperture."""
    n = Vector(normal).normalized() * .006
    vertices = [Vector(p) + n for p in points] + [Vector(p) + n * 2 for p in points]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], [(2, 1, 0), (3, 4, 5), (0, 1, 4, 3),
                                      (1, 2, 5, 4), (2, 0, 3, 5)])
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def aim(obj, target):
    """Aim isolated studio lights and cameras, never an export object."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    """Copy the live source into an independent, flattened, damaged static derivative."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.wm.open_mainfile(filepath=str(LIVE))
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    col = bpy.data.collections["export_car_sable_a"]
    col.name = "export_" + ASSET
    # Remove the live interior, interaction markers and mechanical hierarchy. Preserve world poses.
    objects = list(col.all_objects)
    parts = []
    for obj in objects:
        if obj.type == "MESH" and not obj.name.startswith(("Seat", "CabinFloor", "Dashboard", "MirrorLeft")):
            pose = obj.matrix_world.copy()
            obj.parent = None
            obj.matrix_world = pose
            parts.append(obj)
    for obj in list(bpy.data.objects):
        if obj not in parts:
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.select_all(action="DESELECT")

    plum = material("wreck_sable_plum", (.066, .018, .056), .20, .72)
    coral = material("wreck_sable_coral", (.25, .063, .046), .12, .78)
    char = material("wreck_charcoal", (.016, .022, .026), .18, .87)
    void = material("wreck_glass_void", (.004, .008, .010), 0, 1)
    glass = material("wreck_glass_remnant", (.045, .115, .14), .15, .38)
    rubber = material("wreck_scorched_rubber", (.008, .010, .013), 0, .96)
    metal = material("wreck_exposed_metal", (.105, .125, .14), .55, .7)
    lamp = material("wreck_dead_lamp", (.17, .125, .066), 0, .8)
    mappings = {"body_paint": plum, "hood_inset": coral, "trim": char,
                "glass": void, "tire": rubber, "wheel_hub": metal,
                "headlamp": lamp, "tail_lamp": coral}
    for obj in parts:
        for slot in obj.material_slots:
            slot.material = mappings.get(slot.material.name if slot.material else "", char)
        # Two cuts support broad panel buckles without adding fine detail or extra draw objects.
        if obj.name in ("Body", "Roof", "HoodInset", "RearDeck"):
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            long_edges = [edge for edge in bm.edges if edge.calc_length() > .42]
            bmesh.ops.subdivide_edges(bm, edges=long_edges, cuts=2, use_grid_fill=True)
            bm.to_mesh(obj.data)
            bm.free()
        if "Glass" in obj.name or "Window" in obj.name or obj.name == "Windshield":
            # A sealed matte aperture is a silhouette backing, not a modeled cabin/interior.
            obj.name = "SealedAperture_" + obj.name
        for v in obj.data.vertices:
            x, y, z = v.co
            if obj.name in ("Body", "HoodInset") and y > .85:
                # Bonnet impact: offset broad valley, with shoulders retained at the front corners.
                weight = max(0, 1 - abs(x + .18) / 1.0)
                longitudinal = max(0, 1 - abs(y - 1.42) / .68)
                v.co.z -= .24 * weight * longitudinal * max(0, min(1, (z - .55) / .4))
            if obj.name == "Roof":
                v.co.z -= .13 * max(0, 1 - abs(x - .2) / .85) * max(0, 1 - abs(y + .26) / .85)
            if obj.name in ("Body", "RearDeck") and y < -1.35:
                v.co.z -= .13 * max(0, 1 - abs(x - .2)) * max(0, 1 - abs(y + 1.74) / .5) * max(0, min(1, (z - .55) / .4))
            if obj.name in ("DoorPanelRearLeft", "DoorHandleRearLeft"):
                # Torn lower rear attachment: panel droops inward, never outside the live footprint.
                t = max(0, min(1, (-y - .29) / 1.0))
                v.co.z -= .16 * t
                v.co.x += .08 * t
            if obj.name == "FrontBumper":
                v.co.z -= .14 * max(0, min(1, (-x + .85) / 1.7))
                v.co.y -= .07 * max(0, min(1, (-x + .85) / 1.7))
            if obj.name == "HoodInset":
                # Buckled sheet sits above the separately tessellated body, avoiding coplanar flicker.
                v.co.z += .022
            # Flattened tyre stance with the original ground plane untouched.
            v.co.z *= .93
        if obj.name in ("Roof", "Body", "HoodInset", "RearDeck"):
            obj.data.update()
            index = len(obj.data.materials)
            obj.data.materials.append(char)
            for face in obj.data.polygons:
                p = face.center
                if ((obj.name == "Roof" and p.x > -.34)
                        or (obj.name == "HoodInset" and p.y < 1.48)
                        or (obj.name == "RearDeck" and p.x > .05)
                        or (obj.name == "Body" and (p.y > .8 or p.y < -1.35 or abs(p.x) < .8))):
                    face.material_index = index

    # Sparse, large broken triangles retain the Sable window outlines without an exposed interior.
    def windshield_point(u, v):
        """Map normalized pane coordinates onto the accepted Sable windscreen plane."""
        width = .79 * (1 - v) + .685 * v
        return ((u * 2 - 1) * width, .92 * (1 - v) + .29 * v,
                (1.06 * (1 - v) + 1.405 * v) * .93)

    for i, uv in enumerate([[(0, 0), (.35, 0), (0, .70)],
                            [(1, 0), (1, .82), (.70, .20)],
                            [(.10, 1), (.65, 1), (.31, .70)]]):
        parts.append(shard(col, "BrokenWindshield_" + str(i),
                           [windshield_point(*p) for p in uv], (0, .48, .88), glass))
    # Rear glass and side glass each retain a few large triangular edge fragments.
    for side in (-1, 1):
        parts.append(shard(col, "BrokenSide_" + str(side),
                           [(side * .797, .82, .986), (side * .797, .38, .986),
                            (side * .714, .28, 1.24)], (side, 0, .25), glass))
    parts.append(shard(col, "BrokenRearGlass", [(.79, -1.39, .986),
                       (.20, -1.39, .986), (.685, -.90, 1.29)], (0, -.58, .82), glass))

    for obj in parts:
        if obj.name.startswith(("Tire", "Hub")):
            # Static scorched wheels need less bevel density than the live articulated car.
            bpy.context.view_layer.objects.active = obj
            decimate = obj.modifiers.new("Static wheel density", "DECIMATE")
            decimate.ratio = .55
            bpy.ops.object.modifier_apply(modifier=decimate.name)
            if obj.name.startswith("Tire"):
                ground_offset = min(vertex.co.z for vertex in obj.data.vertices)
                for vertex in obj.data.vertices:
                    vertex.co.z -= ground_offset
        clean(obj)
        group = obj.vertex_groups.new(name=obj.name)
        group.add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = "VehicleWrecks01_Mesh"
    # Remove empty inherited boolean slots and duplicate material references.
    bpy.ops.object.material_slot_remove_unused()
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new("VehicleWrecks01", None)
    col.objects.link(root)
    mesh.parent = root
    root["asset_id"] = "vehicle_wrecks.01"
    root["derived_from"] = "car_sable_a: original commissioned Blender source"
    root["contract"] = "Ground origin; Blender +Y front; static wreck, no interior or mechanics"

    # Non-export reference ruler and render studio are source-only.
    studio = bpy.data.collections.new("STUDIO_non_export")
    scene.collection.children.link(studio)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.012))
    ground = bpy.context.object
    ground.name = "STUDIO_ground"
    for c in list(ground.users_collection):
        c.objects.unlink(ground)
    studio.objects.link(ground)
    ground.data.materials.append(material("STUDIO_slate", (.105, .135, .15), 0, .9))
    ruler = bpy.data.objects.new("REFERENCE_1m", None)
    studio.objects.link(ruler)
    ruler.empty_display_type = "CUBE"
    ruler.empty_display_size = .5
    ruler.location = (3, 0, .5)
    scene.world = bpy.data.worlds.new("STUDIO_world")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.23, .28, .33, 1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = .65
    for name, pos, power, size in [("key", (3, 4, 7), 300, 5),
                                   ("rim", (-4, -2, 5), 360, 4),
                                   ("fill", (-1, 4, 3), 130, 4)]:
        data = bpy.data.lights.new("STUDIO_" + name, "AREA")
        data.energy, data.shape, data.size = power, "DISK", size
        obj = bpy.data.objects.new(data.name, data)
        studio.objects.link(obj)
        obj.location = pos
        aim(obj, (0, 0, .7))
    data = bpy.data.cameras.new("STUDIO_camera")
    camera = bpy.data.objects.new(data.name, data)
    studio.objects.link(camera)
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.compression = 95
    scene.view_settings.view_transform = "AgX"
    camera.location = (-6, 7, 5)
    aim(camera, (0, 0, .65))
    data.type, data.ortho_scale = "ORTHO", 6.4
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    exec(compile(Path(__file__).with_name("export.py").read_text(),
                 str(Path(__file__).with_name("export.py")), "exec"), {"__file__": __file__})
    for name, pos, target, scale in [
            ("hero", (-6, 7, 5), (0, 0, .65), 6.4),
            ("side", (-7, 0, 2.6), (0, 0, .65), 5.4),
            ("detail", (-3, 4.8, 3.3), (0, .7, .9), 3.6)]:
        camera.location = pos
        aim(camera, target)
        data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / (name + ".png"))
        bpy.ops.render.render(write_still=True)
    camera.location, camera.rotation_euler = (0, 0, 47), (0, 0, 0)
    data.type, data.sensor_fit, data.angle = "PERSP", "VERTICAL", math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
