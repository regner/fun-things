"""Author the low service separator in Blender; no downloaded or runtime geometry."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_barriers_03"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
# X is the long axis. Y/Z contour is a low battered concrete body on a metal shoe.
# Explicit chamfers, rather than tiny applied bevels, keep exported topology clean.
CONTOUR = [
    (-.245, .000), (.245, .000), (.275, .025), (.275, .065),
    (.263, .080), (.195, .230), (.175, .570), (.166, .590),
    (.145, .600), (-.145, .600), (-.166, .590), (-.175, .570),
    (-.195, .230), (-.263, .080), (-.275, .065), (-.275, .025),
]
# Rounded end arrises reduce hard corner snags visually; collision remains a single box.
SECTIONS = [(-1.20, .92), (-1.194, .96), (-1.18, .99), (-1.16, 1.0),
            (-.98, 1.0), (-.80, 1.0), (.80, 1.0), (.98, 1.0),
            (1.16, 1.0), (1.18, .99), (1.194, .96), (1.20, .92)]


def material(name, rgb, metallic, roughness):
    """Use the family palette as opaque, backface-culled Principled materials."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*rgb, 1)
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return result


def aim(obj, target):
    """Aim isolated studio cameras and lighting at the inspection target."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def area_light(name, position, energy, size):
    """Keep lighting in the non-export studio collection."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (0, 0, .3))


def build(collection):
    """Create one watertight shell with face-assigned shoe and two upper safety bands."""
    vertices = [(x, y * scale, .3 + (z - .3) * scale)
                for x, scale in SECTIONS for y, z in CONTOUR]
    count = len(CONTOUR)
    faces = [tuple(reversed(range(count)))]
    slots = [0]
    for section in range(len(SECTIONS) - 1):
        midpoint = (SECTIONS[section][0] + SECTIONS[section + 1][0]) / 2
        for edge in range(count):
            next_edge = (edge + 1) % count
            faces.append((section * count + edge, section * count + next_edge,
                          (section + 1) * count + next_edge, (section + 1) * count + edge))
            upper = min(CONTOUR[edge][1], CONTOUR[next_edge][1]) >= .230
            shoe = max(CONTOUR[edge][1], CONTOUR[next_edge][1]) <= .080
            slots.append(2 if .80 < abs(midpoint) < .98 and upper else 1 if shoe else 0)
    faces.append(tuple(range((len(SECTIONS) - 1) * count, len(vertices))))
    slots.append(0)
    mesh = bpy.data.meshes.new("CityBarriers03_Geometry")
    mesh.from_pydata(vertices, [], faces)
    for mat in [material("barrier_pale_concrete", (.48, .50, .46), 0, .78),
                material("barrier_dark_metal", (.025, .075, .090), .45, .46),
                material("barrier_safety_amber", (1.0, .527, .102), 0, .42)]:
        mesh.materials.append(mat)
    for face, slot in zip(mesh.polygons, slots):
        face.material_index = slot
        face.use_smooth = True
    # Recalculate orientation without altering the independent material boundaries.
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new("CityBarriers03_Mesh", mesh)
    collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    modifier = obj.modifiers.new("Broad manufactured highlights", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    root = bpy.data.objects.new("CityBarriers03", None)
    collection.objects.link(root)
    obj.parent = root
    root["asset_id"] = "city_barriers.03"
    root["authorship"] = "Original Blender construction by commissioned production specialist"
    root["ground_datum_m"] = 0.0
    root["front_axis"] = "Symmetric separator; Blender +Y maps to Godot -Z; length along X"
    root["dimensions_status"] = "Provisional 2.40 x 0.60 x 0.55 m in Godot X/Y/Z"


def main():
    """Save editable geometry, export the declared collection and render four fixed views."""
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
    build(collection)
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes["Background"]
    background.inputs[0].default_value = (.19, .24, .29, 1)
    background.inputs[1].default_value = .5
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.002))
    ground = bpy.context.object
    ground.name = "STUDIO_ground"
    ground.data.materials.append(material("STUDIO_slate", (.15, .19, .22), 0, .65))
    area_light("STUDIO_key", (3, 4, 6), 650, 5)
    area_light("STUDIO_rim", (-3, -2, 4), 850, 4)
    area_light("STUDIO_fill", (1, 3, 1.5), 100, 3)
    data = bpy.data.cameras.new("STUDIO_camera")
    camera = bpy.data.objects.new("STUDIO_camera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 100
    scene.view_settings.view_transform = "AgX"
    camera.location = (3, 4, 2.6)
    aim(camera, (0, 0, .29))
    data.type = "ORTHO"
    data.ortho_scale = 3.7
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export_script = Path(__file__).parent / "export.py"
    exec(compile(export_script.read_text(), str(export_script), "exec"), {"__file__": __file__})
    for name, location, target, scale in [
        ("hero", (3, 4, 2.6), (0, 0, .29), 3.7),
        ("side", (0, 4, .30), (0, 0, .30), 3.35),
        ("detail", (2.7, 2.3, 1.8), (.86, 0, .34), 1.45),
    ]:
        camera.location = location
        aim(camera, target)
        data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location = (0, 0, 47)
    camera.rotation_euler = (0, 0, 0)
    data.type = "PERSP"
    data.sensor_fit = "VERTICAL"
    data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
