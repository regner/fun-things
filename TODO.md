# To-do

[Task requirements](docs/plans/task-requirements.md).

## Foundations

Completed foundation tasks are reconciled in the
[P0-GATE packet](docs/reviews/p0-gate-packet-2026-10-09.md); their production
follow-ups remain in the M1 requirements rather than reopening the spikes.

- [ ] **P0-PROFILES — Review the retained Paseo profiles task later.** Non-blocking;
  configuration remains deferred and outside P0-GATE.
- [ ] **S02/S03-R — Complete physical Alt-Tab, control/aim/remote-continuity and feel
  review.** World-relative controls, prediction and exact adverse expiry are implemented;
  use the packet's human instructions.
- [ ] **S04 — Ratify handling through the standalone drive scene.** Record the F12 tuning
  JSON and maneuver-specific feedback before M1-B1 freezes handling.
- [ ] **S05 — Carry remaining wreck, in-flight hydration, lifecycle-race and final-body
  evidence into M1-B3/M1-D3.** Bounded chain logic and 12/12 visible effects are complete.
- [ ] **S06 — Iterate the whole UI and settle minimap size/look.** Layout scale and the
  top-right position are accepted; see [UI concepts](docs/concepts/ui-v1/README.md).
- [ ] **S08 — Run the Linux desktop launch/graphics checklist when a Linux machine is
  available.** This does not block proceeding; keep the ENet workaround and offline review.
- [ ] **P0-GATE — Review the refreshed packet and record the gate disposition.** The
  S17-only quiet record and owner decisions 13–24 are integrated in the
  [review packet](docs/reviews/p0-gate-packet-2026-10-09.md). Under decision 14, the
  remaining human checks and production decisions are not extra foundation prerequisites;
  Linux-only S08 confirmation and P0-PROFILES remain non-blocking.

## First milestone

All M1 tasks follow P0-GATE.

### M1-A — Session and player

- [ ] **M1-A1 — Build the session service and menu flow.** After: P0-GATE.
- [ ] **M1-A2 — Implement player simulation and replication.** Use decision 19's ordered,
  distance-bounded held-input queue and decision 20's tunable short extrapolate→hold→smooth
  remote-motion policy. After: M1-A1.
- [ ] **M1-A3 — Add settings, audio and persistence.** After: P0-GATE.
- [ ] **M1-A-GATE — Verify the multiplayer shell in exported builds.**
  After: M1-A2, M1-A3.

### M1-B — Vehicles, combat and destruction

- [ ] **M1-B1 — Implement vehicles and authoritative driver transitions.** Entry is
  host-confirmed after a short ~0.3 s presentation; transfer control and camera/HUD ownership
  only on acceptance, with no rejection snap. Preserve exit below 0.5 m/s at the authored
  1.5 m offset and add production clearance. After: M1-A-GATE.
- [ ] **M1-B2 — Implement weapons, host-current-time hit verdicts, health, damage and
  respawn.** Use decision 21's accepted combat values as playtest-tuned M1 starting values;
  fire intents carry the shooter's view tick so bounded host-only rewind remains possible
  later. After: M1-A-GATE.
- [ ] **M1-B3 — Implement car explosions, wrecks and chain reactions.** After: M1-B1, M1-B2.
- [ ] **M1-B4 — Add combat feedback and review the vertical slice.** After: M1-B3.

### M1-C — City, population and minimap

- [ ] **M1-C0 — Complete the separately owned staged world concept work** in
  [the world concept handover](docs/workflows/world-concept-handover.md). It is in progress under
  an owner-run agent outside this orchestration; the owner will report when it is integrated.
  The image-provider question is withdrawn.
- [ ] **M1-C1 — Produce the ratified custom art families.** After: P0-GATE and the
  M1-C0 production asset list.
- [ ] **M1-C2 — Assemble the authored district in saved sectors.**
  Needs approved M1-C1 road/building/prop subsets.
- [ ] **M1-C3 — Implement host-owned pedestrians and traffic.** Start S10 production
  behavior work immediately after P0-GATE; report subsystem timings without treating the old
  pedestrian/traffic shares as gates. Integrate with the city after M1-B1, M1-B2 and M1-C2.
- [ ] **M1-C4 — Implement the road minimap and HUD integration.** After: M1-A2;
  final alignment with M1-C2.

### M1-D — Integration and review builds

- [ ] **M1-D1 — Complete production validation tooling and CI.** Grows alongside implementation.
- [ ] **M1-D2 — Run integrated playtests, reviews and feel tuning.** After: M1-B4, M1-C3, M1-C4.
- [ ] **M1-D3 — Verify capacity, adverse-network behavior and performance.** Start the S17
  production host-budget work immediately after P0-GATE; regularly track the soft ~4 ms total
  host p95 at tunable full-population settings, with subsystem timings as reports only. Target
  capped 60 FPS with p95 ≤16.7 ms and p99 ≤20 ms on named desktop hardware. Final gate after:
  M1-D1, M1-B4, M1-C3, M1-C4.
- [ ] **M1-D4 — Export and deliver private milestone review builds.** After: M1-D2, M1-D3.
- [ ] **M1-GATE — Review the first playable milestone.** After: M1-D4.
