"""Author the selected worker in private Blender; no skeleton is invented here."""

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "pedestrian_worker_a"
SOURCE = ROOT / f"art/source/models/pedestrian_civilian/{ASSET_ID}.blend"
PARTS = "worker_editable_parts"
REGIONS = ["skin", "jacket", "yoke", "trousers", "cap", "shirt", "boots", "trim", "hair"]
SWATCHES = ["B77D53", "ECA23E", "326DC0", "48596C", "22525D", "26333B",
            "202B32", "E2D6B9", "392C25"]


def linear(hex_value):
    """Convert authored sRGB swatches to Blender's linear shader colour values."""
    rgb = [int(hex_value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
                 for v in rgb) + (1.0,)


def palette_material():
    """Preview the fixed region mask in Blender; Godot supplies equivalent palette colours."""
    material = bpy.data.materials.new("worker_palette")
    material.diffuse_color = linear(SWATCHES[1])
    material.use_nodes = True
    shader = next(n for n in material.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    shader.inputs["Roughness"].default_value = 0.78
    attribute = material.node_tree.nodes.new("ShaderNodeVertexColor")
    attribute.layer_name = "worker_region"
    separate = material.node_tree.nodes.new("ShaderNodeSeparateColor")
    ramp = material.node_tree.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    for index, colour in enumerate(SWATCHES):
        element = ramp.color_ramp.elements[0] if index == 0 else ramp.color_ramp.elements.new(
            (index - 0.25) / 8)
        element.color = linear(colour)
    links = material.node_tree.links
    links.new(attribute.outputs["Color"], separate.inputs["Color"])
    links.new(separate.outputs["Red"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], shader.inputs["Base Color"])
    material["runtime_mapping"] = "pedestrian_worker_palette.gdshader; COLOR.r * 8"
    return material


def move_to(object_, collection):
    """Keep authored parts in a dedicated non-export collection."""
    for old in list(object_.users_collection):
        old.objects.unlink(object_)
    collection.objects.link(object_)


def region(object_, name):
    """Assign one stable region per face, independent of any chosen NPC colour."""
    attribute = object_.data.color_attributes.get("worker_region")
    if attribute is None:
        attribute = object_.data.color_attributes.new(
            name="worker_region", type="FLOAT_COLOR", domain="CORNER")
    code = REGIONS.index(name) / 8
    for colour in attribute.data:
        colour.color = (code, 0, 0, 1)
    object_["colour_region"] = name


def finish(object_, name, colour, collection, material):
    """Apply source transforms, preserve smooth faces and tag the editable part."""
    object_.name = name
    move_to(object_, collection)
    bpy.context.view_layer.objects.active = object_
    object_.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for face in object_.data.polygons:
        face.use_smooth = True
    object_.data.materials.clear()
    object_.data.materials.append(material)
    region(object_, colour)
    object_.select_set(False)
    return object_


def ellipsoid(name, location, radii, colour, collection, material, segments=16, rings=10):
    """Sculpt a smooth, compact anatomical or clothing mass in Blender coordinates."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments, ring_count=rings, location=location)
    object_ = bpy.context.object
    object_.scale = radii
    return finish(object_, name, colour, collection, material)


def box(name, location, size, bevel, colour, collection, material):
    """Author a broad bevelled hard form such as the boot sole or jacket placket."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    object_ = bpy.context.object
    object_.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    modifier = object_.modifiers.new("soft_edges", "BEVEL")
    modifier.width = bevel
    modifier.segments = 3
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    normal = object_.modifiers.new("broad_normals", "WEIGHTED_NORMAL")
    normal.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=normal.name)
    return finish(object_, name, colour, collection, material)


def sweep(name, sections, colour, collection, material, sides=24):
    """Build a closed elliptical sweep with editable loops for later skin deformation."""
    vertices = []
    for x, y, z, rx, ry in sections:
        for step in range(sides):
            angle = step * math.tau / sides
            vertices.append((x + rx * math.cos(angle), y + ry * math.sin(angle), z))
    faces = []
    for ring in range(len(sections) - 1):
        for step in range(sides):
            a = ring * sides + step
            b = ring * sides + (step + 1) % sides
            faces.append((a, b, b + sides, a + sides))
    faces.append(tuple(range(sides - 1, -1, -1)))
    faces.append(tuple((len(sections) - 1) * sides + i for i in range(sides)))
    mesh = bpy.data.meshes.new(name + "Geometry")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    object_ = bpy.data.objects.new(name, mesh)
    collection.objects.link(object_)
    return finish(object_, name, colour, collection, material)


def capsule(name, a, b, width, depth, colour, collection, material):
    """Author a softened limb mass between two provisional modelling landmarks."""
    middle = (Vector(a) + Vector(b)) / 2
    direction = Vector(b) - Vector(a)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, location=middle)
    object_ = bpy.context.object
    object_.scale = (width, depth, direction.length / 2 + width * 0.24)
    object_.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return finish(object_, name, colour, collection, material)


