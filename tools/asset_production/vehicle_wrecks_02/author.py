"""Author the Crate wreck from its accepted original source; leave the live vehicle untouched."""
import math
from pathlib import Path
import sys

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "vehicle_wrecks_02"
LIVE = ROOT / "art/source/models/vehicles/car_crate_a/car_crate_a.blend"
SOURCE = ROOT / f"art/source/models/vehicles/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
STANCE = .92

# Reuse the delivered family's closed-shell and shading helpers without modifying that sibling.
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools/asset_production/vehicle_wrecks_01"))
from author import aim, clean, material, shard


def roof_crush(x, y):
    """Keep the tall hatch perimeter while depressing a broad off-centre roof valley."""
    return .18 * max(0, 1 - abs(x - .20) / .80) * max(0, 1 - abs(y + .48) / .85)


def windshield_point(u, v):
    """Map normalized points onto the live Crate's sloped windshield, in its lowered stance."""
    width = .78 * (1 - v) + .74 * v
    return ((u * 2 - 1) * width, .66 * (1 - v) + .30 * v,
            (1.06 * (1 - v) + 1.605 * v) * STANCE)


def main():
    """Flatten the mechanical hierarchy and author large readable damage, not runtime destruction."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.wm.open_mainfile(filepath=str(LIVE))
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    col = bpy.data.collections["export_car_crate_a"]
    col.name = "export_" + ASSET
    parts = []
    for obj in list(col.all_objects):
        if obj.type == "MESH" and not obj.name.startswith(
                ("Seat", "CabinFloor", "Dashboard", "MirrorRight")):
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

    ivory = material("wreck_crate_ivory", (.32, .29, .205), .14, .79)
    petrol = material("wreck_crate_petrol", (.008, .065, .077), .18, .77)
    char = material("wreck_charcoal", (.016, .022, .026), .18, .87)
    void = material("wreck_glass_void", (.004, .008, .010), 0, 1)
    glass = material("wreck_glass_remnant", (.045, .115, .14), .15, .38)
    rubber = material("wreck_scorched_rubber", (.008, .010, .013), 0, .96)
    metal = material("wreck_exposed_metal", (.105, .125, .14), .55, .7)
    lamp = material("wreck_dead_lamp", (.17, .125, .066), 0, .8)
    mappings = {"body_paint": ivory, "hood_inset": petrol, "trim": char,
                "glass": void, "tire": rubber, "wheel_hub": metal,
                "headlamp": lamp, "tail_lamp": char}
    for obj in parts:
        for slot in obj.material_slots:
            slot.material = mappings.get(slot.material.name if slot.material else "", char)
        # Sparse supporting cuts make broad dents visible while staying below the live-car budget.
        if obj.name in ("Body", "Roof", "HoodInset") or obj.name.startswith("RoofRib"):
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if e.calc_length() > .42],
                                     cuts=2, use_grid_fill=True)
            bm.to_mesh(obj.data)
            bm.free()
        if "Glass" in obj.name or "Window" in obj.name or obj.name == "Windshield":
            obj.name = "SealedAperture_" + obj.name
        for vertex in obj.data.vertices:
            x, y, z = vertex.co
            if obj.name in ("Body", "HoodInset") and y > .60:
                depth = .23 * max(0, 1 - abs(x + .16) / .95)
                depth *= max(0, 1 - abs(y - 1.14) / .65)
                vertex.co.z -= depth * max(0, min(1, (z - .55) / .4))
            if obj.name == "Roof" or obj.name.startswith("RoofRib"):
                vertex.co.z -= roof_crush(x, y)
            if obj.name == "Body" and y < -1.4:
                # Crate has a hatch, not a sedan boot: fold the hatch sill without lengthening it.
                vertex.co.z -= .16 * max(0, 1 - abs(x - .22)) * max(0, min(1, (z - .45) / .5))
            if obj.name in ("DoorPanelFrontLeft", "DoorHandleFrontLeft"):
                weight = max(0, min(1, (.57 - y) / .82))
                vertex.co.z -= .17 * weight
                vertex.co.x += .09 * weight
            if obj.name == "RearBumper":
                weight = max(0, min(1, (x + .84) / 1.68))
                vertex.co.z -= .12 * weight
                vertex.co.y += .04 * weight
            if obj.name == "HoodInset":
                vertex.co.z += .025  # Keep the buckled inset clear of its differently tessellated support.
            vertex.co.z *= STANCE
        obj.data.update()
        if obj.name in ("Roof", "Body", "HoodInset") or obj.name.startswith("RoofRib"):
            index = len(obj.data.materials)
            obj.data.materials.append(char)
            for face in obj.data.polygons:
                p = face.center
                if ((obj.name == "Roof" and p.x > -.30 + .12 * p.y)
                        or (obj.name.startswith("RoofRib") and p.x > 0)
                        or (obj.name == "HoodInset" and p.x > -.08)
                        or (obj.name == "Body" and (p.y > .60 or p.y < -1.4 or abs(p.x) < .78))):
                    face.material_index = index
        if obj.name in ("DoorPanelFrontRight", "PillarRight"):
            for slot in obj.material_slots:
                slot.material = char

    for i, uv in enumerate([[(0, 0), (.38, 0), (0, .68)],
                            [(1, 0), (1, .85), (.70, .20)],
                            [(.15, 1), (.65, 1), (.31, .72)]]):
        parts.append(shard(col, "BrokenWindshield_" + str(i),
                           [windshield_point(*p) for p in uv], (0, .84, .55), glass))
    for side in (-1, 1):
        parts.append(shard(col, "BrokenSide_" + str(side),
                           [(side * .788, .55, 1.065 * STANCE),
                            (side * .788, .09, 1.065 * STANCE),
                            (side * .75, .28, 1.55 * STANCE)], (side, 0, .09), glass))
        parts.append(shard(col, "BrokenRearSide_" + str(side),
                           [(side * .788, -1.38, 1.065 * STANCE),
                            (side * .788, -.90, 1.065 * STANCE),
                            (side * .75, -1.20, 1.55 * STANCE)], (side, 0, .09), glass))
    parts.append(shard(col, "BrokenHatchGlass",
                       [(.78, -1.48, 1.06 * STANCE), (.20, -1.48, 1.06 * STANCE),
                        (.74, -1.22, 1.605 * STANCE)], (0, -.90, .43), glass))

    for obj in parts:
        if obj.name.startswith(("Tire", "Hub")):
            bpy.context.view_layer.objects.active = obj
            decimate = obj.modifiers.new("Static wheel density", "DECIMATE")
            decimate.ratio = .55
            bpy.ops.object.modifier_apply(modifier=decimate.name)
            if obj.name.startswith("Tire"):
                ground_offset = min(v.co.z for v in obj.data.vertices)
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
    mesh.name = "VehicleWrecks02_Mesh"
    bpy.ops.object.material_slot_remove_unused()
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new("VehicleWrecks02", None)
    col.objects.link(root)
    mesh.parent = root
    root["asset_id"] = "vehicle_wrecks.02"
    root["derived_from"] = "car_crate_a: original commissioned Blender source"
    root["contract"] = "Ground origin; Blender +Y front; static wreck, no interior or mechanics"
    render_studio(scene)


def render_studio(scene):
    """Save the editable source and four isolated views with the same studio as the Sable wreck."""
    studio = bpy.data.collections.new("STUDIO_non_export")
    scene.collection.children.link(studio)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.012))
    ground = bpy.context.object
    ground.name = "STUDIO_ground"
    for col in list(ground.users_collection):
        col.objects.unlink(ground)
    studio.objects.link(ground)
    ground.data.materials.append(material("STUDIO_slate", (.105, .135, .15), 0, .9))
    ruler = bpy.data.objects.new("REFERENCE_1m", None)
    studio.objects.link(ruler)
    ruler.empty_display_type, ruler.empty_display_size = "CUBE", .5
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
    scene.cycles.device, scene.cycles.samples = "CPU", 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.compression = 95
    scene.view_settings.view_transform = "AgX"
    camera.location = (-6, 7, 5)
    aim(camera, (0, 0, .75))
    data.type, data.ortho_scale = "ORTHO", 5.9
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    exec(compile(Path(__file__).with_name("export.py").read_text(),
                 str(Path(__file__).with_name("export.py")), "exec"), {"__file__": __file__})
    for name, pos, target, scale in [
            ("hero", (-6, 7, 5), (0, 0, .75), 5.9),
            ("side", (-7, 0, 2.6), (0, 0, .75), 4.9),
            ("detail", (-3, 4.8, 3.3), (0, .55, 1), 3.4)]:
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
