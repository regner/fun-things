"""Original reusable framed dock crate, with isolated previews of two saved arrangements."""
import importlib.util
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d09_storage_04"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location(
    "storage_family", ROOT / "tools/asset_production/d09_storage_01/author.py")
family = importlib.util.module_from_spec(spec)
spec.loader.exec_module(family)
family.ASSET = ASSET


def build_crate():
    """Make one sealed blue-panel crate with muted timber battens and protective shoes."""
    timber = family.material("storage_support_timber", (.230, .170, .105), 0, .72)
    blue = family.material("storage_crate_blue", (.055, .135, .235), .05, .65)
    slate = family.material("storage_frame_slate", (.055, .085, .120), .45, .43)
    amber = family.material("storage_crate_tab", (.950, .520, .150), .05, .53)
    for x in (-.49, .49):
        family.box("Integral timber runner", (x, 0, .06), (.18, 1.32, .12), timber, .012)
    family.box("Closed blue plywood pack", (0, 0, .56), (1.24, 1.24, .88), blue, .02)
    for x in (-.64, .64):
        for y in (-.64, .64):
            family.box("Corner timber upright", (x, y, .67), (.12, .12, .76), timber, .014)
            family.box("Protective slate shoe", (x, y, .205), (.12, .12, .17), slate, .012)
    for edge in (-.64, .64):
        for height in (.19, .99):
            family.box("Front back batten", (0, edge, height), (1.16, .12, .12), timber, .012)
            family.box("Side batten", (edge, 0, height), (.12, 1.16, .12), timber, .012)
    # Broad braces differentiate the crate from folded-steel containers; no dense slat texture.
    for side in (-1, 1):
        start, end = Vector((-.49, side * .635, .32)), Vector((.49, side * .635, .86))
        midpoint, delta = (start + end) / 2, end - start
        bpy.ops.mesh.primitive_cube_add(size=1, location=midpoint)
        brace = bpy.context.object
        brace.dimensions = (.105, .075, delta.length)
        brace.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
        family.finish(brace, "Single broad diagonal brace", timber, .012)
    family.box("Recessed lid centre batten", (0, 0, 1.019), (.12, 1.16, .062), timber, .012)
    # One small blank warm tab; not an artwork carrier, selected copy or runtime identity.
    family.box("Blank side tab", (.628, .38, .79), (.022, .19, .13), amber, .009)
    # Joining in this order keeps a stable four-slot contract.
    return [timber, blue, slate, amber]


def stage(mesh, positions):
    """Preview only the declared prefab positions using linked source geometry, never exports."""
    for obj in list(bpy.data.objects):
        if obj.name.startswith("STUDIO_crate"):
            bpy.data.objects.remove(obj, do_unlink=True)
    for index, position in enumerate(positions):
        obj = bpy.data.objects.new(f"STUDIO_crate_{index}", mesh.data)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = position


def main():
    """Save the single editable source, explicit export and four capped isolated evidence views."""
    assert bpy.app.version_string == "5.2.2 LTS"
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system, scene.unit_settings.scale_length = "METRIC", 1
    collection = bpy.data.collections.new("export_" + ASSET)
    scene.collection.children.link(collection)
    materials = build_crate()
    bpy.ops.object.select_all(action="DESELECT")
    for obj in family.PARTS:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = family.PARTS[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = "D09Storage04_Mesh"
    old_materials = list(mesh.data.materials)
    assignments = [materials.index(old_materials[face.material_index]) for face in mesh.data.polygons]
    mesh.data.materials.clear()
    for material in materials:
        mesh.data.materials.append(material)
    for face, index in zip(mesh.data.polygons, assignments):
        face.material_index = index
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new("D09Storage04", None)
    collection.objects.link(root)
    mesh.parent = root
    root["asset_id"] = "d09_storage.04"
    root["authorship"] = "Original Blender construction; commissioned implementation specialist"
    root["axes"] = "Ground-centred; braced face Blender +Y / Godot -Z; blank tab on +X"
    root["state"] = "Static closed crate; no cargo inventory, opening or movable-stack mechanic"
    camera = family.studio(scene)
    mesh.hide_render = True  # Only the studio copies render; use_visible=false still exports the source.
    trio = [(-.74, 0, 0), (.74, 0, 0), (-.74, 0, 1.05)]
    stage(mesh, trio)
    camera.location = (7, 9, 6)
    camera.data.ortho_scale = 6.5
    family.aim(camera, (0, 0, .95))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export = Path(__file__).with_name("export.py")
    exec(compile(export.read_text(), str(export), "exec"), {"__file__": str(export)})
    views = [
        ("hero", trio, (7, 9, 6), (0, 0, .95), 6.5),
        ("side", [(-.74, 0, 0), (.74, 0, 0)], (6, 9, 2.5), (0, 0, .50), 4.6),
        ("detail", [(0, 0, 0)], (2.8, 4.2, 2.5), (0, 0, .55), 2.45),
    ]
    for name, positions, location, target, scale in views:
        stage(mesh, positions)
        camera.location = location
        family.aim(camera, target)
        camera.data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    # Show both arrangement silhouettes, at true scale, with a 3.12 m evidence-only gap.
    stage(mesh, [(x - 3, y, z) for x, y, z in trio] + [(2.26, 0, 0), (3.74, 0, 0)])
    camera.location, camera.rotation_euler = (0, 0, 47), (0, 0, 0)
    camera.data.type, camera.data.sensor_fit = "PERSP", "VERTICAL"
    camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
