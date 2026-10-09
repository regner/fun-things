# S10 pedestrian evidence

The accepted corrected measurement receipt is [result.json](result.json). It contains
the exact pinned-engine commands, twelve run summaries (three seeds, two scenarios,
two motion options), admitted S06 route/link/region facts, contention/CPU snapshots,
aggregate calculations and zero harness failures. The short retained import and seed
stdout logs are under [logs](logs/).

Two superseded receipts remain under `history/`:

- `initial-boundary-failure.json` is the first three-seed run. Its coordinate-bound
  metric treated float-clamped values such as `4.8999996` as outside `4.9`. It also
  predates the graph-driven correction and is retained only as failure history.
- `round1-requested-changes-result.json` is the prior technically passing receipt
  reviewed in round 1. It queried S06 but steered and measured against duplicated world
  constants, and its gate could accept zero flee reactions. It is not current evidence.

The corrected harness drives progress, endpoints, lateral projection, replenishment,
events and crossing admission from the current S06 public foot routes. It independently
checks real capsule positions against graph-derived sidewalk/crossing segments and S06
map road strips. Every threat captures its expected live target identities at
publication; all expected reactions must arrive within the six-phase bound. A retained
runtime negative reports failures for an injected 64-target event with zero reactions.

All accepted timing is labelled **contended upper bound**. The corrected repetitions
observed 5/3/3 Godot processes before launch and 6/4/4 during their snapshots. CPU-load
snapshots ranged 2–83% as reported by `Win32_Processor`; they are instantaneous, not
continuous utilization telemetry.
