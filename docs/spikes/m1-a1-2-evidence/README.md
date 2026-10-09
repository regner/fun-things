# M1-A1.2 retained evidence

The final reviewable receipts for this row are retained here; full runner output remains outside the
worktree under `C:/tmp/ft/lanes/m1-a1-2/`.

| File | Evidence |
| --- | --- |
| `real-process-summary.json` | Ten bounded ENet loopback admission/rejection/raw-auth-abuse/cleanup cases and exits |
| `admitted-host.log` / `admitted-client.log` | Successful host/client phase, roster, workaround and cleanup receipts |
| `oversized-auth-attacker.log` | One 71,680-byte raw auth send followed by bounded rejection |
| `oversized-auth-host.log` / `oversized-auth-probe.log` | Same host remains healthy and admits the ordinary probe afterward |
| `gut-session.log` | Focused production GUT summary for session state, codec and UI tests |

The loopback matrix proves the production APIs on Windows with pinned Godot
`4.8.dev7.official.c971f93e7`. Every retained `elapsed_seconds` value is a contended workstation
wall-clock diagnostic, not performance evidence. It does not prove external UDP reachability/NAT
traversal, Linux runtime behavior, Match/world admission, gameplay replication or exported-build
networking. The 70 KiB raw authentication case proves application rejection and subsequent healthy
host admission, but Godot exposes no configurable native ENet receive/reassembly ceiling; native
allocation before the raw auth callback remains a release risk. The host/client runs were headless
and capped; no frame-performance claim is made.
