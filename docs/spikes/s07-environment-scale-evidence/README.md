# S07 environment-scale evidence

`city-6/`, `city-24/` and `city-96/` retain both passing repeats: runner summary,
per-case summary/result, raw little-endian float64 frame rows, sampled working set and
complete short stdout/stderr/engine logs. `city-384/` retains the first-failing crash
case; no result/frame stream exists because the process exited before writing either.

`initial-missing-shader/` preserves the rejected first 6-block attempt. The staged S02
building script preloaded a shader the initial staging list omitted. The retained parse
diagnostic caused the runner to reject that attempt; commit `4f3ad49` added the exact
missing existing shader before accepted measurements.

`captures/` retains one 1280×800 Movie Maker frame and complete capture log for the fixed
saved-camera starting view of the 6- and 96-block passing scenes. They verify drawable
linked content only; Movie Maker encoding figures are not measurement-run timings. The
matching local views are expected because city size changes residency while the camera
starts over one same-density block.

`manifest.json` binds generated scenes and run revisions. `SHA256SUMS` binds this evidence
directory, excluding only the checksum file itself. Frame field order is recorded in each
case's `result.json` and interpreted by `tools/s07_env/run.py`.
