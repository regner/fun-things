# Rocket launcher — concept selection

Concept images for completed production assets were removed during production cleanup; retrieve them from commit `80d0f24`.

9 October 2026. **Regner selected A — Dock Thumper:** “Lets go with A, it provides a
nice top down silhouette”. Production is authorized. These are original fictional
game visuals, not production models or functional weapon designs.

Rocket-launcher lead: Codex / Paseo `29438b4a-4815-4a68-8614-5d0a704809f2`, branch
`art/brackett-rocket-launcher`, baseline `c030d66d7d0a9db19c0c2aebf1aa2b83eded6275`.
Regner selects the visual direction directly here. The external integrator owns
gameplay integration. The concept approval gate was satisfied before source modeling.

This document preserves the original concept checkpoint below. Current sources, measured
contacts, validation and production status are in the [Dock Thumper handoff](../../../assets/rocket_launcher_dock_thumper.md).

The removed review gallery and individual sheets remain available at commit `80d0f24`:

| Option | Sheet | Direction and tradeoff |
| --- | --- | --- |
| **A — Dock Thumper (recommended)** | 01_dock_thumper | Fat shoulder tube, coral muzzle collar, pale upper stripe. Familiar heavy-weapon silhouette and clear front/back contrast; less eccentric than C. |
| B — Arcade Pod | 02_arcade_pod | Broad rounded rectangular body with cyan roof. Bold color footprint; could read as equipment rather than a launcher when the muzzle is hidden. |
| C — Coral Bell | 03_coral_bell | Flared coral muzzle and narrow tube. Strong directional silhouette and playful proportions; the bell risks reading as a horn without the held pose. |

Names are working asset labels, not brands or settled world lore. Selection may
combine a silhouette with another option's palette; the result needs a consistent
selected sheet before detailed production.

## Brief and camera

Reusable launcher visual and its visible rocket, smooth stylized 3D with chunky
readable shapes and dark petrol/coral/cyan accents. Grounded in the viewed
[city reference](../../world-v1/stage-01-setting/15-long-island-cyberpunk.png) and
[current parallel commissioning](../../../workflows/parallel-art-production.md).
Three-quarter views explain volume; top views explain what the game camera sees.
Neutral mannequins illustrate contact needs only, not the player design or rig.

Target: vertically down perspective, north-up, height 47 m, FOV 42°, viewport
1280×800. The S02 ground view is about 57.7×36.1 m. At ground datum this gives
roughly 22 px/m: a provisional 1.4 m launcher is about 31 px long, a 0.45 m
rocket about 10 px. Held height increases projected size slightly. Dimensions
are proposed art envelopes, not measured imported geometry or gameplay clearance.
The gallery's 32 px top-view crops are approximate illustration reductions;
they are not camera-calibrated Godot evidence. The enlarged sheets and mannequin
views are also concept illustrations, not target-camera renders.

## Visual self-review at the concept checkpoint

- All three sheets include an enlarged top view, a useful three-quarter view,
  a distinct matching rocket and a neutral held-pose/silhouette study.
- A's long pale panel and coral collar provide broad contrast. Recommend its
  tube silhouette, retaining those large areas and simplifying grooves/rails.
- B's broad cyan roof reads readily as a color block; final geometry must keep
  its visible heavy-launcher cues when the aperture faces away from the camera.
- C's flare is the strongest directional shape; confirm the horn association is
  acceptable before selecting it. Its illustrated cyan spine is broader than
  prompted and should be an explicit selection choice.
- Generated held illustrations are inconsistent in heading and grip placement;
  they declare a two-hand/shoulder requirement, not exact pose or socket offsets.
  A's small sight details vary between views. Reconcile these in the selected
  direction and measure contacts in Blender before export.
- No real brand or existing weapon identity was requested or intentionally
  incorporated. The surface wear is presentation detail; it does not mandate
  production textures or fine geometry that disappears at the game camera.

Self-review accepts these as selection references; owner approval now selects A.
At that checkpoint no Blender export or saved Godot scene existed. The linked
production handoff supersedes the proposed paths, measurements and tool status below;
gameplay/network and hardware performance acceptance remain separate.

## Concept-stage compatibility and dependencies (historical)

Metres, positive unit roots; Blender +Z up/+Y front converts once to Godot +Y
up/-Z front. Launcher origin is the dominant-hand grip attachment pivot.
Preserve source `socket_grip` and `socket_muzzle`, prefab `Sockets/WeaponMount`
and `Sockets/Muzzle`; muzzle local -Z forward/+Y up. Socket transforms will be
authored in source and relayed to the prefab, not independently hand-tuned.