def author_parts(collection, material):
    """Create the approved cap, stocky civilian clothing and simplified adult face."""
    sweep("Jacket", [(0, 0, .85, .235, .132), (0, 0, .88, .263, .151),
                     (0, 0, 1.02, .274, .165), (0, 0, 1.18, .295, .164),
                     (0, 0, 1.30, .315, .145), (0, 0, 1.38, .275, .115),
                     (0, 0, 1.415, .175, .086)], "jacket", collection, material)
    jacket = bpy.data.objects["Jacket"]
    mask = jacket.data.color_attributes["worker_region"]
    for face in jacket.data.polygons:
        z = sum(jacket.data.vertices[v].co.z for v in face.vertices) / len(face.vertices)
        midpoint = sum((jacket.data.vertices[v].co for v in face.vertices), Vector())
        midpoint /= len(face.vertices)
        code = 2 if z > 1.29 else 1
        if midpoint.y > .1 and abs(midpoint.x) < .09 and z < 1.38:
            code = 5
        for loop in face.loop_indices:
            mask.data[loop].color = (code / 8, 0, 0, 1)
    for side in [-1, 1]:
        suffix = "L" if side == 1 else "R"
        capsule("Collar" + suffix, (side * .08, .075, 1.40),
                (side * .124, .128, 1.335), .027, .022, "jacket", collection, material)
    ellipsoid("Neck", (0, 0, 1.435), (.087, .081, .105), "skin", collection, material)
    sweep("Head", [(0, .01, 1.437, .085, .077), (0, .018, 1.465, .112, .098),
                   (0, .017, 1.51, .143, .118), (0, .006, 1.565, .158, .137),
                   (0, .005, 1.63, .157, .139), (0, 0, 1.69, .151, .128),
                   (0, -.003, 1.745, .118, .104), (0, -.01, 1.777, .06, .06)],
          "skin", collection, material)
    ellipsoid("Nose", (0, .142, 1.594), (.031, .052, .035), "skin", collection, material)
    ellipsoid("BeardChin", (0, .110, 1.491), (.092, .023, .034),
              "hair", collection, material)
    capsule("Moustache", (-.042, .150, 1.545), (.042, .150, 1.545),
            .013, .014, "hair", collection, material)
    for side in [-1, 1]:
        suffix = "L" if side == 1 else "R"
        ellipsoid("Ear" + suffix, (side * .153, 0, 1.61), (.030, .033, .046),
                  "skin", collection, material, 16, 12)
        ellipsoid("EyeWhite" + suffix, (side * .060, .131, 1.639),
                  (.032, .018, .022), "trim", collection, material, 16, 12)
        ellipsoid("Eye" + suffix, (side * .060, .147, 1.638), (.012, .007, .015),
                  "shirt", collection, material, 16, 12)
        capsule("Brow" + suffix, (side * .035, .132, 1.681),
                (side * .091, .117, 1.677), .014, .013, "hair", collection, material)
        ellipsoid("Sideburn" + suffix, (side * .139, .036, 1.647),
                  (.016, .040, .045), "hair", collection, material, 16, 12)
    # The crown and forward brim carry facing at the real overhead camera.
    sweep("CapCrown", [(0, .001, 1.703, .162, .144),
                       (0, -.004, 1.74, .165, .148), (0, -.010, 1.78, .151, .137),
                       (0, -.012, 1.81, .124, .113), (0, -.014, 1.837, .074, .064),
                       (0, -.014, 1.848, .012, .012)], "cap", collection, material, 32)
    ellipsoid("CapBrim", (0, .152, 1.710), (.172, .143, .020),
              "cap", collection, material, 32, 12)
    ellipsoid("CapButton", (0, -.014, 1.849), (.018, .018, .010),
              "cap", collection, material, 16, 8)
    # Broad seam ribs are source geometry, not a noisy baked texture.
    for side in [-1, 1]:
        capsule("CapSeam" + str(side), (side * .099, -.094, 1.783),
                (side * .030, -.050, 1.837), .003, .003, "cap", collection, material)
    box("TrouserSeat", (0, -.008, .790), (.463, .274, .239), .055,
        "trousers", collection, material)
    for side in [-1, 1]:
        suffix = "L" if side == 1 else "R"
        x = side * .135
        sweep("TrouserLeg" + suffix,
              [(x, 0, .135, .079, .082), (x, 0, .18, .087, .094),
               (x, 0, .29, .086, .098), (x, .003, .44, .096, .108),
               (x, .004, .48, .098, .108), (x, 0, .58, .105, .112),
               (x, 0, .73, .113, .119), (x, 0, .835, .108, .123)],
              "trousers", collection, material)
        box("BootSole" + suffix, (x, .047, .041), (.198, .342, .082), .032,
            "trim", collection, material)
        box("Boot" + suffix, (x, .041, .115), (.187, .310, .166), .060,
            "boots", collection, material)
        ellipsoid("BootAnkle" + suffix, (x, -.018, .178), (.089, .094, .108),
                  "boots", collection, material)
        for z, y in [(.163, .139), (.185, .103), (.206, .071)]:
            capsule("BootLace" + suffix + str(z), (x - .046, y, z),
                    (x + .046, y, z), .007, .006, "shirt", collection, material)
        shoulder = (side * .274, 0, 1.326)
        elbow = (side * .394, 0, 1.093)
        wrist = (side * .427, .006, .905)
        sleeve = capsule("JacketSleeve" + suffix, shoulder, elbow, .118, .118,
                         "jacket", collection, material)
        for face in sleeve.data.polygons:
            z = sum(sleeve.data.vertices[v].co.z for v in face.vertices) / len(face.vertices)
            if z > 1.29:
                for loop in face.loop_indices:
                    sleeve.data.color_attributes["worker_region"].data[loop].color = (
                        2 / 8, 0, 0, 1)
        capsule("RolledCuff" + suffix, (side * .375, 0, 1.126),
                (side * .404, 0, 1.072), .096, .106, "trim", collection, material)
        capsule("Forearm" + suffix, (side * .396, 0, 1.08), wrist, .070, .074,
                "skin", collection, material)
        ellipsoid("Hand" + suffix, (side * .431, .012, .866), (.058, .070, .081),
                  "skin", collection, material)
        ellipsoid("Thumb" + suffix, (side * .390, .060, .893), (.027, .031, .050),
                  "skin", collection, material, 16, 12)


