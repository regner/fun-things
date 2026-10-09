# Coral Courier — approved production asset

Regner selected concept A on 9 October 2026 and explicitly chose **one shared skeleton,
separate player and NPC animation libraries**. Future player skins replace the mesh and
inverse-bind resource while retaining the existing skeleton and animation players.

**Status: owner approved for local-main integration on 9 October 2026.** Source,
import, skin swapping, motion playback and stationary weapon contact checks are complete. Gameplay, networking, full-city readability and device
performance belong to the external integrator and are not accepted here.

[Review gallery and motion recording](gallery.html) ·
[Shared binding contract](../shared_humanoid_rig.md) ·
approved concept (image retained at commit `80d0f24`)

## Deliverables and source linkage

| Source | Explicit output / consumer |
| --- | --- |
| `art/source/models/characters/coral_courier/coral_courier.blend`, collection `export_coral_courier` | `art/models/characters/coral_courier/coral_courier.glb`; linked by `scenes/prefabs/player_character/coral_courier.tscn` |
| `art/source/models/characters/shared_humanoid/shared_humanoid_player_motion_v1.blend`, collection `export_shared_humanoid_player_v1` | `art/models/characters/shared_humanoid/shared_humanoid_player_motion_v1.glb`; extracted `art/animations/characters/shared_humanoid/player_v1.tres` |
| The same saved actions, with disjoint track filtering only | `player_upper_v1.tres` and `player_lower_v1.tres` in that animation directory |
| `art/source/models/characters/coral_courier/weapon_profiles.json` | Authored hand-to-grip matrices, saved as wrapper metadata and selected at `Sockets/WeaponMount` |
| Canonical rig checkpoint `3eccf8f691fe34132ee8504d10dfceda4f7e2bb6` | Exact unchanged `shared_humanoid/1.0.0` rest hierarchy; 28 bones |

The model has 5,942 source vertices, 11,600 triangles, twelve opaque PBR material slots,
UVMap coordinates and no external textures. Broad material colours are intentional;
no texture maps are required. Source JSON lists the stable semantic material names.
Weights are normalized, named, and at most two influences per vertex. The latest audit
finds zero degenerate triangles and the exact canonical rest fingerprint. No collision
or gameplay components are added to this presentation-only prefab.

The mesh and motion are original player-lead authorship under verified GPT-6-Astra/high.
Bootstrap instructions and authored numerical choices are preserved in
`tools/assets/characters/coral_courier/author_coral_courier.py` and `author_motion.py`. Subsequent
reexport reads the saved `.blend` through `reexport.py`; it does not reconstruct geometry.
Concept image prompts/provenance remain in the concept directory. No real brands,
external character/rig library, or third-party texture source is used.

## Player animation contract

All clips are in place, baked at 30 FPS. `root` remains fixed; presentation pelvis motion
includes gait bob and death collapse. There are no gameplay events or authoritative
movement tracks. The full library resets all 28 bones with 84 transform channels.

| Clips | Duration | Loop |
| --- | --- | --- |
| `idle` | 2 s | yes |
| `walk`, `walk_back`, `walk_left`, `walk_right` | 1 s | yes |
| `run`, `run_back`, `run_left`, `run_right` | 0.8 s | yes |
| `death` | 1.2 s | no, final pose retained |
| `pistol_hold`, `smg_hold`, `launcher_hold` | 2 s | yes |
| `pistol_walk`, `smg_walk`, `launcher_walk` | 1 s | yes |
| `pistol_run`, `smg_run`, `launcher_run` | 0.8 s | yes |
| `pistol_fire`, `smg_fire` | 0.4 s | no |
| `launcher_fire` | 0.7 s | no |
| `pistol_reload` / `smg_reload` | 1.4 / 1.7 s | no |

