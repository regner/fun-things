"""Original worker skin and NPC motion authoring; canonical player rig is appended unchanged."""

import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[4]
CONTRACT = ROOT / "art/source/models/characters/shared_humanoid/shared_humanoid_v1.json"
CLIPS = {"idle": 60, "walk": 30, "run": 24, "death": 48}


def smooth(low, high, value):
    """Ease a spatial weight or animation phase across a bounded interval."""
    t = max(0.0, min(1.0, (value - low) / (high - low)))
    return t * t * (3 - 2 * t)


def append_rig(collection):
    """Append only the immutable canonical armature, never the technical skin."""
    source = ROOT / "art/source/models/characters/shared_humanoid/shared_humanoid_v1.blend"
    with bpy.data.libraries.load(str(source), link=False) as (available, appended):
        assert "Rig" in available.objects
        appended.objects = ["Rig"]
    rig = appended.objects[0]
    collection.objects.link(rig)
    rig.show_in_front = True
    rig.animation_data_clear()
    rig["contract"] = "shared_humanoid/1.0.0"
    return rig


def map_segment(point, old_a, old_b, new_a, new_b):
    """Fit limb vertices along the canonical rest segment without scaling its thickness."""
    old_a, old_b, new_a, new_b = map(Vector, (old_a, old_b, new_a, new_b))
    axis = (old_b - old_a).normalized()
    offset = point - old_a
    along = offset.dot(axis)
    radial = offset - axis * along
    rotation = axis.rotation_difference((new_b - new_a).normalized())
    return new_a + (new_b - new_a) * (along / (old_b - old_a).length) + rotation @ radial


def write_weights(object_, vertex, weights):
    """Store normalized named influences, dropping only numerical zero weights."""
    positive = {name: weight for name, weight in weights.items() if weight > 1e-6}
    total = sum(positive.values())
    assert 0 < len(positive) <= 4
    for name, value in positive.items():
        group = object_.vertex_groups.get(name) or object_.vertex_groups.new(name=name)
        group.add([vertex.index], value / total, "REPLACE")


def fit_and_weight(parts, rig):
    """Fit the approved source masses to fixed joints and skin weighted transitions."""
    for object_ in parts.objects:
        name = object_.name
        suffix = "r" if name.endswith("R") or "R0." in name else "l"
        side = 1 if suffix == "r" else -1
        arm = name.startswith(("JacketSleeve", "RolledCuff", "Forearm", "Hand", "Thumb"))
        if arm:
            old_shoulder = (side * .274, 0, 1.326)
            old_elbow = (side * .394, 0, 1.093)
            old_wrist = (side * .427, .006, .905)
            upper = rig.data.bones["upper_arm_" + suffix]
            forearm = rig.data.bones["forearm_" + suffix]
            hand = rig.data.bones["hand_" + suffix]
            for vertex in object_.data.vertices:
                if name.startswith(("JacketSleeve", "RolledCuff")):
                    vertex.co = map_segment(vertex.co, old_shoulder, old_elbow,
                                            upper.head_local, upper.tail_local)
                elif name.startswith("Forearm"):
                    vertex.co = map_segment(vertex.co, old_elbow, old_wrist,
                                            forearm.head_local, forearm.tail_local)
                elif name.startswith("Hand"):
                    vertex.co = map_segment(vertex.co, old_wrist,
                                            (side * .431, .012, .814),
                                            hand.head_local, hand.tail_local)
                else:
                    old_center = Vector((side * .390, .060, .893))
                    thumb = rig.data.bones["thumb_" + suffix]
                    center = (thumb.head_local + thumb.tail_local) * .5
                    vertex.co = center + vertex.co - old_center
        for vertex in object_.data.vertices:
            p = vertex.co
            if name.startswith("JacketSleeve"):
                bone = rig.data.bones["upper_arm_" + suffix]
                t = (p - bone.head_local).dot((bone.tail_local - bone.head_local).normalized())
                chest = 1 - smooth(-.035, .075, t)
                elbow = smooth(bone.length - .075, bone.length + .055, t)
                weights = {"chest": chest * .5, "upper_arm_" + suffix: 1 - chest * .5 - elbow,
                           "forearm_" + suffix: elbow}
            elif name.startswith("RolledCuff"):
                weights = {"upper_arm_" + suffix: .35, "forearm_" + suffix: .65}
            elif name.startswith("Forearm"):
                bone = rig.data.bones["forearm_" + suffix]
                t = (p - bone.head_local).dot((bone.tail_local - bone.head_local).normalized())
                upper = (1 - smooth(-.025, .065, t)) * .3
                hand_weight = smooth(bone.length - .045, bone.length + .03, t) * .5
                weights = {"upper_arm_" + suffix: upper,
                           "forearm_" + suffix: 1 - upper - hand_weight,
                           "hand_" + suffix: hand_weight}
            elif name.startswith("Hand"):
                weights = {"hand_" + suffix: 1}
            elif name.startswith("Thumb"):
                weights = {"thumb_" + suffix: 1}
            elif name.startswith("TrouserLeg"):
                thigh = smooth(.42, .59, p.z)
                pelvis = smooth(.78, .92, p.z)
                foot = (1 - smooth(.12, .24, p.z)) * .6
                weights = {"pelvis": pelvis, "thigh_" + suffix: thigh * (1 - pelvis),
                           "shin_" + suffix: (1 - thigh) * (1 - foot),
                           "foot_" + suffix: foot}
            elif name.startswith("Boot"):
                toe = smooth(.13, .24, p.y) * .65
                weights = {"foot_" + suffix: 1 - toe, "toe_" + suffix: toe}
            elif name == "TrouserSeat":
                weights = {"pelvis": 1}
            elif name == "Jacket":
                lower = 1 - smooth(.94, 1.14, p.z)
                upper = smooth(1.12, 1.32, p.z)
                weights = {"pelvis": lower, "spine": max(0, 1 - lower - upper), "chest": upper}
            elif name.startswith("Collar"):
                weights = {"chest": 1}
            elif name == "Neck":
                head = smooth(1.43, 1.50, p.z)
                weights = {"neck": 1 - head, "head": head}
            else:
                weights = {"head": 1}
            write_weights(object_, vertex, weights)


