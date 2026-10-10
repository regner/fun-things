"""Original smaller East Docks crane; reuse the first sibling's structural recipes."""
import importlib.util
import math
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d09_cranes_02"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
# Reuse the family manufacturing recipe, not a duplicated private primitive library.
HELPERS = ROOT / "tools/asset_production/d09_cranes_01/author.py"
sys.dont_write_bytecode = True  # Keep the read-only sibling helper directory untouched.
spec = importlib.util.spec_from_file_location("crane_family", HELPERS)
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
family.ASSET = ASSET
box, beam, cylinder = family.box, family.beam, family.cylinder
material, aim = family.material, family.aim


def build():
    """Build a lower pedestal and shorter triangular boom, not a scaled larger crane."""
    amber = material("crane_working_amber", (1.0, .527, .102), .12)
    dark = material("crane_support_petrol", (.025, .075, .090), .45, .46)
    steel = material("crane_joint_slate", (.115, .165, .185), .55, .40)
    glass = material("crane_cab_glazing", (.026, .13, .17), .25, .23)
    ivory = material("crane_safety_ivory", (.92, .88, .71), .05, .48)
    box("Ground anchor plinth", (0, 0, .325), (4.4, 4.4, .65), dark, .11)
    box("Short sealed pedestal", (0, 0, 3.15), (2.6, 2.6, 5), dark, .08)
    box("Pedestal lower collar", (0, 0, .90), (2.7, 2.7, .38), steel, .05)
    for x in (-1.1, 1.1):
        for y in (-1.1, 1.1):
            beam("Pedestal corner rib", (x, y, .7), (x, y, 5.7), .2, .2, steel)
    for x in (-1.78, 1.78):
        for y in (-1.78, 1.78):
            cylinder("Foundation hex anchor", (x, y, .59), (x, y, .79), .14, steel, 6)
    box("Sealed service door", (0, -1.34, 1.95), (.94, .1, 1.9), steel, .05)
    box("Door inset", (0, -1.397, 1.95), (.8, .024, 1.68), dark, .035)
    cylinder("Lower slew race", (0, 0, 5.6), (0, 0, 5.95), 1.78, steel, 32, .05)
    cylinder("Amber slew ring", (0, 0, 5.95), (0, 0, 6.35), 1.95, amber, 32, .05)
    box("Machinery underframe", (0, -.4, 6.55), (3.75, 4.2, .42), dark, .1)
    box("Compact machinery house", (0, -.65, 7.65), (3.4, 3.5, 1.8), amber, .17)
    box("Quiet machinery roof", (0, -.65, 8.64), (3.5, 3.6, .2), dark, .08)
    for x in (-.8, .8):
        box("Broad roof vent", (x, -.95, 8.84), (.6, 1.35, .22), steel, .06)
    box("Forward cab shell", (1.17, 1.5, 7.85), (1.75, 1.85, 2.2), amber, .14)
    box("Cab windshield", (1.17, 2.432, 8.08), (1.44, .06, 1.32), glass, .07)
    box("Cab outer side pane", (2.052, 1.56, 8.08), (.06, 1.3, 1.32), glass, .07)
    box("Cab roof visor", (1.17, 1.54, 9.05), (1.95, 2.1, .2), amber, .07)
    box("Cab sill identity band", (1.17, 2.469, 7.28), (1.44, .026, .15), ivory, .012)
    for x in (-1.2, 1.2):
        beam("Counterweight bearer", (x, -1, 6.9), (x, -3.5, 6.9), .36, .44, dark)
    box("Counterweight pack", (0, -3.3, 7.65), (3.35, 1.35, 1.85), steel, .11)
    box("Counterweight amber cap", (0, -3.3, 8.66), (3.45, 1.42, .2), amber, .065)
    box("Counterweight seam", (0, -3.991, 7.65), (.07, .025, 1.5), dark, .007)

    # Triangular section: two lower chords, one top spine, four broad open bays.
    # A shallower, shorter reach and single spine distinguish this sibling overhead.
    for side in (-1, 1):
        beam("Lower amber boom chord", (side * .75, 1.0, 8.5),
             (side * .45, 11, 12.4), .26, .26, amber, .035)
        for bay in range(5):
            t = bay / 4
            y, z, x = 1 + 10 * t, 8.5 + 3.9 * t, .75 - .3 * t
            beam("Triangular boom rib", (side * x, y, z), (0, y, z + 1),
                 .17, .17, amber, .022)
        for bay in range(4):
            t0, t1 = bay / 4, (bay + 1) / 4
            start = (side * (.75 - .3 * t0), 1 + 10 * t0, 8.5 + 3.9 * t0)
            end = (0, 1 + 10 * t1, 9.5 + 3.9 * t1)
            beam("Open boom diagonal", start, end, .16, .16, amber, .02)
    beam("Single amber top spine", (0, 1, 9.5), (0, 11, 13.4), .28, .28, amber, .035)
    for bay in range(5):
        t = bay / 4
        x, y, z = .75 - .3 * t, 1 + 10 * t, 8.5 + 3.9 * t
        beam("Boom transverse tie", (-x, y, z), (x, y, z), .18, .18, amber)
    cylinder("Boom heel axle", (-1.05, 1, 8.65), (1.05, 1, 8.65), .31, steel, 20)
    for side in (-1, 1):
        beam("Compact rear A-frame leg", (side * 1.2, -1.9, 8.5),
             (side * .46, -.8, 12.2), .25, .25, amber, .035)
        beam("Compact forward A-frame leg", (side * 1.2, .6, 8.5),
             (side * .46, -.8, 12.2), .23, .23, amber)
        cylinder("Static boom pendant", (side * .46, -.8, 12.2),
                 (side * .28, 10.6, 13.20), .05, dark, 10, 0)
        cylinder("Static backstay", (side * .46, -.8, 12.2),
                 (side * 1.2, -3.15, 8.8), .05, dark, 10, 0)
    cylinder("A-frame head axle", (-.7, -.8, 12.2), (.7, -.8, 12.2), .2, steel)
    cylinder("Boom nose sheave", (-.64, 11, 12.9), (.64, 11, 12.9), .45, steel, 24)
    for x in (-.20, .20):
        cylinder("Static vertical hoist line", (x, 11, 12.9), (x, 11, 6.85),
                 .045, dark, 10, 0)
    box("Suspended sheave block", (0, 11, 6.74), (.7, .66, .86), amber, .08)
    cylinder("Hook block axle", (-.39, 11, 6.75), (.39, 11, 6.75), .19, steel)
    # Reuse the actual family J-hook construction at 80% size, translated to this block.
    family.hook(steel)
    hook = family.PARTS[-1]
    for vertex in hook.data.vertices:
        vertex.co.y = 11 + (vertex.co.y - 15.5) * .8
        vertex.co.z = 6.43 + (vertex.co.z - 10.65) * .8
        vertex.co.x *= .8


