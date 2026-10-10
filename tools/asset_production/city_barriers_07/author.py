"""Author compatible chain-link gate leaves and hinge fittings in pinned Blender."""
import importlib.util
import math
from pathlib import Path
import sys

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[3]
ASSET = "city_barriers_07"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
VARIANTS = ("left", "right", "mount")
HINGE_HEIGHTS = (.65, 1.55)
HINGE_HALF_SPAN = 3.15
POST_OFFSET = .115


def sibling(number):
    """Reuse delivered family construction helpers without modifying their sources."""
    sys.dont_write_bytecode = True
    path = ROOT / f"tools/asset_production/city_barriers_{number}/author.py"
    spec = importlib.util.spec_from_file_location("barrier_" + number, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PANEL = sibling("05")
SUPPORT = sibling("06")


def build(variant, materials):
    """Create a hinge-axis component; fixed collars remain separate from leaf geometry."""
    collection = bpy.data.collections.new(f"export_{ASSET}_{variant}")
    bpy.context.scene.collection.children.link(collection)
    geometry = SUPPORT.Geometry()
    if variant != "mount":
        # Reuse the exact authored panel rhythm, then make gate-specific bracing and hardware.
        PANEL.build(collection)
        original = bpy.data.objects["CityBarriers05_Mesh"]
        geometry.vertices = [(v.co.x + 1.575, v.co.y, v.co.z) for v in original.data.vertices]
        geometry.faces = [tuple(p.vertices) for p in original.data.polygons]
        geometry.slots = [p.material_index for p in original.data.polygons]
        geometry.smooth = [p.use_smooth for p in original.data.polygons]
        bpy.data.objects.remove(original, do_unlink=True)
        bpy.data.objects.remove(bpy.data.objects["CityBarriers05"], do_unlink=True)
        # Back-face tension brace; standoffs connect it to the frame without cutting the weave.
        geometry.rod((.13, -.055, 1.98), (3.02, -.055, .22), .012, 0)
        for x, z in ((.13, 1.98), (3.02, .22)):
            geometry.rod((x, -.06, z), (x, 0, z), .018, 1)
        for height in HINGE_HEIGHTS:
            geometry.lathe([(height - .030, .0125), (height - .030, .027),
                            (height + .030, .027), (height + .030, .0125)],
                           slot=1, closed=True)
            geometry.box((.063, 0, height), (.089, .026, .042), 0)
        if variant == "left":
            # A retained sliding-bolt silhouette, not an operable lock or gameplay state.
            geometry.rod((2.93, .06, 1.1), (3.235, .06, 1.1), .008, 0)
            geometry.rod((2.99, .06, 1.1), (2.99, .11, 1.1), .010, 1)
            for x in (2.96, 3.04):
                geometry.box((x, .039, 1.1), (.026, .05, .050), 1)
        else:
            # Four-sided keeper opening: the left bolt fits through, rather than into a solid block.
            for y in (.036, .084):
                geometry.box((3.10, y, 1.1), (.065, .012, .050), 1)
            for z in (1.081, 1.119):
                geometry.box((3.10, .06, z), (.065, .048, .012), 1)
            geometry.box((3.071, .025, 1.1), (.020, .045, .035), 0)
            geometry.vertices = [(-x, y, z) for x, y, z in geometry.vertices]
    else:
        for height in HINGE_HEIGHTS:
            geometry.lathe([(height - .06, .0405), (height - .06, .047),
                            (height + .06, .047), (height + .06, .0405)],
                           centre=(-POST_OFFSET, 0), slot=1, closed=True, oxide=True)
            for dz in (-.046, .046):
                geometry.box((-.050, 0, height + dz), (.140, .045, .022), 0)
            geometry.lathe([(height - .065, .017), (height - .059, .017),
                            (height - .059, .012), (height + .059, .012),
                            (height + .059, .017), (height + .065, .017)], slot=0)
    name = "CityBarriers07_" + variant.title()
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
    root["asset_id"] = "city_barriers.07"
    root["authorship"] = "Original Blender construction; reuses delivered .05/.06 authoring helpers"
    root["pivot"] = "Vertical hinge axis X=Y=0, projected to ground Z=0"
    root["hinge_heights_m"] = list(HINGE_HEIGHTS)
    root["state"] = "Static component only; no animation, locking or interaction"
    return root


def studio_copy(source, name, x=0, y=0, angle=0):
    """Instance a saved Blender mesh for evidence only, outside all export collections."""
    obj = bpy.data.objects.new("STUDIO_" + name, source.data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = (x, y, 0)
    obj.rotation_euler.z = angle
    return obj


def load_sibling_mesh(number, name):
    """Read existing source meshes for kit-context renders, never export duplicate supports."""
    path = ROOT / f"art/source/models/environment/city_barriers_{number}/city_barriers_{number}.blend"
    with bpy.data.libraries.load(str(path), link=False) as (available, loaded):
        assert name in available.objects
        loaded.objects = [name]
    return loaded.objects[0]


def main():
    """Save neutral component sources, export, then render open/closed kit-context evidence."""
    assert bpy.app.version_string == "5.2.2 LTS"
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    materials = [SUPPORT.material("fence_galvanised_frame", (.32, .38, .39), .70, .48),
                 SUPPORT.material("fence_galvanised_wire", (.19, .25, .26), .60, .55),
                 SUPPORT.material("fence_joint_oxide", (.16, .065, .026), .05, .84)]
    roots = [build(v, materials) for v in VARIANTS]
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.19, .24, .29, 1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = .5
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.002))
    bpy.context.object.name = "STUDIO_ground"
    bpy.context.object.data.materials.append(SUPPORT.material("STUDIO_slate", (.15, .19, .22), 0, .65))
    for name, location, energy, size in [("key", (3, 4, 8), 1400, 7),
                                        ("rim", (-5, -3, 6), 1800, 6)]:
        data = bpy.data.lights.new("STUDIO_" + name, "AREA")
        data.energy, data.shape, data.size = energy, "DISK", size
        light = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(light)
        light.location = location
        SUPPORT.aim(light, (0, 0, 1.1))
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
    camera.location = (8, 12, 8)
    SUPPORT.aim(camera, (0, .8, 1))
    data.type, data.ortho_scale = "ORTHO", 12
    bpy.context.preferences.filepaths.save_version = 0
    # Save/export before adding sibling review context or opening the leaves.
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    script = Path(__file__).parent / "export.py"
    exec(compile(script.read_text(), str(script), "exec"), {"__file__": __file__})
    for root in roots:
        for obj in root.children:
            obj.hide_render = True
    left = studio_copy(bpy.data.objects["CityBarriers07_Left_Mesh"], "Left", -3.15, angle=math.pi / 2)
    right = studio_copy(bpy.data.objects["CityBarriers07_Right_Mesh"], "Right", 3.15, angle=-math.pi / 2)
    mount = bpy.data.objects["CityBarriers07_Mount_Mesh"]
    studio_copy(mount, "MountLeft", -3.15)
    studio_copy(mount, "MountRight", 3.15, angle=math.pi)
    terminal = load_sibling_mesh("06", "CityBarriers06_Terminal_Mesh")
    line = load_sibling_mesh("06", "CityBarriers06_Line_Mesh")
    corner = load_sibling_mesh("06", "CityBarriers06_Corner_Mesh")
    panel = load_sibling_mesh("05", "CityBarriers05_Mesh")
    studio_copy(terminal, "PostLeft", -3.265, angle=math.pi)
    studio_copy(terminal, "PostRight", 3.265)
    studio_copy(panel, "PanelLeft", -4.815)
    studio_copy(panel, "PanelRight", 4.815)
    studio_copy(line, "Line", 6.365)
    studio_copy(panel, "StraightExtension", 7.915)
    studio_copy(terminal, "End", 9.465, angle=math.pi)
    studio_copy(corner, "Corner", -6.365)
    studio_copy(panel, "Return", -6.365, 1.55, math.pi / 2)
    studio_copy(terminal, "ReturnEnd", -6.365, 3.10, -math.pi / 2)
    for name, location, target, scale in [
        ("hero", (10, 15, 10), (1, 1, .9), 19),
        ("side", (0, 12, 1.1), (0, 0, 1.1), 8.3),
        ("detail", (3.7, 2, 1.5), (0, .04, 1.1), .95),
    ]:
        if name != "hero":
            left.rotation_euler.z = right.rotation_euler.z = 0
        camera.location = location
        SUPPORT.aim(camera, target)
        data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    left.rotation_euler.z, right.rotation_euler.z = math.pi / 2, -math.pi / 2
    camera.location = (0, 0, 47)
    camera.rotation_euler = (0, 0, 0)
    data.type, data.sensor_fit = "PERSP", "VERTICAL"
    data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
