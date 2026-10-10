# M1-B1.1 validation evidence

All commands used the Mise-pinned Godot `4.8.dev7.official.c971f93e7` and wrote generated logs
outside the checkout. [`validation.json`](validation.json) records the concise machine-readable
outcomes.

## Current replication and prediction validation

- `python tools/production_checks.py --output
  C:/tmp/ft/lanes/m1-b11b/review2-production`: every canonical layer passed after the assignment
  preflight regressions. GUT ran **207/207 tests** with **8,815 assertions**; the expected isolated
  diagnostic test failed as required.
- The preceding replication acceptance check at `C:/tmp/ft/lanes/m1-b11b/review-fix-production`
  passed **205/205 tests** with **8,800 assertions**.
- `python tools/vehicles/run_vehicle_replication.py --output
  C:/tmp/ft/lanes/m1-b11b/review-fix-enet-final`: fresh-port, readiness-gated, separately bounded
  host/client processes passed direct, normal and adverse profiles. Every profile observed
  authoritative and predicted straight, turn, brake, reverse and handbrake outcomes plus
  authoritative wall and moving-car contacts.
- Direct: **368** authoritative client movement receipts, acknowledgement **460**, **184**
  reconciliations, raw correction p95 **0.018526 m**.
- Normal (75 ms one-way, ±30 ms jitter, 2% loss): **356** receipts, acknowledgement **460**, **178**
  reconciliations, raw correction p95 **0.305130 m**.
- Adverse (125 ms one-way, ±50 ms jitter, 5% loss): **328** receipts, acknowledgement **460**, **164**
  reconciliations, raw correction p95 **0.822337 m**.

The correction target remains **0.5 m**. Direct and normal meet it; adverse does not. The adverse run
finishes converged (acknowledgement 460, empty history and last correction 0), while the rolling raw
p95 rises during active control-phase changes under delayed/lost input and the required three-tick
authority backlog. Candidate investigation levers are host/client tick alignment, replay selection at
phase boundaries, measured snapshot cadence, and command-transition pacing. Presentation smoothing
can improve appearance but cannot lower the raw authoritative-body correction and must not be used to
weaken or relabel the target. No tuning change is claimed here.

## Original standalone receipts

- `review-fix-focused/summary.json`: the earlier vehicle-only canonical slice passed 13/13 focused
  tests and the expected isolated diagnostic failure.
- `vehicle-smoke.log` and `vehicle-smoke.engine.log`: the authored standalone entry loaded the full
  Brackett/flat composition and moved through `VehicleMotion`; distance was 0.700 m in 20 fixed ticks.
- `normalize-scenes.log`: all four saved scenes loaded, instantiated, packed and resaved with the
  pinned engine, followed by a clean headless import.
- The original failed slide setup is retained externally: decision-30 coast and side grip required a
  more pronounced 15 m/s lateral, 7 m/s forward entry slide. The corrected independent test passed
  without changing the ratified formula or values.

No windowed feel or visual review is claimed.
