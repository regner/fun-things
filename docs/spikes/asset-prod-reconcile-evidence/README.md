# Asset-production fixture reconciliation evidence

Recorded 9 October 2026 with Godot `4.8.dev7.official.c971f93e7`, gdstyle `0.3.0`
and Python 3.14 in the `lane/asset-prod-reconcile` worktree.

## Checks

- `godot --headless --editor --path . --import --quit` exited 0. Its only diagnostic was
  the pre-existing MCP addon's advisory that Godot 4.8 is newer than its tested 4.7.
- `check_fixture_scenes.gd` loaded and instantiated all 15 current asset-production scenes;
  see `fixture-load.log`.
- `run_current_observations.gd` completed all Batch 01–03 outcomes; see
  `current-observations.log`. Retained movement positions, clear/blocked outcomes, aim
  targets and fit results match the production integration records. Headless query timing
  is intentionally not compared to historical graphical observations.
- Batch 02 and Batch 03 each passed in two isolated engine processes; see the process logs.
- All three documented Python receipt verifiers passed; see
  `batch-verifiers-summary.json`. The old verifiers initially failed because they resolved
  retained `tests/fixtures/asset_production/` paths literally; the preserved failure is in
  `initial-verifier-failures.log`. They now validate unchanged reviewed resources by hash
  and intentionally migrated fixture scenes by their preserved saved UIDs.
- `python tools/production_checks.py --output
  C:/tmp/ft/lanes/asset-prod-reconcile/production-checks-final` passed all canonical
  checks, including owned-script format/style/compilation, Python tests, headless import,
  positive GUT, and the required negative GUT control. See
  `production-checks-summary.json`.

The logs prove saved fixture and bounded desktop behavior only. They do not accept world
placement, device readability, packaged performance, or multiplayer transport/prediction.
