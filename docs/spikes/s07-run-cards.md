# S07 static fixture inventory and prepared run cards

8 October 2026. **STATIC preparation; all capacity runs UNEXECUTED.** This extends
[the existing method](s07.md#bounded-experiment-method) with saved inputs;
it adds no capability research, fixture, optimization or configuration decision.
Initial clean branch `s07-content-inventory-run-cards` was rebased from `352f5706`
to local main `52941da4b4c92a547a8066b5c13f733043ecbe48`. The accepted TODO-only
cleanup base is `48aef3dbd133876743f504f94a1b788a26d5638f`; its concise remaining-work
format is preserved. Inventory input bytes are bound to the initial accepted base;
the TODO cleanup changes none of them. [Evidence and reproduction](s07-run-card-evidence/README.md)
record scope, checks and raw commission. S07 stays open.

## Actual saved inputs

The [deterministic JSON inventory](s07-run-card-evidence/inventory.json) covers all
files directly in `tests/fixtures/{s02,s04,s05,s05_effect,s06}`, their saved external
resource links and literal existing script references, four Blender sources and
14 GLB exports/import sidecars. It binds 186 input files by byte count and SHA-256.
Editor harness dependencies are included as static references; vendor recursion
stops at `addons/`. S03 dependencies provide inherited session scaffolding, not
additional representative content. This is a bounded inventory, not a production
catalogue or a whole-project runtime dependency resolver.

Saved external UID/path pairs, node IDs, inherited composition, export membership,
GLB headers and source signatures are checked without Godot or Blender. The helper
reuses `tools/check.py:glb`, `tools/s06/check_resources.py:uid` and the saved-effect
link checks from `tools/s05_effect/check_resources.py`; no old engine check is run.
Source-to-export mappings come from the saved handoffs/membership records, not a new
Blender reopen/reexport. Source geometry and current export equality are not re-proved.

| Committed source → explicit collections/exports | Actual saved consumers |
| --- | --- |
| `art/source/models/spikes/s02_kit.blend` → nine `export_s02_*` collections in [membership](../../tools/s02/export_members.json) | `s02` wrappers → corner/corner_wide/weapon_studies; actor/pistol also in S06 intersection. [Source handoff](../assets/s02_kit.md) owns envelopes and downstream consumers. |
| `art/source/models/spikes/s04_kit.blend` → `export_s04_car`, `export_s04_track` in [membership](../../tools/s04/export_members.json) | `s04/kinematic.tscn`, `dynamic.tscn`, `track.tscn` → S04 boot/body comparison; S05 car inherits kinematic, boot/burst reuse car/track; S06 uses two kinematic cars. [Source handoff](../assets/s04_kit.md) owns provisional geometry. |
| `art/source/models/spikes/s05_explosion_carrier.blend` → `export_s05_explosion_carrier`, sole `ExplosionCarrier` → carrier GLB | `s05_effect/explosion.tscn/Visuals/Model` → eight saved `Presentation/Slots/Slot0…Slot7` in inherited boot and burst. [Source preparation](s05-effect-preparation.md) and [saved presentation](s05-saved-presentation.md) retain provenance. |
| `art/source/models/spikes/s06_intersection.blend` → `export_s06_west/east` in [membership](../../tools/s06/export_members.json) | `s06/west.tscn`, `east.tscn/Visuals/Model` → intersection/intersection_wide. [Source handoff](s06-source-handoff.md) and [topology contract](s06-contracts.md) own the two-sector interpretation. |

All exports are under `art/models/spikes/`, with the matching `.glb.import` UID.
All source files are excluded from import by `art/source/.gdignore`. GLB bytes total
433,824; the four sources are 167,214 / 123,668 / 117,308 / 104,919 bytes respectively.
These are **disk bytes**, not loaded resource or GPU allocations. Exact fingerprints,
GLB node transforms and mesh-local POSITION accessor bounds are in the JSON.

| GLB stem | Bytes | Mesh definitions / primitive definitions | Triangles per exported mesh-node placement set | Material definitions |
| --- | ---: | ---: | ---: | ---: |
| s02_ground | 11,840 | 2 / 2 | 376 | 2 |
| s02_low | 22,176 | 4 / 4 | 752 | 4 |
| s02_near | 64,740 | 14 / 14 | 2,632 | 4 |
| s02_tall | 82,268 | 18 / 18 | 3,384 | 4 |
| s02_actor | 38,076 | 7 / 7 | 1,316 | 3 |
| s02_target | 11,864 | 2 / 2 | 376 | 2 |
| s02_pistol | 12,044 | 2 / 2 | 376 | 2 |
| s02_smg | 17,880 | 3 / 3 | 564 | 3 |
| s02_launcher | 17,892 | 3 / 3 | 564 | 3 |
| s04_car | 42,912 | 8 / 8 | 1,504 | 4 |
| s04_track | 33,212 | 6 / 6 | 1,128 | 4 |
| s05_explosion_carrier | 27,536 | 1 / 3 | 1,344 | 3 |
| s06_west | 25,700 | 17 / 17 | 204 | 4 |
| s06_east | 25,684 | 17 / 17 | 204 | 4 |

Triangles are index-count/3 for these triangle primitives; mesh-node reuse is
accounted for separately from definitions. All 14 GLBs contain zero images,
textures, skins and animations. Palettes are embedded source-owned flat materials;
same material names across exports do not establish one shared imported resource.
The carrier's three materials are opaque by GLB default (no `alphaMode`), alpha1,
double-sided, roughness≈0.8. It is no transparent-overdraw or animated VFX proof.
S02 buildings create local shader materials per mesh in `building_view.gd` and use
the cutaway shader; the static palette count excludes those runtime allocations.
The corner has 40 building mesh placements (2×4 +14 +18); their material creation
and discard cost are still unmeasured. None of these primitive counts is a DRAW count.

| Saved composition (`tests/fixtures/`) | Actual linked placements | Saved nodes excluding GLB internals | All-placement primitives / triangles |
| --- | --- | ---: | ---: |
| s02/corner; corner_wide | Ground1, low2, near1, tall1, actor1, pistol1, targets2 | 57 each | 55 / 10,340 each |
| s02/weapon_studies | Ground1, actor3, pistol1, SMG1, launcher1; study assemblies have no gameplay | 24 | 31 / 5,828 |
| s04/boot | Track1, cars2 | 49 | 22 / 4,136 |
| s04/body_comparison | Track1, cars3 (one kinematic/two rigid body candidates) | 46 | 30 / 5,640 |
| s05/boot; burst | Track1, cars3 / cars12 | 55 / 154 | 30 / 5,640; 102 / 19,176 |
| s05_effect/boot; burst | Inherit preceding fixtures, add eight carrier instances each | 80 / 179 | 54 / 16,392; 126 / 29,928 |
| s06/intersection; intersection_wide | West1, East1, actor1, pistol1, cars2 | 79 each | 59 / 5,108 each |

Totals include hidden/passive placements and exclude runtime-spawned S03 markers,
GLB-internal nodes, collision pairs, imported processing and script-created resources.
They express saved composition only. Local transforms/overrides and origin resource
paths are retained in `scenes_and_resources`; they are not world-space AABB estimates.
The eight explosion roots start `visible=false`; an instance link never proves draw.
S02/S04 Suns explicitly enable shadows; S06 saves light energy1.2 without a
shadow override. Import sidecars request generated LODs/shadow meshes; their actual
imported geometry and render cost are outside this offline GLB accounting.
S06 has four saved island StaticBody3Ds, three CharacterBody3Ds and seven saved
collision shapes. Its 13 topology anchors and nine links are not a navmesh: three
FOOT links, two directed TRAFFIC curves and four ROAD links. `derived.tres` retains
fingerprint `eaec39bbde6bd39e0b9c6c5c005f6285be49881faeb3a2cbfa02363014ff1604`;
this session reads it, without recomputing its engine bake/signature.

The commission supplies accepted S05 `a15a7fb` as an input supplement. Existing
saved-presentation/TODO records still describe independent acceptance as pending;
this inventory does not edit that dated disposition or manufacture a review.
Its [actual retained finite ENet result](s05-saved-presentation-evidence/network/result.json.gz)
was decoded/read: twelve zero-health outcomes, 144 visits, eight saved-node peak,
four drops, live12/duplicate12, settled-late zero historical effects. Those are
finite technical node/API receipts, **not eight DRAW receipts, four graphical views,
during-chain join/reset, moving-wreck-contact or sustained capacity**. Earlier S07
supplements' token-only/missing-authored-slot statements are historical snapshots;
the saved slots now exist, while draw/cost remains missing.

## Entry gaps and ownership

| Required input | Actual coverage / blocked entry criterion | Existing owner |
| --- | --- | --- |
| Two-sector technical topology/bodies | Saved source-linked S06 planar intersection exists. Only one commanded body moves at a time; traffic target3.5 m/s, foot default5 m/s. No RPC/prediction/population integration; final bodies/exit/contact/readability still open. | S06, S02/S04; M1-C3 for contested recovery |
| Actual effect presentation | Eight saved linked carriers and finite API/ENet checks exist. Need actual eight-effect DRAW/saturation/fallback and live-versus-hydrated graphical receipts on an authorized surface before an effect-cost row. | S05; ROOT grants drawable work |
| Six-block representative content | No saved six-block district in these inputs. S02 has technical6/46/60 m building masses; S06 is a48×48 m intersection with low islands. Missing production buildings/props/two car silhouettes, textured/animated pedestrian variants and integrated lighting/content density. | M1-C1/C2 asset/world handoffs; Regner accepts representation |
| Production simulation/network | No64 pedestrian/32 live-car district, replenishment, production codecs, four admitted graphical player rigs, complete death/seat/reset/journal lifecycle or population AI load in this inventory. Technical chain/route fixtures cannot stand in. | M1-A/B/C3; S03/S03-R/S04 contracts |
| Hardware and telemetry | No current named machine/build/template/driver/power/storage or trustworthy CPU/GPU/residency/pacing capture has been supplied for these cards. Historical desktop specs in design are not a launch receipt. | S07 experiment worker; S08 exact exports |
| Four separate graphical views | S06 is standalone; S05 finite ENet uses host/live/settled-late headless processes. Need one graphical host plus three admitted clients, one rig/process, together then separated, with real authoritative content. | S07 with gameplay/network owners |
| Physical targets/Steam | LCD/OLED Gaming Mode/input/native1280×800/60 FPS and actual multi-account external Steam remain deferred. No new availability request or substitute. | S08/S03-S, then M1-D3/D4 |

## Common future launch receipt and stop rule

**Prepared cards are not runtime authorization.** ROOT assigns a named experiment
worker, saved-resource ownership and a1–2-day budget only when each card's entry
criteria is satisfied. This static commission authorizes none of that work.

Before each future launch record: exact engine/source/binary/templates/build SHA;
content scene/GLB/import/source and derived-data fingerprints; OS/driver/CPU/GPU/RAM/
storage, power/thermal mode; one explicitly commissioned renderer/API/quality preset,
1280×800 at100% scale; capture tools/versions/intervals/overhead. Those fields are
currently **BLOCKED/unassigned**, not inferred from available hardware or research.
Record per-process role/rig, camera, routes/speeds, seed or deterministic schedule,
saved/visible/resident/active counts and bytes in their separate accounting domains.
Use fully loaded saved sectors. No unloading, streaming, origin, renderer or quality
choice follows from this inventory.

For each selected case:60 s warmup,600 s measurement,20 burst trials where that
card includes real effects, three separate repeats, uncapped and60-capped at identical
content/quality. Retain raw samples and per-run p50/p95/p99/max/variance for CPU main/
render thread, GPU, physics/AI/query/chain, pacing, render counts, per-process memory,
resource/node counts, load/first-use/seam/teardown and network bytes/queues. Missing
telemetry is an explicit gap. Compare to the existing [provisional design envelope](../design.md#provisional-validation-envelope),
not a new budget. CPU/GPU overlap and Deck shared-memory accounting are not summed.
Use [the existing measurement/stop rules](s07.md#measurements-tools-and-stopping-rules):
stop immediately on correctness/identity/collision failure; stop growth on repeated
budget/pacing/residency/lifetime/telemetry failure; one controlled noisy-run rerun
within the total run cap. Keep last passing/first failing and budget-minus-measurement
margin with variance. An all-pass row supports only its tested envelope.

## T — Technical two-sector calibration (BLOCKED, not representative capacity)

Question: can the exact small linked topology and actual bodies be observed
repeatably, with attributable graphical costs and no identity/collision failure?
Future budget: one focused day; at most12 measured runs total, no growth variants.

- Primary input: [S06 intersection](../../tests/fixtures/s06/intersection.tscn),
  West/East at saved identity, source X/Z[-24,24] and seamX0, four islands, one actor/
  pistol/two cars. Camera downward perspective47 m/42°, near0.1/far160 m; inherited
  [wide variant](../../tests/fixtures/s06/intersection_wide.tscn) is50° and remains
  an unused alternative in this card. No height stress exists in this layout.
- Run six primary cases: uncapped/60-capped × three repeats, standalone graphical
  authority only. Deterministic route order through existing `start_route`: `foot`
  west(-20,0.001,6.5)→east(20,0.001,6.5), `east_to_north` car(-20,0,2.25)→(2.25,0,-20),
  `west_to_south` car(20,0,-2.25)→(-2.25,0,20). Neutralize/reset through accepted APIs
  between routes. One moving body at a time, traffic3.5 m/s, foot5 m/s; repeat order
  through the interval. Existing1200/1800-tick timeout is a failure receipt, not a
  completed route. This is neither fast driving nor production AI load.
- Separate effect comparator, only after its own draw gate: at most six cases on
  [saved S05 effect burst](../../tests/fixtures/s05_effect/burst.tscn), same cap/repeat
  split and named graphical host role. Twelve cars at a4 m grid, eight saved slots.
  Use20 single-root trials at measured t=15+30k seconds (k0…19), restoring the same
  accepted baseline between trials. Need an accepted reset/event driver before
  launch; existing finite proof is not that sustained driver. Retain exact car
  outcomes/visits and eight DRAW/four cosmetic drops per supported trial, off-camera
  outcomes and cleared local effects. If unsupported, comparator stays BLOCKED.
  This layout is a separate track control; it is not integrated into S06 or added
  to the5,108-triangle two-sector total.
- Entry: named hardware/build/telemetry and real drawability for primary; actual
  drawable S05 gate plus trial-reset receipts for comparator. Saved scene reload/
  source-link validity must be confirmed by the later authorized owner. Four-view,
  six-block and production-capacity rows remain blocked by the table above even if
  T succeeds. Outputs report technical calibration only; no capacity maximum or
  optimization decision. A noisy rerun replaces a remaining run within the12 cap.

## R — Six-block representative baseline (BLOCKED)

Question: what is the repeatable cost and limiting axis of the ratified district
at its actual content and global load? Future budget: up to two focused days,
max18 measured runs (three role/distribution cases × two cap modes × three repeats).

Inputs must be accepted **new saved content**, not S06 copies labeled production:
the roughly284×187 m buffered six-block reference from [world layout](../world-layout.md),
actual topology/bakes and linked prefab identities, measured building/prop/material/
texture/animation variety and bounds. Freeze the manifest with exact placed counts
and unique bytes before launch; these quantities are missing and deliberately unset.
Integrate the actual actor/car/envelope/effects with64 live pedestrians,32 live cars
(initial24 traffic +8 parked, occupied within32), plus four players; retain the
design's16 wreck/16 dead-presentation/16 rocket/8 explosion/64 transient-effect caps.
These are provisional targets, not implemented or measured loads here.

Cases: standalone; graphical ENet host+three clients together; same four processes
in separated district areas. Name actual separated spawn/camera coordinates in the
new saved manifest before admission; one local rig per process, no split-screen or
headless view substitution. Fixed47 m/42° camera assumptions must be accepted for
that content; towers6/46/60 m supply below/near/above-height controls through real
linked content. Freeze accepted seam-crossing foot/reverse-foot and rapid car routes,
actual speed distributions (S04 technical forward cap20 m/s is not achieved route
speed), seed17 if a real seeded population owner exists, otherwise the owner's exact
replayable event log. Invalid reverse traffic never becomes a route for coverage.

During each600 s interval include20 scheduled actual chain trials at t=15+30k s,
on-camera and off-camera, with reliable outcomes independent of cosmetics. Allocate
join-during/after-burst, reset, leave/rejoin and ten safe teardown/reload cycles to
explicit timed phases in the commissioned recipe; retain separate loading/lifetime
timelines and compare settled resource counts. Do not implement world streaming to
supply the diagnostic. The present fixtures lack those integrated lifecycle recipes.

Entry: six-block saved manifest/representativeness acceptance, production owners/
codecs/animations/population, drawn effects, actual four graphical processes/views,
named hardware/export/telemetry and reproducible event/lifecycle driver. Missing any
relevant subsystem blocks representative capacity acceptance. Retain per-process
costs and aggregate host transport overhead, correctness and explicit target gaps.
Desktop ENet results cannot close Deck/Steam, feel, P0-GATE or M1-D3 acceptance.

## G — One bounded density-growth step (BLOCKED behind R)

Question: at the same six-block bounds, asset variety, camera, four-view distribution
and active population, what headroom remains when saved static placement work doubles?
This is a **candidate density axis**, conditional on R's measured risk implicating
static object/submission work. If R identifies a different limiting axis, stop and
prepare one separately bounded card; do not run this axis or a cross-product matrix.
Future budget: one focused day, two saved layouts total, max12 measured runs.

Freeze R as1× with exactlyN eligible building/prop prefab placements, where N is
read from R's accepted manifest (currently missing). Commission one2× saved variant
with2N placements in the same bounds and comparable declared spatial distribution;
keep shared imported assets/materials/textures and population/event schedule fixed.
The new placements need distinct world IDs, preserved source/UID links, gameplay
clearance and valid affected topology/bakes; doubling colliders is reported explicitly,
not hidden as purely rendering growth. No runtime hierarchy generation or duplicated
spawn identities. Keep both full layouts resident; report total versus visible static
placements and actual bytes. No4× step is allocated by this card and no larger M1
city is authorized.

Use only R's named graphical host+three-separated-client case, uncapped/60-capped ×
three repeats for1× and2× (12 runs including baseline comparison); reuse R's fixed
routes/bursts/lifecycle phases and capture definitions. Entry: accepted R manifest
with N, valid saved2× scene/contact/topology review, measured justification for the
axis, same hardware/build and trustworthy graphical/lifetime telemetry. Retain1×
and2× identities, last-pass/first-fail, margin and limiting evidence. If either point
fails correctness stop; if budgets fail retain that row and do not grow. A passing2×
point establishes at least that tested density envelope, never maximum capacity.
Only subsequent measured attribution can support a cheapest intervention or no-change
recommendation under the existing S07 method.