def bind_mesh(mesh, rig):
    """Bind the single render mesh to the appended rig with identity object transforms."""
    mesh.parent = rig
    mesh.matrix_parent_inverse = Matrix.Identity(4)
    modifier = mesh.modifiers.new("SharedHumanoidSkin", "ARMATURE")
    modifier.object = rig
    modifier.use_deform_preserve_volume = False


def rotation(axis, degrees):
    """Construct a world-space anatomical rotation in authored Blender axes."""
    return Quaternion(Vector(axis), math.radians(degrees))


def aim(bone, direction):
    """Find an absolute pose orientation from the canonical rest segment."""
    delta = (bone.tail_local - bone.head_local).normalized().rotation_difference(direction.normalized())
    return delta @ bone.matrix_local.to_quaternion()


def walking_pose(rig, phase, running=False):
    """Author in-place foot trajectories with analytically bent knees and relaxed arm swing."""
    orientations = {}
    amplitude = .29 if running else .20
    lift = .18 if running else .095
    pelvis_offset = -.105 if running else -.045
    pelvis_offset += (.018 if running else .009) * math.cos(phase * math.tau * 2)
    for side, suffix in [(1, "r"), (-1, "l")]:
        cycle = (phase + (0 if side == 1 else .5)) % 1
        if cycle < .5:
            y = amplitude * (1 - 4 * cycle)
            z = .12
        else:
            swing = (cycle - .5) * 2
            y = -amplitude + 2 * amplitude * smooth(0, 1, swing)
            z = .12 + lift * math.sin(math.pi * swing)
        thigh = rig.data.bones["thigh_" + suffix]
        shin = rig.data.bones["shin_" + suffix]
        hip = thigh.head_local + Vector((0, 0, pelvis_offset))
        ankle = Vector((side * .14, y, z))
        ray = ankle - hip
        distance = min(ray.length, thigh.length + shin.length - .001)
        axis = ray.normalized()
        along = (thigh.length ** 2 - shin.length ** 2 + distance ** 2) / (2 * distance)
        forward = (Vector((0, 1, 0)) - axis * axis.y).normalized()
        knee = hip + axis * along + forward * math.sqrt(max(0, thigh.length ** 2 - along ** 2))
        orientations[thigh.name] = aim(thigh, knee - hip)
        orientations[shin.name] = aim(shin, ankle - knee)
        foot = rig.data.bones["foot_" + suffix]
        orientations[foot.name] = foot.matrix_local.to_quaternion()
        upper = rig.data.bones["upper_arm_" + suffix]
        forearm = rig.data.bones["forearm_" + suffix]
        swing_angle = -(38 if running else 23) * math.cos(cycle * math.tau)
        orientations[upper.name] = (rotation((1, 0, 0), swing_angle) @
                                    rotation((0, 1, 0), side * 37) @
                                    upper.matrix_local.to_quaternion())
        orientations[forearm.name] = (rotation((1, 0, 0), swing_angle + (55 if running else 17)) @
                                      rotation((0, 1, 0), side * 37) @
                                      forearm.matrix_local.to_quaternion())
    return orientations, Vector((0, 0, pelvis_offset))


def apply_pose(rig, orientations, pelvis_offset, death_angle=0):
    """Convert absolute anatomical orientations into bone-local channels without editing rest."""
    posed = {}
    fall = rotation((1, 0, 0), death_angle)
    for bone in rig.data.bones:
        pb = rig.pose.bones[bone.name]
        rest = bone.matrix_local
        parent = bone.parent
        inherited = posed[parent.name] @ parent.matrix_local.inverted() @ rest if parent else rest
        basis = Matrix.Identity(4)
        if bone.name in orientations:
            desired = orientations[bone.name]
            if death_angle and bone.name != "root":
                desired = fall @ desired
            basis = inherited.to_quaternion().inverted().to_matrix().to_4x4() @ desired.to_matrix().to_4x4()
        if bone.name == "pelvis":
            basis = inherited.to_quaternion().inverted().to_matrix().to_4x4() @ (fall @ rest.to_quaternion()).to_matrix().to_4x4()
            basis.translation = inherited.to_3x3().inverted() @ pelvis_offset
        pb.rotation_mode = "QUATERNION"
        pb.location = basis.translation
        pb.rotation_quaternion = basis.to_quaternion()
        pb.scale = (1, 1, 1)
        posed[bone.name] = inherited @ basis