def export_mesh(parts, collection):
    """Join copies for a single runtime surface while preserving editable source pieces."""
    copies = []
    for object_ in parts.objects:
        copy = object_.copy()
        copy.data = object_.data.copy()
        collection.objects.link(copy)
        copies.append(copy)
    bpy.ops.object.select_all(action="DESELECT")
    for object_ in copies:
        object_.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = "WorkerMesh"
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    mesh.data.materials.clear()
    mesh.data.materials.append(bpy.data.materials["worker_palette"])
    for polygon in mesh.data.polygons:
        polygon.material_index = 0
    triangles = mesh.modifiers.new("explicit_triangles", "TRIANGULATE")
    bpy.ops.object.modifier_apply(modifier=triangles.name)
    mesh["asset_id"] = ASSET_ID
    mesh["rig_status"] = "UNBOUND: await player-owned shared_humanoid_rig v1"
    mesh["pose_scope"] = "neutral modelling pose; not production skeleton rest pose"
    for object_ in parts.objects:
        object_.hide_render = True
        object_.hide_set(True)
    return mesh


def studio(scene):
    """Save source-only neutral lighting and overview camera for visual iteration."""
    collection = bpy.data.collections.new("source_only_studio")
    scene.collection.children.link(collection)
    for name, location, power, size in [
        ("Key", (3, 4, 5), 450, 4), ("Fill", (-3, 2, 3), 250, 3),
        ("Rim", (0, -3, 4), 350, 3),
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = power
        data.shape = "DISK"
        data.size = size
        object_ = bpy.data.objects.new(name, data)
        collection.objects.link(object_)
        object_.location = location
        object_.rotation_euler = (Vector((0, 0, 1)) - object_.location).to_track_quat(
            "-Z", "Y").to_euler()
    data = bpy.data.cameras.new("Overview")
    camera = bpy.data.objects.new("Overview", data)
    collection.objects.link(camera)
    camera.location = (2.5, 4.5, 2.9)
    camera.rotation_euler = (Vector((0, 0, .95)) - camera.location).to_track_quat(
        "-Z", "Y").to_euler()
    data.type = "ORTHO"
    data.ortho_scale = 2.45
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 32
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.world = bpy.data.worlds.new("WorkerStudioWorld")
    scene.world.color = (.15, .15, .15)
    scene.view_settings.view_transform = "Standard"


def main():
    """Create source/export collections, explicit exports and a measured unbound receipt."""
    if bpy.app.version_string != "5.2.2 LTS":
        raise RuntimeError("Expected pinned Blender 5.2.2 LTS")
    if Path.cwd().resolve() != ROOT:
        raise RuntimeError("Private process is not bound to the pedestrian worktree")
    print("WORKER_PROCESS", json.dumps({"pid": __import__("os").getpid(),
          "project": str(ROOT), "blender": bpy.app.version_string}))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    parts = bpy.data.collections.new(PARTS)
    scene.collection.children.link(parts)
    collection = bpy.data.collections.new("export_" + ASSET_ID)
    scene.collection.children.link(collection)
    material = palette_material()
    author_parts(parts, material)
    mesh = export_mesh(parts, collection)
    stage = bpy.data.collections.new("export_pedestrian_worker_stage")
    scene.collection.children.link(stage)
    stage_material = bpy.data.materials.new("worker_preview_ground")
    stage_material.use_nodes = True
    shader = next(n for n in stage_material.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    shader.inputs["Base Color"].default_value = linear("455563")
    shader.inputs["Roughness"].default_value = .9
    box("PreviewGround", (0, 0, -.065), (66, 44, .13), .01,
        "shirt", stage, stage_material)
    # Ground has no palette mask; its plain material is a separate preview-only output.
    ground = bpy.data.objects["PreviewGround"]
    ground.data.color_attributes.remove(ground.data.color_attributes["worker_region"])
    studio(scene)
    scene["authorship"] = "Original Codex pedestrian lead geometry; selected imagegen concept C"
    scene["authoring_model"] = "gpt-6-astra/high; verified Paseo runtime before spatial work"
    scene["rig_dependency"] = "player-owned shared_humanoid_rig; no S13 binding or skeleton"
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    namespace = {"__file__": str(Path(__file__).with_name("export_worker.py")),
                 "__name__": "worker_export"}
    exec(Path(namespace["__file__"]).read_text(), namespace)
    namespace["export_all"]()
    coordinates = [mesh.matrix_world @ Vector(corner) for corner in mesh.bound_box]
    minimum = [min(v[axis] for v in coordinates) for axis in range(3)]
    maximum = [max(v[axis] for v in coordinates) for axis in range(3)]
    receipt = {"scope": "unbound geometry checkpoint; no rig/clip acceptance",
               "blender": bpy.app.version_string, "source": str(SOURCE.relative_to(ROOT)),
               "editable_parts": len(parts.objects), "vertices": len(mesh.data.vertices),
               "triangles": len(mesh.data.polygons), "material_surfaces": 1,
               "blender_aabb_min": minimum, "blender_aabb_max": maximum,
               "palette_regions": REGIONS, "default_srgb": SWATCHES}
    path = ROOT / "docs/assets/pedestrian_worker_a-evidence/source.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print("WORKER_SOURCE", json.dumps(receipt))


if __name__ == "__main__":
    main()
