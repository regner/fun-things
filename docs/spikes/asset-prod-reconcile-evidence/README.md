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
  The native Batch 03 visual launcher now caps its owned child at 60 FPS, waits at most 180
  seconds, and terminates only that child (with a bounded kill fallback) on expiry.
- All three documented Python receipt verifiers passed; see
  `batch-verifiers-summary.json`. The old verifiers initially failed because they resolved
  retained `tests/fixtures/asset_production/` paths literally; the preserved failure is in
  `initial-verifier-failures.log`. They now validate unchanged reviewed resources by their
  retained hashes and intentionally migrated fixture scenes by pinned post-reconciliation
  content hashes plus preserved saved UIDs.
- `python tools/production_checks.py --output
  C:/tmp/ft/lanes/asset-prod-reconcile/production-checks-review-fix-final` passed all canonical
  checks, including owned-script format/style/compilation, Python tests, headless import,
  positive GUT, and the required negative GUT control. See
  `production-checks-summary.json`.
- The documented `city_lights_01` Blender 5.2.2 reexport loaded the production shared
  contract from `tools/assets/blender/export_settings.json`, exited 0, and reproduced both
  committed GLBs byte-for-byte. See `city-lights-01-reexport.log`.
- The saved `weapon_effects_a` source loaded the same production shared contract in Blender
  5.2.2, exited 0, and reproduced all six committed GLBs byte-for-byte. See
  `weapon-effects-reexport.log`.
- An `art/**`, `tools/**`, and `scenes/**` archived-settings audit found no live production
  dependency. The remaining `tools/s01` matches are the verifier's rejection assertion and
  the shared contract README's historical archive link. The remaining `prototypes/` matches
  under `tools/**` are the deliberate exclusion in `s08_x/inspect_exports.py` and
  prototype-path rejection vectors in `test_s08_x.py`.

M1-A2.1 landed after these checks. Migrating the fixtures to its production player is a separate
coordinated follow-up because the production capsule radius is 0.35 m and the retained accepted
fixture envelope is 0.38 m. That migration must keep independent clearance expectations and
explicitly reconcile contact-outcome changes rather than silently rebaseline this evidence.

The logs prove saved fixture and bounded desktop behavior only. They do not accept world
placement, device readability, packaged performance, or multiplayer transport/prediction.
