# Task-specific requirements

Open acceptance omitted from the concise [task list](../../TODO.md). Spike records and
canonical guides own their technical detail; this index carries only task-specific
qualification and enough outcome detail for dispatch.

## Foundations

[Owner instruction 12](../reviews/owner-decisions-2026-10-08.md) authorizes S09–S16
and the audit-derived tasks in
[section 4 of the readiness audit](../reviews/p0-readiness-audit-2026-10-08.md).
Their quantitative criteria are orchestrator proposals derived from the current product
budgets, not ratified values; the owner reviews them at P0-GATE.

- **P0-TOOLING:** Repair the validation baseline before production: make the canonical
  script check green, provide one command that discovers every Python test, use a
  cross-platform Mise interpreter, ignore GodotSteam temporary import libraries and
  strip the MCP autoload from compile mirrors. Proposed acceptance is clean execution
  of the complete documented script and Python checks on current main.
- **P0-PROFILES:** Keep this as a Paseo profiles task for later review. It is
  non-blocking and outside P0-GATE; do not configure or install profiles now.
- **S01-W:** Run the S01 reexport pipeline with the installed Windows Blender 5.2,
  recording its exact version and comparing outputs with the Linux-authored GLBs.
  Proposed acceptance is byte identity, or a documented platform pin/semantic check
  when byte identity is impossible, before Windows-authored S13/M1-C1 assets proceed.
- **S02:** The ratified 47 m, north-up 42° camera, normalized screen/world-relative
  WASD movement, mouse-ground facing, left-click fire and cutaway removal are implemented.
  Remaining acceptance is physical-key Alt-Tab/focus plus desktop control/aim/feel review;
  gamepad and Deck work are deferred.
- **S03-S:** The initial game uses ENet only. Review session and transport APIs for
  a later Steam adapter covering friend joins, lobby identity mapping, reliable and
  unreliable lanes, and connection lifecycle. Steam-specific implementation and tests
  are deferred.
- **S03-R:** Close drawn owned/remote response and desktop feel. Historical response
  p95s measured under the S08 ENet defect remain history, not acceptance. The post-fix
  Windows adverse drawn run reached 379 ms but failed its expiry criterion because one
  receipt read 253 ms against the 250 ms boundary; apply or reject the pending
  measurement-boundary analyzer fix and rerun before acceptance.
- **S03-L:** Diagnose the unexplained post-fix Windows authority latency end to end,
  comparing proxy/direct loopback, timer resolution, headless/windowed pacing and engine
  settings. Proposed acceptance is a per-stage latency budget, an artifact fix or explicit
  platform finding, and a disposition of the S03-R adverse expiry-boundary analyzer.
- **S03-P:** Implement required local-character prediction with shared movement rules,
  replay limited to permitted local simulation, no replay side effects and authoritative
  corrections winning. Proposed acceptance covers collision replay, matching-tick
  reconciliation and correction behavior under normal/adverse ENet profiles.
- **S04:** Use the standalone drive scene for owner handling review. Cars cannot fire;
  exit succeeds only below 0.5 m/s and otherwise returns `EXIT_MOVING`; a disconnected
  driver's car coasts without braking. Rerun affected handling/rule cases after S02.
- **S04-P:** Implement required local-driver prediction using shared drive rules,
  side-effect-free replay and authoritative corrections. Proposed acceptance covers
  replay against moving cars and matching-tick correction under normal/adverse profiles.
- **S04-T:** After S03-P/S04-P, prove foot-to-car transitions across predicted bodies
  with host-granted and racing claims, `EXIT_MOVING`, blocked exits, traffic-car theft
  and disconnect coasting.
  Proposed acceptance includes replay-history/camera/HUD ownership transfer plus measured
  discontinuity and corrections for accepted/rejected transitions under both profiles.
- **S05:** Uncapped presentation now passes the saved 12-car fixture with 12 effects
  drawn and none dropped, using the accepted damage/radius/chain/wreck defaults.
  Remaining acceptance is drawn wreck presentation, in-flight rather than settled-only
  hydration, final-dimension/contact checks and effect cost (owned by S15).
- **S06:** The grey-block 9 m roads, 4 m sidewalks and 48 m extent are accepted.
  The minimap's top-right position is accepted; its size and look are not. Commission
  and iterate whole-UI mockups, then revalidate layout/crossing/minimap readability.
  Partial topology is not production traffic or recovery evidence.
