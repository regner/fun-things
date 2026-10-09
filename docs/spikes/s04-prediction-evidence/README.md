# S04-P retained evidence

This directory contains selected bounded receipts from the Windows 11 prediction lane. Full runner
outputs remain external under `C:/tmp/ft/lanes/s04-p/`; the committed files are sufficient to inspect
commands, source hashes, outcomes and the material pass/failure boundaries.

- `focused-result.json`: all five isolated saved-fixture/API checks passed, including bounded history,
  correction replay, `EXIT_MOVING`, stopped exit and disconnect coasting.
- `baseline-final-result.json` / `baseline-final-command.log`: final-source headless baseline pass.
- `normal-final-result.json` / `normal-final-command.log`: final-source normal run; gameplay and
  prediction measurements completed, but the historical authority-response gate missed 1/20.
- `adverse-final-result.json` / `adverse-final-command.log`: final-source adverse run under observed
  workstation contention; it is retained as a failure, not acceptance evidence.
- `normal-development-result.json`: earlier normal technical pass with the same prediction rules,
  before expiry decision-age telemetry was added.
- `adverse-development-result.json`: earlier useful adverse measurement; its only runner failure was
  the old post-step expiry timestamp boundary.
- `windowed-baseline-development-result.json` and the two PNGs: actual Windows drawn-frame receipt.
  This predates only the later moving-exit request timing and expiry telemetry, so it is developmental
  graphical evidence rather than exact-final acceptance.

No receipt proves physical input, subjective handling, another machine, Linux, Steam, exported builds
or production car-to-car rollback. See `../s04-prediction.md` for the measured disposition.
