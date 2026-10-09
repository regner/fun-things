# Vehicle concept checkpoint handoff

9 October 2026. Producer: dedicated vehicle lead. Art selector: Regner.
Receiving gameplay integrator: another person, not yet named.
Stage: all three cars approved by Regner on 9 October 2026; first source/import/preview
checkpoint created. [Production gallery](../../../assets/vehicle_car_evidence/index.html).
New bus/truck concepts presented, approval pending. No finished production vehicles.

## Owner model-routing update — 9 October 2026

Owner instruction supersedes the cohort's earlier Sol lead policy: all geometry,
UV/skin deformation, spatial rig/rest/bone design, keyframes/poses/motion and spatial
VFX authoring use Astra. Non-spatial Godot imports, resource/rig/animation configuration,
bookkeeping and technical wiring may use Sol 6.1 medium/high. Verify effective runtime
model before resuming spatial work; preserve in-flight work and end a Sol turn if the
new settings are only effective next turn. This applies to any art subagent too.

Paseo `get_agent_status` verified active session
`01a12094-3419-70f1-b170-ee8dbb9bacb2`, active turn `codex-turn-6`,
`runtimeInfo.model=gpt-6-astra`, `runtimeInfo.thinkingOptionId=high` before subsequent
spatial mutations. Three first-pass sources and GLBs were already saved by the
in-flight earlier operation. They are preserved, with no process kill or discard.
The owner then raised door opening; movable side doors use rigid hinge pivots and
cosmetic preview clips, without requiring a skinned skeleton or gameplay seat logic.

## Existing evidence and boundary

Read [S04 source handoff](../../../assets/s04_kit.md),
[body/seat contract](../../../spikes/s04-contracts.md), saved
`tests/fixtures/s04/kinematic.tscn` and `dynamic.tscn`, and their listed S05/S06
consumers. Original car source/export/wrappers remain untouched.

S04 imported visual bounds: X 1.88 / Y 1.54 / Z 3.4 m, bottom Y 0. Its collider
is 1.8 × 1.5 × 3.4 m centred at (0, 0.75, 0). Driver candidate is (0, 0.8, 0.1),
entry candidates (±1.3, 0, 0.1), exit candidates (±1.5, 0, 0.1). These are
spike facts, not approved production sizing/grounded seat/exit clearance.
Planar body/handling/authority and collider masks belong to gameplay owners.

No controller, seat transaction, network, physics/body redesign, main launch,
city placement, shared plan/TODO/catalogue edits, merge or push is included.
The proposed selected-family wrapper is a reusable visual asset, not a replacement
for `scenes/entities/vehicle.tscn` or an implicit choice of production body class.

## Proposed selected-family output map

Regner selected all three: `car_latch_a`, `car_crate_a`, `car_sable_a`.
Family directory is `city_cars`; check current consumers before creating paths.

- `art/source/models/city_cars/<asset_id>.blend`, collection `export_<asset_id>`;
  preserve the existing source `.gdignore`.
- `art/models/city_cars/<asset_id>.glb` and Godot `.glb.import`.
- `scenes/prefabs/city_cars/<asset_id>.tscn`, imported `Visuals/Model`, no driving
  controller or gameplay collision authority. Integrator mounts this visual scene
  under its own `PresentationAnchor`.
- `scenes/previews/city_cars/<asset_id>_preview.tscn`, asset-local saved presentation,
  target camera and three-quarter inspection; visible staging geometry also Blender-owned.
- `docs/assets/<asset_id>.md`, exact source/export/material/socket/consumer mapping.
  Any asset-owned external materials/textures live in contract paths and are listed.

Ground-centred visual origin, metres, Blender +Y forward/+Z up → Godot -Z forward/+Y
up, unit transforms. Four separate wheels with axle-centred pivots and named source
markers. Determine simple steering/spin pivots after selection; no humanoid rig or
animation dependency is required for a rigid car. Source empties for `socket_driver`,
`socket_entry_left/right`, `socket_exit_left/right` map to wrapper
`Sockets/DriverSeat`, `EntryLeft/Right`, `ExitLeft/Right`. Preserve source transforms,
document proposed poses, and leave authoritative clearance decisions with gameplay.
Driver fit waits for the player's versioned production dimensions/rest/seat contract;
do not reuse S13's technical seven-bone rig as a production occupant.

Embedded opaque source-owned flat materials are the simplest starting point.
No textures/rig/clips/LOD promised before the selected brief establishes a need.
Any wheel preview playback will demonstrate cosmetic pivots only, not driving,
suspension, seat transitions or network acceptance.

## Tool and ownership receipt

- Worktree HEAD initially `c030d66d7d0a9db19c0c2aebf1aa2b83eded6275`, clean status.
- `/usr/bin/blender --version`: 5.2.2 LTS, hash `d13f752e3b9c`.
- Pinned installed Godot binary: 4.8.dev7.official.c971f93e7.
- Blender MCP addon/scene read probes: could not connect. Godot MCP read probe:
  `CONNECT_FAILED`, refused `127.0.0.1:6550`. No connected editor project identity
  could be established, and no editor mutation or direct-file scene fallback occurred.
- Greybox owns 16650–16654, PID 49308 and `/tmp/brackett-greybox` state; these are
  excluded from vehicle use. No shared configuration or service changed.
- Before production writes, launch/verify private worktree-bound processes and
  isolated state/endpoint ownership. Use suitable editor MCP; if insufficient,
  explain the fallback first and retain save/refresh/reopen evidence. Capped bounded
  previews only. This initial concept work requires no live editor.

## Reconciliation delta for planning owner

Do not apply concurrently to shared files:

- Catalogue: first production vehicle concept checkpoint exists at
  `docs/concepts/assets-v1/vehicle/README.md`; all three cars approved by Regner.
  New `bus_tandem_a` / `truck_keel_a` proposals described in `larger_vehicles.md`,
  pending approval, unique family `city_commercial`; provisional dimensions explicit.
- TODO: car concepts/owner selection done; bus/truck concept approval pending;
  car sources/materials/wheels/hinged side doors/markers, GLB import/metadata and saved
  wrappers/previews now exist. Reexport, imported bounds/sockets, saved roundtrip and
  actual camera/door-pose checks pass. Independent Sol 6.1/high review accepted
  candidate `69219f0` as a first checkpoint with no scoped defects; see
  `docs/assets/vehicle_car_evidence/independent_review_69219f0.md`. Full-loop playback,
  final art polish/owner model acceptance and integration checks remain pending.
- Integration dependencies: final visual/collider envelope reconciliation, driver
  fit, safe entry/grounded exits, district turns/contacts/spawn queries, gameplay
  root/lifecycle/networking, target performance and playable acceptance remain with
  integrator/relevant owners. No foundation TODO closure is claimed.
