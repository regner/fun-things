"""Author the S13 technical humanoid source and explicit GLB export in Blender 5.2."""
import math
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "art/source/models/characters/s13_humanoid.blend"
EXPORT = ROOT / "art/models/characters/s13_humanoid.glb"
COLLECTION_NAME = "export_s13_humanoid"


def material():
    """Create the single palette-remappable opaque body material."""
    body = bpy.data.materials.new("body_paint")
    body.use_nodes = True
    node = next(node for node in body.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
    node.inputs["Base Color"].default_value = (0.92, 0.88, 0.72, 1.0)
    node.inputs["Roughness"].default_value = 0.82
    body.diffuse_color = (0.92, 0.88, 0.72, 1.0)
    return body


def box(collection, body_material, name, size, position):
    """Add one bevelled chunky body part using Godot-space dimensions and position."""
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(position[0], -position[2], position[1]),
    )
    part = bpy.context.object
    part.name = name
    part.scale = (size[0], size[2], size[1])
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    for old_collection in list(part.users_collection):
        old_collection.objects.unlink(part)
    collection.objects.link(part)
    part.data.materials.append(body_material)
    bevel = part.modifiers.new("chunky_bevel", "BEVEL")
    bevel.width = 0.035
    bevel.segments = 1
    bpy.context.view_layer.objects.active = part
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    triangles = part.modifiers.new("explicit_triangles", "TRIANGULATE")
    bpy.ops.object.modifier_apply(modifier=triangles.name)
    for polygon in part.data.polygons:
        polygon.use_smooth = True
    return part


def make_rig(collection):
    """Create the stable seven-bone technical humanoid hierarchy."""
    bpy.ops.object.armature_add(location=(0.0, 0.0, 0.0))
    rig = bpy.context.object
    rig.name = "Rig"
    for old_collection in list(rig.users_collection):
        old_collection.objects.unlink(rig)
    collection.objects.link(rig)
    bpy.ops.object.mode_set(mode="EDIT")
    first = rig.data.edit_bones[0]
    first.name = "root"
    first.head = (0.0, 0.0, 0.0)
    first.tail = (0.0, 0.0, 0.58)
    definitions = {
        "spine": ((0.0, 0.0, 0.58), (0.0, 0.0, 1.38), "root"),
        "head": ((0.0, 0.0, 1.38), (0.0, 0.0, 1.80), "spine"),
        "arm_l": ((-0.18, 0.0, 1.28), (-0.52, 0.0, 0.72), "spine"),
        "arm_r": ((0.18, 0.0, 1.28), (0.52, 0.0, 0.72), "spine"),
        "leg_l": ((-0.15, 0.0, 0.58), (-0.15, 0.0, 0.03), "root"),
        "leg_r": ((0.15, 0.0, 0.58), (0.15, 0.0, 0.03), "root"),
    }
    for name, (head, tail, parent) in definitions.items():
        bone = rig.data.edit_bones.new(name)
        bone.head = head
        bone.tail = tail
        bone.parent = rig.data.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    return rig


def skin(parts, rig):
    """Join body parts into one skinned mesh and assign one influence per vertex."""
    bpy.ops.object.select_all(action="DESELECT")
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = "Skin"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    mesh.data.materials.clear()
    mesh.data.materials.append(bpy.data.materials["body_paint"])
    for polygon in mesh.data.polygons:
        polygon.material_index = 0
    mesh.parent = rig
    armature = mesh.modifiers.new("Skin", "ARMATURE")
    armature.object = rig
    groups = {name: mesh.vertex_groups.new(name=name) for name in
              ["root", "spine", "head", "arm_l", "arm_r", "leg_l", "leg_r"]}
    assignments = {name: [] for name in groups}
    for vertex in mesh.data.vertices:
        x_position = vertex.co.x
        height = vertex.co.z
        if height > 1.36:
            bone = "head"
        elif height > 0.66 and x_position < -0.29:
            bone = "arm_l"
        elif height > 0.66 and x_position > 0.29:
            bone = "arm_r"
        elif height < 0.61 and x_position < 0.0:
            bone = "leg_l"
        elif height < 0.61:
            bone = "leg_r"
        elif height > 0.58:
            bone = "spine"
        else:
            bone = "root"
        assignments[bone].append(vertex.index)
    for name, indices in assignments.items():
        groups[name].add(indices, 1.0, "REPLACE")
    return mesh


def set_rotations(rig, values, frame):
    """Insert rotation keys for every named pose entry at one frame."""
    for bone_name, rotation in values.items():
        pose = rig.pose.bones[bone_name]
        pose.rotation_mode = "XYZ"
        pose.rotation_euler = rotation
        pose.keyframe_insert("rotation_euler", frame=frame, group=bone_name)


def action(rig, name, poses):
    """Create one action and retain its Blender 5 action slot through a muted NLA track."""
    rig.animation_data.action = None
    for frame, values in poses:
        set_rotations(rig, values, frame)
    created = rig.animation_data.action
    created.name = name
    created.use_fake_user = True
    track = rig.animation_data.nla_tracks.new()
    track.name = name
    strip = track.strips.new(name, 1, created)
    strip.action_slot = rig.animation_data.action_slot
    track.mute = True


