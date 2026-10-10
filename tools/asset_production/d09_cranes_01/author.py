"""Original larger East Docks crane, authored in Blender; metres, static intact state."""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
ASSET = "d09_cranes_01"
SOURCE = ROOT / f"art/source/models/environment/{ASSET}/{ASSET}.blend"
EVIDENCE = ROOT / f"docs/assets/production/{ASSET}-evidence"
PARTS = []


def material(name, color, metal=0.0, rough=.42):
    """Create opaque, back-culled PBR paint without image dependencies."""
    result = bpy.data.materials.new(name)
    result.diffuse_color = (*color, 1)
    result.use_nodes = True
    result.use_backface_culling = True
    shader = result.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = rough
    return result


def finish(obj, name, surface, bevel=.04):
    """Make a closed, gently bevelled structural shell with applied transforms."""
    obj.name = name
    for previous in list(obj.users_collection):
        previous.objects.unlink(obj)
    bpy.data.collections["export_" + ASSET].objects.link(obj)
    obj.data.materials.append(surface)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Manufactured edge radius", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    for face in obj.data.polygons:
        face.use_smooth = True
    modifier = obj.modifiers.new("Weighted structural normals", "WEIGHTED_NORMAL")
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    PARTS.append(obj)
    return obj


def box(name, location, size, surface, bevel=.04):
    """Build one original rounded structural mass."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = size
    return finish(obj, name, surface, bevel)


def beam(name, start, end, width, depth, surface, bevel=.025):
    """Build an oriented rectangular member between explicit joint centres."""
    start, end = Vector(start), Vector(end)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(start + end) / 2)
    obj = bpy.context.object
    obj.dimensions = (width, depth, (end - start).length)
    obj.rotation_euler = (end - start).to_track_quat("Z", "Y").to_euler()
    return finish(obj, name, surface, bevel)


def cylinder(name, start, end, radius, surface, segments=16, bevel=.02):
    """Build a capped drum, axle or static cable; no physics or animation."""
    start, end = Vector(start), Vector(end)
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius,
                                       depth=(end - start).length, location=(start + end) / 2)
    obj = bpy.context.object
    obj.rotation_euler = (end - start).to_track_quat("Z", "Y").to_euler()
    return finish(obj, name, surface, bevel)


def hook(surface):
    """Sweep a capped chunky J-shaped hook below the suspended sheave block."""
    path = [(0, 15.5, 10.65), (0, 15.5, 10.20), (0, 15.58, 9.96),
            (0, 15.78, 9.78), (0, 16.02, 9.74), (0, 16.25, 9.86),
            (0, 16.36, 10.06), (0, 16.34, 10.24)]
    vertices, faces = [], []
    count = 10
    for index, point in enumerate(path):
        tangent = Vector(path[min(index + 1, len(path) - 1)]) - Vector(path[max(0, index - 1)])
        across = Vector((1, 0, 0))
        other = tangent.normalized().cross(across)
        radius = .17 if index < len(path) - 1 else .10
        for ring in range(count):
            angle = ring * math.tau / count
            vertices.append(Vector(point) + radius * (math.cos(angle) * across + math.sin(angle) * other))
    faces.append(tuple(reversed(range(count))))
    for ring in range(len(path) - 1):
        for index in range(count):
            a, b = ring * count + index, ring * count + (index + 1) % count
            faces.append((a, b, b + count, a + count))
    faces.append(tuple(range((len(path) - 1) * count, len(vertices))))
    mesh = bpy.data.meshes.new("Forged hook geometry")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("Forged static hook", mesh)
    bpy.context.scene.collection.objects.link(obj)
    finish(obj, obj.name, surface, 0)


def aim(obj, target):
    """Aim an isolated studio object without touching the exported geometry."""
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    """Author the full crane, save editable source, export and render bounded evidence."""
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
    amber = material("crane_working_amber", (1.0, .527, .102), .12)
    dark = material("crane_support_petrol", (.025, .075, .090), .45, .46)
    steel = material("crane_joint_slate", (.115, .165, .185), .55, .40)
    glass = material("crane_cab_glazing", (.026, .13, .17), .25, .23)
    ivory = material("crane_safety_ivory", (.92, .88, .71), .05, .48)

    # One sealed pedestal, not an open gantry or implied walk-through frame.
    box("Ground anchor plinth", (0, 0, .40), (5.6, 5.6, .8), dark, .13)
    box("Closed structural pedestal", (0, 0, 5.10), (3.2, 3.2, 8.6), dark, .08)
    box("Pedestal lower collar", (0, 0, 1.12), (3.34, 3.34, .48), steel, .06)
    for x in (-1.33, 1.33):
        for y in (-1.33, 1.33):
            beam("Pedestal corner rib", (x, y, .85), (x, y, 9.45), .24, .24, steel)
    for x in (-2.22, 2.22):
        for y in (-2.22, 2.22):
            cylinder("Foundation hex anchor", (x, y, .73), (x, y, .96), .17, steel, 6)
    box("Sealed service door", (0, -1.64, 2.20), (1.1, .12, 2.20), steel, .06)
    box("Door inset", (0, -1.709, 2.20), (.94, .025, 1.97), dark, .04)
    cylinder("Lower slew race", (0, 0, 9.35), (0, 0, 9.85), 2.32, steel, 40, .06)
    cylinder("Amber slew ring", (0, 0, 9.85), (0, 0, 10.35), 2.50, amber, 40, .06)
    box("Machinery underframe", (0, -.65, 10.62), (4.8, 5.8, .55), dark, .12)
    box("Rounded machinery house", (0, -1.10, 12.00), (4.45, 4.65, 2.35), amber, .22)
    box("Quiet machinery roof", (0, -1.14, 13.25), (4.5, 4.75, .25), dark, .10)
    for x in (-1.25, 0, 1.25):
        box("Broad roof vent", (x, -1.5, 13.48), (.64, 1.8, .27), steel, .08)
    # Closed operator cab: broad cyan-dark panes, no seat/interior/controls.
    box("Forward cab shell", (1.43, 2.00, 12.15), (2.05, 2.3, 2.6), amber, .17)
    box("Cab windshield", (1.43, 3.155, 12.43), (1.72, .065, 1.62), glass, .09)
    box("Cab outer side pane", (2.462, 2.07, 12.43), (.065, 1.65, 1.62), glass, .09)
    box("Cab roof visor", (1.43, 2.04, 13.53), (2.24, 2.6, .23), amber, .09)
    box("Cab sill identity band", (1.43, 3.202, 11.46), (1.73, .035, .19), ivory, .018)
    for x in (-1.55, 1.55):
        beam("Counterweight bearer", (x, -1.3, 11.1), (x, -4.7, 11.1), .45, .55, dark)
    box("Counterweight pack", (0, -4.45, 12.1), (4.4, 2.1, 2.5), steel, .14)
    box("Counterweight amber cap", (0, -4.45, 13.42), (4.5, 2.15, .22), amber, .08)
    box("Counterweight seam", (0, -5.515, 12.1), (.09, .025, 2.0), dark, .008)

    # Four long chords and sparse Warren diagonals make a legible open boom.
    # Lower-chord centreline runs from (Y=1.25,Z=13.2) to (Y=15.5,Z=20.6).
    for side in (-1, 1):
        x = side * .84
        for height in (0, 1.35):
            beam("Amber boom chord", (x, 1.25, 13.2 + height),
                 (side * .54, 15.5, 20.6 + height), .30, .30, amber, .045)
        for y, z, half_width in [(1.25, 13.2, .84), (15.5, 20.6, .54)]:
            beam("Boom end post", (side * half_width, y, z),
                 (side * half_width, y, z + 1.35), .25, .25, amber)
        for bay in range(5):
            t0, t1 = bay / 5, (bay + 1) / 5
            start = (side * (.84 - .3 * t0), 1.25 + 14.25 * t0,
                     13.2 + 7.4 * t0 + (1.35 if bay % 2 else 0))
            end = (side * (.84 - .3 * t1), 1.25 + 14.25 * t1,
                   13.2 + 7.4 * t1 + (0 if bay % 2 else 1.35))
            beam("Boom diagonal", start, end, .19, .19, amber, .025)
    for bay in range(6):
        t = bay / 5
        x, y, z = .84 - .3 * t, 1.25 + 14.25 * t, 13.2 + 7.4 * t
        beam("Boom transverse tie", (-x, y, z), (x, y, z), .22, .22, amber)
    cylinder("Boom heel axle", (-1.23, 1.25, 13.7), (1.23, 1.25, 13.7), .39, steel, 20)
    for side in (-1, 1):
        beam("Rear A-frame leg", (side * 1.6, -2.5, 13.2),
             (side * .63, -1.1, 19.6), .31, .31, amber, .045)
        beam("Forward A-frame leg", (side * 1.6, .9, 13.2),
             (side * .63, -1.1, 19.6), .27, .27, amber)
        cylinder("Static boom pendant", (side * .63, -1.1, 19.6),
                 (side * .54, 14.9, 21.58), .065, dark, 10, 0)
        cylinder("Static backstay", (side * .63, -1.1, 19.6),
                 (side * 1.55, -4.2, 13.5), .065, dark, 10, 0)
    cylinder("A-frame head axle", (-.94, -1.1, 19.6), (.94, -1.1, 19.6), .25, steel)
    cylinder("Boom nose sheave", (-.80, 15.5, 21.15), (.80, 15.5, 21.15), .60, steel, 24)
    for x in (-.25, .25):
        cylinder("Static vertical hoist line", (x, 15.5, 21.15), (x, 15.5, 11.15),
                 .055, dark, 10, 0)
    box("Suspended sheave block", (0, 15.5, 11.02), (.84, .80, 1.04), amber, .10)
    cylinder("Hook block axle", (-.48, 15.5, 11.04), (.48, 15.5, 11.04), .23, steel)
    hook(steel)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in PARTS:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = PARTS[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = "D09Cranes01_Mesh"
    scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    root = bpy.data.objects.new("D09Cranes01", None)
    collection.objects.link(root)
    mesh.parent = root
    root["asset_id"] = "d09_cranes.01"
    root["authorship"] = "Original Blender construction by commissioned implementation specialist"
    root["axes"] = "Blender +Y water-facing boom = Godot -Z; ground-centred pedestal pivot"
    root["state"] = "Static intact landmark; no rig, controls, freight or access gameplay"

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
        data = bpy.data.lights.new("STUDIO_" + name, "AREA")
        data.energy, data.shape, data.size = energy, "DISK", size
        obj = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(obj)
        obj.location = location
        aim(obj, (0, 4, 11))
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
    camera.location = (34, 40, 27)
    aim(camera, (0, 5, 11))
    data.type, data.ortho_scale = "ORTHO", 47
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    export = Path(__file__).with_name("export.py")
    exec(compile(export.read_text(), str(export), "exec"), {"__file__": str(export)})
    for name, location, target, scale in [
        ("hero", (34, 40, 27), (0, 5, 11), 47),
        ("side", (40, 5, 13), (0, 5, 11.5), 46),
        ("detail", (13, 18, 18), (0, .5, 12.6), 16),
    ]:
        camera.location = location
        aim(camera, target)
        data.ortho_scale = scale
        scene.render.filepath = str(EVIDENCE / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location = (0, 6.7, 47)
    camera.rotation_euler = (0, 0, 0)
    data.type, data.sensor_fit = "PERSP", "VERTICAL"
    data.angle = math.radians(42)
    scene.render.filepath = str(EVIDENCE / "overhead_47m_42deg.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
