# S04-P retained evidence

This directory contains selected bounded receipts from the Windows 11 prediction lane. Full runner
outputs remain external under `C:/tmp/ft/lanes/s04-p/`; the committed files are sufficient to inspect
commands, source hashes, outcomes and the material pass/failure boundaries.

- `focused-result.json`: review-corrected all-five isolated saved-fixture/API pass, including bounded
  history, input-tick fences, correction replay, rate-bounded `EXIT_MOVING`, stopped exit and
  binding-independent disconnect coasting.
- `review1-normal-*`: exact review-corrected normal pass. Matching-tick installation compares the
  body state observed immediately after restore, before replay, rather than copying the wire pose.
- `review1-lifecycle-result.json`: two separate ENet host/client scenarios. Successful stopped exit
  makes the predicted client passive; abrupt process exit leaves a diagnostic-free host that emits
  59 binding-independent coast snapshots and reaches rest.
- `post-rebase-baseline-*`: exact-source baseline measurement; prediction completed 20/20 while the
  historical authority gate missed 6/20, so the runner result is retained as failed.
- `post-rebase-normal-*`: exact-source normal profile pass.
- `post-rebase-adverse-*`: exact-source adverse measurement; prediction completed 20/20 but correction
  p95 exceeded 0.5 m and authority missed 2/20, so it is retained as failed.
- `post-rebase-windowed-*`: exact-source Windows drawn baseline with 20/20 prediction/drawn samples;
  the later wall-stop gate failed under graphical pacing, so this is measurement rather than a pass.
- `baseline-final-*`, `normal-final-*` and `adverse-final-*`: pre-rebase final-owned-source attempts,
  retained for the Windows pacing history rather than exact integrated-source acceptance.
- `normal-development-result.json`: earlier normal technical pass with the same prediction rules,
  before expiry decision-age telemetry was added.
- `adverse-development-result.json`: earlier useful adverse measurement; its only runner failure was
  the old post-step expiry timestamp boundary.
- `windowed-baseline-development-result.json` and its two PNGs: earlier actual Windows drawn-frame
  receipt, retained as developmental graphical evidence rather than exact-final acceptance.

The older receipts' zero matching-tick error field was derived from the wire pose and is not accepted
for installation evidence. They remain only for their historical response/correction/pacing data; the
review-corrected normal receipt and analyzer counterexample supersede that field.

No receipt proves physical input, subjective handling, another machine, Linux, Steam, exported builds
or production car-to-car rollback. See `../s04-prediction.md` for the measured disposition.
