"""Author the original line, terminal and corner chain-link supports in pinned Blender."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_barriers_06"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
VARIANTS = ("line", "terminal", "corner")
CLAMP_HEIGHTS = (.4, 1.1, 1.8)
POST_RADIUS = .04
POST_HEIGHT = 2.16
BRACE_REACH = .9


def material(name, rgb, metallic, roughness):
    """Match the delivered panel's opaque Principled finish values exactly."""
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.use_backface_culling = True
    result.diffuse_color = (*rgb, 1)
    shader = result.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return result


class Geometry:
    """Collect editable closed shells into one static mesh per support variant."""

    def __init__(self):
        """Begin a local per-variant construction buffer."""
        self.vertices, self.faces, self.slots, self.smooth = [], [], [], []

    def face(self, vertices, slot, smooth=True):
        """Keep material boundaries on the authored shell, without floating decals."""
        self.faces.append(tuple(vertices))
        self.slots.append(slot)
        self.smooth.append(smooth)

    def lathe(self, profile, centre=(0, 0), slot=0, closed=False, oxide=False):
        """Revolve a capped post or closed annular clamp with twenty radial sides."""
        count, start = 20, len(self.vertices)
        for z, radius in profile:
            for side in range(count):
                angle = side * math.tau / count
                self.vertices.append((centre[0] + radius * math.cos(angle),
                                      centre[1] + radius * math.sin(angle), z))
        for row in range(len(profile) if closed else len(profile) - 1):
            following = (row + 1) % len(profile)
            for side in range(count):
                a, b = start + row * count + side, start + row * count + (side + 1) % count
                c = start + following * count + (side + 1) % count
                d = start + following * count + side
                self.face((a, b, c, d), 2 if oxide and row == 1 else slot,
                          profile[row][0] != profile[following][0])
        if not closed:
            self.face(reversed(range(start, start + count)), slot, False)
            self.face(range(start + (len(profile) - 1) * count,
                            start + len(profile) * count), slot, False)

    def rod(self, first, last, radius, slot=0):
        """Cap a twelve-sided cylindrical brace or mounting stud at each joint."""
        first, last = Vector(first), Vector(last)
        axis = (last - first).normalized()
        across = axis.cross(Vector((1, 0, 0)))
        if across.length < .01:
            across = axis.cross(Vector((0, 1, 0)))
        across.normalize()
        other = axis.cross(across).normalized()
        start, count = len(self.vertices), 12
        for point in (first, last):
            for side in range(count):
                angle = side * math.tau / count
                self.vertices.append(tuple(point + radius * (math.cos(angle) * across
                                                              + math.sin(angle) * other)))
        for side in range(count):
            following = (side + 1) % count
            self.face((start + side, start + following,
                       start + count + following, start + count + side), slot)
        self.face(reversed(range(start, start + count)), slot, False)
        self.face(range(start + count, start + count * 2), slot, False)

    def box(self, centre, size, slot):
        """Add a small closed stamped tab or ground anchor plate with bevelled corners."""
        # An octagonal plan supplies chamfered edges without degenerate bevel modifiers.
        x, y, z = centre
        hx, hy, hz = (value / 2 for value in size)
        chamfer = min(hx, hy) * .3
        outline = [(-hx + chamfer, -hy), (hx - chamfer, -hy), (hx, -hy + chamfer),
                   (hx, hy - chamfer), (hx - chamfer, hy), (-hx + chamfer, hy),
                   (-hx, hy - chamfer), (-hx, -hy + chamfer)]
        start = len(self.vertices)
        self.vertices.extend((x + px, y + py, height) for height in (z - hz, z + hz)
                             for px, py in outline)
        for i in range(8):
            self.face((start + i, start + (i + 1) % 8,
                       start + 8 + (i + 1) % 8, start + 8 + i), slot, False)
        self.face(reversed(range(start, start + 8)), slot, False)
        self.face(range(start + 8, start + 16), slot, False)


