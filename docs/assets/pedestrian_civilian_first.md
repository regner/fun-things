# First civilian pedestrian — scoped concept handoff

Status: concept options delivered; **selection pending Regner**, 9 October 2026.
Base: `c030d66d7d0a9db19c0c2aebf1aa2b83eded6275`.

Pedestrian lead owns brief, concepts, eventual approved Blender model/materials,
export/import, presentation wrapper and asset-local preview. Regner selects the
concept. Player lead owns the versioned `shared_humanoid_rig.md` and shared sources;
the external gameplay integrator owns AI, population, gameplay wrappers, collision
policy, spawning, lifecycle and network acceptance. Independent production reviewer
will be assigned to a clean-context immutable revision after implementation.

## Brief and current evidence

Purpose: one ordinary unarmed city civilian, readable through chunky head, shoulder,
garment and shoe masses. Style follows the selected island cyberpunk setting and
smooth 3D art direction. [Three sheets, recommendation and self-review](../concepts/assets-v1/pedestrian/README.md)
and [simple gallery](../concepts/assets-v1/pedestrian/review.html) are the deliverables
at this checkpoint. Exact authored prompts, producer and image hashes are retained
beside the sheets. No detailed production has started; no production acceptance is
claimed. No shared catalogue, TODO, launch scene, project configuration or spike
consumer has been changed.

Camera target: vertical-down perspective, north-up, 47 m, FOV42°, 1280×800.
Near-1.8 m person height remains provisional. Final numerical bounds/tolerances,
deformation envelope and density rationale must be recorded against the approved
concept and shared rig before binding. Pivot ground between feet; metre units;
Blender +Z up/+Y front → Godot +Y up/-Z front; unit roots. Decoration supplies no
implicit gameplay collision. Pedestrians have no weapons in this assignment.

## Compatibility dependency

Inspected `docs/assets/s13_humanoid.md`, S13 source/export tooling, imported model
and fixture consumers. S13 is a 1.8 m seven-bone technical crowd fixture without
hand sockets, production rest pose or anatomical rig. Its existing palette swap
wrapper and manual locomotion restart are technical evidence, not production APIs
to duplicate. Existing S13 files are untouched.

Final binding waits for the player-owned versioned hierarchy, rest/bind transforms,
skin influence contract and clip/attachment conventions. Do not author a competing
skeleton. Pedestrian needs in-place `idle`, `walk`, `run` looping and one-shot
`death` holding its final pose, with no simulation-root displacement or gameplay
events. Basic relaxed arm swing and believable knee/elbow deformation are needed.
A's cross-body bag can follow the torso/hip; B may need a hand-bound tote and coat
weight checks; C needs no extra attachment. Confirm whether shared clips suffice
or pedestrian-specific compatible clips belong in the selected asset source.

## Reserved asset-local production paths

Choose one stable ID after approval: `pedestrian_commuter_a`,
`pedestrian_shopper_a`, or `pedestrian_worker_a`. These are alternatives, not three
production promises. Use the unique family `pedestrian_civilian`:

- `art/source/models/pedestrian_civilian/<id>.blend`, collection `export_<id>`.
- `art/models/pedestrian_civilian/<id>.glb` and Godot-generated `.import`.
- Asset-local material IDs prefixed `<id>_`; opaque palette first, textures only
  if the approved appearance requires them, with editable/runtime mappings.
- `scenes/prefabs/pedestrian_civilian/<id>.tscn`, linked presentation model;
  integration-compatible `PresentationAnchor/Visuals/Model`, no AI/spawn rules.
- `tests/fixtures/pedestrian_civilian/<id>_preview.tscn`, saved placement,
  exact camera and bounded capped/VSync clip playback.

Paths above are reserved design intent and do not exist yet. Sources must link the
player-owned rig contract rather than copy its ownership. Actual source/export
mapping, materials, skin/clip paths, imports, bounds, saved identities, refreshed
editor/reopen receipts and acceptance checks will be added with production work.

## Tool discovery and checks

Worktree HEAD matched the supplied baseline and was clean before concept files.
Reference and all three final images were visually inspected. Blender binary is
5.2.2 LTS (`d13f752e3b9c`); pinned Godot binary is available at the Mise
4.8-dev7 install. No private authoring process was needed for raster concepts.
Blender MCP status and scene-info reads reported no connection. Godot read at the
configured endpoint `127.0.0.1:6550` reported `ECONNREFUSED`. Therefore no connected
editor project/unsaved state could be verified and no editor writes were attempted.
Greybox-owned `16650–16654` and its editor/session were not used. A worktree-private
process must be established and ownership checked before later authoring writes.
No 3D direct-file fallback, editor save/reopen, import, rig playback, game-camera,
gameplay, network or performance checks are claimed at this concept checkpoint.

## Small catalogue / TODO delta for later reconciliation

Catalogue proposal: first civilian pedestrian → this handoff; concept pending;
replace the provisional record title with the selected stable asset ID on approval.
TODO proposal: record Regner's selection; obtain player rig contract; implement and
validate approved source/export/materials/compatible clips/presentation/preview;
perform independent production review; pass to gameplay integrator. No existing
TODO is completed by concept selection or these raster sheets.
