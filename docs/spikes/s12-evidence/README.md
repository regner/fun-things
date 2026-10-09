# S12 retained evidence

Canonical measurements were produced on Windows 11 with pinned Godot
`4.8.dev7.official.c971f93e7` after commit `e1771e7` (fixture cadence fix). The
three directories are independent complete repetitions with fresh ports/output:

| Repetition | Ports | Top-level receipt |
| --- | --- | --- |
| canonical01 | 25240 / 25241 | [result](canonical01/result.json) |
| canonical02 | 25250 / 25251 | [result](canonical02/result.json) |
| canonical03 | 25260 / 25261 | [result](canonical03/result.json) |

Each profile retains:

- `result.json`: commands, process IDs/exits, source SHA-256s, load snapshot and
  independently analyzed measurements;
- `host.log` / `client.log`: structured `S12` runtime receipts and engine startup;
- `proxy.jsonl`: actual seeded native UDP deliveries/drops/delays.

[`aggregate.json`](aggregate.json) contains the exact cross-repetition medians,
worst values and totals quoted by the main [S12 record](../s12.md).
[`manifest.sha256`](manifest.sha256) hashes the 27 canonical raw files. Staged
projects, private user directories, import logs and scratch debug/failure runs remain
outside the repository under `C:/tmp/ft/lanes/s12-combat/`; they are not required to
recalculate the committed analyzer output.

All timing is labeled **contended upper bound** because the pre-case inventory found
3–7 concurrent Godot-named processes. CPU load snapshots ranged 0–91%; the Windows
instantaneous 0% observation does not establish an idle machine. A quiet rerun can
use the one command in the main record.

The full runner completed all six canonical profile cases. An earlier debug normal
run exposed probe-accounting deadlock and an early second repetition showed adverse
sample-count instability at 125 ms client cadence. Both failures were retained only
outside the repository; the fixes changed fixture accounting/cadence before these
canonical repetitions, not analyzer formulas or acceptance thresholds.
