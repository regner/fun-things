"""Original matched harbour parapets, using the established sibling manufacturing helpers."""
from pathlib import Path
import runpy

import bpy

ROOT = Path(__file__).resolve().parents[3]
NID = "city_harbour_bridge_02"
SOURCE = ROOT / f"art/source/models/environment/{NID}/{NID}.blend"
SPAN = 91.0
SHOULDER_CENTER = 8.325
BAY_LENGTH = 7.0
# Reuse the family's applied-bevel/normal/material recipe without running its authoring main.
family = runpy.run_path(str(ROOT / "tools/asset_production/city_harbour_bridge_01/author.py"))
box = family["box"]
material = family["material"]


def main():
    """Build two continuous low walls inside the deck's existing 0.35 m shoulder reservations."""
    assert bpy.app.version_string == "5.2.2 LTS"
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    collection = bpy.data.collections.new(f"export_{NID}")
    scene.collection.children.link(collection)
    root = bpy.data.objects.new("CityHarbourBridge02", None)
    collection.objects.link(root)
    root["asset_id"] = "city_harbour_bridge.02"
    root["datum"] = "Deck-centred pair: Godot Y=0, span +X, guard centres Z=+/-8.325 m"
    root["provenance"] = "Original commissioned Blender construction; sibling finish helper reused"
    root["placement"] = "Identity relative to city_harbour_bridge_01; no added roadway geometry"
    concrete = material("bridge_civic_concrete", (0.16, 0.23, 0.25))
    pale = material("bridge_pale_fascia", (0.57, 0.63, 0.60), roughness=0.58)
    steel = material("bridge_petrol_steel", (0.032, 0.081, 0.095), 0.65, 0.43)
    recess = material("bridge_recess", (0.045, 0.071, 0.077), 0.25, 0.6)
    amber = material("bridge_warm_marker", (0.95, 0.69, 0.32), roughness=0.32)
    shader = amber.node_tree.nodes["Principled BSDF"]
    shader.inputs["Emission Color"].default_value = (0.95, 0.69, 0.32, 1)
    shader.inputs["Emission Strength"].default_value = 0.25
    parts = []
    for sign, side in ((1, "North"), (-1, "South")):
        y = sign * SHOULDER_CENTER
        parts.append(box(side + " continuous footing", (0, y, 0.08),
                         (SPAN, 0.35, 0.16), concrete, collection, 0.018))
        parts.append(box(side + " solid concrete guard", (0, y, 0.54),
                         (SPAN, 0.30, 0.88), pale, collection, 0.025))
        parts.append(box(side + " continuous metal coping", (0, y, 1.03),
                         (SPAN, 0.35, 0.14), steel, collection, 0.024))
        # Broad seven-metre casting rhythm, not fragile pickets or a view-obscuring fence.
        for index in range(14):
            x = max(-45.40, min(45.40, -SPAN / 2 + index * BAY_LENGTH))
            parts.append(box(side + " casting joint collar", (x, y, 0.56),
                             (0.18, 0.33, 0.80), concrete, collection, 0.012))
        # Three small warm inset markers per side; appearance only, no real light nodes.
        for x in (-35.0, 0.0, 35.0):
            parts.append(box(side + " marker recess", (x, y - sign * 0.154, 0.78),
                             (0.56, 0.022, 0.16), recess, collection, 0.008))
            parts.append(box(side + " amber marker", (x, y - sign * 0.168, 0.78),
                             (0.40, 0.012, 0.075), amber, collection, 0.004))
    bpy.ops.object.select_all(action="DESELECT")
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = "CityHarbourBridge02_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    mesh.parent = root
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    runpy.run_path(str(Path(__file__).with_name("export.py")))


if __name__ == "__main__":
    main()
