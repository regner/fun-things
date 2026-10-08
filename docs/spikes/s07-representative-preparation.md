# S07 — source-only representative-load preparation

8 October 2026. Exact inspected main/base: `244089785b0d106451160acd89859c6977d30956`.
**Preparation only; every future slice and measurement below is UNEXECUTED.**
No fixture, model, gameplay code, import, build, renderer, pin, transport integration,
streaming architecture, budget or approved load is delivered. S07 TODO stays OPEN.
The [static evidence index](s07-representative-evidence/README.md) binds source/API/
UID claims, immutable prior evidence and this commission's checks/review.

## Answer and boundary

The minimum is **a bounded representative foundation slice**, not finished M1:
a source-linked saved six-block content sample; real shared actor/car steps; real
bounded host population/queries; complete state for the lifecycle cases actually
exercised; an actual four-rig ENet encoding/admission path; and a reproducible event/
reset/lifetime driver. Each has one rule/state owner and independent outcomes below.
Production menus, persistence, polish, full asset-family variant catalogues, delivery
and the general M1 validation suite need not precede this slice. They remain M1 work.

This is not permission to substitute duplicates, idle markers, prescribed pose
animation, synthetic bytes, empty space, token effects or route-following without
collision/AI for R. A transient pedestrian must actually choose legal routes,
respond to threats/blockage, step/query and animate; a car must actually steer,
collide, transfer control and become a wreck. Wire work must encode/decode their
actual state through the one Replication writer, not pad messages to a chosen size.
If the real minimum cannot fit separately commissioned foundation effort, Regner
must resolve feasibility/scope/ordering explicitly. R/G remain blocked; neither a
plan nor technical T waives any R dimension or changes P0's dependency on S07.

