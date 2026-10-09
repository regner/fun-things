# SMG concept checkpoint handoff

Date: 9 October 2026. Base: `c030d66d7d0a9db19c0c2aebf1aa2b83eded6275`.
Owned worktree: `/home/regner/.paseo/worktrees/0u71f39f/brackett-smg`.
Status: three concept sheets delivered; Regner selection awaited. No production
asset, gameplay implementation or integration acceptance is claimed.

## Owners and evidence

SMG brief/concept/source/export/prefab/local-preview owner: persistent SMG lead,
agent `c39c4577-4fa7-4fdf-9123-db3e81a3c554`. Art selection: Regner, pending.
Player/rig/holding owner: `7016b739-5eea-480c-afa3-2c0cbad484a2`.
Effects owner: `c9207bb9-925b-46e4-bd68-e37aaa66a617`.
Gameplay/world integrator: external person, identity and acceptance pending.
Independent production reviewer: to be assigned for immutable finished checkpoint,
Sol 6.1 medium/high per owner instruction. Initial concept self-review is in README.

Inspected canonical assets/scene contracts, parallel-art-production commissioning,
accepted world reference, S02 source handoff, `weapon_studies.tscn`, actor/muzzle
consumer and `tools/s02/export_members.json`. Existing `s02_smg` is a technical
fixture used by the weapon study, not a production family to overwrite. Its recorded
weak game-scale recognition is an explicit reason for these broader overhead cues.
No existing source, fixture, consumer or identity was modified.

Original authorship: this SMG lead wrote the exact prompts in `prompts.json`; built-in
`image_gen.imagegen` generated the three raster references. No third-party model,
texture or real brand incorporated. Concepts do not establish Blender provenance.
Files in this directory are review material, excluded from Godot import by `.gdignore`.

## Contract and dependencies

Grip origin, metres, positive unit roots; Blender +Y front/+Z up maps to Godot
-Z front/+Y up. Source markers `socket_grip` and `socket_muzzle`; stable weapon
wrapper `Sockets/Muzzle`. Player owns its `Sockets/WeaponMount` and rig; SMG does
not create competing shared rig sources or clip definitions. Support hand under
forward receiver and shoulder contact required; measured offsets await selection.
The inspected S13 seven-bone 1.8 m fixture has no hand sockets and is not a retarget rig.

Player and effects received the material dependency brief through Paseo background
messages with finish notification enabled. Effects confirmed no extra anchor;
directional muzzle flash originates at local muzzle origin with -Z/+Y axes. SMG
will supply measured aperture clearance and bounds after approval, with no firing
rules, damage, recoil rules or duplicate embedded VFX. Exact hand offsets/clip matrix
remain player-led. Production target humanoid near 1.8 m remains provisional.

## Tools and private resource boundary

Read-only availability probes during this concept checkpoint:

- `/usr/bin/blender --version`: 5.2.2 LTS, build `d13f752e3b9c`, matching source pin.
- Pinned local Godot executable: `.local/share/mise/installs/` under the user's home,
  `github-godotengine-godot-builds/4.8-dev7/godot`; `--version` returned
  `4.8.dev7.official.c971f93e7`.
- Godot MCP editor read `ProjectSettings.globalize_path('res://')` failed with
  `ECONNREFUSED 127.0.0.1:6550`. No bound project identity established; no writes.
- Blender MCP addon/scene reads could not connect. No live file/process ownership
  established; no writes. A private local authoring process remains available later.
- Native process listing in the command environment showed no Godot/Blender process;
  this does not establish absence on the MCP host.
- Greybox owns `127.0.0.1:16650`, PID49308, runtime16651/ancillary16652–16654 and
  `/tmp/brackett-greybox` XDG state. Those resources were not contacted or changed.

No editor-managed file fallback or infrastructure repair was needed for concepts.
Before production mutations, establish a worktree-private process/project endpoint;
use suitable editor tools or explain their concrete limitation before file fallback.
Preserve unsaved work and record refresh/reopen/save evidence. Bounded graphical
preview uses 60 FPS/VSync. No shared service/configuration changes authorized here.

## Remaining deliverables after Regner selection

Assign a stable family ID from the selected direction, e.g. `smg_wedgewire_a`.
Use `art/source/models/weapons_smg/<asset_id>.blend`, collection
`export_<asset_id>`, explicit `art/models/weapons_smg/<asset_id>.glb` plus import
metadata, and `scenes/prefabs/weapons_smg/<asset_id>.tscn`. Runtime materials remain
asset-owned; textures/rig/clips only if the selected brief requires them. The wrapper
keeps a linked imported `Visuals/Model` and source-relayed socket. Preview/test paths
remain asset-local. No gameplay collision is implied by decoration.

Record actual bounds/AABB, source members/export settings, material slots,
socket transforms, any moving parts/clips, import/UID identities, clean import,
existing-editor inspection, saved/reopened wrapper, source linkage and actual camera
captures. Obtain one proportionate independent clean-context production review.
Integrator then checks equipped player poses, movement/query/network behavior and
effects in the game. Preview playback alone cannot accept those outcomes.

## Small shared-planning delta for later reconciliation

Shared catalogue/TODO were intentionally not edited concurrently.

- Catalogue candidate: `SMG concept selection — docs/concepts/assets-v1/smg/README.md`
  and this scoped handoff; pending Regner concept selection, no production asset ID yet.
- After selection, add chosen asset ID → `docs/assets/<asset_id>.md` with complete
  source/export/prefab/preview mapping. Retain S02 technical fixture records unchanged.
- TODO state remains open: selection → source/model → export/import/wrapper/preview
  → independent review → external integration. No existing TODO completed or removed.

No main scene replacement, main integration, merge, remote push, archive, shared
plan rewrite or foundation closure performed.
