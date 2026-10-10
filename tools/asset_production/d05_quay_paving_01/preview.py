"""Four isolated views; temporary repetitions and source-backed scale refs are not placements."""
import importlib.util
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
NID = "d05_quay_paving_01"
EVIDENCE = ROOT / f"docs/assets/production/{NID}-evidence"


def main():
    """Render the actual textured carrier against shared paving with a calibrated overhead."""
    bpy.ops.wm.open_mainfile(filepath=str(
        ROOT / f"art/source/models/environment/{NID}/{NID}.blend"))
    # Reuse established isolated studio/camera helpers; never execute or save the owner's asset.
    spec = importlib.util.spec_from_file_location(
        "sports_studio", ROOT / "tools/asset_production/d01_sports_surface_01/author.py")
    studio = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(studio)
    scene = bpy.context.scene
    camera = studio.studio(scene)
    ground = bpy.data.objects["STUDIO_ground_NOT_FIELD_ASSET"]
    ground.name = "STUDIO_shared_paving_NOT_EXPORTED"
    material = ground.data.materials[0]
    image = material.node_tree.nodes.new("ShaderNodeTexImage")
    image.image = bpy.data.images.load(str(ROOT /
        "art/textures/environment/city_ground_finishes_01/plain_plaza_paving_albedo.png"))
    material.node_tree.links.new(image.outputs["Color"],
                                material.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    for loop in ground.data.loops:
        point = ground.data.vertices[loop.vertex_index].co
        ground.data.uv_layers.active.data[loop.index].uv = (point.x / 4, point.y / 4)
    original = bpy.data.objects["D05QuayPaving01_Mesh"]
    copies = []
    for x in (-8, 8):
        obj = original.copy()
        obj.parent = None
        obj.location.x = x
        scene.collection.objects.link(obj)
        copies.append(obj)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    for name, location, target, scale, repeat in [
        ("hero", (8, -14, 18), (0, 0, 0), 29, True),
        ("side", (1, -10, 5), (0, 0, 0), 10, False),
        ("detail", (1, -4, 6), (0, 0, 0), 5, False),
    ]:
        for obj in copies:
            obj.hide_render = not repeat
        camera.location = location
        studio.aim(camera, target)
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    for obj in copies:
        obj.hide_render = False
    for path, location in [
        ("art/models/characters/coral_courier/coral_courier.glb", (2, -1.8, 0)),
        ("art/models/vehicles/car_latch_a/car_latch_a.glb", (-4, -4, 0)),
    ]:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(ROOT / path))
        added = set(bpy.data.objects) - before
        for obj in added:
            if obj.parent not in added:
                obj.location += Vector(location)
    camera.location = (0, 0, 47)
    camera.rotation_euler = (0, 0, 0)
    camera.data.type = "PERSP"
    camera.data.sensor_fit = "VERTICAL"
    camera.data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
