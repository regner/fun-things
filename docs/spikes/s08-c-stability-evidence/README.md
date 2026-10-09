# S08-C stability-triage evidence

This directory retains the bounded Windows investigation of the historical S07-ENV
384-block access violation. All Godot processes were capped at 60 FPS by the unchanged
measurement fixture; no uncapped rendering was used.

- `author/` records the pinned-engine authoring of the saved 192- and 288-block bisect
  scenes after a fresh import cache was built.
- `bisect-192/` and `bisect-288/` retain the staged import, first process result, frame
  stream, memory samples, and complete short logs. Both instantiated successfully and
  exited zero. These diagnostic runs used zero warmup, so their first-load frame made
  frame p99 exceed 20 ms and the growth runner stopped before repeat 2. They are
  instantiation evidence, not valid frame-performance measurements.
- `quiet-384/` retains two successful fresh-process repeats after a one-second warmup.
  Both instantiated 52,998 nodes and 3,072 static colliders, produced frame/GPU telemetry,
  and exited zero without diagnostics.
- `bisect-process-counts.txt` and `quiet-384-process-count.txt` label the measurements as
  contended. Other lanes were running on the workstation.
- `wer-localdumps.json` records the temporary per-executable Windows Error Reporting
  minidump configuration. The crash did not recur, so no dump or backtrace was produced;
  the registry key was removed after the run.
- `files.txt` lists retained file sizes. `SHA256SUMS` binds every other evidence file.

The external staged projects and shader caches are intentionally not retained. The
committed result files contain the tested revision, engine identity, commands, scene
results, and source-independent telemetry needed for review.
