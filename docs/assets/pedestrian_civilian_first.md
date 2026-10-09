# Off-Shift Worker — first civilian pedestrian

Status, 9 October 2026: approved concept C implemented as a reusable skinned
presentation asset. Technical and visual checks pass; **independent production
review accepted**, with no unresolved findings on `723ef39`. Gameplay, crowd spawning, collision, network and device/performance
acceptance belong to the external integrator.

[Production gallery](../concepts/assets-v1/pedestrian/production.html) ·
[Concept selection and prompts](../concepts/assets-v1/pedestrian/README.md) ·
[Shared rig contract](shared_humanoid_rig.md)

## Ownership, selection and provenance

Regner selected C with “OK, lets start with that and use option C, the shift worker”.
The unarmed worker has an amber work jacket, cobalt yoke, petrol cap, slate trousers,
chunky boots and no carried props. There are no real brands. This worker is one
silhouette; colour variants do not constitute additional character models.

The pedestrian lead produced the concept sheets using OpenAI imagegen (exact prompts,
output hashes and tool receipts beside the gallery), and authored original Blender
geometry, vertex-region mask, skin weights and NPC clips. No external model, rig,
texture, motion-capture or animation library was used. Blender primitive/sweep tools
and the committed authoring scripts are the original modelling/animation recipe.
The shared armature is original project work by the player lead, appended unchanged.
Regner approves art direction; the independent Sol 6.1 high reviewer accepted the scoped production handoff.
No main merge, push or gameplay integration is included.

Owner model policy: all modelling, skinning and animation work uses Astra. The
pedestrian agent's effective Paseo runtime reported `gpt-6-astra/high` before those
mutations, including the binding checkpoint. Non-spatial Godot configuration may use
Sol 6.1. The immutable dependency `3eccf8f691fe34132ee8504d10dfceda4f7e2bb6`
was cherry-picked unchanged as local `03b0177`; player-owned files remain untouched.
The earlier S13 seven-bone technical rig and its clips are not used.

## Source and runtime mapping

| Purpose | Owned path |
| --- | --- |
| Editable source; 48 source parts, appended canonical Rig, four NPC actions, source studio and preview floor | `art/source/models/pedestrian_civilian/pedestrian_worker_a.blend` |
| Collection `export_pedestrian_worker_a`: Rig + WorkerMesh | `art/models/pedestrian_civilian/pedestrian_worker_a.glb` + `.import` |
| Collection `export_pedestrian_worker_stage`: PreviewGround only | `art/models/pedestrian_civilian/pedestrian_worker_stage.glb` + `.import` |
| Palette shader and shared material | `art/materials/pedestrian_worker_a_palette.gdshader`, `.gdshader.uid`, `.tres` |
| NPC-only reusable library derived from the imported GLB actions | `art/animations/pedestrian_civilian/npc_locomotion_v1.tres` |
| Source-linked reusable presentation prefab | `scenes/prefabs/pedestrian_civilian/pedestrian_worker_a.tscn` |
| Presentation API | `scripts/presentation/pedestrian_civilian/pedestrian_worker_visual.gd` + `.uid` |
| Saved four-instance preview and bounded playback script | `tests/fixtures/pedestrian_civilian/pedestrian_worker_a_preview.tscn`, `pedestrian_worker_preview.gd` + `.uid` |
| Source authoring/export/checks and Godot authoring context | `tools/pedestrian_civilian/` |

Source `.gdignore` excludes Blender data from runtime import/export. The preview floor
is also Blender-authored. There are no runtime-generated visible meshes, gameplay
colliders, weapon sockets, actor AI or population rules. Wrapper structure is
`PresentationAnchor/Visuals/Model`, with Model remaining an imported GLB instance.
No direct imported-child override or embedded duplicate mesh appears in the prefab.
The four preview instances override wrapper palette/initial clip only; no inherited
asset variant is commissioned at this checkpoint.