[Checkpoint09](../reviews/plan-check-2026-10-08-09.md#whole-task-disposition-and-ordering)
identified S07→P0→M1→R→S07 as a latent planning cycle, not a mandate to start M1.
The [existing T/R/G cards](s07-run-cards.md) remain the run authority specification,
not runtime permission. This record supplies their missing preparation and a
prospective phase proposal; it does not replace those cards. The accepted
[57-traversal/600-declared-second driver](s07-sustained-driver.md) is preserved and
must not be reopened or repeated as a historical experiment. Its simulation-only
receipt is not graphical T, R, G, S07, P0 or M1 acceptance.

## Saved inputs and identity binding

All paths here are relative to repository root. `references.json` in the adjacent
package binds exact base Git blobs, byte counts and SHA-256, scene/import/script
UIDs and asserted API symbols. It also selects accepted historical note/report
identities from the immutable checkpoint ledger, without copying their payloads.
Saved world IDs, resource UIDs, entity generations and engine node IDs are separate.
The accepted186-input inventory binds its original52941da base, not every current
byte: `tests/fixtures/s03/{proof,session}.gd` later gained log-only lifecycle telemetry
at `53f0c8fd00a05271948087099eee9d7ca1c22989`; the other184 inputs are unchanged.
Current source bindings use this task's exact2440897 base. That telemetry is not
new R gameplay or proof of original-main20ms/clean-release behavior.

| Binding | Existing saved consumer and identity / owner |
| --- | --- |
| I1 — primary T | `tests/fixtures/s07_driver/intersection.tscn`, UID `uid://cauba1m1nenjw`, inherits `tests/fixtures/s06/intersection.tscn`, UID `uid://c61a1l4vio22q`; root-only script override `fixture.gd`. S07DriverFixture `begin_route`, `saved_start_valid`, `passive_valid`, `cancel_owned`; S06Fixture `start_route`, `body_state`, `stop_route`, `route_finished`. One commanded body at a time. |
| I2 — topology | `tests/fixtures/s06/{west,east}.tscn`, UIDs `uid://b243gxu4qpp0a` / `uid://chhg1wj1jcwpu`, saved `City/Sectors/West` (node1973761027), `City/Sectors/East` (node443909768) at identity. `s06/sector/west`, `s06/sector/east`; explicit foot/lane/road IDs remain in those scenes. `derived.tres` UID `uid://dt54nay70c1tr`, fingerprint `eaec39bbde6bd39e0b9c6c5c005f6285be49881faeb3a2cbfa02363014ff1604`. `city.gd` owns `validate_content`, `signature`, `bake_content`, `route`, `map_data`; `controller.gd` owns `bind_route`, `intent`, `clear`. |
| I3 — actor and height controls | `tests/fixtures/s02/actor.tscn` UID `uid://dl05tre3pd6e0`, `actor_motion.gd` owns `step`, `neutralize`, `motion_state`, `muzzle_position`. `corner.tscn`, `corner_wide.tscn`, `building_view.gd`, `camera_rig.gd`, `aim_probe.gd` supply linked 6/46/60 m technical masses, cutaway, camera and actual pistol-ray work. `art/source/models/spikes/s02_kit.blend` → nine exports under `art/models/spikes/s02_*.glb` via `tools/s02/export_members.json`; [handoff](../assets/s02_kit.md). |
| I4 — car/body/seat adapter | `tests/fixtures/s04/kinematic.tscn` UID `uid://cyyhi67pisbql` → `s04_car.glb` UID `uid://g2exvhxy70wu`; `s04/track.tscn` → `s04_track.glb`; source `art/source/models/spikes/s04_kit.blend`, `tools/s04/export_members.json`, [handoff](../assets/s04_kit.md). `drive_rules.gd:advance/neutral` is the handling owner; `kinematic.gd:configure/step/neutralize/install_pose/retire/motion_state/display_state` is the body boundary. `s04/match.gd` is a fixed two-driver retained-seat/resync adapter, not VehicleInteraction. |
| I5 — comparator / effects | `tests/fixtures/s05_effect/burst.tscn` UID `uid://bdtfsc6kyavum` inherits `s05/burst.tscn`; twelve saved cars inherit `s05/car.tscn` → I4. Saved `View/Match/Presentation/Slots/Slot0…Slot7` link `explosion.tscn` UID `uid://dbge3dp3s53r3` → `s05_explosion_carrier.glb` UID `uid://dembbyrbteuwu` → `art/source/models/spikes/s05_explosion_carrier.blend`. `s05_effect/match.gd` injects slots/bodies; `presentation.gd:bind/consume/advance_cosmetic/clear/receipt/visible_count` extends the existing fence, never damage. [Saved-effect record](s05-saved-presentation.md). |
| I6 — damage/current state | `tests/fixtures/s05/damage.gd` owns `begin/register_shooter/resolve_shot/advance/cut/valid_cut/apply_cut/retire_shooter/clear`; `car.gd:apply_life` installs neutralized wreck collision. `s05/match.gd:baseline/apply_baseline/submit_fire/apply_cars/rollback/clear`; `s05/replication.gd:send_fire/publish_cars/publish_blast/forget/clear`. No canonical PlayerLifecycle/WeaponState/Projectile simulation is implemented by these adapters. |
| I7 — session / foot response | `tests/fixtures/s03/{boot,local_rig}.tscn`, `session.gd`, `transport.gd`, `match.gd`, `replication.gd` provide tiny four-channel ENet admission/held/subset-refresh scaffolding and one placeholder rig. `tests/fixtures/s03_r/boot.tscn` UID `uid://jd5igfvwkrvk` reuses it with two saved real actor bodies, `match.gd:local_body/prepare_resync/pose_for_entity/apply_movement`, `actor.gd:install_pose/retire/display_state`. No four actual actor rigs or integrated car/population codec. |
| I8 — source-linked roads | `art/source/models/spikes/s06_intersection.blend` → `s06_west.glb` UID `uid://dh88hp6iu51tm` and `s06_east.glb` UID `uid://cldnd3ynk3e46`, through `tools/s06/export_members.json`, I2 wrappers and [source handoff](s06-source-handoff.md). These are a 48×48 m planar intersection, not six saved blocks. |

### Actual diversity and accounting limits

The [accepted inventory](s07-run-cards.md#actual-saved-inputs) has 14 GLBs,
433,824 total export disk bytes; **zero images, textures, skins and animations**
in every GLB. Flat embedded palettes have 2–4 material definitions per export.
S06 sectors each have 17 mesh/primitive definitions and 204 placed triangles;
S04 car has 8 primitives/1,504 triangles, track 6/1,128; S02 actor 7/1,316;
carrier 1 mesh/3 primitives/1,344. Carrier materials are opaque by default,
double-sided, alpha1: no smoke transparency/particle/debris/overdraw equivalence.

I1/I2 total saved composition is 79 nodes (excluding imported internals), 59
all-placement primitives/5,108 triangles, actor+pistol+two cars+West/East. I5
inherits 179 saved nodes, 126 all-placement primitives/29,928 triangles, including
eight initially hidden carriers. These are **not draw calls or live render counts**.
I3 corner has 40 building mesh placements; `building_view.gd` creates local shader
materials per mesh. Repeated export material names do not prove shared imports.
Sidecars request generated LOD/shadow meshes; imported output/caches are not measured.

For every future manifest/sample separate: saved static placements and distinct IDs;
unique model/material/texture/skin/clip resources and formats; instantiated nodes,
resident shared/unique mesh/texture/animation bytes and reference roots; visible
per-camera surfaces/triangles/overdraw/shadow work; active host bodies/controllers/
queries/path requests/rockets/chains; passive client interpolation/animation/effects.
Disk GLB/source bytes cannot stand in for RAM/GPU allocation. Fully loaded sectors
remain resident even when culled; visibility cannot disable authority. Costs of
loading/instantiation/tree entry/first draw, reset/retirement and stable traversal
are separate. No unloaded-resource or separate open-editor synchronization claim
follows from these saved files.

## Requirement-by-requirement readiness matrix

Status vocabulary: **present** = saved executable subset/accepted bounded receipt;
**extendable** = named reusable boundary, extension still unimplemented;
**missing** = no honest representative input/API/coverage; **blocked** = launch/
acceptance lacks an entry condition; **ratification** = Regner's unresolved choice.
Multiple statuses on a row distinguish a reusable subset from the missing dimension.
Provisional numbers are inherited targets, not new approvals or measurements.

| ID / requirement | Actual present/extendable input and cost | Missing work / blocker / ratification; proposed slice |
| --- | --- | --- |
| T1 — two-sector graphical T | **present** I1/I2/I3/I4, source/bake IDs, passive pre-tree roles; accepted 57 traversals/36,461 samples over 608.639614 actual s for 600 declared s. Foot5 m/s, traffic target3.5 m/s, hard1200/1800-tick failure stops. | **blocked** named hardware/build/telemetry and separately authorized drawability; camera47 m/42°, near0.1/far160 m are candidates. Six primary cap/repeat runs still UNEXECUTED; no new simulation-driver work needed. Final envelopes/readability need **ratification** and affected checks. |
| T2 — separate effect comparator | **present** I5/I6; finite twelve outcomes/144 visits, peak4 target visits/tick, eight saved-node reservations/four cosmetic drops; settled late hydration emits no historical effects. **extendable** clear/epoch/deadline and damage APIs. | **missing** twenty-trial driver with genuine new identities/restored body/life/control/collision and no reset of floors inside the same context; **blocked** eight actual DRAW/live-versus-hydrated proof and reset receipts. Natural local expiry/visible_count is not DRAW. Slice C0. No geometry added to T1 totals. |
| R1 — six-block bounds/topology | **present** reference roughly284×187 m, six blocks/West-Centre-East design, I2 route/map/signature rules. **extendable** explicit graph/bake/content admission. | **missing** saved six-block composition, stable spawn/route/link IDs, two loops/alley/plaza/chain yard, final-body seam/turn/exit/boundary clearance, accepted bake. S0664-anchor/128-link/4096-sample bounds may not fit: return a concrete scope/bound decision, not silently increase. **ratification** dimensions/placement counts. C1/C2. |
| R2 — geometry/material/texture variety and residency | **present** I3 height controls6/46/60 m, I8 roads, flat I4 car, opaque I5 carrier; actual diversity above. | **missing** genuine distinctive building/prop subsets, two car silhouettes/damaged state, textured/skinned animated people and intended VFX work. Number of placements, unique models/materials/textures, resolutions/formats/mips, surfaces, lights/shadows, clip/rig complexity and camera-visible distribution are unset **ratification** choices. Palette repeats cannot represent them. C1; final M1 catalogue/polish stays later. |
| R3 — 64 pedestrians / 32 live cars + four players | **present** I3/I4 real motion; **extendable** I2 controller intent. | **missing** host-owned64 pedestrians/24 traffic+8 parked globally, replenishment/retention, simultaneous real body/query/collision work, wandering/crossing/fleeing, blockage/stuck/wreck recovery/reservations. One scripted S06 route is not population AI; parked cars count within32. Seed17 only if actual seeded owner exists, otherwise replayable log. Caps are **provisional targets**, not measured. C3. |
| R4 — navigation/query cost | **present** I2 directed traffic/undirected foot/ROAD map; finite BFS/curve search, four static islands, three CharacterBody3Ds/seven saved shapes; no navmesh. | **missing** district route/path request distribution, contested crossings and actual shared spawn/exit clearance query, threat/obstruction/contact workload. Do not introduce NavAgent dummy work or claim navmesh cost. If intended free-area detours require navmesh, ratify representation/feasibility and commission it explicitly; route graph alone leaves that dimension unrepresented. C2/C3/C4. |
| R5 — four distinct graphical views/processes | **present** I7 tiny Session/admission; S03-R/S04 each exactly two real bodies. **extendable** one saved rig and local-body binding. | **missing** one graphical authority plus three admitted graphical clients, distinct actual player EntityRefs/spawns, each one local camera/input/HUD/minimap rig following committed foot/car control; together then four distant areas. Headless markers/split screen/duplicate rigs fail. Exact spawn/camera coordinates missing; **ratification** camera/control assumptions. C4/C5. |
| R6 — authority, encoding and actual traffic | **present** I7 channels0 reliable session/action,1 reliable state,2 ordered-unreliable held,3 ordered-unreliable motion; I6 current car cut/fire/events and sender mapping. S03 baseline8192 bytes/two chunks; held1200 bytes, rate60/s burst8; S05 fire512 Variant bytes,4/s burst4/window16, cut8192 UTF-8 bytes/12 fixed rows. | **missing** real population/player/car/weapon/projectile EntityRef codecs and exact-field primitive decoders, content/bake handshake, dynamic generations/tombstones, batching/refresh of all entities, dependency-wait bounds, wire overhead and four-view rates. S03-R/S04 coordinate limit100 m/fixed2 pose rows/revision1 are district incompatibilities, not reusable capacity defaults. Steam public proposal is unselected/untested and **deferred**, not an ENet proxy. C5. |
| R7 — burst/gameplay queues/events/caps | **present** I6 twelve reserved car jobs,4 accepted roots/4 target visits per tick; shot floor survives active-cache completion/departure; current radius4.1 m/delay6 ticks/health100/damage100/wreck300 ticks. Eight cosmetics independent of outcomes. | **missing** general actual hitscan/rocket/fire/ammo/reload work,16 active rocket state/contact/expiry, sixteen wreck/dead states and64 transient presentations, dependency/event retired floors beyond finite match1, journal during chains. Future limits must follow owners and draft caps, not S05's twelve-car-only capacity. **ratification** blast/obstruction/falloff/timing/wreck choices; target peaks/count mix. C4/C5/C6. |
| R8 — join during/after chain | **present** I6/I7 settled cut/handoff and passive install; only one tiny health journal example. | **missing** immutable real full baseline plus car/player/population/rocket durable journal while host continues, cancel/overflow/timeout rollback and fresh movement after dependencies. Draft baseline1 MiB/16 KiB chunks, journal2 MiB or4096 records and deadlines are proposed limits, not measured. Four total slots includes loading; no fifth peer used as a capacity join. C5/C6. |
| R9 — death/seat/wreck/respawn | **present** I4 seated resync retains injured marker/equipment; I6 sentinel9001 dies/releases once, stationary old box retires after deadline and completion. | **missing** actual admitted-player death, one driver claim/blocked exit, AI-to-player transfer, death/disconnect/destruction atomic seat transaction, safe three-second respawn/default loadout, failed spawn/retry, moving wreck contact and current hydration. Sentinel cannot stand in. Shared queries/reservations and health/life/control/collision fences required. C4/C6. |
| R10 — reset/leave/rejoin/ten teardown cycles | **present** I1 safe one-shot saved reload; I6 effects clear/epoch; I7 tiny leave/host-loss/cancel/resync. | **missing** host-only Match reset retaining admitted peers, new match revision/generations without tick rewind, neutral input/actions/shots/chains/AI/reservations/histories, rehydration before control, original authored placement invariant and complete callbacks/resource release. S05 begin resets match1/floors; not an in-place match reset. Four-lifetime-shooter guard blocks repeated join churn without extension. C4/C5/C6. |
| R11 — hardware, telemetry, costs | **present** inherited measurement definitions/cards and provisional brief/API targets. | **blocked** exact hardware/OS/driver/power/storage/build/templates/renderer/API/quality, drawable authorization, per-role trustworthy CPU/GPU/pacing/RAM/resource/wire/queue telemetry and overhead control. Missing counters are gaps, never zero. Device/Steam acquisition excluded. C7 only after distinct grant. |
| G1 — one conditional growth axis | **present** existing G card: same six-block bounds/variety/camera/population/events, eligible static placements N→2N only if measured R implicates submission/static object density. | **blocked** accepted R, manifest N, attribution, one separately saved valid2× variant/IDs/topology/contact checks; no4× or cross-product. **ratification** eligible placement set/distribution; doubled colliders reported. No maximum-city or selected optimization. C1/C2 then C7 conditional. |
| X1 — unproved external/full gates | **present** public Steam source/interface research, historical bounded foundation receipts only. | Actual Steam gameplay, Deck LCD/OLED hosting/client/native1280×800/60FPS/Gaming Mode/physical input/suspend, Windows/Linux target compatibility/clean release, final feel/product choices, full S07/P0/M1 remain **OPEN/deferred** as their sources establish. Source preparation or desktop ENet cannot certify them. |

The [brief](../design.md#provisional-validation-envelope) ratifies1–4 players,
six-block scope, native Deck resolution/60 FPS and gameplay policy; its population,
retention/effect counts and numerical performance envelope remain provisional
experiment targets. [API limits](../api-contracts.md#provisional-limits-and-failure-codes)
are draft limits: 60 Hz simulation/up to30 Hz input/20 Hz motion, all-entity revisit
within250 ms, motion≤1200 bytes and lifecycle/event batches≤16 KiB between complete
transactions; held expiry250 ms/8 frames per participant, reliable actions4096 bytes/
16 queued/4 per participant per tick/cache64/rate16 per s burst32. Future-state wait
is latest row only,256 rows or256 KiB/1 s; event window512 IDs/retired floor/2 s age;
spawn10 candidates/tick/0.10 m skin/5 s search and reset/retry once per5 s.
Entity allocation/tombstones stop at65536 spawned refs per match revision; live
history cannot be discarded to make room. None is implemented wholesale by I6/I7. C4–C6 must measure actual bounds/overflow outcomes;
changing them needs their owner/user disposition, not another constants collection.

## Individually commissionable minimum preparation slices

**Proposals, not implementation commissions.** Each later assignment must name
owned saved/API paths, exact base, reviewer, editor/source leases if needed, total
attempt/time/cleanup cap and observables before mutation/runtime. Effort estimates
below are stop-boxes for one focused slice, not an aggregate M1 schedule or a claim
all representative work fits a day. Stop/escalate missing scope/identity/ratification,
unsafe work, failed correctness or exhausted attempts; no automatic next slice.

### C0 — comparator event/reset driver (independent of R)

- Owner: S07 experiment coordinator owns trial scheduling/fixture lifetime only;
  S05Damage remains the gameplay owner, S05SavedPresentation the cosmetic owner.
- Reuse I5 saved burst and I6 public APIs. Prefer retiring/reloading the whole saved
  comparator with a **fresh session** per trial, passive pre-tree roles and source/
  start/body/life/collision checks; do not call `begin` to erase shot floors while
  keeping an old session or graft reset behavior onto presentation. Stop producers,
  clear effects, observe deferred retirement, then load/admit the next saved fixture.
- Independent checks: all twelve car identities destroyed once, each blast completes,
 144 visits/peak4 under the unchanged accepted fixture, eight slots/four drops;
  stale previous-session ShotId/event/callback cannot affect the new trial, saved
  positions restored, zero held velocity, no live job after retirement, clear local
  effects. Outcome equality must be literal/API based, not copied damage formulas.
- Separate loading/first-draw/reset spans from chain cost. This does not prove Match
  reset, in-flight joining, occupied-player death or production VFX. Needs separately
  accepted real draw gate before graphical comparator. Proposed stop-box: one day,
  one authoring batch and two development groups; no capacity run within this slice.

### C1 — representative content sample and saved manifest

- Owner: asset/source owners author immutable model/rig/material/texture/clip content;
  world integrator alone owns saved placement. No gameplay rule in an asset.
- After Regner's D1/D2 decisions, propose linked limited variants of the six starting
  building families and six prop/sign families, below/near/above-camera towers, two
  recognizable car silhouettes/damaged states, one real shared skin/rig with player/
  pedestrian outfit differentiation and idle/walk/run/death clips, and actual intended
  muzzle/impact/tracer/rocket/explosion/smoke/sparks/debris mechanisms. Exact subset,
  variant/placement/texture/light/effect counts are **missing decisions**, not chosen
  here. If a smaller family subset cannot represent intended geometry/variety/residency,
  return that scope question; do not repeat technical masses to fake variety.
- Reuse I3/I4/I8 source handoffs/envelopes and I5 saved slot contract only where their
  real content is appropriate. New source/output/prefab identities must be explicit
  Blender→export collections→GLB/import→saved linked wrapper/source provenance.
  No embedded generated render meshes; intentional shader/particle procedural work
  must be documented separately. No assumed need for textures merely to inflate cost:
  Regner selects intended material/texture treatment, and the sample must actually use it.
- Check export membership, sockets/bones/clips/material bindings/import ancestry,
  distinct silhouette/content identities, inherited save/reopen, source-derived bounds,
  actual animation/material/alpha/shadow first-use and draw counters. Declare shared
  versus unique residency and reference roots. No asserted production-art acceptance.
- Stop-box: first one-day brief/manifest review; then separately commission source
  family batches at≤two focused days each with one author/save/reload validation batch.
  Do not silently expand to the complete M1-C1 catalogue. If necessary real rig/VFX/
  variety cannot fit these batches, return feasibility to Regner before R entry.

### C2 — saved six-block queryable foundation district

- Owner: saved sectors own composition; CityData/S06City is the single topology/
  bake/route/map/shared-clearance rule owner (query extension still missing).
- After C1 envelopes/subsets and D3, compose a new saved district, not six S06 clones:
  three sectors with six differentiated blocks/two loops/alley/plaza/yard, authored
  legal foot/reverse-foot/traffic routes, distinct safe-spawn/exit anchors, linked
  model instances and colliders. Record exact placement N, transforms/IDs and bakes.
- Extend I2's `route/map_data/validate_content` and editor-only explicit bake to this
  content. First inventory required anchors/links/curve lengths/samples against S06
  bounds; if they do not fit, stop for a reviewed bounded API decision. One shared
  clearance query serves spawn/exit/AI, never three formula copies. No runtime bake,
  SVG placement writer, streaming or independent minimap street list.
- Independent checks: unique IDs/dependency UIDs, saved unchanged transforms after
  reset/reload, stale content/duplicate ID/missing endpoint/invalid width rejection,
  actual final bodies through each legal seam/turn/alley and blocked-yard alternative,
  collision/contact/whole footprint and minimap-road agreement. Source-linked height
  controls stay above camera rather than cropping away the problem.
- Stop-box:≤two days, one composition/save/reopen batch plus two bounded route/query
  groups on a later grant. Not M1-C2 production polish/interiors/expanded city.

### C3 — real bounded population representative

- Owner: Population owns slots, replenishment, NPC life/retention, AI controllers and
  junction reservations; ActorMotion/VehicleMotion alone step bodies; CityData alone
  supplies route/clearance truth. Host configures roles before tree entry.
- After C2 and C4's lifecycle boundaries, instantiate saved C1 actor/car prefabs using
  explicit authored dynamic descriptors, not authored static hierarchy generation.
  Reuse I3 `step/neutralize/motion_state`, I4 handling/body APIs and I2 `bind_route/intent`.
  Implement only this district's actual sidewalk wandering/crossing/fleeing and legal
  traffic turns/blockage/stuck/wreck/abandoned-car/replenishment policies with bounded
  queries/replans/reservations. I2's neutralized timeout alone is insufficient.
- Initial target remains64 pedestrians/24 traffic+8 parked within32 live cars plus
  players, globally; occupied cars count within32. Initial state and replenishment
  must make20 chains possible without exceeding live/retained caps or deleting active
  jobs to regain room. Declare actual AI/path/query/event rates and seeded schedule
  or replay log, not every actor receiving identical lockstep commands.
- Independent checks: every active representative records nonempty decision/route/
  collision/query/animation work as appropriate; lawful turns/crossings, threat-flee,
  blocked/stuck finite recovery, occupied/abandoned AI stopped, off-camera same outcomes,
  live/dead/wreck counts and replenishment never exceed accepted caps. Geometry/poses
  alone fail this slice. Unimplemented free-space detours/production population variety
  remain explicit; if required for R, stop for feasibility rather than waive them.
- Stop-box: two-day minimal decision/ownership prototype, two development groups;
  capacity launch excluded. Further missing behaviors are separately commissioned,
  not an automatic full M1-C3 order or R entry from a partial prototype.

### C4 — coherent actual player/car/combat lifecycle representative

- Owners follow [architecture](../architecture.md#state-and-rule-owners): Match
  allocates identities/tick/reset; VehicleInteraction seats/control; PlayerLifecycle
  death/respawn; Health damage state; WeaponState ammo/timers/ShotId; DamageResolver
  queries/jobs; Explosions chains/wreck lifecycle; Projectile motion/contact/expiry.
  These are ownership responsibilities, not a demand for one new class per row.
- Reuse I3/I4 steps/queries, I6 reserved-work/retired-shot logic and I4 retained-seat
  preflight, but do not inherit fixed marker/sentinel IDs as canonical player/car refs.
  Define a bounded saved actor/vehicle/weapon/projectile component composition with
  shared rules for standalone/host; presentation reads state. Four real players must
  bind distinct bodies before graphical rigs can prove R5. No client outcome writer.
- Implement only declared representative paths: real enter/exit/claim conflict,
  blocked exit, traffic transfer, damage/destruction/driver death/disconnect/parked car,
  three-second safe respawn/default equipment and spawn failure/retry; actual pistol/
  SMG/ranged hitscan, finite rocket/contact/expiry, ammo/reload/cooldown and blast work.
  Reserve complete accepted chain work independently of cosmetics. Collision/life/
  control/equipment complete before publishing; reset restores initial dynamic state
  around unchanged static placement, neutralizes all obsolete work and retains peers.
- Independent checks: one claimant, unchanged blocked exit, one terminal/blast per
  car/one driver death/seat cleared, no pre-three-second respawn or overlapping spawn,
  correct full defaults/new life/control refs, duplicate retired ShotId no outcome,
  invalid seated/empty/reloading/cooldown fire no shot, rocket survives equip but not
  reset, stale old-match command/movement cannot resurrect. Use literal known target
  sets/ray hits and actual production-style public boundaries, not synthetic sentinels.
- Stop-box: first one-day identity/state-transition design and feasibility review;
  each motion/seat/lifecycle/combat sub-batch separately≤two days/two development
  groups. If real intended work cannot be achieved under bounded spikes, return the
  unresolved R/P0 scope decision to Regner. Full general M1-B feature/UI/feel suite
  is not commissioned; missing required paths still block R.

### C5 — actual four-player state encoding/admission

- Owner: existing SessionService owns mapping/roster; Replication is the only wire
  validator/state publisher/replica installer; Match supplies committed owner state.
  No new routing framework, Synchronizer or second field writer.
- After C2/C4 schema, reuse I7 ENet endpoints/admission/held/subset-refresh and I6 cut/
  event preflight as examples; extend fixed two-body/100 m/match1/four-lifetime-shooter
  restrictions explicitly for declared district/entities/revisions/churn. Encode real
  EntityRefs, content/bake/definition fingerprints, player/car/NPC/rocket/retained
  state, transactional seats/collision, current weapon timers and durable journal.
- Measure real logical/decoded/wire sizes, per-entity revisit, message split points,
  target rows/rates and host aggregate queues/cost. Enforce draft limits or stop for
  an owner decision; never claim native predecoder allocation is bounded by a later
  Variant size check. Steam adoption/framing/native callback/public proposal remains
  separate and deferred; ENet proof cannot close Steam.
- Independent negatives/outcomes: sender admission/ownership/NaN/type/size/rate/stale
  revision rejection before mutation; subset loss refresh; current baseline+journal
  before fresh movement/input; collision before pose; bounded journal overflow aborts
  only join; canceled provisional player releases all work/reservations once; resync
  retains injured seated state with fresh control; duplicate ack cannot enable input.
- Save four distinctly bound local rigs/cameras/HUD/map consumers through editor;
  parent injects committed controlled body. One rig per process, no placeholder proof.
- Stop-box: one-day codec/size design, then≤two-day admission/replication spike with
  two separate-process development groups, no Steam/runtime grant here. Unproved
  transport decoder/native bounds and full production/adverse suite stay explicit.

### C6 — representative schedule, lifecycle and lifetime driver

- Owner: S07 driver schedules public APIs and reads outcomes; Match alone owns reset
  and gameplay lifetimes. It never directly repairs health/pose/seats/population.
- After C2–C5, accept a saved deterministic route/event recipe, initial spawn/content
  hash, actual bounded replenishment of twelve-car burst cohorts within32 live cars,
  event identities and twenty-trial expected target tables. Cohort replacement uses
  lifecycle removal/new generations; cannot reset dedup floors in an unchanged match.
- Exercise join during and after actual chain, death/driver destruction/seat races/
  blocked exit/disconnect/respawn, reset while driving/firing/joining, leave/rejoin,
  then ten safe teardown/reload cycles. Assert stable static identities, original
  dynamic descriptors, fresh sessions/refs, neutral producers, no stale callbacks/
  admission/history/jobs, and settled node/resource counts/reference roots per phase.
- Keep raw timestamps from stop→deferred free→retirement→load→tree ready→admission→
  first draw, actual queue peaks/work and traffic. Persistent cache/shared resource
  plateaus are explained, not assumed leaks or unloaded bytes. No world streaming.
- Stop-box:≤two days, one recipe review/two development groups; correctness precedes
  graphical capacity. I1's saved-route reload remains an accepted T prerequisite,
  not proof of this integrated Match reset or a reason to rerun its historical group.

### C7 — telemetry / later authorized measurement readiness

- Owner: S07 capacity worker records costs; S08 owns exact target exports/input,
  Regner hardware/quality/representation/budget decisions. No environment repair.
- After D1–D4 and accepted relevant slices, preflight named build/hardware/surface,
  per-role capture counters/wire accounting/tool overhead and fixed phase/run caps
  below. If any required telemetry/drawability is unavailable, stop before launch.
- Proposed stop-box: one static launch-recipe review; runtime/export/capture each
  needs a separate grant. Physical input/Deck/Steam/full production remain unproved.

**Dependency/order:** D1–D3→C1/C2; C4 state/schema design can run independently of
art, then C2 query acceptance→C4 actual transitions; C2+C4→C3; C2+C4→C5;
C3+C4+C5→C6; D4+accepted relevant receipts→C7. C0 is independent, only for the
comparator. Graphical T can be authorized on its own existing prerequisites without
waiting for R preparation. No circular requirement to complete M1 is introduced.

## Concrete future measurement proposal — UNEXECUTED

Use the [common receipt and stop rule](s07-run-cards.md#common-future-launch-receipt-and-stop-rule)
and original [measurement definitions](s07.md#measurements-tools-and-stopping-rules).
The following is a proposed launch-phase allocation to make missing lifecycle work
commissionable; Regner/ROOT must accept it in a future exact recipe, not execute now.

### Entry / closure / roles

- Fill **named hardware H1**, OS/driver/CPU/GPU/RAM/storage/power/thermal state,
  build/content SHA, exact source/binary/templates/export identity, renderer/API/
  quality preset and capture tool/version/interval/overhead. All are currently
  **missing launch inputs**; historical desktop specifications are not a receipt.
  Native1280×800/100% scale, identical quality/content for uncapped/60-capped modes.
  No renderer/build/pin is selected here. S08 clean release/export and drawability
  gates must be independently satisfied for a qualifying graphical build.
- Freeze the two-sector closure I1→I2/I3/I4/I8 with all scripts/models/imports/UIDs/
  derived dependencies (accepted driver staged closure has46 files/five GLBs), not
  merely root scene. Comparator is its separate I5/I6/I7/I4 closure. Freeze a NEW
  six-block R closure with all C1–C6 saved prefabs/definitions/rigs/compiled scripts/
  derived data/resource identities and exact density/unique variety/bytes/placements.
  No six-block closure presently exists; path/count/fingerprint fields stay missing.
- R standalone has one local graphical authority. Network R has four processes:
  H graphical host/rig0 and C1/C2/C3 graphical clients/rig1/2/3, four unique admitted
  participant/player refs and safe spawn IDs. Together and separated are distinct
  cases, not four cameras in one process. Before launch save exact spawn coordinates,
  yaw, controlled refs, route IDs and camera frusta; these are missing choices, not
  the SVG's unvalidated candidate spawns. Separate views sample West shops/tower,
  Centre plaza/depot/alley, East housing/tower and yard/perimeter; prove all four
  frusta/distributions really differ while all global authority continues.
- Camera47 m/42° is provisional desktop candidate;50° is inherited alternative,
  not an extra matrix axis. Include genuine below/near/above-height towers, fast
  achieved car motion, foot/reverse-foot seams, abrupt control/view transitions and
  distant views. Freeze actual speed distribution/routes; S04 cap20 m/s is not an
  achieved route speed. If final camera/body/controls change, affected rows need new
  validation; a provisional row is labeled and cannot certify final feel/dimensions.

### Timed phases and attempt boundaries

The existing cards' measured caps remain: **T≤12**, **R≤18**, **G≤12** runs;
T one focused day, R≤two days, G one day. No run is executed or newly granted here.
One noisy-run replacement consumes an unused run slot, never adds a thirteenth/
nineteenth run. A failed correctness/identity/collision/telemetry row stops its case;
repeated budget/pacing/residency failure stops growth. No allocation-to-crash search.

| Card / phase | Concrete proposed recipe within the existing case boundaries |
| --- | --- |
| Primary T | Six runs: standalone uncapped/60-capped×three repeats,60 s warmup then600 s graphical route interval using unchanged accepted I1 admission/cancel/retire/reload APIs and route order `foot/east_to_north/west_to_south`. Preserve literal destination≤0.5 m/heading≤10°/nonempty progress/zero solid contact/one seam/max step≤0.15 m/route-error≤1 m checks and source identity. Report reload/first-use separately. This is new graphical measurement after a grant, not a repeated historical simulation acceptance group. |
| T comparator | Up to six runs, same cap/repeat split on I5, only after C0 and real draw gate.60 s warmup/600 s measure; twenty roots at t=15+30k s, k0…19; fresh-session saved baseline restoration between trials, loading/retirement explicitly marked. Each unchanged fixture trial expects twelve terminal cars/144 visits/peak4 target work, eight actual drawn slots/four cosmetic drops and off-camera same authoritative outcomes. No in-flight join/reset credit or new S06 triangles. |
| R capacity | Eighteen runs maximum: standalone, ENet four together, ENet four separated ×uncapped/60-capped×three repeats.60 s warmup/600 s full capacity interval with20 scheduled real chain roots t=15+30k s. All four network participants remain admitted for this interval. Freeze on/off-camera trial labels and exact expected cohort/outcome table before launch, real replenishment within32 live cars, actor/traffic/parked/global counts and projectile/cosmetic peak schedule. Unlike the comparator, integrated all-target/query work need not equal144: declare actual candidate targets/visits, accepted root/queue/completion deadlines and no dropped gameplay. |
| R lifecycle probes | Separately timed after the600 s capacity interval, same run/build/process identities; not scored as four-admitted steady capacity. Propose exactly TWO additional root probes per run: L1 one client leaves, current spare slot joins during chain; L2 same slot leaves/joins after chain settles. No fifth slot. Standalone substitutes same live/hydrate-state API checks, labeled non-network, never join proof. In L1 hold admission at a declared cut, commit actual car/player/population changes, then apply journal/handoff; one host reset interrupts hydration while another player drives/fires. Retain original join deadline and exactly-once current outcomes; no stale old-match effects/control. L2 checks settled state/active rockets without historical blast/sound replay. Exact gameplay expectations/safe timeouts need C6 receipt before launch. |
| R ten-cycle lifetime | After probes, exactly ten cycles per run: host reset with current peers→settled rehydrated counts; one client leave/rejoin→settled counts; safe Match teardown/all peers close→saved district reload/new session/admission→same settled counts. Standalone omits remote step, clearly labeled. These are diagnostic full-fixture reloads, not unloading sectors in travel. No chains added to these cycles. Track cache roots and per-process wire/residency at each boundary. |
| G conditional | Only if accepted R attribution implicates static placement/submission: existing card's N→2N, same bounds/assets/population/four-separated rigs/quality/events/lifecycle recipe. Twelve runs total for1×/2××two cap modes×three repeats. New2× scene distinct IDs/valid clearance/bake, doubled collider cost explicit. If another limiting axis appears, STOP; prepare one separate bounded proposal rather than cross-product or4×. |

The TWO extra lifecycle roots are an explicit **proposed phase allocation**, not
an unnoticed replacement of the cards' twenty measured trials or additional
approval: maximum22 roots per R/G run,20 per comparator; primary T has none.
Regner/ROOT must ratify this allocation or return a bounded alternative before
launch. All loading/teardown/probe timelines remain separate from normal percentiles;
burst costs within the600 s interval remain in full-interval percentiles.

Future launch envelope proposal: one entry preflight, no runtime repair, one start
attempt per allocated run, one controlled noisy replacement inside those caps;
no automatic restart after crash or failed correctness. Reserve cleanup **inside**
each card's total day cap. For a concrete supervisor, propose capacity wall cap
60+600+120 s per run, followed by separately instrumented lifecycle cap600 s total
for probes/ten cycles and30 s owned cleanup; stop admission/commands and retire only
owned handles at deadline. These are **proposed execution caps needing acceptance**,
not new gameplay/performance budgets. If draft join/close deadlines/ten-cycle work
cannot fit, stop at preflight and return a revised bounded recipe; never shorten
required phases or discard unfinished streams. At most one fresh authoring batch
for G2× before G, no fixture mutation during measurements. Hardware/export/transport/
renderer/device changes require a separate grant/case, not retries inside this cap.

### Outcome / traffic / resource cost packet

Retain every run's role/rig/spawn/content/bake/definition/build identity; real/absent
subsystem declaration; timestamped full raw samples/logs/diagnostics including failed
phases. Independent outcomes include route/contact/seam/map correctness, lawful
NPC work/off-camera outcomes, exact expected terminal/shot/event counts, live/wreck/
dead/rocket/cosmetic counts, identity fences/seat/death/respawn/reset invariants and
no callbacks/commands after teardown. Baseline/journal/movement/events all refer to
actual current state, not plausible synthetic payloads.

Record p50/p95/p99/max/variance per run/process for CPU main/render thread/GPU,
physics/AI/path/query/chain/encoding/apply; OS pacing/hitches; visible draw/surface/
geometry/material switches/shadow/light/alpha work; saved/resident/active counts
and unique/shared bytes; load/instantiate/tree entry/first-use/retirement costs;
OS resident/peak RAM and GPU allocation estimates with tool domain limits. Record
actual logical/decoded/baseline/journal/chunk/transport bytes, messages/rows/revisit
rates, per-client and aggregate-host traffic worst10 s windows/short peaks and
queue/overflow/per-tick processing. Capture overhead control uses the same case
without heavy profiling, consuming a run slot; if this cannot fit the cap, preflight
must return a scoped capture choice, not quietly add runs.

Compare only to the existing provisional brief/API values, separately labeled:
frame p95≤16.67 ms/p99≤20 ms; simulation p95≤4 ms/p99≤8 ms; resident≤2 GiB/GPU≤1 GiB;
host outgoing≤256 KiB/s/incoming≤128 KiB/s, client incoming≤96 KiB/s/outgoing≤48 KiB/s;
baseline≤1 MiB and draft load30 s/transfer10 s/handoff5 s/total60 s. No values are
approved here. CPU/GPU overlap, Deck shared memory and caches cannot be summed into
a fictitious budget. Report budget-minus-measured margin with variance, last passing/
first failing point, attribution and cheapest proposed intervention **or no-change**.
A passing2× point is only at least that tested density envelope, never maximum city.

## Separate user decision sheet

No acquisition/access request. Regner can commission each preparation slice later;
“Proceed” authorized this source-only plan, not the entries below. Record answers
with date/source and affected rows before any preparation/measurement launch.

| Decision | What must be decided / consequence of missing answer |
| --- | --- |
| D1 — representativeness/feasibility | Accept/revise this genuine bounded foundation approach and which actual systems/content subset honestly represents R's complete dimensions. Missing systems cannot be replaced with proxies. If real AI/combat/codecs/lifecycle/variety cannot be built within bounded spikes, resolve scope/ordering explicitly with retained risk; do not silently waive R or order M1 before P0. Required full target/Steam gates remain open. |
| D2 — counts/diversity/content | Choose exact six-block static placement/density N and eligible G set; building/prop family subsets/variants and distribution, two-car paint/damaged variety, outfit/rig/clip diversity, intended material/texture/shader/alpha/lighting/shadow treatment, texture dimensions/formats/mips and actual burst projectile/transient mix/peaks. Brief families and64/32/retained16/rocket16/explosion8/transient64 are inherited scope/provisional targets as labeled, not final manifests or measured loads. No unapproved variety counts filled in here. |
| D3 — final dimensions/camera/control | Settle S02/S04 camera/FOV/body/turn/exit/control/feel/prediction, S05 blast/wreck and S06 routes/map/clearance decisions with their required evidence.47 m/42°/50° and technical body/radius candidates are not ratified by this plan. Identify affected saved content/bakes/route/contact/graphics rows for revalidation; keep tall building problem and physical input proof. |
| D4 — budgets and measurement recipe | Ratify/revise existing numerical brief/API performance/size/rate/queue/deadline targets with their owners; preserve confirmed native Deck/60 FPS constraints. Name later hardware/build/telemetry/quality/drawable boundary, choose the proposed separate lifecycle allocation22 roots/ten cycles and execution/cleanup caps or return another finite recipe. This record chooses no budget, renderer, pin, streaming, integration or target acquisition. |

Future M1 still owns production shell/settings/audio/polish/catalogue/general lifecycle/
population validation, selected Steam integration/delivery and sustained target tests.
Bounded preparation acceptance means only its stated source/content/API outcomes;
R still needs honest integrated representative work and actual graphical costs.
T/R/G/S07/P0/M1, hardware/drawability/physical-input/product and actual Steam gates
remain OPEN. S08 original-main20ms diagnostic is **NOT authorized**; no follow-up
preparation slice or test is launched by this delivery. ROOT alone integrates/archives.