No launcher reload is required by its static weapon handoff. Reload clips are player
hand gestures; weapon mechanism/magazine changes and event timing are integrator-owned.
NPC motion is separately owned by the pedestrian track, accepted at
`211df6e72e80d791521d91fa70cd80425366ec35`; its library is
`art/animations/characters/pedestrian_worker/npc_locomotion_v1.tres`. No competing NPC library
is shipped in this player checkpoint.

`PlayerCharacterVisual.play_clip(name)` selects a full-body clip. `play_layered(lower,
upper)` uses complementary bone tracks: lower contains root/pelvis/spine/legs, upper
contains chest/neck/head/clavicles/arms/hands. For example, `walk_left` + `smg_hold`
allows locomotion relative to the aimed character heading. The integrator owns heading,
blend timing, movement speed and authoritative state. These are animation assets and
presentation APIs, not a player controller or a gameplay AnimationTree.

## Skins and attachments

`apply_skin(PackedScene)` accepts one skinned mesh on the exact canonical skeleton,
with identity object ancestry, matching ordered bones/parents/rests and valid inverse
binds. It swaps only Mesh/Skin resources. A technical BindTemplate swap and restoration
prove different geometry can retain Skeleton3D identity, AnimationPlayer identity and
playback time. The exported `appearance` property is also exercised before `_ready()`;
its startup swap runs outside assertions, so release assertion removal cannot skip it. S13 and transformed candidates are rejected. This does not certify
unseen skins or different proportions; each new skin needs its own deformation check.

Right hand is dominant; left hand supports SMG/launcher; right shoulder is used for
stock/pad contact. `select_grip(&"pistol" | &"smg" | &"launcher")` selects source-authored
bone-to-grip data on `Sockets/WeaponMount`. Attach the weapon's existing wrapper there,
with identity transform. Its own `Sockets/Muzzle` remains the muzzle authority. Bone
local axes are not the weapon frame; tests establish the converted grip frame is
Godot -Z front / +Y up. Do not substitute wrist origins for weapon surface contacts.

Measured immutable weapon inputs and SHA256s are retained in
[evidence/weapon_dependencies.json](evidence/weapon_dependencies.json). Their GLBs were
staged temporarily from Git objects solely for the asset-local fit scene. No peer source
was edited, no duplicated weapon assets are part of this deliverable, and no combined
game implementation was created. `stage_weapon_fits.py` reproduces this staging. The
editor bridge builds and saves the temporary fit scene; it requires an editable
project-owned Courier wrapper instance to retain its added weapon children.

Current captures prove attachment playback and the source/import grip conversion.
A source-mesh ray/nearest-surface check places the SMG shoulder contact 2.69 mm within
its cloth surface, the launcher pad 0.40 mm within its shoulder surface, and both support
palms 2.62 mm from their weapon markers. These small clearances are within the declared
5 mm static fit tolerance. Launcher head/weapon horizontal bounds have 6.72 mm clearance.
See [measured contacts](evidence/weapon_contacts.json), reproduced by
`audit_weapon_contacts.py`. A slight launcher head lean is animated; no rest bones moved.
These are stationary fitted-pose checks, not gameplay collision or universal skin fit.
Fire recovery intentionally releases/compresses the shoulder contact; reload hands leave
the support target. Gameplay timing, weapon effects and combined movement/aim acceptance
remain external integration work.

## Preview and checks

Open `scenes/prefabs/player_character/preview.tscn` and run that scene: Left/Right cycles
clips; Tab switches close/game camera. Preview caps at 60 FPS with VSync. Saved game
camera: vertically down, north up, height 47 m, FOV 42°, near 0.1 m, far 160 m. Captures
are native 1280×800, Forward+ Vulkan on GTX 1070. Close camera is at
(-2.7,2.1,-3.9) m, looking at (0,0.95,0), FOV 32°; this support-side view keeps
the launcher wearer’s face visible. They use unchanged source-linked S02
ground (`art/source/models/spikes/s02_kit.blend` provenance in S02), not city placement.

