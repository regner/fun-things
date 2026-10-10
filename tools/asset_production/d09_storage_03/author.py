"""Original low dock freight stack with a closed draped cover and restrained webbing."""
import math
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[3]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools/asset_production/d09_storage_01"))
import author as family

ASSET = "d09_storage_03"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
# A sparse tailored cross-section, not noisy cloth simulation or a subdivided box.
COVER_X = [-1.57, -1.55, -1.51, -1.44, -1.32, -.86, -.60, -.20,
           .20, .60, .86, 1.32, 1.44, 1.51, 1.55, 1.57]
COVER_Z = [.68, .94, 1.23, 1.47, 1.55, 1.59, 1.58, 1.636,
           1.636, 1.58, 1.59, 1.55, 1.47, 1.23, .94, .68]
COVER_Y = [-2.26, -2.22, -2.16, -2.08, -1.92, -1.65, -1.4, -.7,
           0, .7, 1.4, 1.65, 1.92, 2.08, 2.16, 2.22, 2.26]
END_Z = [.68, .95, 1.25, 1.46, 1.57, 1.65, 1.65, 1.65,
         1.65, 1.65, 1.65, 1.65, 1.57, 1.46, 1.25, .95, .68]


def closed_sheet(name, rows, material, thickness):
    """Give a tailored grid a real inward thickness and closed, manifold hems."""
    width = len(rows[0])
    vertices = [point for row in rows for point in row]
    count = len(vertices)
    vertices += [(x, y, z - thickness) for x, y, z in vertices]
    faces = []
    for row in range(len(rows) - 1):
        for col in range(width - 1):
            a = row * width + col
            face = (a, a + 1, a + width + 1, a + width)
            faces.append(face)
            faces.append(tuple(index + count for index in reversed(face)))
    rim = (list(range(width)) + [row * width + width - 1 for row in range(1, len(rows))]
           + list(range(count - 2, count - width - 1, -1))
           + [row * width for row in range(len(rows) - 2, 0, -1)])
    for index, a in enumerate(rim):
        b = rim[(index + 1) % len(rim)]
        faces.append((a, a + count, b + count, b))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return family.finish(obj, name, material, 0)


def build_stack():
    """Author one supported low load, with its contents and cover in the same assembly."""
    timber = family.material("storage_support_timber", (.23, .17, .105), 0, .72)
    cargo = family.material("storage_cargo_slate", (.24, .30, .34), .10, .65)
    blue = family.material("storage_cover_blue", (.055, .135, .235), 0, .83)
    webbing = family.material("storage_webbing_slate", (.055, .085, .12), 0, .82)
    amber = family.material("storage_tie_amber", (.95, .52, .15), .05, .53)
    # Support is part of this assembly. Fork recesses are not actor-sized passages.
    for x in (-1.36, 0, 1.36):
        family.box("Ground timber runner", (x, 0, .065), (.32, 4.6, .13), timber, .018)
    for y in (-2.14, -1.4, 0, 1.4, 2.14):
        family.box("Pallet cross bearer", (0, y, .185), (3.2, .32, .11), timber, .015)
    # Four low freight packs show a deliberate stacked seam below the hanging skirt.
    for z in (.47, .965):
        for y in (-1.08, 1.08):
            family.box("Closed freight pack", (0, y, z), (3.02, 2.12, .43), cargo, .045)
    for x in (-1.22, 0, 1.22):
        family.box("Stack separator", (x, 0, .715), (.12, 4.26, .06), timber, .012)
    family.box("Upper packed load", (0, 0, 1.32), (2.82, 4.05, .27), cargo, .08)
    # End drapes and the side skirts are one closed sheet. Broad fold ridges remain quiet.
    rows = []
    for y, end_height in zip(COVER_Y, END_Z):
        row = []
        for x, z in zip(COVER_X, COVER_Z):
            # Relaxed hems expose the stacked seam; tie-down stations stay taut.
            side_lift = .14 * max(0, 1 - abs(y) / 1.1) if abs(x) > 1.55 else 0
            end_lift = .14 * max(0, 1 - abs(x) / 1.32) if abs(y) > 2.22 else 0
            row.append((x, y, min(z, end_height) + side_lift + end_lift))
        rows.append(row)
    closed_sheet("Tailored blue tarpaulin", rows, blue, .012)
    for y in (-1.4, 1.4):
        rows = [[(x, edge, z + .014) for x, z in zip(COVER_X, COVER_Z)]
                for edge in (y - .065, y + .065)]
        closed_sheet("Continuous webbing over cover", rows, webbing, .013)
        for side in (-1, 1):
            family.box("Webbing lower anchor", (side * 1.568, y, .485),
                       (.024, .13, .43), webbing, .005)
            family.box("Restrained tie buckle", (side * 1.583, y, .51),
                       (.024, .19, .15), cargo, .01)
            family.box("Small amber buckle tab", (side * 1.597, y, .51),
                       (.006, .105, .068), amber, .002)


def main():
    """Save a standalone Blender source and GLB, then render four isolated review views."""
    assert bpy.app.version_string == "5.2.2 LTS"
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system, scene.unit_settings.scale_length = "METRIC", 1
    family.ASSET = ASSET
    family.PARTS.clear()
    collection = bpy.data.collections.new("export_" + ASSET)
    scene.collection.children.link(collection)
    build_stack()
    bpy.ops.object.select_all(action="DESELECT")
    for obj in family.PARTS:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = family.PARTS[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = "D09Storage03_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new("D09Storage03", None)
    collection.objects.link(root)
    mesh.parent = root
    root["asset_id"] = "d09_storage.03"
    root["authorship"] = "Original Blender construction; shared storage-family finish and studio"
    root["axes"] = "Ground-centred; long axis Blender Y / Godot Z"
    root["state"] = "Static intact covered freight; no inventory, simulation or removable cover"
    camera = family.studio(scene)
    camera.location = (9, 10, 7)
    family.aim(camera, (0, 0, .8))
    camera.data.ortho_scale = 8
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    script = Path(__file__).with_name("export.py")
    exec(compile(script.read_text(), str(script), "exec"), {"__file__": str(script)})
    for name, location, target, scale in [
        ("hero", (9, 10, 7), (0, 0, .8), 8),
        ("side", (12, 0, 3), (0, 0, .78), 6.8),
        ("detail", (6, 6, 2.9), (1.0, 1.1, .75), 3.4),
    ]:
        camera.location = location
        family.aim(camera, target)
        camera.data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location, camera.rotation_euler = (0, 0, 47), (0, 0, 0)
    camera.data.type, camera.data.sensor_fit = "PERSP", "VERTICAL"
    camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
