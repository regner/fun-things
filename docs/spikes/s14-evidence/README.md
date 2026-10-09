# S14 retained evidence

`run02-summary.json` is the complete structured receipt for the accepted local run.
It includes the exact commands, source SHA-256 manifest, settings roundtrips, category
voice counts, environment sample before every case, and aggregate context timings.

- `run02-import.log`: clean isolated-project import on Godot 4.8-dev7.
- `run02-headless-1.log`: representative Dummy-driver run. It retains the pinned
  engine's intermittent, exact audio-playback teardown diagnostics; the runner
  reports these separately and does not broadly suppress diagnostics.
- `run02-windowed-1.log`: representative WASAPI windowed run with no diagnostics.

The complete external runner directory remains at
`C:\tmp\ft\lanes\s14-audio\run02` on the measurement workstation. It is not a
portable project artifact. The committed summary is sufficient to reproduce and
review the bounded claims in [the S14 record](../s14.md).
