# M1-B1.1 validation evidence

All commands used the Mise-pinned Godot `4.8.dev7.official.c971f93e7` and placed generated logs under
`C:/tmp/ft/lanes/m1-b1-1/`. `validation.json` records the concise outcomes.

- `review-fix-focused/summary.json`: canonical layers with GUT limited to
  `tests/unit/vehicles`; all layers passed, including 13/13 focused tests and the expected isolated
  diagnostic failure.
- `vehicle-smoke.log` and `vehicle-smoke.engine.log`: the authored standalone entry loaded the full
  Brackett/flat composition and moved through `VehicleMotion`; distance was 0.700 m in 20 fixed ticks.
- `normalize-scenes.log`: all four new saved scenes loaded, instantiated, packed and resaved with the
  pinned engine. Resource identities were then added and verified by another headless import.
- The first focused run is retained externally as a development failure receipt: its original 5/5
  slide setup did not meet the decision-30 slip-share margin because decision 30 increased coast and
  side grip from the archived fixture defaults. The final independent relative test uses a pronounced
  15 m/s lateral, 7 m/s forward entry slide and passes both required relative thresholds without
  changing the ratified formula or values.

The full all-owner production check is recorded after the focused run in this task's final report.
No windowed feel or visual review is claimed.
