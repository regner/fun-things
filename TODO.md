# To-do

[Task requirements](docs/plans/task-requirements.md) ·
[ordered backlog](docs/plans/m1-production-plan.md#52-ordered-backlog).

## Foundations

Completed foundation tasks are reconciled in the
[P0-GATE packet](docs/reviews/p0-gate-packet-2026-10-09.md); their production
follow-ups remain in the M1 requirements rather than reopening the spikes.

- [ ] **P0-PROFILES — Review the retained Paseo profiles task later.** Non-blocking;
  configuration remains deferred and outside P0-GATE.

## First milestone

M1 builds the whole Brackett island, starting in the delivered greybox; the six-block area is
dropped. The fastest path runs four playable checkpoints — P1 walk together, P2 drive together,
P3 fight together, P4 living city — with road-tool and content tracks in parallel; see the
[production plan](docs/plans/m1-production-plan.md#51-fastest-path-to-a-playable-multiplayer-slice).
Decision 35 assigns gameplay integration to the orchestrator, pending owner confirmation.
[Owner questions](docs/plans/m1-production-plan.md#61-owner-questions-from-the-whole-city-replan)
on population placement, towers/camera, spawns, wreck art and M1-GATE scope have
recommendations and do not block P1.

### M1-A — Session and player

- [ ] **M1-A1 — Build the session service and menu flow.** A1.1 Boot/session is done; A1.2
  adds ENet host/join. Carry the S06 whole-UI direction into authored menus.
- [ ] **M1-A2 — Implement player simulation, presentation and replication.** Use decision 19's
  ordered, distance-bounded held-input queue and decision 20's tunable short
  extrapolate→hold→smooth remote-motion policy; present the delivered Coral Courier under the
  47 m / 42° camera in the Brackett greybox; include drawable remote-continuity acceptance from
  S03-R. After: M1-A1, M1-C2.1.
- [ ] **M1-A3 — Add production audio buses and voice policy.** Use default bus levels with no
  settings dependency; listening waits for real assets.
- [ ] **M1-A-GATE — Verify the multiplayer shell in exported builds (P1).** After: M1-A2,
  M1-C4.1. Validate two exported ENet processes walking together in Brackett,
  lifecycle/reset/error flows and the S08 Linux desktop checklist with Steam absent.

### M1-B — Vehicles, combat and destruction

- [ ] **M1-B1 — Implement vehicles and authoritative driver transitions (P2).** Use the three
  delivered cars and decision 30's owner-approved handling. Entry is host-confirmed after a
  short ~0.3 s presentation; transfer control and camera/HUD ownership only on acceptance, with
  no rejection snap. Preserve exit below 0.5 m/s at the authored 1.5 m offset and add production
  clearance. After: M1-A2.3, M1-A2.4.
- [ ] **M1-B2 — Implement weapons, host-current-time hit verdicts, health, damage and
  respawn (P3).** Use the delivered pistol, SMG, launcher and weapon effects with decision 21's
  playtest-tuned starting values; the shooter sees an immediate cosmetic muzzle flash and
  hitscan tracer (decision 18; tracer scene from C1.2a), with impact/damage on host
  confirmation. Fire intents carry the shooter's view tick so bounded host-only rewind remains
  possible later. After: M1-A2.3, M1-A2.4, M1-C1.2a.
- [ ] **M1-B3 — Implement car explosions, wrecks and chains.** Carry S05 wreck, in-flight
  hydration, lifecycle-race and final-body evidence into acceptance. After: M1-B1, M1-B2.
- [ ] **M1-B4 — Add combat feedback and review the vertical slice (P3).** After: M1-B3.

### M1-C — City, population and minimap

- [ ] **M1-C0 — Run the staged world concept work** in
  [the world concept handover](docs/workflows/world-concept-handover.md) under the owner-run
  agent (decision 24). Stages 1–3 are approved; per-district concepts and asset lists follow
  the [parallel content workflow](docs/workflows/parallel-art-production.md). The owner reports
  when it is integrated.
- [ ] **M1-C1 — Produce production art families.** C1.1 district building/prop families after
  M1-C0's asset lists; C1.2 follow-ups to the delivered character/vehicle/weapon/effect assets,
  starting with C1.2a, the hitscan tracer effect from the weapon-effects lead, and including
  car wreck states; C1.3 Blender road fixtures (signals, street lights, prefab intersection
  pieces).
- [ ] **M1-C2 — Integrate the Brackett world.** C2.1 makes the greybox the play world with
  content identity, spawn/parked-car anchors, traversal checks and a whole-island capacity
  baseline; C2.2 later replaces greybox districts with production art, keeping `world_id`s.
- [ ] **M1-C3 — Implement host-owned pedestrians and traffic (P4).** Decision 14 makes S10
  pedestrian behavior/budget first production work: **C3.0 starts now** with compact state, a
  spatial grid, crossing reservations (decision 32), recorded behavior thresholds and
  reporting-only timings (decision 22), against an injected navigation interface and synthetic
  graphs. C3.1 traffic and C3.2 pedestrian world integration consume RT-06/RT-07 load-time
  graphs. AI traffic yields to marked-crosswalk reservations; player cars do not. C3.1/C3.2
  after: M1-B1, M1-B2, C3.0 and the owner's population-placement answer.
- [ ] **M1-C4 — Implement the HUD and road minimap.** C4.1 HUD shell after M1-A2; C4.2 minimap
  from RT-09 ROAD data (P4). Settle S06's minimap size/look and carry the whole-UI direction
  into the HUD.

### M1-RT — Road tool

Decisions 40–44: conditional Road Generator pilot, no bake, live generation and load-time
derivation, generated road infrastructure exception, signals plus street lights, hybrid
intersections. The world integrator owns CityData and road revisions.

- [ ] **RT-01 — Harden and vendor Road Generator 0.9.4.** Accepted on `lane/rt-01`; held for
  the owner's hands-on editor trial before landing.
- [ ] **RT-02 — Add road presets, identities and revisions.** After: RT-01, M1-C2.1.
- [ ] **RT-03 — Generate road infrastructure live in the editor and at load.** After: RT-02.
- [ ] **RT-04 — Build hybrid prefab/procedural intersections.** After: RT-03, M1-C1.3.
- [ ] **RT-05 — Derive road data at load with host/client consistency.** After: RT-04.
- [ ] **RT-06 — Derive the traffic graph and spawns.** After: RT-05.
- [ ] **RT-07 — Derive the foot graph, crossings and reservations.** After: RT-06, M1-C3.0.
- [ ] **RT-08 — Place traffic signals and street lights.** After: RT-07, M1-C1.3.
- [ ] **RT-09 — Derive minimap ROAD data.** After: RT-05.
- [ ] **RT-10 — Pilot the connected island and replace greybox roads.** After: RT-08, RT-09.
- [ ] **RT-11 — Gate runtime packaging and upgrades.** After: RT-10.

### M1-D — Integration and review builds

- [ ] **M1-D1 — Complete production validation tooling and CI.** D1.1 pinned test-only GUT and
  `tools/production_checks.py` are done (decision 31); D1.2 grows alongside implementation.
- [ ] **M1-D2 — Run integrated playtests, reviews and feel tuning.** After: M1-A-GATE, M1-B4,
  M1-C3, M1-C4, RT-10.
- [ ] **M1-D3 — Verify capacity, adverse-network behavior and performance.** Decision 14 makes
  S17 host-budget work first production work: **D3.0 starts now**, instrumenting the host tick
  from the first simulation rows and tracking the soft ~4 ms total host p95 at tunable
  full-population settings as each simulation row lands and at every checkpoint, with subsystem
  timings as reports only. Final D3 is the integrated acceptance. Include S05 final-body
  chain evidence. Target capped 60 FPS with p95 ≤16.7 ms and p99 ≤20 ms on named desktop hardware
  across the whole island. Final gate after: M1-D1, M1-B4, M1-C3, M1-C4.
- [ ] **M1-D5 — Add the settings screen and settings persistence.** Audio volumes/mutes first;
  validate defaults, corrupt-file recovery and live preview. Device settings never mutate shared
  gameplay. Before: M1-D4.
- [ ] **M1-D4 — Export and deliver private milestone review builds.** After: M1-D2, M1-D3,
  M1-D5, RT-11.
- [ ] **M1-GATE — Review the first playable milestone.** After: M1-D4.