## Shared rig, skin and clips

Uses `shared_humanoid/1.0.0`, exact 28-bone A-pose from the canonical source, rest
fingerprint `df5a1e7117a9de8800df2ab5766f70e8018700878dd5bc84877b86767abc25c9`.
Append Rig object + armature data; never append BindTemplate as production art.
All source rest matrices match exactly. Every render vertex has normalized named
weights; maximum observed influences is 2, below the contract limit of 4. Shoulders,
elbows, hips, knees and wrists have weighted transitions. Simple mitten-like hands
follow the hand bones; these civilian clips do not exercise individual finger poses.

NPC and player libraries are separate. `npc_locomotion_v1.tres` contains `idle` (2 s),
`walk` (1 s), `run` (0.8 s), and `death` (1.6 s), authored at 30 fps. The first three
loop with matching endpoint transforms. Death is a one-shot backward fall, with the
last 0.3 s held; Godot retains the pose after completion. Locomotion is in-place;
all clips keep bone `root` and the scene root fixed. Death moves only the presentation
pelvis. Clip tracks address `Rig/Skeleton3D:<bone>` relative to the imported model;
another compatible skin must preserve that animation-root/path mapping or explicitly
remap it. This checkpoint proves reuse by worker instances, not another production
skin's deformation quality. Player weapon animation reuse is neither needed nor claimed.

Use `play_clip("walk")`, `play_clip("run")`, `play_clip("idle")`, or
`play_clip("death")` on the presentation wrapper. The integrator decides when those
states apply. Replaying idle after death is a presentation request, not a gameplay
respawn. No animation track dispatches gameplay events or changes collision.

## Appearance and measured envelope

One shared shader material uses a constant face-region mask in vertex `COLOR.r`:
index / 8 for skin, jacket, yoke, trousers, cap, shirt, boots, trim, hair. The other
channels carry no appearance data. `apply_palette(PackedColorArray)` requires those
nine colours in order and writes per-instance shader uniforms. Inspector palette edits refresh the live
`@tool` instance through the same setter; invalid-length palettes are rejected.
Instances share the
same mesh and material without changing each other's colours. No textures or UV
maps are required for this deliberately flat-colour treatment. Blender's material
previews the same region mapping; the Godot wrapper applies the runtime shader.

Metres; Blender +Z up/+Y front becomes Godot +Y up/-Z front. Identity object roots;
origin at ground between the feet. Canonical reference is near 1.8 m; cap raises this
worker to 1.859 m. Godot A-pose AABB approximately min `(-0.769,0,-0.295)`, max
`(0.769,1.859,0.165)` m. The extended A-pose width is not an actor collision envelope.
Standing animated width is about 0.752 m. All sampled source poses stay within
0.000001 m of the ground tolerance, except the intentional 0.003 m fall clearance.
Combined death/locomotion source extrema are retained in `motion.json`; max height
1.864 m and forward/back span about 1.923 m. Gameplay clearance remains unaccepted.

7,360 Blender render-mesh vertices, 14,528 triangles, 9,030 exported vertices after
normal/region splits, one surface, one skin, 28 joints. No arbitrary crowd triangle
budget is claimed. Imported automatic LOD generation is enabled; actual crowd/device
cost and a stronger distant-silhouette variant remain measurement tasks.

The measured game view is native 1280×800, vertically down, north-up, perspective
47 m/42° (near .1 m, far 250 m). At that scale, hat/shoulder colour and facing dominate;
facial detail is only apparent in the closer overview. The floor and dusk lighting
are an asset-local review setup, not integrated city readability acceptance.

## Verification and editor receipt

Blender 5.2.2 LTS (`d13f752e3b9c`), S01 explicit GLB preset, with named vertex colour
and animation export enabled for the worker only. Freshly reopening the saved source
and exporting both declared collections produced byte-identical GLBs. See
[fingerprints](pedestrian_worker_a-evidence/fingerprints.json),
[source](pedestrian_worker_a-evidence/source.json), and
[all-frame motion checks](pedestrian_worker_a-evidence/motion.json).

