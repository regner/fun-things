# To-do

This is the concise list of unfinished tasks. Their detailed task-specific acceptance
is indexed in [task requirements](docs/plans/task-requirements.md); canonical technical
contracts remain in their existing guides and spike records.

## Foundations

- [ ] **P0-PROFILES — Reassess orchestration profiles.** Configuration remains deferred and outside
  P0-GATE.
- [ ] **S02 — Settle foot controls, camera, aiming and feel.** See [spike](docs/spikes/s02.md).
- [ ] **S03-S — Establish Steam friend connectivity and gameplay transport.** Steam testing remains
  deferred, not accepted. See [spike](docs/spikes/s03-s.md).
- [ ] **S03-R — Settle networked on-foot response and prediction.** See
  [spike](docs/spikes/s03-r.md).
- [ ] **S04 — Settle car handling, dimensions and network response.** See
  [spike](docs/spikes/s04.md).
- [ ] **S05 — Complete explosion-chain feasibility and policy evidence.** See
  [spike](docs/spikes/s05.md).
- [ ] **S06 — Settle shared city topology, navigation and minimap.** See
  [spike](docs/spikes/s06.md).
- [ ] **S07 — Complete graphical map-capacity and growth measurements.** The sustained primary-T
  route driver is accepted; graphical capacity remains open. See [spike](docs/spikes/s07.md) and
  [driver result](docs/spikes/s07-sustained-driver.md).
- [ ] **S08 — Complete release lifecycle diagnosis and target compatibility.** See
  [spike](docs/spikes/s08.md) and [lifecycle record](docs/spikes/s08-release-lifecycle.md).
- [ ] **P0-GATE — Review foundation evidence and ratify the first milestone plan.**
  After: S02, S03-S, S03-R, S04, S05, S06, S07, S08.

## First milestone

All M1 tasks follow P0-GATE.

### M1-A — Session and player

- [ ] **M1-A1 — Build the session service and menu flow.** After: P0-GATE.
- [ ] **M1-A2 — Implement player simulation and replication.** After: M1-A1.
- [ ] **M1-A3 — Add settings, audio and persistence.** After: P0-GATE.
- [ ] **M1-A-GATE — Verify the multiplayer shell in exported builds.**
  After: M1-A2, M1-A3.

### M1-B — Vehicles, combat and destruction

- [ ] **M1-B1 — Implement vehicles and authoritative driver transitions.** After: M1-A-GATE.
- [ ] **M1-B2 — Implement weapons, health, damage and respawn.** After: M1-A-GATE.
- [ ] **M1-B3 — Implement car explosions, wrecks and chain reactions.** After: M1-B1, M1-B2.
- [ ] **M1-B4 — Add combat feedback and review the vertical slice.** After: M1-B3.

### M1-C — City, population and minimap

- [ ] **M1-C1 — Produce the ratified custom art families.** After: P0-GATE.
- [ ] **M1-C2 — Assemble the authored district in saved sectors.** After: M1-C1.
- [ ] **M1-C3 — Implement host-owned pedestrians and traffic.** After: M1-B1, M1-B2, M1-C2.
- [ ] **M1-C4 — Implement the road minimap and HUD integration.** After: M1-A2, M1-C2.

### M1-D — Integration and review builds

- [ ] **M1-D1 — Complete production validation tooling and CI.** Grows alongside implementation.
- [ ] **M1-D2 — Run integrated playtests, reviews and feel tuning.** After: M1-B4, M1-C3, M1-C4.
- [ ] **M1-D3 — Verify capacity, adverse-network behavior and performance.**
  After: M1-D1, M1-B4, M1-C3, M1-C4.
- [ ] **M1-D4 — Export and deliver private milestone review builds.** After: M1-D2, M1-D3.
- [ ] **M1-GATE — Review the first playable milestone.** After: M1-D4.