All options need dominant hand at grip, support hand forward beneath the body,
shoulder contact behind grip, head clearance and a stable horizontal aiming pose.
Exact shoulder/support contact markers, transforms, handedness, rest alignment,
and hold/aim/reload clip matrix await selection with the player lead. A marker
name beyond the reserved grip/muzzle pair is a proposal until agreed.

Player lead `7016b739-5eea-480c-afa3-2c0cbad484a2` owns the versioned
`shared_humanoid_rig.md` and shared sources. Near-1.8 m actor height is provisional.
S13's seven-bone fixture has no hand sockets and is not a production rest/retarget
rig. No rig, hand offset or clip contract is copied from it. Dependency message
sent through Paseo with background execution and finish notification.

This lead owns the rocket visual source/export; effects lead
`c9207bb9-925b-46e4-bd68-e37aaa66a617` owns trail/explosion presentation. Proposed
rocket convention is agreed with the effects owner: unit root, metres, -Z
forward/+Y up, source `socket_trail` at the exhaust centre with that same
orientation, relayed to stable wrapper `Sockets/Trail`. Emitted exhaust extends
behind along local +Z. Exact transform/aperture follows the approved rocket model.
Effects owns world-space fading puffs retained after emission stops; no other
anchor was requested. No projectile simulation, damage,
combat, trail or explosion implementation belongs in this asset.

## Existing consumers and scoped future paths

Inspected S02 `s02_launcher` source/export handoff and saved
`prototypes/s02/tests/fixtures/s02/weapon_studies.tscn`: a technical visual fixture with a shared
source and provisional actor mount, not a production launcher to replace.
Inspected S15 `prototypes/s15/tests/fixtures/s15/rocket.tscn`: an effects-study rocket with
different axial/trail placement. These existing resources remain independent.
Do not duplicate their conventions into a second gameplay implementation.

After selection, unique families will be `rocket_launcher` for the launcher and
rocket source/export, prefab and owned materials. Stable asset IDs will reflect
the selected silhouette. Planned paths follow [assets](../../../assets.md):

- `art/source/models/weapons/dock_thumper/<selected_asset_id>.blend`
- `art/models/weapons/dock_thumper/<selected_asset_id>.glb` and `.glb.import`
- `art/materials/weapons/dock_thumper/<material_id>.tres` when external materials are needed
- `scenes/prefabs/rocket_launcher/<selected_asset_id>.tscn`
- `scenes/prefabs/rocket_launcher/<selected_rocket_id>.tscn` (visual only)
- `tests/assets/weapons/dock_thumper/preview.tscn`
- `docs/assets/rocket_launcher_<selected_direction>.md` scoped production handoff

Sources live under the existing `art/source/.gdignore`. Visible preview geometry
also needs committed Blender sources/linked imports. Decoration has no implicit
collision. Future asset completion requires source/export/socket checks, actual
camera captures, appropriate clips or explicit not-applicable reasons, saved
Godot scene refresh/reopen, and one clean-context independent production review.
That review follows explicit concept selection; it is not a concept approval gate.

## Concept tool receipt and process boundaries (historical)

Built-in imagegen generated all three sheets; exact prompts and modes are in
[prompts.json](prompts.json). Images were copied into this worktree unchanged;
original generated outputs were left in place. No external models, stock textures,
fonts or downloaded brands were used. AI concept references do not establish
Blender authorship; later sources must record their own creator/tool prompts.
No third-party attribution is required for deliberately incorporated material;
no separate asset license is asserted by this concept record.

Available binaries report Blender 5.2.2 LTS `d13f752e3b9c` and pinned Godot
4.8.dev7 `c971f93e7`. Blender MCP status could not connect. Godot MCP read-only
project identity query could not connect to `127.0.0.1:6550` (`CONNECT_FAILED`).
No editor write, process launch, external-file fallback or scene mutation occurred.
These failures do not block image concept delivery. Future authoring will use
verified worktree-private processes; no shared endpoint/config changes.
Greybox owns ports 16650–16654, PID49308 and `/tmp/brackett-greybox`; avoid them.

Gallery QA: image sheets visually inspected from imagegen output; static local
links, PNG structure and prompt count checked. Browser-rendered gallery inspection
was unavailable: sandbox denied the private local HTTP listener, and CUA reported
the in-app browser unavailable. No service/config changes or infrastructure
recovery project was attempted. The static gallery remains directly openable.

## Concept-stage reconciliation delta (historical)

Shared catalogue/TODO/planning files were not edited. Proposed later catalogue
entry: selected launcher and rocket IDs → scoped production handoff above, with
source/export/prefab/material/socket/preview mapping after authoring. No existing
TODO is complete at concept stage; no removal delta yet. Pending dependency:
Regner selected A; player/effects contracts now refine
contacts/emission mapping. Main integration, remote push, workspace archival and
unrelated foundation closure are outside this handoff.