- Saved-source skin and motion reexports are byte-identical to committed candidates.
- Fresh isolated Godot 4.8.dev7 asset profile imports without errors/warnings.
- 24 clips pass duration, loop endpoint, finite-transform and fixed-root checks. Every
  extracted animation key is compared against the current imported motion GLB.
- Skin swapping, clip reset coverage, disjoint layer writers and authored grip transforms pass.
- Source deformation bounds are sampled every three frames. Death settles 2.5 mm above
  the source ground plane; no sampled pose goes below the plane.
- Editor wrapper/preview save and reopen completed. No detached runtime visible mesh
  generation or embedded model replacement was introduced.
- Pinned gdstyle scoped lint passes. Initial independent findings and the review fix are retained below.

Reproduce source/export and clean asset checks with `python tools/assets/characters/coral_courier/verify_delivery.py`.
The fresh profile excludes gameplay/addons and is not full-project compilation or Deck
performance evidence. The original worktree runtime captures include the actual project
renderer and saved scenes. Source checks, logs, captures and recording are in `evidence/`.

## Independent review follow-up

The [initial independent Sol 6.1/high audit](evidence/independent-review/initial-review.md)
reviewed immutable `4f92259c127c8051350448faf41ee430ae582fc8` against baseline
`c030d66d7d0a9db19c0c2aebf1aa2b83eded6275`. It found one P2: an Inspector-selected
skin was applied inside a debug assertion. The startup call now executes outside
assertions, with a regression check for initialization through the exported property.
No matching release export template was available; no packaged release run is claimed.

The review also requested armed-action visual evidence. `armed_close/game.mp4` show
all eleven weapon walk/run/fire/reload clips at full duration, and
`layered_close/game.mp4` show eight directional lower-body + weapon upper-body pairs.
The capture logs record ordered clips, frame offsets and durations; all are sampled
at 30 FPS from saved animation resources, using the same immutable weapon dependencies.
The source/rest/keyframes did not change in this review follow-up. These recordings
cover asset deformation and hand/recovery paths, not gameplay event timing or blends.
The owner subsequently approved local-main integration and explicitly waived further
review unless rebase file conflicts occur. Rebase onto `43e593c81d009151794eee8b90491b4cf996e83a`
completed without conflicts; player asset content remained byte-identical to the
review-fix candidate `93e815136a0fae43268b5ea008919e81c9776b0e`. No new review gate is imposed.
The already-running delta review is advisory to this owner-authorized integration.

## Runtime routing checkpoint — 9 October 2026

Owner instruction: “Any time any of those workspaces are doing modeling or animation
work they should be using the Astra model. Work in Godot that doesn't need spatial
awarness, such as configuring animations and rigs or importing models, can use Sol 6.1.”

Spatial authoring was performed after runtime receipts reported `gpt-6-astra/high`.
At the next planned spatial fit pass, runtime verification unexpectedly returned
`gpt-6-luna/high` despite the configured Astra lead. No further geometry, rest, pose or
keyframe mutation proceeded after that receipt. Sources/editor state and bounded capture results were preserved. A subsequent active-turn
receipt confirmed `gpt-6-astra/high`; the spatial contact correction then proceeded under
Astra. The initial independent audit and technical follow-up are recorded above.

## Catalogue / TODO reconciliation delta for the integrator

- Add `coral_courier` → this handoff, selected concept A, owner-approved production asset.
- Add shared rig `shared_humanoid/1.0.0` → `docs/assets/shared_humanoid_rig.md`; canonical
  skeleton shared with pedestrian, separate libraries.
- Remaining external acceptance: gameplay/network/city/device integration.

Shared catalogue, TODO, planning and main launch scene were not edited. The owner
explicitly authorized a rebase and fast-forward into local main; no remote push or
workspace archival is authorized. Unrelated main-worktree changes and the private
editor/temporary fit scene are preserved.
