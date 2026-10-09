# S11 retained evidence

Canonical measured run: `C:\tmp\ft\lanes\s11-population-net\full-11`, using
Godot `4.8.dev7.official.c971f93e7` on Windows 11. The run used three clients and
three repetitions each of the normal and adverse profiles. Adverse includes both the
one-second bidirectional delivery interruption and deterministic 250 ms host stall.

`result.json` binds the run to clean commit
`43ed816642a83ae7d230569eb4d1f77bd3409de1`, tree
`5adbc14ce6447b52e5d035bd2d9cc6a408776afd`, SHA-256 fingerprints for every
staged fixture source, and hashes for `tools/run_s11.py`, its imported
`tools/run_s03.py` cleanup helper, and `tools/script_checks.py`. The runner hash is
`81a3491cc30205cf38b42ded2f9ff8f68f603e3e46822d940715bc5741e242ff`.

- `result.json`: full commands, identities/fingerprints, process/environment records,
  per-case profile delivery, stall receipts, measurements and process results.
- `summary.json`: derived median/worst tables plus per-case delivered route aggregates
  used by the spike record. These include ingress/delivery counts, random/blackout
  drops, loss rates, actual delay and delay-variation distributions, interruption
  duration, host-stall duration and loopback route identity.
- `console.log`: one-line measurement summaries emitted during the run.
- `probe.log`: public API codec and population-policy checks.

The raw external directory additionally retains isolated projects, private user
folders, engine/stdout logs, and each proxy's datagram schedule. Failed development
attempts and superseded runs remain separately under
`C:\tmp\ft\lanes\s11-population-net\full-01` through `full-10`; they are not accepted
measurements. Early runs exposed teardown windows; `full-09` omitted the required
host stall, and `full-10` preceded retained delay-variation accounting. The final
fixture retains a bounded retransmission window, completes clients on authoritative
close, and `full-11` completed all six cases without engine/script diagnostics.
