"""Construct an original framed woven chain-link panel in pinned Blender."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_barriers_05"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
# Provisional kit interface: 3 m panel, ground datum 0, frame from .10 to 2.10 m.
FRAME_RADIUS = .025
CORNER_RADIUS = .065
WIRE_RADIUS = .0035
WIRE_WEAVE_DEPTH = .006
STRAND_COUNT = 24
STRAND_PITCH = .12
ROW_COUNT = 16
BOTTOM_CENTRE = .125
TOP_CENTRE = 2.075


def material(name, rgb, metallic, roughness):
    """Use opaque uniform Principled finishes without textures or alpha-cutout geometry."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*rgb, 1)
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return result


def tube(vertices, faces, slots, path, radius, sides, slot, closed=False, rust=False):
    """Sweep manifold rings through an authored path; cap each open wire inside its carrier."""
    start = len(vertices)
    points = [Vector(point) for point in path]
    count = len(points)
    reference = Vector((0, 0, 1)) if all(p.z == points[0].z for p in points) else Vector((0, 1, 0))
    for index, point in enumerate(points):
        before = points[(index - 1) % count] if closed else points[max(0, index - 1)]
        after = points[(index + 1) % count] if closed else points[min(count - 1, index + 1)]
        tangent = (after - before).normalized()
        across = tangent.cross(reference).normalized()
        depth = tangent.cross(across).normalized()
        for side in range(sides):
            angle = side * math.tau / sides
            vertices.append(tuple(point + radius * (math.cos(angle) * across
                                                    + math.sin(angle) * depth)))
    for index in range(count if closed else count - 1):
        next_index = (index + 1) % count
        # A few short lower joint arcs carry quiet oxide, never random surface noise.
        segment_slot = 2 if rust and index in (0, 1, 18) else slot
        for side in range(sides):
            next_side = (side + 1) % sides
            faces.append((start + index * sides + side, start + index * sides + next_side,
                          start + next_index * sides + next_side, start + next_index * sides + side))
            slots.append(segment_slot)
    if not closed:
        faces.extend([tuple(reversed(range(start, start + sides))),
                      tuple(range(start + (count - 1) * sides, start + count * sides))])
        slots.extend([slot, slot])


def build(collection):
    """Author one joined mesh of closed frame/wires; actual diamond voids remain unobstructed."""
    vertices, faces, slots = [], [], []
    frame = []
    # Counterclockwise rounded rectangular centreline in Blender X/Z.
    for cx, cz, first_angle in [(1.410, .190, -90), (1.410, 2.010, 0),
                                 (-1.410, 2.010, 90), (-1.410, .190, 180)]:
        for step in range(6):
            angle = math.radians(first_angle + step * 18)
            frame.append((cx + CORNER_RADIUS * math.cos(angle), 0,
                          cz + CORNER_RADIUS * math.sin(angle)))
    tube(vertices, faces, slots, frame, FRAME_RADIUS, 12, 0, closed=True, rust=True)
    for column in range(STRAND_COUNT):
        anchor = (column - (STRAND_COUNT - 1) / 2) * STRAND_PITCH
        path = []
        for row in range(ROW_COUNT + 1):
            phase = 1 if (column + row) % 2 == 0 else -1
            path.append((anchor + phase * STRAND_PITCH / 2,
                         phase * WIRE_WEAVE_DEPTH,
                         BOTTOM_CENTRE + row * (TOP_CENTRE - BOTTOM_CENTRE) / ROW_COUNT))
        tube(vertices, faces, slots, path, WIRE_RADIUS, 6, 1)
    # Three closed tie wires per side attach the outer weave knuckles to the frame.
    for side in (-1, 1):
        for row in (3, 8, 13):
            z = BOTTOM_CENTRE + row * (TOP_CENTRE - BOTTOM_CENTRE) / ROW_COUNT
            loop = [(side * (1.458 + .038 * math.cos(i * math.tau / 12)),
                     .029 * math.sin(i * math.tau / 12), z) for i in range(12)]
            tube(vertices, faces, slots, loop, .0025, 6, 1, closed=True)
    mesh = bpy.data.meshes.new("CityBarriers05_Geometry")
    mesh.from_pydata(vertices, [], faces)
    for mat in [material("fence_galvanised_frame", (.32, .38, .39), .70, .48),
                material("fence_galvanised_wire", (.19, .25, .26), .60, .55),
                material("fence_joint_oxide", (.16, .065, .026), .05, .84)]:
        mesh.materials.append(mat)
    for face, slot in zip(mesh.polygons, slots):
        face.material_index = slot
        face.use_smooth = len(face.vertices) == 4
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new("CityBarriers05_Mesh", mesh)
    collection.objects.link(obj)
    root = bpy.data.objects.new("CityBarriers05", None)
    collection.objects.link(root)
    obj.parent = root
    root["asset_id"] = "city_barriers.05"
    root["authorship"] = "Original Blender construction by commissioned production specialist"
    root["ground_datum_m"] = 0.0
    root["front_axis"] = "Blender +Y maps to Godot -Z; repeat direction X"
    root["dimensions_status"] = "Provisional 3.00 x 2.00 x .063 m visual; bottom .10 m above ground"
    root["kit_interface"] = "Panel edges X +/-1.50; frame centre X +/-1.475; top 2.10; ground 0"


def aim(obj, target):
    """Aim isolated studio cameras and lighting at the inspection target."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def area_light(name, position, energy, size):
    """Keep lighting outside the declared export collection."""
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = position
    aim(obj, (0, 0, 1.1))


def main():
    """Save editable source, export its collection and render four isolated evidence views."""
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
    area_light("STUDIO_key", (3, 4, 6), 850, 5)
    area_light("STUDIO_rim", (-3, -2, 4), 1000, 4)
    area_light("STUDIO_fill", (1, 3, 1.5), 100, 3)
    data = bpy.data.cameras.new("STUDIO_camera")
    camera = bpy.data.objects.new("STUDIO_camera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 100
    scene.view_settings.view_transform = "AgX"
    camera.location = (3.5, 6, 3.2)
    aim(camera, (0, 0, 1.1))
    data.type = "ORTHO"
    data.ortho_scale = 4.7
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export_script = Path(__file__).parent / "export.py"
    exec(compile(export_script.read_text(), str(export_script), "exec"), {"__file__": __file__})
    for name, location, target, scale in [
        ("hero", (3.5, 6, 3.2), (0, 0, 1.1), 4.7),
        ("side", (0, 6, 1.1), (0, 0, 1.1), 4.5),
        ("detail", (2.2, 3, 1.9), (1.24, 0, .49), 1.15),
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
