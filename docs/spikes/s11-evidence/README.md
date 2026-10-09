# S11 retained evidence

Canonical measured run: `C:\tmp\ft\lanes\s11-population-net\full-12`, using
Godot `4.8.dev7.official.c971f93e7` on Windows 11. The run used three clients and
three repetitions each of the normal and adverse profiles. Adverse includes both the
one-second bidirectional delivery interruption and deterministic 250 ms host stall.

`result.json` binds the run to clean commit
`f179fddd924d1cb3d871cdedf6b1bf68fb5a0351`, tree
`cbf7a3caeb7d59b7efbb4f4a184145604d21f4c0`, SHA-256 fingerprints for every
staged fixture source, and hashes for `tools/run_s11.py`, its imported
`tools/run_s03.py` cleanup helper, and `tools/script_checks.py`. The runner hash is
`897d4bd87051bcbc79536565c4b9e5f5a51f6bc9fbe54f48b97edd3c584269a8`.

- `result.json`: full commands, identities/fingerprints, process/environment records,
  per-case profile delivery, stall receipts, measurements and process results.
- `summary.json`: derived median/worst tables plus per-case delivered route aggregates
  used by the spike record. These include ingress/delivery counts, random/blackout
  drops, loss rates, actual delay and delay-variation distributions, interruption
  duration, host-stall duration, loopback route identity, delivery-delay guard and
  unexplained-excursion count. Environment sampling runs in a background thread so
  proxy polling continues throughout measurement.
- `console.log`: one-line measurement summaries emitted during the run.
- `probe.log`: public API codec and population-policy checks.

The raw external directory additionally retains isolated projects, private user
folders, engine/stdout logs, and each proxy's datagram schedule. Failed development
attempts and superseded runs remain separately under
`C:\tmp\ft\lanes\s11-population-net\full-01` through `full-11`; they are not accepted
measurements. Early runs exposed teardown windows; `full-09` omitted the required
host stall, `full-10` preceded retained delay-variation accounting, and `full-11`
blocked proxy polling during synchronous environment observation. The final fixture
retains a bounded retransmission window, completes clients on authoritative close,
and `full-12` completed all six cases without engine/script diagnostics or unexplained
delivery-delay excursions.
