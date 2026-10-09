# Shared humanoid rig — v1 binding contract

9 October 2026. Player lead owns this contract and `art/source/models/shared_humanoid/`.
Regner approved Coral Courier and explicitly selected **one underlying skeleton with
separate player and NPC animation libraries**, including interchangeable future player
skins. Spatial authoring uses verified `gpt-6-astra/high`; technical imports/configuration
may use Sol 6.1. S13 remains an unchanged technical fixture and is not a compatible rig.

## Binding checkpoint

Contract ID **`shared_humanoid/1.0.0`**. This first checkpoint freezes the 28-bone rest
hierarchy for skin authoring; it does not accept production motion or weapon fit.
The authoritative numeric source/export map and every armature-space rest matrix are in
[`shared_humanoid_v1.json`](../../art/source/models/shared_humanoid/shared_humanoid_v1.json).
Rest SHA256: `df5a1e7117a9de8800df2ab5766f70e8018700878dd5bc84877b86767abc25c9`.

| File | Role |
| --- | --- |
| `art/source/models/shared_humanoid/shared_humanoid_v1.blend` | Canonical `Rig` armature, A-pose; original player-lead authorship |
| `art/source/models/shared_humanoid/shared_humanoid_v1.json` | Exact ordered names/parents/Blender rest matrices, compatibility fingerprint |
| `art/models/shared_humanoid/shared_humanoid_bind_v1.glb` | Explicit `export_shared_humanoid_bind_v1` collection; `Rig` plus technical `BindTemplate` |
| `tools/player_character/author_shared_rig.py` | Original bootstrap prompt-as-code; not a runtime or reexport geometry generator |
| `tools/player_character/reexport.py` | Reexport saved source; does not reconstruct geometry |

Append/copy the canonical **Rig object and armature datablock** from the saved blend
into an owned skin source. Preserve armature object identity transform and the exact
rest data. Skin meshes may be entirely different geometry/materials, but bind in this
A-pose. Never resize or re-roll the skeleton to fit clothing. Adjust vertices instead.
No automatic retargeting is assumed. The technical `BindTemplate` mesh is a rest/clip
carrier only; it is not player or pedestrian production art and need not be copied.

Metres, Blender +Z up/+Y front; one glTF Y-up conversion gives Godot +Y up/-Z forward.
+X denotes the character's authored right; `r` bones lie at positive X in rest, `l`
at negative X. Origin at ground between feet; reference height 1.8 m. Rig/object
roots have identity rotation/location and unit positive scale. No root correction
rotation/scale is allowed. Per-skin mesh origins/transforms must also be identity.

Hierarchy:

```text
root
└── pelvis
    ├── spine → chest → neck → head
    │            ├── clavicle_r → upper_arm_r → forearm_r → hand_r
    │            │                                            ├── thumb_r
    │            │                                            ├── index_r
    │            │                                            └── fingers_r
    │            └── clavicle_l → upper_arm_l → forearm_l → hand_l
    │                                                         ├── thumb_l
    │                                                         ├── index_l
    │                                                         └── fingers_l
    ├── thigh_r → shin_r → foot_r → toe_r
    └── thigh_l → shin_l → foot_l → toe_l
```

The single thumb/index/grouped-finger segments are intentionally simple stylized
controls, not a detailed hand or facial rig. Head covers face/hair; clothing follows
body joints. No cloth simulation, accessory bones or facial animation is required.
All edit bones have roll zero in the authored Blender definition; **the saved matrices,
not that sentence, are the binding authority**. Bone directions differ across limbs.

Skin requirements: named vertex groups map to these bones; normalized weights, at
most four influences per vertex, no unweighted vertices, no negative weights. Use
weighted elbow/knee/shoulder/hip transitions where the mesh spans joints; rigid
accessories may use one influence. Preserve inverse binds and validate imported
rest matrices by name, not exporter-dependent joint index. Rest/parent/name changes
are breaking: issue a new contract and coordinate every skin/clip/attachment.
Palette/material variants do not change rig compatibility. Different body proportions
must preserve joint locations or be treated as a new rig/retargeting task.

## Animation libraries and attachments

Player motion: `art/source/models/shared_humanoid/shared_humanoid_player_motion_v1.blend`
→ `art/models/shared_humanoid/shared_humanoid_player_motion_v1.glb` →
`art/animations/shared_humanoid/player_v1.tres`. It contains 24 full-body clips with
all 84 bone transform channels retained. `player_upper_v1.tres` and `player_lower_v1.tres`
filter those same keys into disjoint upper-body and locomotion tracks; they do not
invent motion. [Player handoff](player_character/README.md) lists durations, loops,
source collections, skin-swap API and the remaining external integration work.

The pedestrian owns its separate NPC idle/walk/run/death library at
`art/animations/pedestrian_civilian/npc_locomotion_v1.tres`, independently accepted at
`211df6e72e80d791521d91fa70cd80425366ec35`. Player motion does not overwrite NPC actions.
Both preserve these exact rest transforms. `root` never receives gameplay movement;
death animates only the presentation skeleton. Clip transitions/event timing and
combined gameplay movement/aim are integrator-owned.

Right hand is dominant, left hand supports SMG/launcher, right shoulder receives the
stock/pad. Source `socket_grip` and `socket_muzzle` remain weapon-owned. Player wrapper
`Sockets/WeaponMount` selects the authored offsets from
`art/source/models/player_character/weapon_profiles.json`; the equipped weapon wrapper
retains its own `Sockets/Muzzle`. Hand-bone local axes are not the weapon frame. The
source-to-import checks confirm -Z front / +Y up at the selected grip frame.

The current Coral Courier fit uses immutable Coral Stub, Wedgewire and Dock Thumper
static GLBs listed with revisions/hashes in
[player weapon dependencies](player_character/evidence/weapon_dependencies.json).
Stationary shoulder and support contacts are within 5 mm of the deformed skin surfaces;
launcher head lateral clearance is 6.72 mm. Source ray/nearest-surface measurements are
in [weapon contacts](player_character/evidence/weapon_contacts.json). These offsets fit
Coral Courier's skin. Another compatible skin must separately check garment/hand/head
clearance; shared rest compatibility alone does not accept unseen deformation or fit.
No S02/S13 wrist/rest assumptions were inherited. No launcher reload is required.

## Checks and consumers

Blender 5.2.2 LTS / build d13f752e3b9c; explicit S01 GLB settings. Initial inspection
found exactly 28 exported joints, one skin, no animation, images or GLB extensions.
Fresh saved-source reexport was byte-identical. Godot imported all 28 joint names,
parents and global rest origins within 0.00001 m; see
[player evidence](player_character/evidence/rig_checkpoint.json). Motion and skin-swapping checks now pass in the player candidate; see its evidence.
The initial player audit and its fixed P2 are retained in the player handoff. Regner
approved local-main integration with no further review gate absent rebase conflicts.
Import does not establish gameplay.

Consumers: player Coral Courier and pedestrian Off-Shift Worker (pedestrian-owned
mesh). No existing S13 consumer is migrated. The original source is project-owned,
with no external rig/mesh/texture library. Source is under the committed `.gdignore`.
Production completion requires source/export freshness, UID/import metadata, rig/skin
compatibility checks, actual-camera animation/attachment review, saved scene roundtrip
and one clean-context independent review. Gameplay/network/Deck acceptance belongs to
later integration and is not claimed by this binding checkpoint.
