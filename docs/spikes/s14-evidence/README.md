# S14 retained evidence

`run04-summary.json` is the complete structured receipt for the accepted local run.
It includes the exact commands, source SHA-256 manifest, settings roundtrips, category
voice counts, environment sample before every case, and aggregate context timings.

- `run04-import.log`: clean isolated-project import on Godot 4.8-dev7.
- `run04-headless-1.log`: representative final Dummy-driver run with no diagnostics.
- `run04-windowed-1.log`: representative final WASAPI windowed run with no diagnostics.
- `run02-dummy-teardown.log`: earlier committed-source Dummy run retaining the pinned
  engine's intermittent, exact audio-playback teardown diagnostics. The runner
  reports these separately and does not broadly suppress diagnostics.

The complete external runner directory remains at
`C:\tmp\ft\lanes\s14-audio\run04` on the measurement workstation. It is not a
portable project artifact. The committed summary is sufficient to reproduce and
review the bounded claims in [the S14 record](../s14.md).
