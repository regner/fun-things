# To-do

[Task requirements](docs/plans/task-requirements.md).

## Foundations

Completed foundation tasks are reconciled in the
[P0-GATE packet](docs/reviews/p0-gate-packet-2026-10-09.md); their production
follow-ups remain in the M1 requirements rather than reopening the spikes.

- [ ] **P0-PROFILES — Review the retained Paseo profiles task later.** Non-blocking;
  configuration remains deferred and outside P0-GATE.

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

- [ ] **M1-B1 — Implement vehicles and authoritative driver transitions.** Start production
  handling from decision 30's owner-approved values. Entry is host-confirmed after a short
  ~0.3 s presentation; transfer control and camera/HUD ownership only on acceptance, with no
  rejection snap. Preserve exit below 0.5 m/s at the authored 1.5 m offset and add production
  clearance. After: M1-A-GATE.
- [ ] **M1-B2 — Implement weapons, host-current-time hit verdicts, health, damage and
  respawn.** Use decision 21's accepted combat values as playtest-tuned M1 starting values;
  fire intents carry the shooter's view tick so bounded host-only rewind remains possible
  later. After: M1-A-GATE.
- [ ] **M1-B3 — Implement car explosions, wrecks and chain reactions.** Carry S05 wreck,
  in-flight hydration, lifecycle-race and final-body evidence into acceptance. After: M1-B1,
  M1-B2.
- [ ] **M1-B4 — Add combat feedback and review the vertical slice.** After: M1-B3.

### M1-C — City, population and minimap

- [ ] **M1-C0 — Run the staged world concept work** in
  [the world concept handover](docs/workflows/world-concept-handover.md):
  setting, city map, districts, roads, lighting, buildings, props, landmarks, greybox
  and production asset list, each owner-approved before the next.
  Stage 1 approved: [Brackett — cyberpunk island](docs/concepts/world-v1/decisions.md#9-october-2026--brackett-named-stage-1-complete).
  [Stage 2 whole-city map options](docs/concepts/world-v1/stage-02-city-structure/README.md)
  have structure A and nine district identities accepted; all names are placeholders.
  Stage 2 complete: 1.2 × 0.65 km planning size and Signal Row / Ironreach M1 slice accepted.
  The six-block programme is retained; Stage 3 district identity briefs are next.
- [ ] **M1-C1 — Produce the ratified custom art families.** After: P0-GATE and the
  M1-C0 production asset list.
- [ ] **M1-C2 — Assemble the authored district in saved sectors.**
  Needs approved M1-C1 road/building/prop subsets.
- [ ] **M1-C3 — Implement host-owned pedestrians and traffic.** S10 production behavior is
  current priority work; report subsystem timings without treating the old pedestrian/traffic
  shares as gates. AI traffic yields to marked-crosswalk reservations; player cars do not
  (decision 32). Integrate with the city after M1-B1, M1-B2 and M1-C2.
- [ ] **M1-C4 — Implement the road minimap and HUD integration.** Settle S06's minimap
  size/look and carry the whole-UI direction into the HUD. After: M1-A2; final alignment with
  M1-C2.

### M1-D — Integration and review builds

- [ ] **M1-D1 — Complete production validation tooling and CI.** Grows alongside implementation.
  Use pinned, test-only GUT excluded from exports (decision 31).
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
