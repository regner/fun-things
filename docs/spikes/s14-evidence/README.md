# S14 retained evidence

`run07-summary.json` is the complete structured receipt for the accepted local run.
It includes the exact commands, 26-path committed inventory and matching SHA-256
manifest (including eight `.import` files and no ignored bytecode), settings
roundtrips, category voice counts, environment samples, and context timings.

- `run07-import.log`: clean isolated-project import on Godot 4.8-dev7.
- `run07-headless-1.log`: representative final Dummy-driver run with no diagnostics.
- `run07-windowed-1.log`: representative final WASAPI windowed run with no diagnostics.
- `resource-roundtrip.json`: resource/dependency/node identity counts, source hashes,
  bus-route counts, and byte-identical save/reload result.
- `resource-roundtrip-import.log` and `resource-roundtrip-save.log`: clean isolated
  addon-free pinned-editor import and no-preview save/reload logs.
- `run02-dummy-teardown.log`: earlier committed-source Dummy run retaining the exact
  generic 23-object/7-resource teardown observation. The log does not attribute its
  cause. The runner matches only both complete lines with these counts under Dummy;
  either line alone, different counts, and the complete pair under WASAPI remain
  failures.

The complete external runner directory remains at
`C:\tmp\ft\lanes\s14-audio\run07` on the measurement workstation. It is not a
portable project artifact. The committed summary is sufficient to reproduce and
review the bounded claims in [the S14 record](../s14.md).
