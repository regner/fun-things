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

**No production clips are ready for reuse at this first binding checkpoint.**
The source/export contains no animations. Subsequent motion sources and libraries
will be separate for `npc` and `player`, on these same rest transforms.
NPC coverage: in-place looping idle/walk/run with elbow/knee motion; one-shot death
retaining final pose. Player additionally needs weapon holding/aiming while stationary
and moving, independent move/aim directions, pistol/SMG reload and weapon firing
recovery. Exact clip names/source frame ranges and import-loop evidence follow with
those deliverables. Root `root` and gameplay simulation transforms never receive
locomotion translation or gameplay events; death may animate the presentation pelvis.

Weapon pose convention: right dominant hand, left support, right shoulder for SMG/
launcher. `socket_grip` / `socket_muzzle` remain weapon-owned source markers;
`Sockets/WeaponMount` / `Sockets/Muzzle` remain prefab-facing contracts. A hand bone's
local basis is **not** the weapon frame. Player-owned bone-to-grip offsets and hand
pose are still pending fit checks. Weapon contact markers use -Z front/+Y up and
identify contact surfaces; surface normals are supplied separately. Do not substitute
wrist origins for those markers or infer production offsets from S02/S13.

Measured candidate inputs:

- Coral Stub `b8363f55a6cfe8ab6cf02b1458a3d193629de59b`: pivot zero, handle width
  0.117–0.122 m, muzzle (0,0.122,-0.421) m. Optional support cups the same grip;
  no shoulder contact. Its technical-mannequin preview is not player fit acceptance.
- Dock Thumper (reviewed revision forthcoming): grip cross-section 0.090 X × 0.100 Z m,
  Y range [-0.075,0.175]. Support (0,-0.0825,-0.430) m, shoulder (0,0.085,0.280) m,
  both contact normals (0,-1,0); muzzle (0,0.300,-0.905) m. Full visual AABB minimum
  (-0.203,-0.0825,-0.900), size (0.406,0.585,1.430) m. Hold/aim/fire recovery only;
  no launcher reload animation required.
- Wedgewire selected: grip/support/stock shoulder contact; exact exported contact
  measurements still awaited.

## Checks and consumers

Blender 5.2.2 LTS / build d13f752e3b9c; explicit S01 GLB settings. Initial inspection
found exactly 28 exported joints, one skin, no animation, images or GLB extensions.
Fresh saved-source reexport was byte-identical. Godot imported all 28 joint names,
parents and global rest origins within 0.00001 m; see
[player evidence](player_character/evidence/rig_checkpoint.json). Motion/skin-swapping
evidence remains pending; no import alone establishes production motion or gameplay.

Consumers: player Coral Courier and pedestrian Off-Shift Worker (pedestrian-owned
mesh). No existing S13 consumer is migrated. The original source is project-owned,
with no external rig/mesh/texture library. Source is under the committed `.gdignore`.
Production completion requires source/export freshness, UID/import metadata, rig/skin
compatibility checks, actual-camera animation/attachment review, saved scene roundtrip
and one clean-context independent review. Gameplay/network/Deck acceptance belongs to
later integration and is not claimed by this binding checkpoint.
