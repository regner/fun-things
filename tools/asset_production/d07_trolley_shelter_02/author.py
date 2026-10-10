"""Original static retail trolley; pinned Blender CLI, no live editor dependencies."""
import importlib.util
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d07_trolley_shelter_02"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
sys.dont_write_bytecode = True
# Reuse this lane's existing manufacture/studio helpers without editing the shelter.
spec = importlib.util.spec_from_file_location(
    "shelter_author", ROOT / "tools/asset_production/d07_trolley_shelter_01/author.py")
shelter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shelter)


def tube(collection, name, start, end, radius, mat, vertices=12):
    """Make a closed, capped metal/rubber cylinder with applied transforms."""
    direction = Vector(end) - Vector(start)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                       depth=direction.length,
                                       location=(Vector(start) + Vector(end)) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return shelter.finish(obj, collection, mat, .004 if radius >= .035 else 0)


def panel(collection, name, outline, thickness, mat):
    """Extrude a closed basket floor following its rising, tapered profile."""
    count = len(outline)
    vertices = outline + [(x, y, z - thickness) for x, y, z in outline]
    faces = [tuple(range(count)), tuple(reversed(range(count, count * 2)))]
    for i in range(count):
        j = (i + 1) % count
        faces.append((i, j, j + count, i + count))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return shelter.finish(obj, collection, mat, .004)


def basket_point(side, along, height):
    """Interpolate tapered basket corners; front narrows and floor rises for static nesting."""
    bottom = Vector((side * (.255 - .065 * along), -.31 + .69 * along, .53 + .13 * along))
    top = Vector((side * (.315 - .075 * along), -.35 + .78 * along, 1.00 - .06 * along))
    return bottom.lerp(top, height)


def main():
    """Author a single low-detail trolley, export and render four isolated evidence views."""
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
    petrol = shelter.material("trolley_frame_petrol", (.025, .075, .09), .45, .46)
    silver = shelter.material("trolley_basket_metal", (.55, .64, .65), .65, .38)
    rubber = shelter.material("trolley_wheel_rubber", (.018, .028, .032), 0, .72)
    coral = shelter.material("trolley_handle_coral", (1.0, .168, .11), .1, .48)
    parts = []
    # Open-ended tapered chassis, broad rear stance and narrower leading casters.
    for side in (-1, 1):
        parts.append(tube(collection, "Lower side rail", (side * .285, -.465, .25),
                          (side * .215, .465, .25), .026, petrol))
        parts.append(tube(collection, "Handle upright", (side * .285, -.465, .25),
                          (side * .305, -.49, 1.045), .022, petrol))
        # Rear cantilever supports leave the leading basket/chassis clear for nested copies.
        parts.append(tube(collection, "Rear basket brace", (side * .293, -.44, .48),
                          (side * .255, -.31, .53), .020, petrol))
        for y, x in ((-.43, .285), (.43, .215)):
            parts.append(tube(collection, "Caster stem", (side * x, y, .12),
                              (side * x, y, .25), .028, silver))
            parts.append(tube(collection, "Rubber wheel", (side * x - .035, y, .095),
                              (side * x + .035, y, .095), .095, rubber, 16))
            parts.append(tube(collection, "Wheel hub", (side * x - .037, y, .095),
                              (side * x + .037, y, .095), .038, silver))
    parts.append(tube(collection, "Chassis front crossbar", (-.215, .465, .25),
                      (.215, .465, .25), .026, petrol))
    # Sparse thick ribs carry the basket silhouette without a dense fine-wire grid.
    for side in (-1, 1):
        for height, radius in ((0, .013), (.5, .012), (1, .021)):
            parts.append(tube(collection, "Basket side rail", basket_point(side, 0, height),
                              basket_point(side, 1, height), radius, silver))
        for along in (0, .25, .5, .75, 1):
            parts.append(tube(collection, "Basket side rib", basket_point(side, along, 0),
                              basket_point(side, along, 1), .012, silver))
    for height, radius in ((0, .013), (.5, .012), (1, .021)):
        parts.append(tube(collection, "Basket nose rail", basket_point(-1, 1, height),
                          basket_point(1, 1, height), radius, silver))
    for across in (-.5, 0, .5):
        parts.append(tube(collection, "Basket nose rib", basket_point(across, 1, 0),
                          basket_point(across, 1, 1), .012, silver))
    parts.append(tube(collection, "Rear basket lip", basket_point(-1, 0, 1),
                      basket_point(1, 0, 1), .021, silver))
    parts.append(panel(collection, "Pressed basket floor",
                       [tuple(basket_point(side, along, 0))
                        for side, along in ((-1, 0), (1, 0), (1, 1), (-1, 1))], .018, silver))
    # The rear is intentionally open: static nested copies do not need a moving gate.
    parts.append(tube(collection, "Coral push handle", (-.34, -.49, 1.045),
                      (.34, -.49, 1.045), .035, coral, 16))
    for side in (-1, 1):
        parts.append(tube(collection, "Handle link", (side * .305, -.49, 1.045),
                          (side * .315, -.35, 1.00), .021, petrol))
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = "D07TrolleyShelter02_Mesh"
    obj.data.name = "D07TrolleyShelter02_Geometry"
    # Explicit order remains stable regardless of construction order.
    names = [mat.name for mat in obj.data.materials]
    indices = [names[face.material_index] for face in obj.data.polygons]
    obj.data.materials.clear()
    mats = [petrol, silver, rubber, coral]
    for mat in mats:
        obj.data.materials.append(mat)
    for face, name in zip(obj.data.polygons, indices):
        face.material_index = [mat.name for mat in mats].index(name)
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new("D07TrolleyShelter02", None)
    collection.objects.link(root)
    obj.parent = root
    root["asset_id"] = "d07_trolley_shelter.02"
    root["authorship"] = "Original Blender construction by commissioned production specialist"
    root["front_axis"] = "Basket nose Blender +Y maps to Godot -Z"
    root["ground_datum_m"] = 0.0
    root["state"] = "Static dressing; open nesting rear; no pushing, shopping or loose physics"
    camera = shelter.studio(scene)
    camera.location = (2.3, 3.0, 2.0)
    shelter.aim(camera, (0, 0, .53))
    camera.data.ortho_scale = 2.7
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export_script = Path(__file__).parent / "export.py"
    exec(compile(export_script.read_text(), str(export_script), "exec"), {"__file__": __file__})
    for name, position, target, scale in [
        ("hero", (2.3, 3.0, 2.0), (0, 0, .53), 2.7),
        ("side", (3, 0, 1.4), (0, 0, .53), 2.5),
        ("detail", (1.6, -2.2, 2.0), (0, -.22, .84), 1.75),
    ]:
        camera.location = position
        shelter.aim(camera, target)
        camera.data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location = (0, 0, 47)
    camera.rotation_euler = (0, 0, 0)
    camera.data.type = "PERSP"
    camera.data.sensor_fit = "VERTICAL"
    camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