- **S07:** The [completed environment-scale record](../spikes/s07-environment-scale.md)
  measured saved grey-block cities at 6/24/96/384 blocks with the 42° camera. Six, 24
  and 96 blocks passed its desktop stop limits; 384 crashed before telemetry, making
  96 the last observed pass and 384 the first fail. This is planning guidance, not a
  capacity gate or M1 district expansion. S08-C owns the distinct 384-block diagnosis.
- **S08:** Stay on Godot 4.8-dev7. Keep the S03Transport workaround for the upstream
  ENet bandwidth defect and retain the offline upstream review; do not file the proposed
  issue yet. Windows is the current development platform. Linux original-main and
  Linux-only release-diagnostic confirmation remain follow-up for a Linux machine and
  do not block proceeding. M1 targets Windows/Linux desktop; Deck is later.
- **S08-X:** Prove real-project export configuration rather than another stripped scratch
  export. Add a minimal boot/main scene and Windows/Linux presets, decide GodotSteam's
  M1 exclusion, verify MCP export inactivity and bind template versions/hashes. Proposed
  acceptance includes Windows launch with Steam absent and a later Linux Vulkan launch
  checklist at 1280×800 on the available Linux machine.
- **S08-C:** Diagnose the 384-block `0xC0000005` with one quiet rerun, crash/backtrace
  capture, a bounded block-count bisection and cutaway on/off comparison. Proposed
  acceptance records the first-fail boundary/cause limits and replaces unsafe uncapped
  GPU-headroom runs with a documented capped RenderingServer timing method.
- **S09:** Decide host-owned traffic path following, car following, intersection,
  blockage recovery and out-of-view replenishment while using the shared S04 drive
  rules. Proposed acceptance uses saved loop/intersection/wreck scenarios at 24 and
  32 moving cars, three seeded 10-minute runs, cost/collision/deadlock/recovery/lane-error
  results and a proposed share of the host physics budget.
- **S10:** Decide host-owned pedestrian wandering, crossing, avoidance, flee, car-hit
  and bounded replenishment rules on S06 topology. Proposed acceptance compares at least
  two motion options with 64 pedestrians, flee and traffic interactions, three seeded
  10-minute runs, behavior/cost metrics and a proposed host-tick budget share.
- **S11:** Decide population snapshot/lifecycle replication, interpolation, interest
  and spawn policy for the full global caps. Proposed acceptance uses separate ENet
  processes under normal/adverse profiles, reliable lifecycle isolation and measured
  worst-window host/client
  bandwidth and join bytes against the existing budgets, smoothness/codec CPU results,
  and bounded out-of-view safe replenishment/reset rules.
- **S12:** Decide authoritative hit registration for predicted shooters and interpolated
  targets by comparing host-time validation with bounded host rewind. Proposed acceptance
  uses separate normal/adverse ENet processes, hitscan agreement/false-positive results,
  rewind CPU and
  history memory, rocket presentation offset, and recommended M1 combat bounds/defaults.
- **S13:** Decide the shared player/pedestrian rig, animation update and palette-variant
  strategy. Proposed acceptance uses a source-linked Blender/GLB technical blockout and
  saved crowd of 68 live plus 16 dead characters, capped windowed/headless measurements,
  and
  with/without off-screen throttling frame/CPU/GPU/draw/skinning results.
- **S14:** Decide listener placement, buses, voice priority/caps, 3D attenuation,
  variation and settings persistence for the required audio families. Proposed acceptance
  uses generated licence-tracked placeholders and a saved 32-engine/24-explosion/SMG stress
  scene, bounded voice/mix results, settings roundtrip and an owner listening checklist.
- **S15:** Decide cost-effective saved muzzle, impact, tracer, rocket-trail and explosion
  effects while preserving an effect for every explosion. Proposed acceptance uses capped
  Forward+ stress at 12/24 explosions, four SMG shooters and 16 rockets, retained frame/CPU/GPU/
  particle/draw evidence, per-effect budgets and a non-dropping quality fallback.
- **S16:** The completed [M1 production-plan proposal](m1-production-plan.md) maps rule
  owners and simulation boundaries, disposes S02–S15 fixtures, proposes testing/CI,
  orders and sizes the backlog, identifies the first five tasks, and records risks and
  owner questions. P0-GATE reviews the proposal; this task is not reopened.
- **S17:** After S09–S12, compose one full-cap headless host from their fixtures: 64
  pedestrians, 24 moving plus 8 parked cars, four firing players, a 12-car chain and
  S11 encoding for three clients. Proposed acceptance measures subsystem and total tick
  median/p95/p99 in quiet and contended runs, compares proposed p95 ≤4 ms/p99 ≤8 ms,
  and reconciles oversubscribed subsystem shares before production architecture freezes.
