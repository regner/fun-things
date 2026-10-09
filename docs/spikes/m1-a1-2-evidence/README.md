# M1-A1.2 retained evidence

The final reviewable receipts for this row are retained here; full runner output remains outside the
worktree under `C:/tmp/ft/lanes/m1-a1-2/`.

| File | Evidence |
| --- | --- |
| `real-process-summary.json` | Seven bounded ENet loopback admission/rejection/cleanup cases and exits |
| `admitted-host.log` / `admitted-client.log` | Successful host/client phase, roster, workaround and cleanup receipts |
| `gut-session.log` | Focused production GUT summary for session state and UI tests |

The loopback matrix proves the production APIs on Windows with pinned Godot
`4.8.dev7.official.c971f93e7`. It does not prove external UDP reachability/NAT traversal, Linux runtime
behavior, Match/world admission, gameplay replication or exported-build networking. The host/client
runs were headless and capped; no frame-performance claim is made.
