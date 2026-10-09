# To-do

[Task requirements](docs/plans/task-requirements.md).

## Foundations

Completed foundation tasks are reconciled in the
[P0-GATE packet](docs/reviews/p0-gate-packet-2026-10-09.md); their production
follow-ups remain in the M1 requirements rather than reopening the spikes.

- [ ] **P0-PROFILES — Review the retained Paseo profiles task later.** Non-blocking;
  configuration remains deferred and outside P0-GATE.
- [ ] **S04 — Finish the handbrake fix and owner handling re-test.** Decision 26 records
  the completed drive-scene session and F12 values (`coast_mps2` 10.0,
  `grip_per_second` 9.0); the handbrake applied no longitudinal braking. The fix lane is in
  progress, followed by owner re-test before M1-B1 freezes handling.

## First milestone

### M1-A — Session and player

- [ ] **M1-A1 — Build the session service and menu flow.** Carry the S06 whole-UI direction
  into authored menus.
- [ ] **M1-A2 — Implement player simulation and replication.** Use decision 19's ordered,
  distance-bounded held-input queue and decision 20's tunable short extrapolate→hold→smooth
  remote-motion policy; include drawable remote-continuity acceptance from S03-R. After: M1-A1.
- [ ] **M1-A3 — Add production audio buses and voice policy.** Use default bus levels with no
  settings dependency; listening waits for real assets.
- [ ] **M1-A-GATE — Verify the multiplayer shell in exported builds.** After: M1-A2. Validate
  two exported ENet processes, lifecycle/reset/error flows and the S08 Linux desktop checklist
  with Steam absent.

### M1-B — Vehicles, combat and destruction

- [ ] **M1-B1 — Implement vehicles and authoritative driver transitions.** Entry is
  host-confirmed after a short ~0.3 s presentation; transfer control and camera/HUD ownership
  only on acceptance, with no rejection snap. Preserve exit below 0.5 m/s at the authored
  1.5 m offset and add production clearance. After: M1-A-GATE.
- [ ] **M1-B2 — Implement weapons, host-current-time hit verdicts, health, damage and
  respawn.** Use decision 21's accepted combat values as playtest-tuned M1 starting values;
  fire intents carry the shooter's view tick so bounded host-only rewind remains possible
  later. After: M1-A-GATE.
- [ ] **M1-B3 — Implement car explosions, wrecks and chain reactions.** Carry S05 wreck,
  in-flight hydration, lifecycle-race and final-body evidence into acceptance. After: M1-B1,
  M1-B2.
- [ ] **M1-B4 — Add combat feedback and review the vertical slice.** After: M1-B3.

### M1-C — City, population and minimap

- [ ] **M1-C0 — Complete the separately owned staged world concept work** in
  [the world concept handover](docs/workflows/world-concept-handover.md). It is in progress under
  an owner-run agent outside this orchestration; the owner will report when it is integrated.
  Its image-provider/concept-method question belongs to that owner-run work under decision 24,
  not to this orchestration.
- [ ] **M1-C1 — Produce the ratified custom art families.** After: the M1-C0 production
  asset list.
- [ ] **M1-C2 — Assemble the authored district in saved sectors.**
  Needs approved M1-C1 road/building/prop subsets.
- [ ] **M1-C3 — Implement host-owned pedestrians and traffic.** S10 production behavior is
  current priority work; report subsystem timings without treating the old pedestrian/traffic
  shares as gates. Integrate with the city after M1-B1, M1-B2 and M1-C2.
- [ ] **M1-C4 — Implement the road minimap and HUD integration.** Settle S06's minimap
  size/look and carry the whole-UI direction into the HUD. After: M1-A2; final alignment with
  M1-C2.

### M1-D — Integration and review builds

- [ ] **M1-D1 — Complete production validation tooling and CI.** Grows alongside implementation.
- [ ] **M1-D2 — Run integrated playtests, reviews and feel tuning.** After: M1-B4, M1-C3, M1-C4.
- [ ] **M1-D3 — Verify capacity, adverse-network behavior and performance.** S17 production
  host-budget work is current priority work; regularly track the soft ~4 ms total host p95 at
  tunable full-population settings, with subsystem timings as reports only. Include S05 final-body
  chain evidence. Target capped 60 FPS with p95 ≤16.7 ms and p99 ≤20 ms on named desktop hardware.
  Final gate after: M1-D1, M1-B4, M1-C3, M1-C4.
- [ ] **M1-D5 — Add the settings screen and settings persistence.** Audio volumes/mutes first;
  validate defaults, corrupt-file recovery and live preview. Device settings never mutate shared
  gameplay. Before: M1-D4.
- [ ] **M1-D4 — Export and deliver private milestone review builds.** After: M1-D2, M1-D3,
  M1-D5.
- [ ] **M1-GATE — Review the first playable milestone.** After: M1-D4.