def studio(scene):
    """Prepare isolated fixed-daylight review renders; studio members never export."""
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.19, .24, .29, 1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = .65
    bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, -.015))
    bpy.context.object.name = "STUDIO_ground"
    bpy.context.object.data.materials.append(material("STUDIO_ground", (.15, .19, .22), 0, .65))
    for name, location, energy, size in [
        ("key", (15, 9, 32), 18000, 18), ("rim", (-14, -6, 25), 24000, 15),
        ("fill", (0, 22, 18), 6500, 12),
    ]:
        light = bpy.data.lights.new("STUDIO_" + name, "AREA")
        light.energy, light.shape, light.size = energy, "DISK", size
        obj = bpy.data.objects.new(light.name, light)
        scene.collection.objects.link(obj)
        obj.location = location
        aim(obj, (0, 3, 7))
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
    data.type, data.ortho_scale = "ORTHO", 30
    camera.location = (25, 30, 21)
    aim(camera, (0, 3.5, 6.8))
    return camera


def main():
    """Save one editable static source, export its named collection and render evidence."""
    assert bpy.app.version_string == "5.2.2 LTS"
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system, scene.unit_settings.scale_length = "METRIC", 1
    collection = bpy.data.collections.new("export_" + ASSET)
    scene.collection.children.link(collection)
    build()
    bpy.ops.object.select_all(action="DESELECT")
    for obj in family.PARTS:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = family.PARTS[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = "D09Cranes02_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new("D09Cranes02", None)
    collection.objects.link(root)
    mesh.parent = root
    root["asset_id"] = "d09_cranes.02"
    root["authorship"] = "Original Blender construction; commissioned implementation specialist"
    root["axes"] = "Blender +Y water-facing boom = Godot -Z; ground-centred pedestal pivot"
    root["state"] = "Static intact landmark; no rig, controls, freight or access gameplay"
    camera = studio(scene)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export = Path(__file__).with_name("export.py")
    exec(compile(export.read_text(), str(export), "exec"), {"__file__": str(export)})
    for name, location, target, scale in [
        ("hero", (25, 30, 21), (0, 3.5, 6.8), 30),
        ("side", (35, 3.5, 9), (0, 3.5, 6.8), 30),
        ("detail", (11, 14, 13), (0, .6, 8), 12),
    ]:
        camera.location = location
        aim(camera, target)
        camera.data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    # Final overhead is a translation-only family comparison, not a district placement.
    # Append only the existing export collection AFTER source save/export; never resave it.
    sibling = ROOT / "art/source/models/environment/d09_cranes_01/d09_cranes_01.blend"
    with bpy.data.libraries.load(str(sibling), link=False) as (available, requested):
        requested.collections = ["export_d09_cranes_01"]
    scene.collection.children.link(requested.collections[0])
    bpy.data.objects["D09Cranes01"].location.x = -12
    root.location.x = 12
    camera.location = (0, 6.7, 47)
    camera.rotation_euler = (0, 0, 0)
    camera.data.type, camera.data.sensor_fit = "PERSP", "VERTICAL"
    camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
