# S14 retained evidence

`run05-summary.json` is the complete structured receipt for the accepted local run.
It includes the exact commands, source SHA-256 manifest, settings roundtrips, category
voice counts, environment sample before every case, and aggregate context timings.

- `run05-import.log`: clean isolated-project import on Godot 4.8-dev7.
- `run05-headless-1.log`: representative final Dummy-driver run with no diagnostics.
- `run05-windowed-1.log`: representative final WASAPI windowed run with no diagnostics.
- `resource-roundtrip.json`: resource/dependency/node identity counts, source hashes,
  bus-route counts, and byte-identical save/reload result.
- `resource-roundtrip-import.log` and `resource-roundtrip-save.log`: clean isolated
  addon-free pinned-editor import and no-preview save/reload logs.
- `run02-dummy-teardown.log`: earlier committed-source Dummy run retaining the exact
  generic 23-object/7-resource teardown observation. The log does not attribute its
  cause. The runner matches only both complete lines with these counts under Dummy;
  different counts and the same lines under WASAPI remain failures.

The complete external runner directory remains at
`C:\tmp\ft\lanes\s14-audio\run05` on the measurement workstation. It is not a
portable project artifact. The committed summary is sufficient to reproduce and
review the bounded claims in [the S14 record](../s14.md).