def build(variant, materials):
    """Fit supports to panel edges ±1.50 m and the inherited 3.10 m panel pitch."""
    collection = bpy.data.collections.new(f"export_{ASSET}_{variant}")
    bpy.context.scene.collection.children.link(collection)
    geometry = Geometry()
    geometry.lathe([(0, .048), (.005, .048), (.026, .045), (.045, POST_RADIUS),
                    (2.105, POST_RADIUS), (2.108, .044), (2.14, .044),
                    (POST_HEIGHT, .035)], oxide=True)
    directions = [(1, 0), (-1, 0)] if variant == "line" else [(1, 0)]
    if variant == "corner":
        directions.append((0, 1))
    for height in CLAMP_HEIGHTS:
        geometry.lathe([(height - .022, .04), (height - .022, .046),
                        (height + .022, .046), (height + .022, .04)], slot=1, closed=True)
        for dx, dy in directions:
            geometry.lathe([(height - .020, .0255), (height - .020, .030),
                            (height + .020, .030), (height + .020, .0255)],
                           centre=(dx * .075, dy * .075), slot=1, closed=True)
            geometry.box((dx * .047, dy * .047, height),
                         (.034 if dx else .018, .034 if dy else .018, .032), 1)
    if variant != "line":
        for index, (dx, dy) in enumerate(directions):
            # Stagger corner attachments so the two inward braces never intersect.
            height = 1.72 - index * .16
            offset = (.065 * dy, .065 * dx)
            geometry.rod((0, 0, height), (*offset, height), .026, 1)
            geometry.rod((*offset, height),
                         (dx * BRACE_REACH + offset[0], dy * BRACE_REACH + offset[1], .07),
                         .013)
            foot = (dx * BRACE_REACH + offset[0], dy * BRACE_REACH + offset[1])
            geometry.box((*foot, .015), (.10 if dx else .09, .10 if dy else .09, .03), 0)
            geometry.lathe([(.03, .023), (.045, .023), (.06, .023), (.10, .019)],
                           centre=foot, slot=1, oxide=True)
    name = "CityBarriers06_" + variant.title()
    mesh = bpy.data.meshes.new(name + "_Geometry")
    mesh.from_pydata(geometry.vertices, [], geometry.faces)
    for mat in materials:
        mesh.materials.append(mat)
    for face, slot, smooth in zip(mesh.polygons, geometry.slots, geometry.smooth):
        face.material_index, face.use_smooth = slot, smooth
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name + "_Mesh", mesh)
    collection.objects.link(obj)
    root = bpy.data.objects.new(name, None)
    collection.objects.link(root)
    obj.parent = root
    root["asset_id"] = "city_barriers.06"
    root["authorship"] = "Original Blender construction by commissioned production specialist"
    root["ground_datum_m"] = 0.0
    root["panel_centres_m"] = "Line: X +/-1.55; terminal: X +1.55; corner: X +1.55 and Y +1.55"
    root["axes"] = "Blender +Z up / +Y forward maps to Godot +Y / -Z"
    return root, obj


def aim(obj, target):
    """Aim isolated studio cameras and lights without exporting them."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    """Save unshifted production components, then show temporary linked studio copies."""
    assert bpy.app.version_string == "5.2.2 LTS"
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    materials = [material("fence_galvanised_frame", (.32, .38, .39), .70, .48),
                 material("fence_galvanised_wire", (.19, .25, .26), .60, .55),
                 material("fence_joint_oxide", (.16, .065, .026), .05, .84)]
    parts = [build(variant, materials) for variant in VARIANTS]
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes["Background"]
    background.inputs[0].default_value = (.19, .24, .29, 1)
    background.inputs[1].default_value = .5
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.002))
    ground = bpy.context.object
    ground.name = "STUDIO_ground"
    ground.data.materials.append(material("STUDIO_slate", (.15, .19, .22), 0, .65))
    for name, location, energy, size in [("key", (3, 4, 6), 850, 5),
                                         ("rim", (-3, -2, 4), 1000, 4)]:
        data = bpy.data.lights.new("STUDIO_" + name, "AREA")
        data.energy, data.shape, data.size = energy, "DISK", size
        light = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(light)
        light.location = location
        aim(light, (0, 0, 1.1))
    data = bpy.data.cameras.new("STUDIO_camera")
    camera = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 100
    scene.view_settings.view_transform = "AgX"
    camera.location = (4, 7, 3.8)
    aim(camera, (0, 0, 1.05))
    data.type, data.ortho_scale = "ORTHO", 5.4
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export_script = Path(__file__).parent / "export.py"
    exec(compile(export_script.read_text(), str(export_script), "exec"), {"__file__": __file__})
    # Evidence-only offsets; saved source and exports keep every root at the ground origin.
    for (root, _), offset in zip(parts, (-1.6, -.4, 1.0)):
        root.location.x = offset
    for name, location, target, scale in [
        ("hero", (4, 7, 3.8), (.1, .2, 1.05), 5.4),
        ("side", (0, 7, 1.1), (.1, 0, 1.1), 5.3),
        ("detail", (2.8, 3.0, 2.3), (1.02, .04, 1.75), .72),
    ]:
        camera.location = location
        aim(camera, target)
        data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location = (0, 0, 47)
    camera.rotation_euler = (0, 0, 0)
    data.type, data.sensor_fit = "PERSP", "VERTICAL"
    data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
