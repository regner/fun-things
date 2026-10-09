# S12 retained evidence

Canonical measurements were replaced after review round 1 and produced on Windows 11
with pinned Godot `4.8.dev7.official.c971f93e7` after the complete-adverse-profile fix.
The result source manifests bind the exact fixture/tool bytes. The three directories are
independent complete normal/adverse repetitions with fresh ports/output:

| Repetition | Ports | Top-level receipt |
| --- | --- | --- |
| canonical01 | 25310 / 25311 | [result](canonical01/result.json) |
| canonical02 | 25320 / 25321 | [result](canonical02/result.json) |
| canonical03 | 25330 / 25331 | [result](canonical03/result.json) |

Each profile retains:

- `result.json`: commands, process IDs/exits, source SHA-256s, load snapshot, explicit
  criteria and independently analyzed measurements;
- `host.log` / `client.log`: structured `S12` runtime receipts and engine startup;
- `proxy.jsonl`: actual seeded native UDP deliveries/drops/delays.

Every adverse result asserts one proxy blackout begin/end, traffic dropped during that
one-second interruption, and one observed host stall of at least 250 ms while the
96-shot/rocket schedule remains active. Blackout drop counts were 38/35/37 and observed
host stalls were 265/278/266 ms. Every profile also asserts the three probe-specific
verdicts independently: duplicate sequence 96 `STALE_SEQUENCE`, nonfinite sequence 97
`INVALID`, and oversized sequence 98 `INVALID`.

[`aggregate.json`](aggregate.json) contains the exact cross-repetition medians, worst
values, interruption/stall observations and probe reasons quoted by the main
[S12 record](../s12.md). [`manifest.sha256`](manifest.sha256) hashes the 27 canonical
raw files. Staged projects, private user directories, import logs and scratch debug runs
remain outside the repository under `C:/tmp/ft/lanes/s12-combat/`; they are not required
to recalculate the committed analyzer output.

All timing is labeled **contended upper bound** because the pre-case inventory found
4–13 concurrent Godot-named processes. CPU load snapshots ranged 0–77%; the Windows
instantaneous 0% observation does not establish an idle machine. A quiet rerun can use
the one command in the main record.

The earlier committed evidence measured adverse delay/jitter/loss but ended before the
S03 proxy interruption and had no host stall. Review round 1 rejected it. These six
replacement cases supersede those measurements; all passed the strengthened runner
criteria. Debug failures and superseded evidence remain outside the repository rather
than being represented as accepted results.