def author_clips(rig):
    """Store four original NPC actions on the common skeleton, wholly separate from player clips."""
    scene = bpy.context.scene
    scene.render.fps = 30
    rig.animation_data_create()
    for name, end in CLIPS.items():
        rig.animation_data.action = None
        action = bpy.data.actions.new(name)
        action.use_fake_user = True
        rig.animation_data.action = action
        for frame in range(end + 1):
            phase = frame / end
            orientations, offset = walking_pose(rig, phase if name in ("walk", "run") else .25,
                                                 name == "run")
            angle = 0
            if name == "idle" or name == "death":
                # The idle starts and ends with planted feet and a gentle breathing arc.
                orientations, offset = walking_pose(rig, .25)
                offset = Vector((0, 0, 0))
                for part in ("thigh", "shin", "foot"):
                    for suffix in ("r", "l"):
                        bone = rig.data.bones[part + "_" + suffix]
                        orientations[bone.name] = bone.matrix_local.to_quaternion()
                motion_phase = phase if name == "idle" else min(phase, .8)
                for side, suffix in [(1, "r"), (-1, "l")]:
                    for part, bend in [("upper_arm", 0), ("forearm", 14)]:
                        bone = rig.data.bones[part + "_" + suffix]
                        orientations[bone.name] = (rotation((1, 0, 0), bend + 2 * math.sin(motion_phase * math.tau)) @
                                                    rotation((0, 1, 0), side * 37) @
                                                    bone.matrix_local.to_quaternion())
                if name == "idle":
                    chest = rig.data.bones["chest"]
                    orientations["chest"] = rotation((1, 0, 0), 1.2 * math.sin(phase * math.tau)) @ chest.matrix_local.to_quaternion()
                else:
                    fall = smooth(.08, .80, phase)
                    angle = 90 * fall
                    # Presentation pelvis falls; the ground/simulation root never moves.
                    offset = Vector((0, -.24 * fall, -.735 * fall))
                    for part in ("thigh", "shin", "foot"):
                        for suffix in ("r", "l"):
                            bone = rig.data.bones[part + "_" + suffix]
                            orientations[bone.name] = bone.matrix_local.to_quaternion()
            apply_pose(rig, orientations, offset, angle)
            if name == "death":
                # Fit the authored fall to the ground without moving the simulation root.
                bpy.context.view_layer.update()
                evaluated = bpy.data.objects["WorkerMesh"].evaluated_get(bpy.context.evaluated_depsgraph_get())
                minimum = min(v.co.z for v in evaluated.data.vertices)
                offset.z += .003 - minimum
                apply_pose(rig, orientations, offset, angle)
            for pb in rig.pose.bones:
                pb.keyframe_insert("location", frame=frame, group=pb.name)
                pb.keyframe_insert("rotation_quaternion", frame=frame, group=pb.name)
                pb.keyframe_insert("scale", frame=frame, group=pb.name)
        action["scope"] = "NPC only; shared_humanoid/1.0.0"
        action["loop"] = name != "death"
        track = rig.animation_data.nla_tracks.new()
        track.name = "NPC_" + name
        strip = track.strips.new(name, 0, action)
        strip.action_slot = rig.animation_data.action_slot
        track.mute = True
    rig.animation_data.action = None
    for pb in rig.pose.bones:
        pb.matrix_basis.identity()
    scene.frame_set(0)
    scene.frame_end = 60


def validate(mesh, rig):
    """Compare rest matrices to the immutable contract and audit every normalized skin vertex."""
    contract = json.loads(CONTRACT.read_text())
    assert len(rig.data.bones) == 28
    maximum = 0
    for row in contract["bones"]:
        bone = rig.data.bones[row["name"]]
        assert (bone.parent.name if bone.parent else None) == row["parent"]
        expected = row["matrix_blender_armature"]
        error = max(abs(bone.matrix_local[i][j] - expected[i][j]) for i in range(4) for j in range(4))
        maximum = max(maximum, error)
        assert error < 1e-7
    for vertex in mesh.data.vertices:
        assert 1 <= len(vertex.groups) <= 4
        assert abs(sum(group.weight for group in vertex.groups) - 1) < 1e-5
        assert all(mesh.vertex_groups[group.group].name in rig.data.bones for group in vertex.groups)
    return {"contract": contract["contract"], "rest_sha256": contract["rest_sha256"],
            "max_rest_matrix_error": maximum, "bones": 28, "weighted_vertices": len(mesh.data.vertices),
            "max_influences": max(len(v.groups) for v in mesh.data.vertices),
            "clips_seconds": {name: frames / 30 for name, frames in CLIPS.items()}}
