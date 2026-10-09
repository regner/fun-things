# To-do

[Task requirements](docs/plans/task-requirements.md).

## Foundations

- [ ] **P0-PROFILES — Review the retained Paseo profiles task later.** Non-blocking;
  configuration remains deferred and outside P0-GATE.
- [ ] **S02 — Implement and validate WASD movement, mouse-facing, 42° camera and no cutaway.**
  See [spike](docs/spikes/s02.md).
- [ ] **S03-S — Review ENet session APIs for a later Steam adapter.** Steam implementation
  and testing are deferred. See [spike](docs/spikes/s03-s.md).
- [ ] **S03-R — Close on-foot response, adverse expiry and feel evidence.** See
  [spike](docs/spikes/s03-r.md).
- [ ] **S03-P — Implement and validate required local on-foot prediction.**
- [ ] **S04 — Validate car handling and rules through the drive scene.** See
  [spike](docs/spikes/s04.md).
- [ ] **S04-P — Implement and validate required local-car prediction.**
- [ ] **S04-T — Prove predicted foot-to-car control transitions and seat races.**
- [ ] **S05 — Remove the explosion-effect cap and remeasure chains.** See
  [spike](docs/spikes/s05.md).
- [ ] **S06 — Iterate whole-UI mockups and settle minimap size/look.** Layout scale and
  top-right position are accepted. See [spike](docs/spikes/s06.md).
- [ ] **S07 — Measure the graphical environment cost-versus-block envelope.** This is
  guidance, not a gate; network/AI/population are out of scope. See [spike](docs/spikes/s07.md).
- [ ] **S08 — Follow up 4.8-dev7 Linux confirmation when a Linux machine is available.**
  This does not block proceeding; keep the ENet workaround and offline upstream review.
- [ ] **P0-TOOLING — Repair the validation baseline and complete test discovery.**
- [ ] **S01-W — Verify the S01 art reexport pipeline with Windows Blender.**
- [ ] **S03-L — Diagnose Windows ENet authority latency and adverse expiry timing.**
- [ ] **S08-X — Prove real-project Windows/Linux export configuration and launch.**
- [ ] **S08-C — Triage the 384-block crash and define safe GPU measurement.**
- [ ] **S09 — Prototype and measure host-owned traffic AI.**
- [ ] **S10 — Prototype and measure host-owned pedestrian AI.**
- [ ] **S11 — Prove population replication, bandwidth and spawning bounds.**
- [ ] **S12 — Compare and select authoritative combat hit registration.**
- [ ] **S13 — Prove the character rig, animation strategy and crowd cost.**
- [ ] **S14 — Prove bounded, readable audio and settings persistence.**
- [ ] **S15 — Measure weapon/explosion VFX cost without dropping explosion effects.**
- [ ] **S16 — Propose the M1 production architecture, test strategy and backlog.**
- [ ] **S17 — Measure the integrated full-cap host physics-tick composition.**
- [ ] **P0-GATE — Review remaining foundation evidence against the ratified decisions.**
  After: unfinished blocking S02–S08 work; S03-P, S04-P, S04-T, S09–S17,
  P0-TOOLING, S01-W, S03-L, S08-X and S08-C. S07 environment guidance, Linux-only
  S08 confirmation and P0-PROFILES remain non-blocking.

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
- [ ] **M1-C2 — Assemble the authored district in saved sectors.**
  Needs approved M1-C1 road/building/prop subsets.
- [ ] **M1-C3 — Implement host-owned pedestrians and traffic.** After: M1-B1, M1-B2, M1-C2.
- [ ] **M1-C4 — Implement the road minimap and HUD integration.** After: M1-A2;
  final alignment with M1-C2.

### M1-D — Integration and review builds

- [ ] **M1-D1 — Complete production validation tooling and CI.** Grows alongside implementation.
- [ ] **M1-D2 — Run integrated playtests, reviews and feel tuning.** After: M1-B4, M1-C3, M1-C4.
- [ ] **M1-D3 — Verify capacity, adverse-network behavior and performance.**
  After: M1-D1, M1-B4, M1-C3, M1-C4.
- [ ] **M1-D4 — Export and deliver private milestone review builds.** After: M1-D2, M1-D3.
- [ ] **M1-GATE — Review the first playable milestone.** After: M1-D4.
