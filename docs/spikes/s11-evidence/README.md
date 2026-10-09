# S11 retained evidence

Canonical measured run: `C:\tmp\ft\lanes\s11-population-net\full-09`, using
Godot `4.8.dev7.official.c971f93e7` on Windows 11. The run used three clients,
three repetitions each of the normal and adverse profiles, and source fingerprints
embedded in `result.json`.

- `result.json`: full commands, fingerprints, process/environment records, per-case
  measurements and process results.
- `summary.json`: derived median/worst tables used by the spike record.
- `console.log`: one-line measurement summaries emitted during the run.
- `probe.log`: public API codec and population-policy checks.

The raw external directory additionally retains isolated projects, private user
folders, engine/stdout logs, and each proxy's datagram schedule. Failed development
attempts remain separately under `C:\tmp\ft\lanes\s11-population-net\full-01` through
`full-08`; they are not accepted measurements. They exposed teardown windows that
could close before adverse reliable retransmission completed. The final fixture
retains a bounded retransmission window, completes clients on authoritative close,
and `full-09` completed all six cases without engine/script diagnostics.
