# Task-specific requirements

Open acceptance omitted from the concise [task list](../../TODO.md). Spike records and
canonical guides own their technical detail; this index carries only task-specific
qualification and enough outcome detail for dispatch.

## Foundations

- **P0-PROFILES:** Keep this as a Paseo profiles task for later review. It is
  non-blocking and outside P0-GATE; do not configure or install profiles now.
- **S02:** Implement the ratified 47 m, north-up 42° camera and replace tank turning
  with normalized screen/world-relative WASD movement at 5 m/s, instant start/stop,
  mouse-ground facing each physics tick and left-click fire. Remove building cutaway;
  keep held weapon silhouettes. Revalidate focus and control/aim/feel on desktop;
  gamepad and Deck work are deferred.
- **S03-S:** The initial game uses ENet only. Review session and transport APIs for
  a later Steam adapter covering friend joins, lobby identity mapping, reliable and
  unreliable lanes, and connection lifecycle. Steam-specific implementation and tests
  are deferred.
- **S03-R:** Implement required local-character prediction with shared movement rules,
  replay limited to permitted local simulation, no replay side effects and authoritative
  corrections winning. Then close drawn owned/remote response and desktop feel. Historical
  response p95s measured under the S08 ENet defect remain history, not acceptance.
- **S04:** Add a standalone drive scene for handling review. Cars cannot fire; exit
  succeeds only below 0.5 m/s and otherwise returns `EXIT_MOVING`; a disconnected
  driver's car coasts without braking. Local-driver prediction is required under the
  same replay/correction rules as S03-R. Rerun affected cases after S02 choices.
- **S05:** Remove the on-screen explosion cap: every explosion receives its effect.
  Start from 100 car HP, 100 blast damage, 4.1 m radius, no falloff or obstruction,
  0.1 s chain delay, 5 s wreck duration and friendly fire/self-damage always on.
  Remeasure effect cost and update saturation evidence without dropped presentations;
  settled hydration is not in-flight proof.
- **S06:** The grey-block 9 m roads, 4 m sidewalks and 48 m extent are accepted.
  The minimap's top-right position is accepted; its size and look are not. Commission
  and iterate whole-UI mockups, then revalidate layout/crossing/minimap readability.
  Partial topology is not production traffic or recovery evidence.
- **S07:** Reframe this as a visual/graphical environment-scaling investigation, not
  a requirement or capacity gate. Build saved city variants of increasing block counts
  (for example 6, 24, 96 and 384; stop early at a limit) from existing grey-block sectors
  and building prefabs. Measure load time, RAM/VRAM, node/static-collider counts and
  60-capped frame time along a 42° camera route. Report a cost-versus-block envelope,
  caveating shared grey-block assets versus production-art variety and no Deck result.
  Network, AI and population are out of scope; budgets are guidance only. Do not repeat
  the accepted sustained primary-T driver.
- **S08:** Stay on Godot 4.8-dev7. Keep the S03Transport workaround for the upstream
  ENet bandwidth defect and retain the offline upstream review; do not file the proposed
  issue yet. Windows is the current development platform. Linux original-main and
  Linux-only release-diagnostic confirmation remain follow-up for a Linux machine and
  do not block proceeding. M1 targets Windows/Linux desktop; Deck is later.
- **S09:** Decide host-owned traffic path following, car following, intersection,
  blockage recovery and out-of-view replenishment while using the shared S04 drive
  rules. Accept with saved loop/intersection/wreck scenarios at 24 and 32 moving cars,
  three seeded 10-minute runs, tick-cost/collision/deadlock/recovery/lane-error results
  and a proposed share of the host physics budget.
- **S10:** Decide host-owned pedestrian wandering, crossing, avoidance, flee, car-hit
  and bounded replenishment rules on S06 topology. Accept after comparing at least two
  motion options with 64 pedestrians, flee and traffic interactions, three seeded
  10-minute runs, behavior/cost metrics and a proposed host-tick budget share.
- **S11:** Decide population snapshot/lifecycle replication, interpolation, interest
  and spawn policy for the full global caps. Accept with separate ENet processes under
  normal/adverse profiles, reliable lifecycle isolation, measured worst-window host/client
  bandwidth and join bytes against the existing budgets, smoothness/codec CPU results,
  and bounded out-of-view safe replenishment/reset rules.
- **S12:** Decide authoritative hit registration for predicted shooters and interpolated
  targets by comparing host-time validation with bounded host rewind. Accept with separate
  normal/adverse ENet processes, hitscan agreement/false-positive results, rewind CPU and
  history memory, rocket presentation offset, and recommended M1 combat bounds/defaults.
- **S13:** Decide the shared player/pedestrian rig, animation update and palette-variant
  strategy. Accept with a source-linked Blender/GLB technical blockout and saved crowd
  of 68 live plus 16 dead characters, capped windowed and headless measurements, and
  with/without off-screen throttling frame/CPU/GPU/draw/skinning results.
- **S14:** Decide listener placement, buses, voice priority/caps, 3D attenuation,
  variation and settings persistence for the required audio families. Accept with
  generated licence-tracked placeholders, a saved 32-engine/24-explosion/SMG stress
  scene, bounded voice/mix results, settings roundtrip and an owner listening checklist.
- **S15:** Decide cost-effective saved muzzle, impact, tracer, rocket-trail and explosion
  effects while preserving an effect for every explosion. Accept with capped Forward+
  stress at 12/24 explosions, four SMG shooters and 16 rockets, retained frame/CPU/GPU/
  particle/draw evidence, per-effect budgets and a non-dropping quality fallback.
- **S16:** Propose production architecture, fixture promotion, test/CI strategy and an
  ordered M1 backlog. Accept for owner review when the plan maps single rule owners and
  standalone/authority/prediction/replication boundaries, disposes S02-S15 fixtures,
  selects a Godot test approach, identifies dependencies/sizes/parallel lanes and first
  five tasks, and records risks and owner questions.
- **P0-GATE:** Review foundation evidence against the 8 October owner decisions after
  S09, S10, S11, S12, S13, S14, S15 and S16. Do not reopen the ratified camera/control,
  vehicle, explosion, layout, ENet or target choices without a new owner decision.
  S07 graphical budgets are guidance, Linux S08 confirmation is follow-up, and
  P0-PROFILES is not a prerequisite. Record other unresolved items.

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