- **P0-GATE:** Review foundation evidence against the 8 October owner decisions after
  unfinished blocking S02–S06 and S08 work; S03-P, S04-P, S04-T, S09–S15, S17,
  P0-TOOLING, S01-W, S03-L, S08-X and S08-C. Completed S07 guidance and the S16 plan
  are gate inputs, not open tasks. Do not reopen ratified choices without a new owner
  decision. New quantitative criteria are orchestrator proposals pending owner review;
  Linux-only S08 confirmation and P0-PROFILES remain non-blocking.

## Checkpoint follow-up

Completed discovery reconciliation: [P0-DOC14 record](../reviews/p0-doc14.md).

## First milestone

- **M1-A1:** Deliver standalone/ENet sessions and Steam-adapter-capable boundaries;
  menu flows must handle cancel, stale/failure/host loss and cleanup. Only host/standalone
  can reset. Steam friend sessions are owner-deferred beyond M1.
- **M1-A2:** Share rules offline/authority/permitted prediction; handle focus/expiry,
  respawn and reset rehydration before input while rejecting stale-match commands.
- **M1-A3:** Persist validated audio settings with defaults/recovery and live preview;
  device settings cannot mutate shared gameplay.
- **M1-A-GATE:** Validate two exported ENet processes, settings and lifecycle/reset/error
  flows with Steam absent. Actual Steam gameplay transport is owner-deferred beyond M1.
- **M1-B1:** Implement vehicle handling and authoritative driver transitions; resolve
  claim/exit/death/disconnect/destruction races and preserve parked-car policy.
- **M1-B2:** Implement the ratified weapons and authoritative damage/death state; reject
  stale fire commands and hydrate late joiners.
- **M1-B3:** Bound/deduplicate chains and complete wreck/collision lifecycle; late join
  and reset restore current state without replaying old effects/work.
- **M1-B4:** Add readable bounded effects and licensed/source-tracked audio; review the
  walk/shoot/drive/chain slice for duplicate feedback, aim/map readability and cost.
- **M1-C1:** Produce ratified buildings, roads/props, character rigs, cars/wrecks, weapons
  and VFX. Preserve Blender-linked sources, catalogue/ancestry and reexport/reload.
- **M1-C2:** Start with approved M1-C1 road/building/prop subsets; don't wait for unrelated
  art families. Use S06 topology and S07 environment-envelope guidance to compose saved
  sectors, routes, play space, spawns and boundaries; preserve placement and prove
  seams/clearance/readability.
- **M1-C3:** Implement bounded host-owned pedestrians/traffic, legal routes, crossing and
  blocked/stuck recovery, NPC transfer, late joins and reset without moving city content.
- **M1-C4:** After M1-A2 and the S06 contract (covered by P0-GATE), build the road map
  from shared city data and local entity marker; align with M1-C2 when the district is ready.
  Check walking/driving/late-join seams and read HUD values from gameplay owners.
- **M1-D1:** Build reproducible local/CI checks that catch owned code/resource/gameplay
  violations, including unused scripts, without broad suppression or copied formulas.
- **M1-D2:** Playtest desktop keyboard/mouse multiplayer feel, camera/aim, driving,
  spectacle, exploration, menus/focus and audio; fix findings or have the user scope
  them out. Gamepad/controller playtesting is owner-deferred.
- **M1-D3:** On named Windows/Linux hardware, verify ratified performance/capacity and
  bounded adverse-network lifecycle through real ENet processes/APIs; measure frame/
  physics, draw, memory, bandwidth, queues and response. Culling cannot stop required
  simulation and optimization needs evidence. Steam transport testing is owner-deferred.
- **M1-D4:** Export Windows/Linux targets with exact templates/identity/exclusions and
  verify launch, keyboard/mouse input, audio and ENet routes. Retain results/rollback.
  Steam private-branch delivery and Deck/gamepad checks are owner-deferred.
- **M1-GATE:** User reviews the ratified playable district, gameplay/population/minimap,
  readable feedback, audio/settings, menu/lifecycle/reset, ENet multiplayer, desktop feel,
  Windows/Linux targets and delivery. Deferred Steam, Deck and gamepad evidence does not
  block M1.

### Owner-deferred follow-up after M1

- Implement and test actual Steam friend sessions, authorized-account gameplay transport,
  external routes, install/update/invite flows and private-branch delivery while preserving
  ENet/offline availability and the abstraction contracts reviewed in S03-S.
- Implement and review gamepad/controller gameplay and menu flow, then validate native
  1280×800 LCD/OLED Deck Gaming Mode, 60 FPS, hosting/joining, suspend and Steam delivery.