Godot 4.8-dev7 `c971f93e7`: private editor PID 100062 bound to this worktree, editor
22650/runtime22651, XDG under `/tmp/brackett-pedestrian-production/`. The configured
MCP endpoint 6550 and Blender MCP were unavailable; source authoring used private
Blender CLI. Godot work then used the toolkit's authenticated private WebSocket
commands, without changing shared connector configuration. Scripts were written and
compile-checked by editor tools. The editor created resources/scenes, then refreshed,
saved, closed and reopened both prefab and preview with no discarded unsaved changes.
Saved resource UIDs and editor node identities are committed. The pinned headless
editor emits a dummy-renderer thumbnail `texture_2d_get` null-texture diagnostic on
save; native runtime and clean asset checks do not reproduce it.

[Native runtime check](pedestrian_worker_a-evidence/godot_checks.json) verifies all
28 names/parents/rest origins (maximum error 0.000000231 m), mesh/material sharing,
independent recolouring, live exported-palette updates and invalid-palette rejection,
clip API/loop policy/root
invariance, matching loop endpoints and retained death pose. A separate CPU check
reconstructs imported skin positions from Godot pose/bind matrices: sampled idle
contact is effectively zero, walk/run contact within 3.5 mm and death +3 mm, all
inside the 6 mm contact tolerance; see `imported_contact.json`. Forward+/Vulkan on
GTX 1070; previews capped at 60 fps/VSync and bounded. The default preview quits after
20 s. `-- --worker-overview` selects the closer view. The 20 fps review recording is
sampled playback, not a frame-rate/performance measurement.

A disposable private asset-only project performs a clean import and repeats the
resource checks without project addons or a populated import cache. Its scope does
not certify the full project's unrelated scripts, plugins or packaged game. Initial
sandbox socket setup and pre-refresh UID warnings were corrected before the retained
final checks. Source GLTF exporter reports unavailable optional MeshOptimizer; no
MeshOptimizer compression/extension is used. No remaining runtime error is suppressed. Pinned gdstyle reports no errors; its
19 warnings are confined to authoring/check tooling (long functions/lines and the
intentional frame-capture await loop). The runtime presentation/preview scripts
have no style warnings.

Run `check_source.py` inside pinned Blender with the saved source, and
`godot --path . --script res://tools/pedestrian_civilian/check_worker.gd` with a private
runtime port. `export_worker.py -- <scratch-directory>` exports from saved source
without reconstructing geometry. `author_worker.py` and `author_scenes.gd` are initial
creation recipes; do not rerun them over edited production sources/scenes merely to
refresh an export, as that can replace artist edits or node identities.

## Acceptance and integration delta

Accepted: Regner's concept C selection. Technical self-checks: source/export freshness,
rig/rest/weight rules, palette reuse, imported clips, source linkage and saved preview.
[Independent production review](pedestrian_worker_a-evidence/independent-review/review.md):
accepted on immutable `723ef39cac4bf193497dd6a4c07f7bc826d8dff5`, no unresolved findings.
The initial Inspector palette-refresh defect was fixed and independently rechecked.
Regner retains final art judgement. Pending external acceptance: integrator's collision, movement-speed/stride matching, clip transitions under actual
states, crowd variety/readability, lifecycle/network behavior and device performance.
No gameplay/network gate is closed by this preview.

Catalogue delta for later reconciliation: add `pedestrian_worker_a` → this record,
family `pedestrian_civilian`, concept C selected, source/prefab/preview paths above.
TODO delta: concept and first source/import/presentation implementation complete;
record independent production acceptance; retain external integration tasks and
Regner's final art judgement. Do not
close S13 or any other foundation item. Shared catalogue/TODO/planning files were
not edited in this worktree.
