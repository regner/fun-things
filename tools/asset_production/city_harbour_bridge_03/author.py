"""Original reusable bank-end trim, constructed with the existing family finish recipe."""
from pathlib import Path
import runpy

import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "city_harbour_bridge_03"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
WIDTH = 17.0
TRIM_DEPTH = 0.12
TERMINAL_LENGTH = 0.60
SHOULDER_CENTER = 8.325
family = runpy.run_path(str(ROOT / "tools/asset_production/city_harbour_bridge_01/author.py"))
box = family["box"]
material = family["material"]


def main():
    """Build one bank interface; rotate a second instance for the opposite bridge end."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    collection = bpy.data.collections.new(f"export_{NID}")
    scene.collection.children.link(collection)
    root = bpy.data.objects.new("CityHarbourBridge03", None)
    collection.objects.link(root)
    root["asset_id"] = "city_harbour_bridge.03"
    root["datum"] = "Bank join X=0, deck top Y=0 in Godot; +X extends bankward"
    root["provenance"] = "Original commissioned Blender construction; sibling finish helper reused"
    root["placement"] = "East X=45.5; west X=-45.5 rotated 180 degrees around Godot Y"
    concrete = material("bridge_civic_concrete", (0.16, 0.23, 0.25))
    pale = material("bridge_pale_fascia", (0.57, 0.63, 0.60), roughness=0.58)
    steel = material("bridge_petrol_steel", (0.032, 0.081, 0.095), 0.65, 0.43)
    recess = material("bridge_recess", (0.045, 0.071, 0.077), 0.25, 0.6)
    # A narrow vertical end fascia, never a raised full-width road threshold or new ramp.
    fascia = box("Square bank fascia", (TRIM_DEPTH / 2, 0, -0.275),
                 (TRIM_DEPTH, WIDTH, 0.55), pale, collection, 0)
    for polygon in fascia.data.polygons:
        polygon.use_smooth = False
    parts = [fascia]
    parts.append(box("Below-datum metal reveal", (0.117, 0, -0.245),
                     (0.006, 16.96, 0.07), recess, collection, 0.002))
    for sign, side in ((1, "North"), (-1, "South")):
        y = sign * SHOULDER_CENTER
        parts.append(box(side + " terminal footing", (TERMINAL_LENGTH / 2, y, 0.08),
                         (TERMINAL_LENGTH, 0.35, 0.16), concrete, collection, 0.018))
        parts.append(box(side + " terminal concrete", (TERMINAL_LENGTH / 2, y, 0.54),
                         (TERMINAL_LENGTH, 0.30, 0.88), pale, collection, 0.025))
        parts.append(box(side + " terminal metal coping", (TERMINAL_LENGTH / 2, y, 1.03),
                         (TERMINAL_LENGTH, 0.35, 0.14), steel, collection, 0.024))
        parts.append(box(side + " splice collar", (0.09, y, 0.56),
                         (0.18, 0.33, 0.80), concrete, collection, 0.012))
        # Dark broad end plate closes the casting without adding another warm beacon.
        parts.append(box(side + " bankward end plate", (0.591, y, 0.55),
                         (0.018, 0.22, 0.55), steel, collection, 0.008))
    bpy.ops.object.select_all(action="DESELECT")
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = fascia
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = "CityHarbourBridge03_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    mesh.parent = root
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    runpy.run_path(str(Path(__file__).with_name("export.py")))


if __name__ == "__main__":
    main()