def make_actions(rig):
    """Author in-place idle, walk, run and one-shot death technical clips."""
    rig.animation_data_create()
    zero = {name: (0.0, 0.0, 0.0) for name in
            ["root", "spine", "head", "arm_l", "arm_r", "leg_l", "leg_r"]}
    idle_mid = dict(zero, spine=(0.0, 0.0, 0.045), head=(0.0, 0.0, -0.035),
                    arm_l=(0.04, 0.0, 0.0), arm_r=(-0.04, 0.0, 0.0))
    action(rig, "idle", [(1, zero), (31, idle_mid), (61, zero)])
    walk_a = dict(zero, arm_l=(0.48, 0.0, 0.0), arm_r=(-0.48, 0.0, 0.0),
                  leg_l=(-0.48, 0.0, 0.0), leg_r=(0.48, 0.0, 0.0))
    walk_b = dict(zero, arm_l=(-0.48, 0.0, 0.0), arm_r=(0.48, 0.0, 0.0),
                  leg_l=(0.48, 0.0, 0.0), leg_r=(-0.48, 0.0, 0.0))
    action(rig, "walk", [(1, zero), (8, walk_a), (16, zero), (23, walk_b), (31, zero)])
    run_a = dict(zero, spine=(0.16, 0.0, 0.0), arm_l=(0.85, 0.0, 0.0),
                 arm_r=(-0.85, 0.0, 0.0), leg_l=(-0.82, 0.0, 0.0),
                 leg_r=(0.82, 0.0, 0.0))
    run_b = dict(zero, spine=(0.16, 0.0, 0.0), arm_l=(-0.85, 0.0, 0.0),
                 arm_r=(0.85, 0.0, 0.0), leg_l=(0.82, 0.0, 0.0),
                 leg_r=(-0.82, 0.0, 0.0))
    action(rig, "run", [(1, zero), (6, run_a), (11, zero), (16, run_b), (21, zero)])
    fallen = dict(zero, root=(math.radians(82.0), 0.0, 0.12),
                  spine=(0.12, 0.0, -0.16), head=(-0.18, 0.0, 0.0),
                  arm_l=(0.35, 0.0, -0.45), arm_r=(-0.22, 0.0, 0.5),
                  leg_l=(0.22, 0.0, 0.0), leg_r=(-0.18, 0.0, 0.0))
    action(rig, "death", [(1, zero), (12, dict(zero, root=(0.4, 0.0, 0.04))),
                           (31, fallen)])
    rig.animation_data.action = None


def export(output):
    """Export only the declared collection with the shared explicit glTF settings."""
    import json

    settings = json.loads((ROOT / "tools/s01/export_settings.json").read_text())
    settings["collection"] = COLLECTION_NAME
    settings["export_animations"] = True
    settings["filepath"] = str(output)
    bpy.ops.export_scene.gltf(**settings)


def main():
    """Build, validate, save and explicitly export the technical source."""
    if bpy.app.version_string != "5.2.2 LTS":
        raise RuntimeError(f"expected Blender 5.2.2 LTS, got {bpy.app.version_string}")
    source = SOURCE
    output = EXPORT
    if "--" in sys.argv:
        arguments = sys.argv[sys.argv.index("--") + 1:]
        if arguments:
            source = Path(arguments[0]).resolve()
        if len(arguments) > 1:
            output = Path(arguments[1]).resolve()
    source.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.fps = 30
    collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(collection)
    body_material = material()
    definitions = [
        ("Torso", (0.56, 0.68, 0.32), (0.0, 1.02, 0.0)),
        ("Pelvis", (0.50, 0.30, 0.30), (0.0, 0.58, 0.0)),
        ("Head", (0.48, 0.44, 0.44), (0.0, 1.58, -0.015)),
        ("Arm_L", (0.20, 0.64, 0.22), (-0.40, 1.03, 0.0)),
        ("Arm_R", (0.20, 0.64, 0.22), (0.40, 1.03, 0.0)),
        ("Leg_L", (0.22, 0.58, 0.25), (-0.15, 0.30, 0.0)),
        ("Leg_R", (0.22, 0.58, 0.25), (0.15, 0.30, 0.0)),
        ("Foot_L", (0.24, 0.14, 0.40), (-0.15, 0.07, -0.09)),
        ("Foot_R", (0.24, 0.14, 0.40), (0.15, 0.07, -0.09)),
    ]
    parts = [box(collection, body_material, *definition) for definition in definitions]
    rig = make_rig(collection)
    mesh = skin(parts, rig)
    make_actions(rig)
    triangle_count = sum(len(polygon.vertices) - 2 for polygon in mesh.data.polygons)
    if triangle_count >= 1500:
        raise RuntimeError(f"triangle budget exceeded: {triangle_count}")
    bpy.context.scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(source))
    export(output)
    print("S13_AUTHORED", source, output, "triangles", triangle_count,
          "blender", bpy.app.version_string)


if __name__ == "__main__":
    main()
